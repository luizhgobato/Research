// ══════════════════════════════════════════════════════════════════════════════════════════
// COTAÇÕES — Yahoo Finance primeiro, brapi como reserva  (20/09/2026)
// ══════════════════════════════════════════════════════════════════════════════════════════
// Pedido do usuário: "no radar o atualizar cotação não está funcionando. Coloque pra pegar a
// cotação do yahoo finance".
//
// O botão NUNCA esteve quebrado — verificado no browser: `atualizarCotacoes` existe, o
// onclick dispara, as 15 funções de que ela depende estão todas definidas e o console fica
// limpo. O que falhava era FONTE, e o desenho anterior falhava de quatro jeitos ao mesmo
// tempo:
//
//  1 · A BUSCA DO RADAR NEM CHEGAVA NO YAHOO. `fetchCotacoesBatch` (brapi) resolvia os 35
//      tickers e só quem voltasse vazio caía no `fetchCotacao` (Yahoo). Com a brapi fora do
//      ar ou o token estourado, os 35 caíam de uma vez no fallback — 35 × 2 URLs × 3 proxies
//      = até 210 requisições disparadas juntas, o que derruba qualquer proxy gratuito por
//      rate limit. O fallback morria por excesso de uso do próprio fallback.
//  2 · O `corsproxy.io` ESTAVA NA FORMA DEPRECADA. `https://corsproxy.io/?<url>` deixou de
//      existir; a forma viva é `?url=<url>`. O proxy respondia erro em 100% das chamadas.
//  3 · PROXY MORTO CUSTAVA O TEMPO TODO. Sem memória de falha, um proxy fora do ar era
//      tentado de novo para cada um dos 35 tickers — 35 timeouts de 7s enfileirados antes de
//      passar para o próximo. A atualização parecia travada porque, em termos práticos,
//      estava.
//  4 · `carteira-manual.js` CHAMA `fetchCotacoesBatch` E SÓ TINHA BRAPI. As carteiras da
//      Flávia e do Luiz não tinham fallback nenhum: brapi fora, cotação fora.
//
// O conserto é de SEAM, não de remendo: `fetchCotacao` passa a ser a única definição de "onde
// se busca preço" e `fetchCotacoesBatch` vira só a versão em lote dela. Uma definição, três
// consumidores (radar, carteiras manuais, fundamentos) — a lição que este projeto reaprendeu
// em cada seção da metodologia.

// Yahoo não manda `Access-Control-Allow-Origin` no v8/chart, então o browser precisa de um
// intermediário. A tentativa DIRETA vem primeiro mesmo assim: custa uma requisição e funciona
// quando a página roda como arquivo local ou de dentro de uma extensão.
const YF_HOSTS = ['query1.finance.yahoo.com', 'query2.finance.yahoo.com'];

// ⚠️ v8/finance/chart é de propósito. O endpoint v7/finance/quote, mais óbvio, exige `crumb`
// + cookie de sessão desde 2023 e responde 401 para chamada anônima. O v8/chart continua
// aberto e traz `meta.regularMarketPrice`.
const yfUrl = (host, t) => `https://${host}/v8/finance/chart/${encodeURIComponent(t)}?interval=1d&range=1d`;

const COT_PROXIES = [
  {nome: 'direto',     url: u => u},
  {nome: 'allorigins', url: u => `https://api.allorigins.win/raw?url=${encodeURIComponent(u)}`},
  {nome: 'codetabs',   url: u => `https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(u)}`},
  {nome: 'corsproxy',  url: u => `https://corsproxy.io/?url=${encodeURIComponent(u)}`},
  {nome: 'jina',       url: u => `https://r.jina.ai/${u}`},
];

// Diagnóstico exposto de propósito: `COT_DIAG` no console do browser diz, por ticker, qual
// fonte respondeu e o que cada uma devolveu. Sem isso, "não está funcionando" não tem como
// virar causa — foi exatamente o que faltou para achar os quatro bugs acima.
const COT_DIAG = [];
const _cotMortos = new Set();   // proxies que já falharam demais NESTA rodada

