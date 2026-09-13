// ══════════════════════════════════════════════════════
// BASE DE DADOS — Indicadores Fundamentalistas
// ══════════════════════════════════════════════════════

const BANCOS_TICKERS = ['BBAS3','ITUB3','BRBI11','ITSA4'];
const FUND_CACHE_KEY = 'fund_cache_v3';

// Semáforo: retorna {dot, cls} conforme thresholds [{min,max,color}]
function semaforo(val, rules) {
  if(val === null || val === undefined || isNaN(val)) return {dot:'sem-n', cls:'gray'};
  for(const r of rules){
    const ok = (r.min===undefined||val>=r.min) && (r.max===undefined||val<r.max);
    if(ok) return {dot:`sem-${r.color[0]}`, cls:r.color};
  }
  return {dot:'sem-n', cls:'gray'};
}

const RULES = {
  pl:       [{min:0,max:12,color:'green'},{min:12,max:20,color:'yellow'},{min:20,color:'red'},{max:0,color:'red'}],
  pvp:      [{min:0,max:1.5,color:'green'},{min:1.5,max:3,color:'yellow'},{min:3,color:'red'}],
  dy:       [{min:8,color:'green'},{min:4,max:8,color:'yellow'},{max:4,color:'red'}],
  roe:      [{min:20,color:'green'},{min:10,max:20,color:'yellow'},{max:10,color:'red'}],
  mgLiq:    [{min:15,color:'green'},{min:5,max:15,color:'yellow'},{max:5,color:'red'}],
  mgBruta:  [{min:30,color:'green'},{min:15,max:30,color:'yellow'},{max:15,color:'red'}],
  mgEbitda: [{min:20,color:'green'},{min:10,max:20,color:'yellow'},{max:10,color:'red'}],
  evEbitda: [{min:0,max:8,color:'green'},{min:8,max:15,color:'yellow'},{min:15,color:'red'}],
  divPl:    [{max:1,color:'green'},{min:1,max:3,color:'yellow'},{min:3,color:'red'}],
  roic:     [{min:15,color:'green'},{min:8,max:15,color:'yellow'},{max:8,color:'red'}],
  margSeg:  [{min:10,color:'green'},{min:0,max:10,color:'yellow'},{max:0,color:'red'}],
};

function fmtVal(v, digits=2, suffix='') {
  if(v===null||v===undefined||isNaN(v)) return '<span class="fund-val gray">—</span>';
  return `${v.toFixed(digits).replace('.',',')}${suffix}`;
}
function fmtMoney(v) {
  if(v===null||v===undefined||isNaN(v)) return '<span class="fund-val gray">—</span>';
  const abs=Math.abs(v), neg=v<0?'-':'';
  if(abs>=1e12) return `<span class="fund-val">R$ ${neg}${(abs/1e12).toFixed(2).replace('.',',')} tri</span>`;
  if(abs>=1e9)  return `<span class="fund-val">R$ ${neg}${(abs/1e9).toFixed(2).replace('.',',')} bi</span>`;
  return        `<span class="fund-val">R$ ${neg}${(abs/1e6).toFixed(0)} mi</span>`;
}

function semCell(val, ruleKey, digits=1, suffix='') {
  if(val===null||val===undefined||isNaN(val)) return '<span class="fund-val gray">—</span>';
  const s = semaforo(val, RULES[ruleKey]);
  return `<div class="fund-cell"><span class="sem ${s.dot}"></span><span class="fund-val ${s.cls}">${val.toFixed(digits).replace('.',',')}${suffix}</span></div>`;
}

// ── COLUNAS FUNDAMENTALISTAS NO RADAR ──────────────────────────────────────

