function renderFundRow(ticker, d) {
  const row = document.querySelector(`#fundBody tr[data-ticker="${ticker}"]`);
  if(!row || !d) return;
  const isBanco = BANCOS_TICKERS.includes(ticker);

  // Preço
  const precoCell = row.querySelector('.fund-preco-cell');
  if(precoCell){
    precoCell.classList.remove('fund-loading');
    precoCell.innerHTML = d.preco ? `<span class="fund-val" style="color:var(--blue);">R$ ${d.preco.toFixed(2).replace('.',',')}</span>` : '<span class="fund-val gray">—</span>';
  }

  // DRE — valores absolutos
  const q = s => row.querySelector(s);
  q('.fund-receita-cell').innerHTML    = fmtMoney(d.receita);
  q('.fund-custos-cell').innerHTML     = fmtMoney(d.custos);
  q('.fund-lucrobruto-cell').innerHTML = fmtMoney(d.lucrobruto);
  q('.fund-ebitda-cell').innerHTML     = isBanco ? '<span class="fund-val gray">N/A</span>' : fmtMoney(d.ebitda);
  q('.fund-ebit-cell').innerHTML       = fmtMoney(d.ebit);
  q('.fund-imposto-cell').innerHTML    = fmtMoney(d.imposto);
  q('.fund-lucrolin-cell').innerHTML   = fmtMoney(d.lucrolin);

  // Balanço
  q('.fund-divbruta-cell').innerHTML = isBanco ? '<span class="fund-val gray">N/A</span>' : fmtMoney(d.divbruta);
  q('.fund-divliq-cell').innerHTML   = isBanco ? '<span class="fund-val gray">N/A</span>' : fmtMoney(d.divliq);

  // Margens
  q('.fund-mgbruta-cell').innerHTML  = isBanco ? '<span class="fund-val gray">N/A</span>' : semCell(d.mgBruta,  'mgBruta',  1, '%');
  q('.fund-mgebitda-cell').innerHTML = isBanco ? '<span class="fund-val gray">N/A</span>' : semCell(d.mgEbitda, 'mgEbitda', 1, '%');
  q('.fund-mgliq-cell').innerHTML    = semCell(d.mgLiq, 'mgLiq', 1, '%');

  // Rentabilidade
  q('.fund-roe-cell').innerHTML  = semCell(d.roe,  'roe',  1, '%');
  q('.fund-roic-cell').innerHTML = semCell(d.roic, 'roic', 1, '%');

  // Múltiplos
  q('.fund-pl-cell').innerHTML  = semCell(d.pl,  'pl',  1, 'x');
  q('.fund-pvp-cell').innerHTML = semCell(d.pvp, 'pvp', 2, 'x');
  q('.fund-dy-cell').innerHTML  = semCell(d.dy,  'dy',  1, '%');
  q('.fund-ev-cell').innerHTML  = (d.evEbitda!=null && d.evEbitda>0 && !isBanco)
    ? semCell(d.evEbitda,'evEbitda',1,'x')
    : '<span class="fund-val gray">N/A</span>';
  const divplCell = q('.fund-divpl-cell');
  if(divplCell) divplCell.innerHTML = isBanco ? '<span class="fund-val gray">N/A</span>' : semCell(d.divPl,'divPl',2,'x');
  q('.fund-lpa-cell').innerHTML = d.lpa!=null && !isNaN(d.lpa)
    ? `<span class="fund-val">R$ ${d.lpa.toFixed(2).replace('.',',')}</span>`
    : '<span class="fund-val gray">—</span>';

  // Atualiza colunas fundamentalistas no Radar
  atualizarCelulasRadarFund(ticker, d);
}

// Atualiza os KPIs de resumo
function atualizarFundKPIs(_cache) { /* removido — bloco KPI desativado */ }

// ══════════════════════════════════════════════════════════════════════════════════════════
// "Atualizar Dados" da Base de Dados
// ══════════════════════════════════════════════════════════════════════════════════════════
// ANTES este botão buscava do Investidor10/brapi e fazia merge por cima do HIST_SEED, campo a
// campo, SEM avisar. Isso corrompia a base: os fundamentos são do MCP Partnr (CVM), coletados
// e validados um a um, e o Investidor10 usa outras definições (foi a causa das divergências de
// P/L investigadas em 31/08). O cabeçalho continuava dizendo "Fonte: MCP Partnr" — virava mentira.
//
// POR QUE NÃO BUSCA DO PARTNR DIRETO: o Partnr é autenticado com a chave de API do usuário.
// Um HTML estático só conseguiria chamá-lo embutindo essa credencial no arquivo, o que a
// exporia a qualquer pessoa com quem o arquivo fosse compartilhado. A autenticação do MCP é
// server-side por design. Então a atualização dos fundamentos é feita FORA do arquivo: pedindo
// ao Claude, que re-roda scripts/RECEITA_PARTNR.md e regrava data/historico.data.js.
//
// O botão agora: recarrega o snapshot do Partnr (desfazendo qualquer resíduo de cache antigo
// do Investidor10 que ainda esteja no localStorage) e informa a idade da coleta.
const FUND_SNAPSHOT_DATA = '2026-09-03';   // data da última coleta via MCP Partnr

