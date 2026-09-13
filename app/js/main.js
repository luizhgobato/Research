let _dadosIniciados = false;
let _flaviaChartsIniciados = false;
let _luizChartsIniciados = false;
const _showPageOrig = showPage;
// Patch showPage para inicializar dados ao entrar na aba
(function(){
  const orig = showPage;
  window.showPage = function(id){
    orig(id);
    if(id==='dados' && !_dadosIniciados){
      _dadosIniciados = true;
      buildDadosRows();   // já inclui pré-preenchimento HIST_SEED LTM
      initRadarRealCells();
      restaurarCacheFund(); // merge API cache + HIST_SEED
      if(typeof buildSetorialTable==='function') buildSetorialTable();
    }
    // Gráficos de Carteira Luiz/Flavia (js/graficos-resumo.js) só ficam com largura correta
    // depois que a aba vira display:block — por isso o init roda na primeira abertura, não
    // no load da página (a aba começa oculta, um SVG desenhado com offsetWidth=0 fica vazio).
    if(id==='flavia' && !_flaviaChartsIniciados && typeof initRpCharts==='function'){
      _flaviaChartsIniciados = true;
      initRpCharts('Flavia');
      // Restaura Qtd/PM gravados no navegador, recalcula e passa a salvar a cada edição.
      if(typeof initCarteiraEditavel==='function') initCarteiraEditavel('flaviaPosBody');
    }
    if(id==='resumoluiz' && !_luizChartsIniciados && typeof initRpCharts==='function'){
      _luizChartsIniciados = true;
      initRpCharts('Luiz');
      if(typeof initCarteiraEditavel==='function') initCarteiraEditavel('luizPosBody');
    }
  };
})();

// A propagação pós-cotação (gráfico de posição, Patrimônio, Carteira Ideal, Segmento e os
// números do topo) vive em _cwPropagar(), em js/carteira-manual.js — assim vale tanto para
// "Atualizar Cotação" quanto para a edição manual de Qtd/PM, sem duplicar a lógica aqui.

// Quando cotações do Radar são atualizadas, atualiza cotação na Base de Dados se já inicializada
const _atualizarCotOrig = atualizarCotacoes;
window.atualizarCotacoes = async function(){
  await _atualizarCotOrig();
  if(_dadosIniciados){
    document.querySelectorAll('#fundBody tr[data-ticker]').forEach(row=>{
      const ticker = row.dataset.ticker;
      const radarRow = document.querySelector(`#tableBody tr[data-ticker="${ticker}.SA"]`);
      if(!radarRow) return;
      const cotCell = radarRow.querySelector('.cotacao-cell');
      const val = cotCell?.textContent;
      if(!val || val==='—' || val==='...') return;
      const precoCell = row.querySelector('.fund-preco-cell');
      if(precoCell){ precoCell.classList.remove('fund-loading'); precoCell.innerHTML=`<span class="fund-val" style="color:var(--blue);">${val}</span>`; }
    });
  }
};

// Injeta colunas no Radar e popula com cache existente (independe de abrir aba Base de Dados)
(function initRadarFromCache() {
  try {
    const raw = localStorage.getItem(FUND_CACHE_KEY);
    if (!raw) return;
    const saved = JSON.parse(raw);
    if (!saved.data || (Date.now()-saved.ts) >= 86400000) return;
    initRadarRealCells();
    initRadarFundCols();
    Object.entries(saved.data).forEach(([ticker, d]) => atualizarCelulasRadarFund(ticker, d));
  } catch {}
})();

renderToggles();
renderReportCells();
applyMobileColHide();