function _precoDoTexto(txt){
  // Tenta JSON; se o proxy embrulhou, envelopou ou cuspiu texto, cai na extração por regex.
  // Proxy gratuito mexe no corpo com frequência e perder a cotação por causa do invólucro
  // seria desperdiçar uma resposta que veio certa.
  try{
    const j = JSON.parse(txt);
    const m = j?.chart?.result?.[0]?.meta;
    const p = m?.regularMarketPrice ?? m?.previousClose;
    if(p > 0) return p;
    if(j?.contents){ return _precoDoTexto(j.contents); }   // envelope do allorigins /get
  }catch{}
  const m = txt.match(/"regularMarketPrice"\s*:\s*([0-9.]+)/);
  if(m && parseFloat(m[1]) > 0) return parseFloat(m[1]);
  return null;
}

const _espera = ms => new Promise(r => setTimeout(r, ms));

// ⚠️ 429 NÃO É "PROXY MORTO" — 20/09/2026, com a tela do usuário na mão. A primeira versão
// somava qualquer falha e matava o proxy na terceira: com `direto`, `allorigins`, `codetabs`
// e `corsproxy` fora do ar, o `jina` era O ÚNICO caminho vivo, e o limite de requisições dele
// respondia 429 para as chamadas simultâneas — três 429 e a régua executava o único proxy que
// estava funcionando. Resultado: "31 ok · 4 erros". Limite de uso pede ESPERA, não execução.
const _limitado = e => /\b(429|503|502|504|rate|limit)\b/i.test(String(e && e.message || e));

async function _tentar(url, ms){
  const res = await fetch(url, {signal: AbortSignal.timeout(ms)});
  if(!res.ok) throw new Error('HTTP ' + res.status);
  return _precoDoTexto(await res.text());
}

// Preço de UM ticker. Yahoo (direto → proxies) e, só se tudo falhar, brapi.
async function fetchCotacao(ticker){
  for(const px of COT_PROXIES){
    if(_cotMortos.has(px.nome)) continue;
    for(const host of YF_HOSTS){
      try{
        // 12s, não 7s: dois saltos (browser → proxy → Yahoo) não cabem em sete segundos e o
        // timeout curto estava matando resposta que ia chegar.
        const p = await _tentar(px.url(yfUrl(host, ticker)), 12000);
        if(p){ COT_DIAG.push({ticker, fonte: 'yahoo/' + px.nome, preco: p}); return p; }
      }catch(e){
        COT_DIAG.push({ticker, fonte: 'yahoo/' + px.nome, erro: String(e.message || e)});
        if(_limitado(e)){
          // Estourou o limite do proxy: espera e tenta de novo NESTE mesmo, com recuo
          // crescente. Não conta para a régua de morte e não desiste do ticker.
          for(const atraso of [900, 2200, 4500]){
            await _espera(atraso);
            try{
              const p = await _tentar(px.url(yfUrl(host, ticker)), 12000);
              if(p){ COT_DIAG.push({ticker, fonte: 'yahoo/' + px.nome, preco: p, esperou: atraso}); return p; }
            }catch(e2){ if(!_limitado(e2)) break; }
          }
          break;
        }
        // Falha DURA (rede, TLS, 404, timeout) em 3 tickers diferentes: o proxy está fora do
        // ar e não vale gastar os 32 restantes nele.
        const duras = COT_DIAG.filter(d => d.fonte === 'yahoo/' + px.nome && d.erro && !_limitado(d.erro)).length;
        if(duras >= 3) _cotMortos.add(px.nome);
        break;   // host alternativo do Yahoo não ajuda se o problema é o proxy
      }
    }
  }
  // Reserva: brapi. Fica por último por dois motivos — o usuário pediu o Yahoo, e o achado
  // de 17/09/2026 (commit c895971, sessão paralela): o plano grátis tem teto de 15.000
  // requisições/mês a 1 ticker por requisição, e 35 tickers por clique estouram a cota rápido
  // com uso normal. ⚠️ E quando estoura, FALHA EM SILÊNCIO: o `catch` apenas deixa de
  // preencher o mapa e a tabela parava de atualizar sem mensagem nenhuma. Por isso toda
  // falha aqui agora vira linha no COT_DIAG, com o status HTTP.
  // Continua no fim da fila porque já salvou o dia quando o Yahoo mudou endpoint.
  try{
    const res = await fetch(`https://brapi.dev/api/quote/${ticker.replace('.SA','')}?token=${BRAPI_TOKEN}`,
                            {signal: AbortSignal.timeout(12000)});
    if(res.ok){
      const r = (await res.json())?.results?.[0];
      if(r?.regularMarketPrice > 0){
        COT_DIAG.push({ticker, fonte: 'brapi', preco: r.regularMarketPrice});
        return r.regularMarketPrice;
      }
    }
    COT_DIAG.push({ticker, fonte: 'brapi', erro: 'HTTP ' + res.status});
  }catch(e){ COT_DIAG.push({ticker, fonte: 'brapi', erro: String(e.message || e)}); }
  return null;
}

