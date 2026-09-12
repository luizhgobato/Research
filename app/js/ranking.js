// ── RANKING ──\n
// Score multifatorial 0–10. Pesos: margem 30% · desvio P/L 25% · DY 20% · ROE 15% · dív/EBITDA 10%.
// Critério sem dado é EXCLUÍDO e os pesos re-normalizados (badge ganha * e tooltip mostra o breakdown).
function calcularRanking(){
  const rows = Array.from(document.querySelectorAll('#tableBody tr[data-ticker]'));
  if(!rows.length) return;

  const parseCell = (cells, i) => {
    const t = (cells[i]?.textContent || '').trim();
    if(!t || t === '—' || t === '...' || t === 'Erro') return null;
    const v = parseFloat(t.replace(/[^0-9,.\-]/g,'').replace(',','.'));
    return isNaN(v) ? null : v;
  };

  const dados = rows.map(row => {
    const cells = row.querySelectorAll('td');
    const margem = parseCell(cells, 20);
    const plHist = parseCell(cells, 14);
    const plProj = parseCell(cells, 12);
    const desvioPL = (plHist > 0 && plProj > 0) ? ((plHist - plProj) / plHist) * 100 : null;
    const dyRaw = parseFloat(row.dataset.dyProj) || 0;
    const dyProj = dyRaw > 0 ? dyRaw * 100 : null;
    const roe = parseCell(cells, 16);
    const divVal = parseCell(cells, 17);
    return { row, margem, desvioPL, dyProj, roe, divVal };
  });

  // Pontuação 0–10 por critério
  function scoreMargem(v){
    if(v >= 30) return 10;
    if(v >= 15) return 7 + (v-15)/15*3;
    if(v >= 0)  return 3 + (v/15)*4;
    if(v >= -20) return Math.max(0, 3 + (v/20)*3);
    return 0;
  }
  function scoreDesvioPL(v){
    if(v >= 30) return 10;
    if(v >= 0)  return 4 + (v/30)*6;
    return Math.max(0, 4 + (v/30)*4);
  }
  function scoreDY(v){
    if(v >= 12) return 10;
    if(v >= 4)  return 4 + ((v-4)/8)*6;
    return (v/4)*4;
  }
  function scoreROE(v){
    if(v >= 20) return 10;
    if(v >= 10) return 4 + ((v-10)/10)*6;
    if(v >= 0)  return (v/10)*4;
    return 0;
  }
  function scoreDivEbitda(v){
    if(v <= 1) return 10;
    if(v <= 2) return 7 + (2-v)*3;
    if(v <= 3) return 4 + (3-v)*3;
    if(v <= 4) return (4-v)*4;
    return 0;
  }

  const CRITERIOS = [
    { nome:'Margem seg.', peso:0.30, val:d=>d.margem,   fn:scoreMargem },
    { nome:'Desvio P/L',  peso:0.25, val:d=>d.desvioPL, fn:scoreDesvioPL },
    { nome:'DY proj.',    peso:0.20, val:d=>d.dyProj,   fn:scoreDY },
    { nome:'ROE',         peso:0.15, val:d=>d.roe,      fn:scoreROE },
    { nome:'Dív/EBITDA',  peso:0.10, val:d=>d.divVal,   fn:scoreDivEbitda },
  ];

  const scores = dados.map(d => {
    let somaPeso = 0, soma = 0; const partes = [];
    CRITERIOS.forEach(c => {
      const v = c.val(d);
      if(v === null){ partes.push(c.nome + ': sem dado (excluído)'); return; }
      const s = c.fn(v);
      somaPeso += c.peso; soma += s * c.peso;
      partes.push(c.nome + ': ' + s.toFixed(1) + ' × peso ' + Math.round(c.peso*100) + '%');
    });
    const completo = somaPeso >= 0.999;
    const score = somaPeso > 0 ? Math.round((soma / somaPeso) * 10) / 10 : null;
    let tip = partes.join('\n');
    if(score !== null && !completo) tip += '\n* score parcial — pesos re-normalizados';
    return { row: d.row, score, completo, tip };
  });

  const sorted = [...scores].sort((a, b) => (b.score ?? -1) - (a.score ?? -1));
  const medal = ['🥇','🥈','🥉'];

  sorted.forEach((item, idx) => {
    const cell = item.row.querySelector('.rank-cell');
    if(!cell) return;
    if(item.score === null){
      cell.innerHTML = '<span class="rank-badge rank-low">—</span>';
      cell.querySelector('.rank-badge').appendChild(_varTipBtn('Sem dados suficientes — atualize cotações e a Base de Dados'));
      cell.dataset.score = '';
      return;
    }
    const pos = idx + 1;
    const scoreStr = item.score.toFixed(1) + (item.completo ? '' : '*');
    let cls, icon;
    if(pos === 1){ cls='rank-1'; icon=medal[0]; }
    else if(pos === 2){ cls='rank-2'; icon=medal[1]; }
    else if(pos === 3){ cls='rank-3'; icon=medal[2]; }
    else if(pos <= 6){ cls='rank-top'; icon=''; }
    else if(pos <= 12){ cls='rank-mid'; icon=''; }
    else { cls='rank-low'; icon=''; }
    const label = icon
      ? '<span class="rank-badge ' + cls + '">' + icon + ' ' + pos + 'º · ' + scoreStr + '</span>'
      : '<span class="rank-badge ' + cls + '">#' + pos + ' · ' + scoreStr + '</span>';
    cell.innerHTML = label;
    cell.dataset.score = item.score;
    const badge = cell.querySelector('.rank-badge');
    const tipTexto = 'Score ' + item.score.toFixed(1) + '\n' + item.tip;
    if(badge){
      badge.dataset.tip = tipTexto;   // hover no badge também mostra
      badge.style.cursor = 'help';
    }
    if(badge) badge.appendChild(_varTipBtn(tipTexto)); // ⓘ DENTRO do badge (flex, não quebra linha)
  });
}
let _sortCol = -1, _sortDir = 1;
function sortTable(colIndex){
  const tbody = document.getElementById('tableBody');
  if(!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr'));
  _sortDir = (_sortCol === colIndex) ? _sortDir * -1 : 1;
  _sortCol = colIndex;
  document.querySelectorAll('.col-header th').forEach(th=>{
    th.classList.remove('sort-asc','sort-desc');
    if(parseInt(th.dataset.col) === colIndex)
      th.classList.add(_sortDir === 1 ? 'sort-asc' : 'sort-desc');
  });
  function cellVal(row){
    const tds = row.querySelectorAll('td');
    const td = tds[colIndex];
    if(!td) return { n: null, s: '' };
    let raw = td.textContent.trim();
    let s = raw.toLowerCase();
    // Remove símbolos e converte unidades ANTES de qualquer replace
    let work = raw
      .replace(/R\$\s*/g, '')   // Remove R$
      .replace(/\s+/g, '')       // Remove espaços
      .trim();
    // Multiplica bi e mi pelo valor correto
    let multiplier = 1;
    if(/bi$/i.test(work))      { multiplier = 1e9;  work = work.replace(/bi$/i, ''); }
    else if(/mi$/i.test(work)) { multiplier = 1e6;  work = work.replace(/mi$/i, ''); }
    else if(/%$/.test(work))   { multiplier = 1;    work = work.replace(/%$/, ''); }
    else if(/x$/.test(work))   { multiplier = 1;    work = work.replace(/x$/, ''); }
    // Remove IPCA+ prefix
    work = work.replace(/IPCA\+/i, '');
    // Converte vírgula decimal
    work = work.replace(',', '.');
    // Remove qualquer char não numérico exceto . - +
    work = work.replace(/[^0-9.\-+]/g, '');
    const n = parseFloat(work);
    return { n: isNaN(n) ? null : n * multiplier, s };
  }
  rows.sort((a, b) => {
    const va = cellVal(a), vb = cellVal(b);
    // Nulls sempre no final independente da direção
    if(va.n === null && vb.n === null) return 0;
    if(va.n === null) return 1;
    if(vb.n === null) return -1;
    // Ordenação primária
    const diff = (va.n - vb.n) * _sortDir;
    if(diff !== 0) return diff;
    // Ordenação secundária estável por nome da empresa
    const na = (a.dataset.empresa||'').toLowerCase();
    const nb = (b.dataset.empresa||'').toLowerCase();
    return na.localeCompare(nb, 'pt-BR');
  });
  rows.forEach(r => tbody.removeChild(r));
  rows.forEach(r => tbody.appendChild(r));
  applyFilters();
}

function renderReportCells(){
  document.querySelectorAll('tr[data-report]').forEach(row=>{
    const cell = row.querySelector('.report-cell');
    if(!cell) return;
    const report = row.dataset.report;
    const date = row.dataset.reportDate;
    const ticker = (row.dataset.ticker||'').replace('.SA','');
    const nome = row.querySelector('.empresa-name')?.textContent || ticker;
    const veredicto = row.dataset.veredicto || 'pendente';
    const temReport = (report && date) || REPORTS[ticker];
    if(temReport){
      cell.innerHTML = `<button class="btn-ver" onclick="abrirReport('${ticker}','${nome}','${date||''}','${veredicto}')">📄 Ver</button><span class="report-date">${date||''}</span>`;
    } else {
      cell.innerHTML = `<span class="btn-ver-off">📄 Pendente</span>`;
    }
  });
}

function solicitarRelatorio(ticker){
  const cmd=`/empresa ${ticker}`;
  navigator.clipboard.writeText(cmd).catch(()=>{});
  showToast(`✓ Copiado: "${cmd}" — cole no chat do Claude`);
}
function showToast(msg){const t=document.getElementById('toast');t.textContent=msg;t.classList.add('show');setTimeout(()=>t.classList.remove('show'),3500);}