// Restaurar cotações do cache
(function(){
  try {
    const raw = localStorage.getItem('cotacoes_cache') || sessionStorage.getItem('cotacoes_cache');
    if(!raw) return;
    const saved = JSON.parse(raw);
    if(!saved.data || (Date.now()-saved.ts) >= 86400000) return;
    document.querySelectorAll('#tableBody tr[data-ticker]').forEach(r=>{
      const val = saved.data[r.dataset.ticker];
      if(!val) return;
      const c = r.querySelector('.cotacao-cell');
      // Captura cotação e DY antigos ANTES de atualizar a célula
      const _oldCot=parseFloat((c?.textContent||'').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
      const _oldDy =parseFloat(r.dataset.dyProj) || 0;
      if(c){ c.textContent=val; c.classList.add('updated'); }
      const preco = parseFloat(val.replace(/[^0-9,.]/g,'').replace(',','.'));
      const cells = r.querySelectorAll('td');
      // Preserva DPS real: novo DY% = DPS / novo preço (DPS = dyProj_antigo × cotacao_antiga)
      if(_oldDy>0&&_oldCot>0&&preco>0) r.dataset.dyProj=(_oldDy*_oldCot/preco).toFixed(4);
  atualizarDivDY(r, preco);   // DPS = LPA × payout; DY = DPS ÷ preço (js/calculos.js)
      calcularPrecoTeto(r, preco);
      const precoJusto = parseFloat(r.dataset.precoJusto)||null;
      const margemCell = r.querySelector('.margem-cell');
      if(preco>0 && margemCell && precoJusto){
        const pct = ((precoJusto-preco)/precoJusto)*100;
        margemCell.innerHTML = margemTag(pct);
        const ret = ((precoJusto-preco)/preco)*100 + (dyProj*100);
        if(cells[17]) cells[17].textContent = (ret>=0?'+':'')+ret.toFixed(1)+'%';
      }
      if(typeof atualizarPLAtualLinha==='function') atualizarPLAtualLinha(r);
    });
    const agora = new Date(saved.ts).toLocaleString('pt-BR',{day:'2-digit',month:'2-digit',hour:'2-digit',minute:'2-digit'});
    document.getElementById('lastUpdate').textContent = `Cache ${agora}`;
    const sd=document.getElementById('statusDot');if(sd)sd.className='nav-status-dot ok';
  } catch(e){ console.warn('[Cache]',e); }
})();

renderPosicoes();
renderMobileCards();
renderDivProjTable();
applyFilters();
// Converte ticker badge em link para Investidor10 (aplica a todos os ativos presentes e futuros)
document.querySelectorAll('#tableBody tr[data-ticker] td.frozen-2 .ticker-badge').forEach(badge => {
  const ticker = badge.textContent.trim().toLowerCase();
  const a = document.createElement('a');
  a.href = `https://investidor10.com.br/acoes/${ticker}/`;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.style.cssText = 'color:inherit;text-decoration:underline;';
  badge.parentNode.insertBefore(a, badge);
  a.appendChild(badge);
});

// Converte nome da empresa (coluna Empresa) em link para Investidor10, usando o ticker da
// própria linha (data-ticker, sem o sufixo ".SA") — mesmo padrão de URL do ticker badge acima.
document.querySelectorAll('#tableBody tr[data-ticker] td.frozen-1 .empresa-name').forEach(nameEl => {
  const row = nameEl.closest('tr[data-ticker]');
  const ticker = (row?.dataset.ticker || '').replace(/\.SA$/i, '').toLowerCase();
  if (!ticker) return;
  const a = document.createElement('a');
  a.href = `https://investidor10.com.br/acoes/${ticker}/`;
  a.target = '_blank';
  a.rel = 'noopener noreferrer';
  a.style.cssText = 'color:inherit;text-decoration:underline;';
  nameEl.parentNode.insertBefore(a, nameEl);
  a.appendChild(nameEl);
});
initRadarRealCells();
// Sincroniza as células do Radar com o ano mais recente que a fonte tem para cada ticker
// (antes exigia o ano corrente — quem fechou o último exercício no ano anterior ficava vazio).
Object.keys(HIST_SEED).forEach(t=>{ const d=histSeedUltimoAno(t); if(d) atualizarCelulasRadarFund(t,d); });
// Recalcula derivados do Radar (P/L proj, margem, retorno) agora que LPA/DY reais
// do HIST_SEED já foram sincronizados nas células — evita ficar com "—" quando o
// <td> de LPA começa vazio no HTML e só é preenchido depois deste ponto.
calcularDerivadosRadar();
// P/L atual: recalcula a partir de cotação ao vivo ÷ LPA LTM travado (data-lpa-ltm) para os
// tickers que usam esse motor — ver atualizarPLAtualLinha em js/fundamentos.js.
atualizarTodosPLAtual();

// Renderiza gráficos da Carteira quando a página ficar visível (aba está oculta por
// enquanto — ver comentário no <nav> — mas o código continua pronto para quando voltar)
function tryBuildCharts(){
  const el = document.getElementById('chartClasse');
  if(!el) return;
  const w = el.getBoundingClientRect().width;
  if(w > 50){
    renderPosicoes();
    buildCharts();
  }
}
// Aguarda layout completo
if(document.readyState === 'complete'){
  setTimeout(tryBuildCharts, 100);
} else {
  window.addEventListener('load', ()=>setTimeout(tryBuildCharts, 100));
}

// Normaliza as bordas divisórias (.sep) do Radar: garante que cada <td> tenha a
// classe "sep" exatamente nas mesmas colunas que o <th> correspondente no cabeçalho.
// Corrige o desalinhamento das linhas divisórias entre grupos de colunas (ex.: P/L
// proj. colando em P/L atual LTM) sem depender de manter cada linha do HTML em dia
// manualmente — roda uma vez após o Radar ser populado e vale para qualquer nova
// empresa adicionada no futuro.
(function normalizarSepRadar(){
  try {
    const headerRow = document.querySelector('#mainTable thead tr.col-header');
    const rows = document.querySelectorAll('#mainTable tbody tr[data-ticker]');
    if(!headerRow || !rows.length) return;
    const ths = Array.from(headerRow.children);
    const sepIdx = new Set();
    ths.forEach((th,i)=>{ if(th.classList.contains('sep')) sepIdx.add(i); });
    rows.forEach(row=>{
      Array.from(row.children).forEach((td,i)=>{
        if(sepIdx.has(i)) td.classList.add('sep');
        else td.classList.remove('sep');
      });
    });
  } catch(e){ /* noop */ }
})();