async function atualizarFundamentos() {
  const btn   = document.getElementById('btnUpdateFund');
  const stEl  = document.getElementById('fundStatus');
  const stTxt = document.getElementById('fundStatusText');
  if (btn) { btn.disabled = true; btn.classList.add('loading'); }
  if (stTxt) stTxt.textContent = 'Recarregando snapshot...';

  // Limpa cache de API antigo — é dele que vinha a contaminação por Investidor10
  try { localStorage.removeItem(FUND_CACHE_KEY); } catch {}

  let n = 0;
  document.querySelectorAll('#fundBody tr[data-ticker]').forEach(row => {
    const d = (typeof histSeedUltimoAno === 'function') ? histSeedUltimoAno(row.dataset.ticker) : null;
    if (!d) return;
    renderFundRow(row.dataset.ticker, d);
    if (typeof atualizarCelulasRadarFund === 'function') atualizarCelulasRadarFund(row.dataset.ticker, d);
    n++;
  });

  // Cotação continua ao vivo (brapi) — ela não conflita com os fundamentos
  if (typeof atualizarCotacoes === 'function') { try { await atualizarCotacoes(); } catch {} }

  const dias = Math.floor((Date.now() - new Date(FUND_SNAPSHOT_DATA).getTime()) / 86400000);
  const velho = dias > 100;
  if (stEl)  stEl.className = 'update-status' + (velho ? '' : ' ok');
  if (stTxt) {
    const dt = new Date(FUND_SNAPSHOT_DATA).toLocaleDateString('pt-BR');
    stTxt.textContent = velho
      ? `${n} empresas · coleta de ${dt} (${dias} dias) — peça ao Claude para atualizar`
      : `${n} empresas · Partnr (CVM), coleta de ${dt}`;
  }
  if (btn) { btn.disabled = false; btn.classList.remove('loading'); }
}

function restaurarCacheFund() {
  // Antes: lia o cache de API (Investidor10/brapi) do localStorage e fazia merge por cima do
  // HIST_SEED na abertura da aba. Como o snapshot do Partnr passou a ser a fonte única dos
  // fundamentos, esse caminho só serviria para reintroduzir dados de outra fonte sem aviso.
  // Agora apenas descarta qualquer cache remanescente e renderiza direto do snapshot.
  try { localStorage.removeItem(FUND_CACHE_KEY); } catch {}
  initRadarRealCells();
  initRadarFundCols();
  const st = document.getElementById('fundStatusText');
  if (st) {
    const dt = new Date(typeof FUND_SNAPSHOT_DATA !== 'undefined' ? FUND_SNAPSHOT_DATA : Date.now())
      .toLocaleDateString('pt-BR');
    st.textContent = `Partnr (CVM), coleta de ${dt}`;
  }
  const stEl = document.getElementById('fundStatus');
  if (stEl) stEl.className = 'update-status ok';
}

function filtrarDados() {
  const s = (document.getElementById('fundSearch')?.value||'').toLowerCase();
  const activeSeg = document.querySelector('#fundSegFilter .filter-btn.active')?.dataset.seg||'';
  document.querySelectorAll('#fundBody tr[data-ticker]').forEach(row=>{
    const match = (s===''||row.dataset.empresa.toLowerCase().includes(s))
      && (activeSeg===''||row.dataset.seg===activeSeg);
    row.classList.toggle('fund-hidden', !match);
    // Esconder/mostrar linhas de histórico associadas
    const ticker = row.dataset.ticker;
    const isOpen = row.querySelector('.expand-btn')?.classList.contains('open');
    document.querySelectorAll(`#fundBody tr[data-hist-ticker="${ticker}"]`).forEach(hr => {
      hr.style.display = (match && isOpen) ? '' : 'none';
    });
  });
}

let _fundSortCol=-1,_fundSortDir=1;
function sortFund(col){
  _fundSortDir = _fundSortCol===col ? _fundSortDir*-1 : 1;
  _fundSortCol = col;
  const tbody = document.getElementById('fundBody');
  const rows = Array.from(tbody.querySelectorAll('tr[data-ticker]'));
  rows.sort((a,b)=>{
    const getN = r => {
      const td=r.querySelectorAll('td')[col];
      if(!td) return null;
      const t=td.textContent.replace(/[^0-9,.\-]/g,'').replace(',','.');
      const n=parseFloat(t);
      return isNaN(n)?null:n;
    };
    const na=getN(a),nb=getN(b);
    if(na===null&&nb===null) return 0;
    if(na===null) return 1;
    if(nb===null) return -1;
    return (na-nb)*_fundSortDir;
  });
  rows.forEach(r=>{
    tbody.appendChild(r);
    // Mover as linhas de histórico junto com a linha pai
    document.querySelectorAll(`#fundBody tr[data-hist-ticker="${r.dataset?.ticker}"]`)
      .forEach(hr => tbody.appendChild(hr));
  });
  filtrarDados();
}

// Dados fundamentais estáticos (Investidor10) — usados como seed antes do cache dinâmico
// STATIC_FUND_SEED removido — dados LTM agora em HIST_SEED[ticker][anoAtual]

// Dados históricos anuais por ticker (Fonte: Investidor10) — pré-populados estaticamente