// Lote com LIMITE DE PARALELISMO. `Promise.all` sobre 35 tickers é o que derrubava os proxies
// gratuitos: eles cortam em poucas requisições por segundo e devolvem 429 para o resto. Seis
// por vez atravessa; trinta e cinco de uma vez não.
// ⚠️ APELIDO, nao uma segunda implementacao. A sessao paralela de 17/09/2026 criou
// `fetchCotacoesBatchYahoo` para rodar o Yahoo antes da brapi; aqui a ordem das fontes ja
// vive dentro de `fetchCotacao`, entao o nome aponta para a mesma funcao em vez de duplicar
// a logica. Duas implementacoes de "buscar preco" foi exatamente o que deixou as carteiras
// manuais sem fallback.
async function fetchCotacoesBatch(tickers, aoResolver){
  // Estado de rodada zerado AQUI, não no radar: os três consumidores (radar, carteiras
  // manuais, fundamentos) passam por esta função, e um proxy marcado como morto numa busca
  // de dez minutos atrás não deve condenar a próxima.
  COT_DIAG.length = 0; _cotMortos.clear();
  const map = {}, fila = [...tickers];
  const trabalhador = async () => {
    for(let t = fila.shift(); t !== undefined; t = fila.shift()){
      const p = await fetchCotacao(t);
      if(p){ map[t] = p; }
      if(aoResolver) aoResolver(t, p, tickers.length - fila.length, tickers.length);
    }
  };
  await Promise.all(Array.from({length: Math.min(6, tickers.length)}, trabalhador));

  // ── SEGUNDA PASSADA, DEVAGAR ──────────────────────────────────────────────────────────
  // Quem falhou na primeira quase sempre falhou por concorrência, não por não existir: seis
  // pedidos ao mesmo tempo estouram o limite do proxy e alguns tickers levam o 429. Refazer
  // os que faltaram UM A UM, com pausa, recupera a maioria — foi a diferença entre "31 ok ·
  // 4 erros" e a tabela inteira. Só os que sobraram, então o custo é proporcional ao estrago.
  const faltaram = tickers.filter(t => !map[t]);
  if(faltaram.length && faltaram.length < tickers.length){
    for(const t of faltaram){
      await _espera(700);
      const p = await fetchCotacao(t);
      if(p){ map[t] = p; if(aoResolver) aoResolver(t, p, tickers.length, tickers.length, true); }
    }
  }
  return map;
}