// Adiciona classes CSS às células "reais" do Radar (DY, P/L, ROE, Dív/EBITDA)
// para poder atualizá-las com dados do fundamentus sem depender de índice de coluna.
function initRadarRealCells() {
  // ⚠️ dyReal SAIU do mapa em 13/09/2026. A coluna que ela marcava virou "Div. Yield 2025",
// gerada de data/historico.data.js como todo o resto. Sem a classe .radar-dy-real, o bloco
// de runtime mais abaixo não acha a célula e não reescreve nada — que é o comportamento
// desejado: aquele bloco sobrepunha o valor da API por cima de um número digitado à mão, e
// nenhum dos dois vinha da base que alimenta a tabela.
  const COL = { plAtual:12, roe:13, divEbitda:14 };  // layout de 20 colunas (13/09/2026)
  document.querySelectorAll('#tableBody tr[data-ticker]').forEach(row => {
    const cells = row.querySelectorAll('td');
    cells[COL.plAtual]?.classList.add('radar-pl-atual');
    cells[COL.roe]?.classList.add('radar-roe-real');
    cells[COL.divEbitda]?.classList.add('radar-div-eb-real');
  });
}

function initRadarFundCols() { /* removido — colunas duplicadas eliminadas */ }

// ── P/L ATUAL: recalculado a partir de LPA LTM travado (data-lpa-ltm), não hardcoded ──────
// Um P/L digitado direto de agregador (StatusInvest etc.) fica errado assim que a cotação se
// move — no dia seguinte já não bate mais. LPA LTM muda pouco (só a cada resultado
// trimestral), então travamos ELE no <tr> (data-lpa-ltm + data-lpa-fonte) e recalculamos
// P/L = cotação ao vivo ÷ LPA LTM toda vez que a cotação atualiza — mesmo padrão já usado
// para Preço Teto/Margem/Retorno (ver aplicarPrecoRadar em js/cotacoes.js). Número e tooltip
// são regenerados juntos a cada chamada, então a tooltip nunca mais fica órfã/quebrada.
// Tickers sem data-lpa-ltm mantêm o texto estático do HTML porque o P/L não deve ser
// calculado ali: setor não usa P/L (ALOS3/shoppings), proibido pela metodologia (IRBR3/
// resseguradora — P/L de 1 ano é enganoso para lucro estruturalmente volátil), ou fontes
// divergentes demais para uma leitura única (BMEB4 — ver relatório, faixa 9,4x-12,2x).
function atualizarPLAtualLinha(row) {
  const lpaLtm = parseFloat(row.dataset.lpaLtm);
  const plCell = row.querySelector('.radar-pl-atual');
  if (!plCell) return;
  // LPA LTM NEGATIVO: a AURE3 e a SHUL4 saíam com a célula sem ⓘ porque a função abortava
  // antes de escrever. P/L sobre prejuízo não é múltiplo — é um número que muda de sinal e
  // engana quem ordena a coluna. Declara a ausência em vez de sair calado.
  if (!lpaLtm) {
    plCell.innerHTML = '<span style="color:#9ca3af">—</span><span class="col-tip" data-tip="P/L não calculável: a linha não tem LPA LTM na base.&#10;Fonte: MCP Partnr (B3/CVM).">ⓘ</span>';
    return;
  }
  if (lpaLtm <= 0) {
    plCell.innerHTML = '<span style="color:#9ca3af">—</span><span class="col-tip" data-tip="P/L NÃO CALCULÁVEL — a empresa tem PREJUÍZO no LTM (LPA R$ ' + lpaLtm.toFixed(2).replace('.', ',') + ').&#10;&#10;P/L sobre lucro negativo não é múltiplo: o número muda de sinal e fica maior quanto MENOR o prejuízo, o que inverte a leitura de quem ordena a coluna. Célula vazia é melhor que número enganoso.&#10;Fonte: MCP Partnr (B3/CVM), TTM 2T26.">ⓘ</span>';
    return;
  }
  const cotCell = row.querySelector('.cotacao-cell');
  const preco = parseFloat((cotCell?.textContent || '').replace(/[^0-9,.-]/g, '').replace(',', '.'));
  if (!preco || preco <= 0) return;
  const pl = preco / lpaLtm;
  const fonte = row.dataset.lpaFonte || '';
  const tip = `Cotação R$ ${preco.toFixed(2).replace('.', ',')} ÷ LPA LTM R$ ${lpaLtm.toFixed(2).replace('.', ',')}${fonte ? ' — ' + fonte : ''}. Recalculado automaticamente a cada atualização de cotação (LPA travado até o próximo resultado trimestral).`;
  plCell.innerHTML = `${pl.toFixed(1).replace('.', ',')}x<span class="col-tip" data-tip="${tip.replace(/"/g, '&quot;')}">ⓘ</span>`;
  plCell.style.cssText = pl <= 0 ? 'color:#dc2626' : pl <= 12 ? 'color:#059669;font-weight:600' : pl <= 20 ? 'color:#2563eb' : 'color:#dc2626';
}
function atualizarTodosPLAtual() {
  document.querySelectorAll('#tableBody tr[data-ticker][data-lpa-ltm]').forEach(atualizarPLAtualLinha);
}

