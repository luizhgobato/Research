// ══════════════════════════════════════════════════════════════════════════════════════════
// CÉLULA E MODAL DA COLUNA "CENÁRIO DE TESE" — 16/09/2026
// ══════════════════════════════════════════════════════════════════════════════════════════
// Espelha o padrão de js/ranking.js (renderReportCells/abrirReport), mas para o objeto
// window.TESES de data/teses.data.js. Nenhuma lógica de cálculo aqui — só leitura e exibição
// do que já foi escrito à mão naquele arquivo.

function renderTeseCells(){
  document.querySelectorAll('#tableBody tr[data-ticker]').forEach(row=>{
    const cell = row.querySelector('.tese-cell');
    if(!cell) return;
    const ticker = (row.dataset.ticker||'').replace('.SA','');
    const tese = (window.TESES || {})[ticker];
    if(tese){
      cell.innerHTML = `<button class="btn-tese" onclick="abrirTese('${ticker}')">📌 Ver tese</button>`;
    } else {
      cell.innerHTML = `<span class="btn-tese-off">— Sem tese</span>`;
    }
  });
}

function _teseFmtR(n){
  if(n === null || n === undefined || isNaN(n)) return '—';
  return 'R$ ' + Number(n).toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
}

function abrirTese(ticker){
  const tese = (window.TESES || {})[ticker];
  if(!tese) return;
  const nomeEl = document.querySelector(`#tableBody tr[data-ticker="${ticker}.SA"] .empresa-name`);
  const nome = nomeEl ? nomeEl.textContent : ticker;

  document.getElementById('teseTitulo').textContent = `${nome} (${ticker})`;
  document.getElementById('teseData').textContent = tese.data ? `Registrada em ${tese.data}` : '';
  document.getElementById('teseGatilho').textContent = tese.gatilho || '—';
  document.getElementById('tesePremissa').textContent = tese.premissa || '—';
  document.getElementById('tesePrecoOficial').textContent = _teseFmtR(tese.precoOficial);
  document.getElementById('tesePrecoCenario').textContent = _teseFmtR(tese.precoCenario);
  document.getElementById('teseConfianca').textContent = tese.confianca || '—';
  document.getElementById('teseRevisao').textContent = tese.condicaoDeRevisao || '—';
  const fonteEl = document.getElementById('teseFonte');
  if(tese.fonte){
    fonteEl.innerHTML = 'Fonte: <a href="' + tese.fonte + '" target="_blank" rel="noopener">' + tese.fonte + '</a>';
  } else {
    fonteEl.textContent = '';
  }

  document.getElementById('teseOverlay').classList.add('show');
}

function fecharTese(){
  document.getElementById('teseOverlay').classList.remove('show');
}