function margemTag(pct){
  if(pct===null) return '<span class="muted">—</span>';
  const fmt=(pct>=0?'+':'')+pct.toFixed(0)+'%';
  if(pct>=10) return `<span class="tag tag-green">${fmt}</span>`;
  if(pct>=0)  return `<span class="tag tag-blue">${fmt}</span>`;
  return `<span class="tag tag-red">${fmt}</span>`;
}
// Aplica o preço numa linha do radar e recalcula todos os indicadores derivados
function aplicarPrecoRadar(row, preco){
  const ticker=row.dataset.ticker;
  const cotacaoCell=row.querySelector('.cotacao-cell'),margemCell=row.querySelector('.margem-cell'),cells=row.querySelectorAll('td');
  // Captura cotação e DY antigos ANTES de atualizar a célula
  const _oldCot=parseFloat((cells[20]?.textContent||'').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
  const _oldDy =parseFloat(row.dataset.dyProj) || 0;
  cotacaoCell.classList.remove('loading','error');
  cotacaoCell.classList.add('updated');
  cotacaoCell.textContent=`R$ ${preco.toFixed(2).replace('.',',')}`;
  // Preserva DPS real: novo DY% = DPS / novo preço (DPS = dyProj_antigo × cotacao_antiga)
  if(_oldDy>0&&_oldCot>0&&preco>0) row.dataset.dyProj=(_oldDy*_oldCot/preco).toFixed(4);
  // Atualiza células de DY proj
  atualizarDivDY(row, preco);   // DPS = LPA × payout; DY = DPS ÷ preço (js/calculos.js)
  // ⚠️ DOIS BUGS AQUI, e o primeiro escondia o segundo — 14/09/2026, pergunta do usuário:
  // "à medida que as cotações forem alteradas, os valores vão atualizar correto e as margens
  // de segurança também?" Não iam.
  //
  //  1 · `row.dataset.precoTeto` NÃO EXISTE MAIS. O campo virou `precoJusto` quando "preço
  //      teto" saiu do projeto (seção 30), e esta leitura ficou para trás. `precoTeto` saía
  //      sempre null, a condição do `if` nunca era verdadeira e A MARGEM NUNCA RECALCULAVA:
  //      a cotação mudava na tela e a margem continuava a do último build. Reproduzido com o
  //      ITUB3 — cotação de R$ 41,66 para R$ 30,00 e a margem parada em +11%.
  //  2 · `dyProj` NÃO ESTÁ DEFINIDO neste escopo. Se o `if` do item 1 algum dia fosse
  //      verdadeiro, a linha lançaria ReferenceError e a atualização inteira morreria ali.
  //      O bug 1 mantinha o bug 2 dormente — por isso nunca apareceu erro no console.
  //
  // O caminho certo já existia em calcularDerivadosRadar() (js/calculos.js): lê precoJusto do
  // dataset e dyProj da linha. Aqui passa a fazer o mesmo.
  calcularPrecoJusto(row, preco);
  const precoJusto = parseFloat(row.dataset.precoJusto) || 0;
  const dyProj     = parseFloat(row.dataset.dyProj) || 0;
  const qtd=parseFloat(row.dataset.qtd)||0,pm=parseFloat(row.dataset.pm)||0;
  if(qtd>0){
    row.dataset.saldo=(qtd*preco).toFixed(2);
    if(pm>0)row.dataset.rent=(((preco-pm)/pm)*100>=0?'+':'')+((preco-pm)/pm*100).toFixed(2);
  }
  if(margemCell && precoJusto > 0){
    renderMargemRetorno(cells, margemCell, precoJusto, preco, dyProj);
  }
  if(typeof atualizarPLAtualLinha==='function') atualizarPLAtualLinha(row);
}

async function atualizarCotacoes(){
  const btn=document.getElementById('btnUpdate'),statusEl=document.getElementById('updateStatus'),statusText=document.getElementById('updateText');
  btn.disabled=true;btn.classList.add('loading');statusText.textContent='Buscando...';statusEl.className='update-status';
  const arr=Array.from(document.querySelectorAll('#tableBody tr[data-ticker]'));
  arr.forEach(r=>{const c=r.querySelector('.cotacao-cell');if(c){c.classList.add('loading');c.textContent='...';}});
  let ok=0,errs=0;

  // UMA passada só. A versão anterior fazia brapi para todos e DEPOIS Yahoo para quem
  // sobrasse; agora a ordem das fontes (Yahoo → proxies → brapi) vive dentro de
  // `fetchCotacao` e o lote apenas a executa com 6 em paralelo. Cada linha se resolve na
  // fonte que responder primeiro, sem esperar o lote inteiro falhar antes de tentar a
  // reserva.
  const porTicker=Object.fromEntries(arr.map(r=>[r.dataset.ticker,r]));
  await fetchCotacoesBatch(arr.map(r=>r.dataset.ticker),(t,p,feitos,total,repescado)=>{
    const row=porTicker[t]; if(!row) return;
    if(p){
      aplicarPrecoRadar(row,p);ok++;
      if(repescado){errs--;}   // já tinha contado como erro na primeira passada
    }
    else{
      const c=row.querySelector('.cotacao-cell');
      c.classList.remove('loading');c.classList.add('error');c.textContent='Erro';errs++;
      // ⚠️ SEM COTAÇÃO, SEM MARGEM. A margem que ficava na tela era a do último build,
      // calculada contra um preço que a linha não mostra mais — a Bradsaúde exibia "Erro" ao
      // lado de "−327%", número que não corresponde a nada visível. Número órfão ao lado de
      // um erro é pior que campo vazio: parece dado.
      // ⚠️ O Retorno Total é a VIZINHA da margem, não a célula 22. Escrever o índice aqui
      // repetiria o erro que a seção 43 da metodologia acabou de arrancar do gerador: índice
      // decorado é a aposta de que o layout nunca muda, e ele mudou três vezes numa semana.
      const m=row.querySelector('.margem-cell');
      if(m){
        m.innerHTML='<span class="muted">—</span>';
        const ret=m.nextElementSibling;
        if(ret) ret.innerHTML='<span class="muted">—</span>';
      }
    }
    // A linha atualiza assim que a resposta chega, em vez de tudo de uma vez no fim: com
    // seis por vez os 35 levam alguns segundos e a tela parada não dizia se estava andando.
    statusText.textContent=`Buscando… ${feitos}/${total}`;
  });
  // ── RECALCULA KPI CARDS ──
  recalcularKPIs();
  btn.disabled=false;btn.classList.remove('loading');
  const agora=new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  statusEl.className=errs===0?'update-status ok':'update-status err';
  // Qual fonte de fato respondeu entra na mensagem. "35 cotações" não distingue Yahoo de
  // brapi, e era justamente essa distinção que faltava para saber o que tinha caído.
  const fontes=[...new Set(COT_DIAG.filter(d=>d.preco).map(d=>d.fonte))].join(', ');
  let msg=errs===0?`${ok} cotações às ${agora}`:`${ok} ok · ${errs} erros · ${agora}`;
  if(fontes) msg+=` · via ${fontes}`;
  // Zero cotações é problema de FONTE, não do botão — e o usuário precisa saber onde olhar.
  if(ok===0) msg=`Nenhuma fonte respondeu às ${agora} — veja COT_DIAG no console (F12)`;
  statusText.textContent=msg;
  const lu=document.getElementById('lastUpdate');const sd=document.getElementById('statusDot');
  if(lu)lu.textContent=msg;
  if(sd){sd.className='nav-status-dot '+(errs===0?'ok':'err');}
  // ── RERENDER TUDO ──
  renderPosicoes();renderMobileCards();
  buildCharts();buildDivProjChart();renderDivProjTable();
  calcularDerivadosRadar();
  // Salvar cache
  const cache={};document.querySelectorAll('#tableBody tr[data-ticker]').forEach(r=>{const c=r.querySelector('.cotacao-cell');if(c&&c.textContent!=='...'&&c.textContent!=='Erro'&&c.textContent!=='—')cache[r.dataset.ticker]=c.textContent;});
  try{localStorage.setItem('cotacoes_cache',JSON.stringify({ts:Date.now(),data:cache}));}catch(e){sessionStorage.setItem('cotacoes_cache',JSON.stringify({ts:Date.now(),data:cache}));}
}

function recalcularKPIs(){
  // Soma saldos de ações B3 (data-carteira=true, são ações)
  const carteiraRows = getCarteiraRows();
  const totalAcoes = carteiraRows.reduce((s,r)=>s+(parseFloat(r.dataset.saldo)||0),0);
  // Patrimônio total = ações + outros investimentos fixos
  const outrosFixo = 126826 + 72076 + 9695; // Previdência + RF + ETF Int.
  const totalPatr = totalAcoes + outrosFixo;
  // Atualiza KPI Ações B3
  const kpiAcoes = document.querySelector('.kpi-card:nth-child(2) .kpi-val');
  if(kpiAcoes){
    const pctAcoes=(totalAcoes/totalPatr*100).toFixed(1);
    kpiAcoes.innerHTML=`<span class="valor-rs">R$ ${Math.round(totalAcoes).toLocaleString('pt-BR')}</span><span class="valor-pct">${pctAcoes}%</span>`;
  }
  // Atualiza KPI Patrimônio Total
  const kpiPatr = document.querySelector('.kpi-card.accent .kpi-val');
  if(kpiPatr){
    kpiPatr.innerHTML=`<span class="valor-rs">R$ ${Math.round(totalPatr).toLocaleString('pt-BR')}</span><span class="valor-pct">100%</span>`;
  }
  // Atualiza subtítulo do header
  const sub = document.querySelector('.carteira-header p');
  if(sub) sub.textContent=`Patrimônio total: R$ ${Math.round(totalPatr).toLocaleString('pt-BR')} · Ações + Prev. + Renda Fixa + ETFs · Atualizado agora`;
}

const fetchCotacoesBatchYahoo = fetchCotacoesBatch;