function calcScoreFund(ticker, d) {
  const isBanco = BANCOS_TICKERS.includes(ticker);
  let score = 0;
  const check = (val, rule) => {
    if (val != null && !isNaN(val) && semaforo(val, RULES[rule]).cls === 'green') score++;
  };
  check(d.pl,     'pl');
  check(d.pvp,    'pvp');
  check(d.dy,     'dy');
  check(d.roe,    'roe');
  check(d.mgLiq,  'mgLiq');
  if (!isBanco && d.evEbitda != null && d.evEbitda > 0) check(d.evEbitda, 'evEbitda');
  if (!isBanco) check(d.divPl, 'divPl');
  return score;
}

function atualizarCelulasRadarFund(ticker, d) {
  const radarRow = document.querySelector(`#tableBody tr[data-ticker="${ticker}.SA"]`);
  if (!radarRow) return;
  // Atualiza células "reais" no corpo do Radar (DY, P/L, ROE, Dív/EBITDA)
  const dyReal    = radarRow.querySelector('.radar-dy-real');
  const plAtual   = radarRow.querySelector('.radar-pl-atual');
  const roeReal   = radarRow.querySelector('.radar-roe-real');
  const divEbReal = radarRow.querySelector('.radar-div-eb-real');
  const fmtPct = v => v.toFixed(1).replace('.',',') + '%';
  const fmtX   = v => v.toFixed(1).replace('.',',') + 'x';
  // Nota: cada bloco abaixo checa "!cell.querySelector('.col-tip')" antes de sobrescrever —
  // se a célula já carrega uma tooltip curada manualmente (fonte específica, ressalva, nota
  // metodológica), o auto-sync de dados da API/HIST_SEED NÃO pode apagá-la (era exatamente
  // isso que quebrava a tooltip: textContent substituía o <span class="col-tip"> inteiro).
  // P/L atual NÃO é mais tocado aqui — ver atualizarPLAtualLinha() (js/fundamentos.js), que
  // recalcula a partir de data-lpa-ltm + cotação ao vivo em vez de um valor estático da API.
  // dy === 0 na base significa AUSÊNCIA de dado, não dividendo zero (CPFE3 paga proventos e
  // vem com 0 no Partnr). Publicar "0,0%" afirma algo falso; "—" declara a lacuna.
  if (dyReal && d.dy != null && d.dy > 0 && !dyReal.querySelector('.col-tip')) {
    // Auditoria 06/09/2026: esta coluna aparecia SEM ⓘ em 24 das 30 linhas. Passa a declarar
    // a fonte na própria célula — a regra do projeto é que todo número exibido diga de onde veio.
    dyReal.innerHTML = `<span style="${d.dy >= 8 ? 'color:#059669;font-weight:600' : d.dy >= 4 ? '' : 'color:#dc2626'}">${fmtPct(d.dy)}</span>` +
      `<span class="col-tip" data-tip="DIVIDEND YIELD REALIZADO (LTM)&#10;&#10;Dividendos pagos nos últimos 12 meses ÷ cotação de fechamento da data-base, direto do campo DIVIDEND_YIELD da base.&#10;Fonte: MCP Partnr (B3/CVM), data-base 30/06/2026.&#10;&#10;É o que a empresa JÁ PAGOU. Não confundir com a coluna Div. Yield PROJ., que é o dividendo projetado (LPA normalizado × payout) sobre a cotação de hoje.">ⓘ</span>`;
  }
  if (dyReal && d.dy === 0 && !dyReal.querySelector('.col-tip')) {
    dyReal.innerHTML = '<span style="color:#9ca3af;">—</span><span class="col-tip" data-tip="A base Partnr devolve DIVIDEND_YIELD = 0 para este ticker, o que aqui significa dado ausente e não dividendo zero. O payout mediano usado na TIR foi calculado com os anos que têm dado.">ⓘ</span>';
  }
  if (roeReal && d.roe != null && !roeReal.querySelector('.col-tip')) {
    roeReal.innerHTML = `<span style="${d.roe >= 20 ? 'color:#059669;font-weight:600' : d.roe >= 10 ? 'color:#2563eb' : 'color:#9ca3af'}">${fmtPct(d.roe)}</span>` +
      `<span class="col-tip" data-tip="ROE — RETORNO SOBRE O PATRIMÔNIO LÍQUIDO (LTM)&#10;&#10;Campo ROE da base, série TTM, data-base 30/06/2026. Fonte: MCP Partnr (B3/CVM).&#10;&#10;⚠️ É o ROE PONTUAL (lucro LTM ÷ patrimônio final), não o ROE_AVG sobre patrimônio médio — as duas definições dão números diferentes e o projeto usa a pontual em toda parte, inclusive no motor de preço-teto.&#10;Critério nº 2 do Radar: ROE ≥ 15%.">ⓘ</span>`;
  }
  if (divEbReal && !divEbReal.querySelector('.col-tip')) {
    if (d.divEbitda != null) {
      divEbReal.innerHTML = `<span style="${Math.abs(d.divEbitda) <= 2 ? 'color:#059669;font-weight:600' : Math.abs(d.divEbitda) <= 4 ? 'color:#2563eb' : 'color:#dc2626'}">${fmtX(d.divEbitda)}</span>` +
        `<span class="col-tip" data-tip="DÍVIDA LÍQUIDA ÷ EBITDA (LTM)&#10;&#10;Campo da base, série TTM, data-base 30/06/2026. Fonte: MCP Partnr (B3/CVM).&#10;Negativo = caixa líquido (a empresa tem mais caixa que dívida).&#10;Critério nº 3 do Radar: abaixo de 3x.">ⓘ</span>`;
    } else {
      divEbReal.innerHTML = '<span style="color:#9ca3af">—</span>' +
        '<span class="col-tip" data-tip="NÃO SE APLICA a instituição financeira.&#10;&#10;Em banco e seguradora o passivo é a MATÉRIA-PRIMA do negócio, não alavancagem: captar barato e emprestar caro é a operação. Dívida líquida/EBITDA não descreve risco aqui, e a base nem publica EBITDA para essas empresas.&#10;&#10;Por isso este critério sai do DENOMINADOR do score em vez de contar como reprovação — a empresa é avaliada em 3 critérios, não 4.">ⓘ</span>';
    }
  }
  // Sincroniza LPA (cells[6]) e data-dy-proj com dados reais da API/HIST_SEED
  // Garante que Preço Teto use sempre LPA e DY reais (LTM)
  const radarCells = radarRow.querySelectorAll('td');
  // data-lpa-manual="true": a coluna 7 é "LPA proj.", e quando a análise publicou um LPA
  // PROJETADO (lucro projetado ÷ ações) ele não pode ser sobrescrito pelo LPA LTM do
  // HIST_SEED — senão a coluna volta a mostrar o realizado e a projeção some, deixando o
  // preço-teto sem como ser auditado. Mesmo princípio de data-dy-manual logo abaixo.
  if (d.lpa != null && radarCells[7] && radarRow.dataset.lpaManual !== 'true') {
    // × FATOR_UNIT: o LPA do Partnr é POR AÇÃO e esta coluna convive com preço e dividendo
    // POR UNIT (ver js/config.js). Sem isso o SANB11 exibia LPA R$2,02 ao lado de um
    // dividendo de R$1,91 — payout aparente de 95% num banco que distribui metade disso.
    const _fu = (typeof FATOR_UNIT !== 'undefined')
      ? (FATOR_UNIT[(radarRow.dataset.ticker || '').replace(/\.SA$/i, '')] || 1) : 1;
    radarCells[7].textContent = `R$ ${(d.lpa * _fu).toFixed(2).replace('.',',')}`;
  }
  // Quando data-dy-manual="true" (payout >100% — motor exige DY sustentável, não o real
  // LTM/guidance, ver METODOLOGIA_ANALISE.md seção 6), preserva o valor definido na análise
  // e não deixa o sync do LTM real sobrescrever a projeção usada no Preço Teto/Retorno.
  if (d.dy != null && radarRow.dataset.dyManual !== 'true') {
    radarRow.dataset.dyProj = (d.dy / 100).toFixed(4);
  }
}

// ── HISTÓRICO 5 ANOS (expansível) ───────────────────────────────────────────

const _histCache = {};

async function fetchHistoricoEmpresa(ticker) {
  if (_histCache[ticker]) return _histCache[ticker];

  // Dados estáticos pré-populados têm prioridade
  if (HIST_SEED[ticker]) {
    _histCache[ticker] = HIST_SEED[ticker];
    return _histCache[ticker];
  }

  // Fallback: brapi.dev + Yahoo Finance (tickers sem seed estático)
  const [brapiRes, chartRes] = await Promise.allSettled([
    fetch(`https://brapi.dev/api/quote/${ticker}?modules=incomeStatementHistory,financialDataHistory,defaultKeyStatistics&token=${BRAPI_TOKEN}`, {signal:AbortSignal.timeout(12000)}),
    fetch(`https://corsproxy.io/?${encodeURIComponent(`https://query1.finance.yahoo.com/v8/finance/chart/${ticker}.SA?range=6y&interval=1mo&events=dividends`)}`, {signal:AbortSignal.timeout(10000)})
  ]);

  let fdh=[], inc=[], sharesOut=null, priceByYear={}, divByYear={};

  if (brapiRes.status==='fulfilled' && brapiRes.value.ok) {
    try {
      const j = await brapiRes.value.json(), r = j?.results?.[0];
      fdh = r?.financialDataHistory ? Object.values(r.financialDataHistory) : [];
      inc = r?.incomeStatementHistory ? Object.values(r.incomeStatementHistory) : [];
      sharesOut = r?.defaultKeyStatistics?.sharesOutstanding ?? null;
    } catch {}
  }
  if (chartRes.status==='fulfilled' && chartRes.value.ok) {
    try {
      const json = JSON.parse(await chartRes.value.text());
      const result = json?.chart?.result?.[0];
      const ts=result?.timestamp||[], cl=result?.indicators?.quote?.[0]?.close||[];
      const latestByYear={};
      ts.forEach((t,i)=>{ const dt=new Date(t*1000),y=dt.getFullYear(),m=dt.getMonth(),p=cl[i]; if(p&&p>0){if(m===11)priceByYear[y]=p; latestByYear[y]=p;} });
      Object.entries(latestByYear).forEach(([y,p])=>{ if(!priceByYear[y])priceByYear[y]=p; });
      Object.values(result?.events?.dividends||{}).forEach(ev=>{ const y=new Date(ev.date*1000).getFullYear(); divByYear[y]=(divByYear[y]||0)+ev.amount; });
    } catch {}
  }

  const hist={};
  [2020,2021,2022,2023,2024].forEach(year=>{
    const yF=fdh.find(f=>typeof f.endDate==='string'&&f.endDate.startsWith(String(year)));
    const yI=inc.find(i=>typeof i.endDate==='string'&&i.endDate.startsWith(String(year)));
    const price=priceByYear[year]||null, divs=divByYear[year]||0;
    const netInc=yI?.netIncome??null, eps=(sharesOut&&netInc!=null&&sharesOut>0)?netInc/sharesOut:null;
    hist[year]={
      preco:price, lpa:eps,
      roe:   yF?.returnOnEquity!=null ? yF.returnOnEquity*100 : null,
      mgLiq: yF?.profitMargins !=null ? yF.profitMargins *100 : null,
      mgBruta: yF?.grossMargins!=null ? yF.grossMargins  *100 : null,
      mgEbitda:yF?.ebitdaMargins!=null? yF.ebitdaMargins *100 : null,
      divPl: yF?.debtToEquity  !=null ? yF.debtToEquity       : null,
      roic:  yF?.returnOnCapitalEmployed!=null ? yF.returnOnCapitalEmployed*100 : null,
      receita:yI?.totalRevenue??null, lucrobruto:yI?.grossProfit??null,
      ebitda:yI?.ebitda??null, ebit:yI?.operatingIncome??null,
      imposto:yI?.incomeTaxExpense??null, lucrolin:netInc,
      custos:null, divbruta:null, divliq:null, pvp:null, evEbitda:null,
      pl:  (price&&eps&&eps>0) ? price/eps : null,
      dy:  (price&&divs>0)     ? (divs/price)*100 : null,
    };
  });
  _histCache[ticker]=hist;
  return hist;
}

// Constrói TRs de histórico alinhados às colunas do #fundTable (sem tabela interna)
function buildHistYearRows(ticker, hist) {
  const currentYear = new Date().getFullYear();
  const years = Object.keys(hist).map(Number).filter(y => y !== currentYear).sort((a,b)=>b-a);
  if (!years.length) return '';

  const fM = v => {
    if(v==null||isNaN(v)) return '<span class="hist-n">—</span>';
    const abs=Math.abs(v), neg=v<0?'-':'';
    if(abs>=1e9)  return `${neg}R$&nbsp;${(abs/1e9).toFixed(2).replace('.',',')} bi`;
    return        `${neg}R$&nbsp;${(abs/1e6).toFixed(0)} mi`;
  };
  const fP = (v,d=1,s='') => (v!=null&&!isNaN(v)) ? `${v.toFixed(d).replace('.',',')}${s}` : '<span class="hist-n">—</span>';
  const sc = (v,rule) => (v!=null&&!isNaN(v)) ? 'hist-'+semaforo(v,RULES[rule]).cls : 'hist-gray';

  const dataRows = years.map(y => {
    const d = hist[y] || {};
    const isLTM = y === currentYear;
    const anoCell = `<div class="hist-year-cell">
      <span class="hist-year-num">${y}</span>
      ${isLTM ? '<span class="hist-ltm-badge">LTM</span>' : ''}
    </div>`;
    return `<tr class="hist-year-row${isLTM?' hist-ltm-row':''}" data-hist-ticker="${ticker}">
      <td class="left">${anoCell}</td>
      <td></td><td></td>
      <td>${d.preco!=null ? `R$&nbsp;${d.preco.toFixed(2).replace('.',',')}` : '<span class="hist-n">—</span>'}</td>
      <td>${fM(d.receita)}</td>
      <td>${fM(d.custos)}</td>
      <td>${fM(d.lucrobruto)}</td>
      <td>${fM(d.ebitda)}</td>
      <td>${fM(d.ebit)}</td>
      <td>${fM(d.imposto)}</td>
      <td>${fM(d.lucrolin)}</td>
      <td>${fM(d.divbruta)}</td>
      <td>${fM(d.divliq)}</td>
      <td class="${sc(d.mgBruta,'mgBruta')}">${fP(d.mgBruta,1,'%')}</td>
      <td class="${sc(d.mgEbitda,'mgEbitda')}">${fP(d.mgEbitda,1,'%')}</td>
      <td class="${sc(d.mgLiq,'mgLiq')}">${fP(d.mgLiq,1,'%')}</td>
      <td class="${sc(d.roe,'roe')}">${fP(d.roe,1,'%')}</td>
      <td class="${sc(d.roic,'roic')}">${fP(d.roic,1,'%')}</td>
      <td class="${sc(d.pl,'pl')}">${fP(d.pl,1,'x')}</td>
      <td class="${sc(d.pvp,'pvp')}">${fP(d.pvp,2,'x')}</td>
      <td class="${sc(d.dy,'dy')}">${fP(d.dy,1,'%')}</td>
      <td>${fP(d.evEbitda,1,'x')}</td>
      <td>${d.divPl!=null ? fP(d.divPl,2,'x') : '<span class="hist-n">—</span>'}</td>
      <td>${d.lpa!=null ? `R$&nbsp;${d.lpa.toFixed(2).replace('.',',')}` : '<span class="hist-n">—</span>'}</td>
    </tr>`;
  }).join('');

  const noteText = (typeof HIST_SEED_NOTES !== 'undefined' && HIST_SEED_NOTES[ticker])
    ? HIST_SEED_NOTES[ticker]
    : HIST_SEED[ticker]
      ? 'Fonte: dados pré-carregados (ver comentário do ticker em data/historico.data.js)'
      : '⚠ Dados parciais via brapi.dev / Yahoo Finance';

  return dataRows +
    `<tr class="hist-note-row" data-hist-ticker="${ticker}"><td colspan="24">${noteText}</td></tr>`;
}

async function toggleHistorico(ticker) {
  const mainRow = document.querySelector(`#fundBody tr[data-ticker="${ticker}"]`);
  if (!mainRow) return;
  const btn = mainRow.querySelector('.expand-btn');

  // Se já existem linhas de histórico, apenas alternar visibilidade
  const existing = [...document.querySelectorAll(`#fundBody tr[data-hist-ticker="${ticker}"]`)];
  if (existing.length) {
    const isHidden = existing[0].style.display === 'none';
    existing.forEach(r => r.style.display = isHidden ? '' : 'none');
    if (btn) btn.classList.toggle('open', isHidden);
    return;
  }

  // Primeira abertura: loading placeholder
  if (btn) btn.classList.add('open');
  const colCount = mainRow.querySelectorAll('td').length;
  mainRow.insertAdjacentHTML('afterend',
    `<tr class="hist-year-row hist-loading-ph" data-hist-ticker="${ticker}">
      <td colspan="${colCount}" style="padding:10px 14px;color:var(--text3);font-style:italic;font-size:11px;border-left:3px solid var(--accent)!important;text-align:left;">
        Carregando histórico…
      </td>
    </tr>`
  );

  try {
    const hist = await fetchHistoricoEmpresa(ticker);
    // Remove placeholder e insere as linhas reais
    document.querySelectorAll(`#fundBody tr[data-hist-ticker="${ticker}"]`).forEach(r => r.remove());
    mainRow.insertAdjacentHTML('afterend', buildHistYearRows(ticker, hist));
  } catch {
    document.querySelectorAll(`#fundBody tr[data-hist-ticker="${ticker}"]`).forEach(r => r.remove());
    mainRow.insertAdjacentHTML('afterend',
      `<tr class="hist-year-row" data-hist-ticker="${ticker}">
        <td colspan="${colCount}" style="padding:10px 14px;color:var(--red);font-size:11px;border-left:3px solid var(--accent)!important;text-align:left;">
          Erro ao carregar histórico.
        </td>
      </tr>`
    );
    if (btn) btn.classList.remove('open');
  }
}

// Preenche a tabela com as linhas do radar (sem fundamentos ainda)
// Último ano disponível no HIST_SEED para um ticker (não necessariamente o ano corrente:
// empresas cujo exercício fechado mais recente é o ano anterior ficariam sem nenhum dado).
// Devolve {ano, ...campos} ou null.
function histSeedUltimoAno(ticker) {
  const m = (typeof HIST_SEED !== 'undefined') ? HIST_SEED[ticker] : null;
  if (!m) return null;
  const anos = Object.keys(m).map(Number).filter(n => !isNaN(n)).sort((a, b) => b - a);
  return anos.length ? m[anos[0]] : null;
}

function buildDadosRows() {
  const tbody = document.getElementById('fundBody');
  if(!tbody) return;
  const radarRows = Array.from(document.querySelectorAll('#tableBody tr[data-ticker]'));
  let html = '';
  radarRows.forEach(row => {
    const ticker = (row.dataset.ticker||'').replace('.SA','');
    const nome = row.querySelector('.empresa-name')?.textContent||ticker;
    const seg = row.dataset.segmento||'—';

    html += `<tr data-ticker="${ticker}" data-seg="${seg}" data-empresa="${nome} ${ticker}">
      <td class="left"><div style="display:flex;align-items:center;gap:6px;"><button class="expand-btn" onclick="toggleHistorico('${ticker}')" title="Ver histórico">▶</button><div class="fund-empresa">${nome}</div></div></td>
      <td><span class="ticker-badge">${ticker}</span></td>
      <td><span class="fund-seg">${seg}</span></td>
      <td class="fund-preco-cell fund-loading">—</td>
      <td class="fund-receita-cell">—</td>
      <td class="fund-custos-cell">—</td>
      <td class="fund-lucrobruto-cell">—</td>
      <td class="fund-ebitda-cell">—</td>
      <td class="fund-ebit-cell">—</td>
      <td class="fund-imposto-cell">—</td>
      <td class="fund-lucrolin-cell">—</td>
      <td class="fund-divbruta-cell">—</td>
      <td class="fund-divliq-cell">—</td>
      <td class="fund-mgbruta-cell">—</td>
      <td class="fund-mgebitda-cell">—</td>
      <td class="fund-mgliq-cell">—</td>
      <td class="fund-roe-cell">—</td>
      <td class="fund-roic-cell">—</td>
      <td class="fund-pl-cell">—</td>
      <td class="fund-pvp-cell">—</td>
      <td class="fund-dy-cell">—</td>
      <td class="fund-ev-cell">—</td>
      <td class="fund-divpl-cell">—</td>
      <td class="fund-lpa-cell">—</td>
    </tr>`;
  });
  tbody.innerHTML = html;

  // Preenche dados do HIST_SEED imediatamente (sem esperar API), usando o ano mais recente
  // que a fonte tem para cada ticker — antes exigia o ano corrente, então toda empresa cujo
  // último exercício fechado era o ano anterior aparecia com a linha inteira vazia.
  radarRows.forEach(r => {
    const t = (r.dataset.ticker||'').replace('.SA','');
    const d = histSeedUltimoAno(t);
    if(d) renderFundRow(t, d);
  });

  // Filtros de segmento
  const segsUniq = [...new Set(radarRows.map(r=>r.dataset.segmento).filter(Boolean))].sort();
  const sf = document.getElementById('fundSegFilter');
  if(sf){
    sf.innerHTML = '';
    let activeFundSeg = '';
    segsUniq.forEach(s=>{
      const b = document.createElement('button');
      b.className='filter-btn'; b.dataset.seg=s; b.textContent=s;
      b.style.cssText='font-size:10px;padding:4px 8px;';
      b.addEventListener('click',()=>{
        sf.querySelectorAll('.filter-btn').forEach(x=>x.classList.remove('active'));
        if(activeFundSeg===s){activeFundSeg='';filtrarDados();}
        else{b.classList.add('active');activeFundSeg=s;filtrarDados();}
      });
      sf.appendChild(b);
    });
  }

  initRadarFundCols();
}

// Mapeamento ticker → IDs do Investidor10 (ticker_id para cotação/indicadores, company_id para DRE)
// Padrão para adicionar nova empresa: INV10_IDS + HIST_SEED + <tr data-ticker> no HTML
// IDs: abra investidor10.com.br/acoes/TICKER/ e capture /api/cotacao/ticker/{t} e /api/balancos/.../chart/{c}/
