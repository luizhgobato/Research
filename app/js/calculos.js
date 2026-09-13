// ── MOBILE: esconde células correspondentes às colunas ocultas ──
// Índices das colunas ocultas no mobile (0-based, contando todas as td, já sem as colunas
// removidas de Ranking/Desvio P/L/P/L Histórico/Preço-Lucro projetado/Retorno Real):
// 3=Lucro2025, 5=LucroEst, 6=Cresc, 7=LPA, 8=Payout, 9=Div/Ação, 12=P/L atual, 13=ROE,
// 14=Dív/EBITDA, 15=PreçoTeto, 18=RetornoTotal
const MOB_HIDE_COLS = [3,5,6,7,8,9,12,13,14,15,18];
function calcCrescimentoLucro() {
  function parseLucroVal(text) {
    let t = text.replace(/R\$\s*/g,'').replace(/\*/g,'').replace(/\s+/g,'');
    const neg = t.startsWith('-');
    t = t.replace('-','').replace(',','.');
    let mult = 1;
    if (/bi/i.test(t)) { mult = 1e9; t = t.replace(/bi.*/i,''); }
    else if (/mi/i.test(t)) { mult = 1e6; t = t.replace(/mi.*/i,''); }
    const v = parseFloat(t) * mult;
    return isNaN(v) ? null : (neg ? -v : v);
  }
  document.querySelectorAll('#tableBody tr').forEach(row => {
    const cell = row.querySelector('.cresc-lucro-cell');
    if (!cell) return;
    const tds = row.querySelectorAll('td');
    // ⚠️ SEMÂNTICA INVERTIDA em 06/09/2026. A coluna 4 passou a ser o lucro LTM e a 5 o lucro
    // NORMALIZADO do motor de setor; esta coluna deixou de ser "crescimento projetado" e virou
    // "distância do normalizado" = LTM ÷ normalizado − 1. Positivo = ganhando acima do próprio
    // padrão; negativo = abaixo. Não é previsão, é diagnóstico de ciclo.
    const vLtm  = parseLucroVal(tds[4]?.textContent || '');
    const vNorm = parseLucroVal(tds[5]?.textContent || '');
    if (vLtm === null || vNorm === null) {
      _celTip(cell, '<span class="muted">—</span>');
      return;
    }
    const v2025 = vNorm, vEst = vLtm;   // base = normalizado, comparado = LTM
    if (vNorm <= 0) {
      _celTip(cell, '<span class="muted">—</span>');
      return;
    }
    const pct = (vEst - v2025) / v2025 * 100;
    if (Math.abs(pct) < 0.5) {
      _celTip(cell, '<span class="muted">0%</span>');
    } else {
      const sign = pct >= 0 ? '+' : '';
      const cls = pct >= 5 ? 'tag-green' : pct < 0 ? 'tag-red' : 'tag-blue';
      _celTip(cell, `<span class="tag ${cls}">${sign}${pct.toFixed(0)}%</span>`);
    }
  });
}

// ══════════════════════════════════════════════════════════════════════════════════════════
// DIVIDENDO POR AÇÃO E DY — a inversão de 06/09/2026
// ══════════════════════════════════════════════════════════════════════════════════════════
// O usuário achou o defeito perguntando por que, na ALOS3, LPA R$2,04 × payout 84% dava R$1,71
// e a coluna mostrava R$2,30. A conta dele estava certa; a tabela é que não fechava.
//
// COMO ERA (errado): o DPS era `data-dy-proj × cotação`. Três consequências ruins:
//   1. O DIVIDENDO POR AÇÃO FLUTUAVA COM O PREÇO DA AÇÃO. Se o papel subisse 10%, a tabela
//      passava a dizer que a empresa pagaria 10% mais dividendo. Isso é o mundo ao contrário:
//      o dividendo é decisão da empresa sobre o lucro dela, não sobre a cotação.
//   2. O DY ficava CONGELADO — era ele o número fixo — quando o DY é justamente a parte que
//      deve se mover com o preço.
//   3. O payout era TEXTO ESTÁTICO, escrito na análise, sem relação viva com nenhum dos dois.
//      As três células diziam coisas de bases diferentes e ninguém percebia.
//
// COMO É AGORA (invertido):
//      DPS = LPA exibido × payout          ← fundamento, NÃO depende do preço
//      DY  = DPS ÷ cotação                 ← deriva, e varia com o preço, como deve
//
// Para isso a linha precisa declarar `data-payout`. Sem ele, o comportamento antigo continua
// valendo (é o caso das linhas cujo DY veio de guidance e não de payout × lucro), e a coluna
// de payout mostra "—" em vez de mentir sobre uma relação que não existe.
//
// ⚠️ O LPA usado é o EXIBIDO na coluna 7, e é por isso que as linhas com base própria levam
// `data-lpa-manual="true"`: o payout da análise foi aplicado a UMA base (FFO por ação no
// shopping, LPA FY2025 na indústria, LPA 2026E na seguradora). Deixar o sync do Partnr trocar
// essa base por baixo quebra a conta de novo — foi exatamente o que aconteceu com a ALOS3.
// ── Escrita de célula que NÃO DESTRÓI A TOOLTIP ──────────────────────────────────────────
// A auditoria de 06/09/2026 mostrou que várias colunas apareciam sem ⓘ mesmo tendo tooltip
// escrita no HTML: o JS reescrevia a célula com `textContent = ...`, e isso apaga o
// <span class="col-tip"> junto com o valor. O usuário pediu que TODO campo tenha racional
// declarado — de nada adianta gerar a tooltip se o primeiro recálculo a remove.
//
// _celTip() guarda a tooltip original no dataset na primeira passada e a reanexa sempre.
// Se a célula não tinha tooltip, aceita uma de fallback passada pelo chamador.
function _celTip(cell, valorHTML, tipFallback) {
  if (!cell) return;
  if (cell.dataset.tipOrig === undefined) {
    const t = cell.querySelector('.col-tip');
    cell.dataset.tipOrig = t ? (t.dataset.tip || '') : '';
  }
  const tip = cell.dataset.tipOrig || tipFallback || '';
  cell.innerHTML = valorHTML + (tip
    ? `<span class="col-tip" data-tip="${tip.replace(/"/g, '&quot;')}">ⓘ</span>` : '');
}

function atualizarDivDY(row, cotacao) {
  const cells = row.querySelectorAll('td');
  if (!cotacao || !cells[9] || !cells[10]) return;
  const payout = parseFloat(row.dataset.payout) || 0;
  const lpa = parseFloat((cells[7]?.textContent || '').replace(/[^0-9,.-]/g, '').replace(',', '.')) || 0;

  if (payout > 0 && lpa > 0) {
    const dps = lpa * payout;
    _celTip(cells[9], `R$ ${dps.toFixed(2).replace('.', ',')}`);
    _celTip(cells[10], ((dps / cotacao) * 100).toFixed(2).replace('.', ',') + '%');
    row.dataset.dyProj = (dps / cotacao).toFixed(4);   // mantém o resto do app consistente
    return;
  }
  const dyProj = parseFloat(row.dataset.dyProj) || 0;  // rota antiga, para linha sem payout
  if (dyProj > 0) {
    _celTip(cells[9], `R$ ${(dyProj * cotacao).toFixed(2).replace('.', ',')}`);
    _celTip(cells[10], (dyProj * 100).toFixed(2).replace('.', ',') + '%');
  }
}

function calcularDerivadosRadar() {
  document.querySelectorAll('#tableBody tr[data-ticker]').forEach(row => {
    const cells = row.querySelectorAll('td');
    const dyProj  = parseFloat(row.dataset.dyProj) || 0;
    const cotacao = parseFloat((cells[17]?.textContent||'').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
    if (!cotacao) return;

    // Div./Ação proj (cell 9) e DY proj (cell 10) — ver atualizarDivDY() acima
    atualizarDivDY(row, cotacao);

    // Preço Justo
    calcularPrecoJusto(row, cotacao);

    // Margem de segurança (.margem-cell), Retorno total (cell 18), IPCA+ (cell 19)
    const precoJusto = parseFloat(row.dataset.precoJusto) || 0;
    const margemCell = row.querySelector('.margem-cell');
    if (precoJusto > 0 && margemCell) {
      renderMargemRetorno(cells, margemCell, precoJusto, cotacao, dyProj);
    }
  });
}

// ⚠️ 13/09/2026 — O PREÇO-TETO SAIU DA PLANILHA. Decisão do usuário: "vou querer deixar
// somente o preço justo e a margem de segurança para o preço justo, pra simplificar".
// Antes havia DOIS números de valor na mesma linha — o justo (mediana dos métodos) e o teto
// (piso da faixa, que embutia uma margem própria de 4% a 28% conforme a empresa). Dois
// números para a mesma pergunta confundem mais do que informam, e a margem que o teto embutia
// agora é escolha explícita de quem lê: a coluna mostra a margem contra o JUSTO e cada um
// define o mínimo que aceita.
// A função abaixo é o cálculo de fallback por múltiplo histórico (data-pl-hist) — está
// dormente, nenhum ticker define esse atributo hoje, e passou a escrever precoJusto.
//
// Preço Justo (fallback) = (DPS + P_alvo) / (1 + IPCA + PREMIO_IPCA)
// P_alvo = LPA × P/L Histórico; DPS = DY proj × cotação
// P/L Histórico não é mais uma coluna visível — vem do atributo oculto data-pl-hist do <tr>
// (ver comentário no topo de data/radar-rows.data.js).
function calcularPrecoJusto(row, cotacaoOverride) {
  const cells   = row.querySelectorAll('td');
  const lpa     = parseFloat((cells[7]?.textContent||'').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
  const plHist  = parseFloat(row.dataset.plHist) || 0;
  const cotacao = cotacaoOverride || parseFloat((cells[17]?.textContent||'').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
  const dyProj  = parseFloat(row.dataset.dyProj) || 0;
  if (!lpa || !plHist || !cotacao) return;
  const pAlvo = lpa * plHist;             // preço-alvo por múltiplo histórico
  const dps   = dyProj * cotacao;         // dividendo projetado por ação
  const desc  = 1 + IPCA + PREMIO_IPCA;   // taxa de desconto exigida
  const justo = (dps + pAlvo) / desc;
  row.dataset.precoJusto = justo.toFixed(2);
  if (cells[16]) {
    const tip = [
      'PREÇO JUSTO — variáveis','',
      'LPA proj.: ' + _fmtBR(lpa),
      'P/L Histórico: ' + _fmtNM(plHist),
      'DY proj.: ' + _fmtPC(dyProj),
      'Cotação: ' + _fmtBR(cotacao),
      '──────────────',
      'P-alvo = LPA × P/L Hist = ' + _fmtBR(pAlvo),
      'DPS = DY × Cotação = ' + _fmtBR(dps),
      'Desconto = 1 + IPCA ' + _fmtPC(IPCA) + ' + Prêmio ' + _fmtPC(PREMIO_IPCA) + ' = ' + _fmtNM(desc, 3),
      '──────────────',
      'Justo = (DPS + P-alvo) ÷ Desconto',
      '= (' + _fmtBR(dps) + ' + ' + _fmtBR(pAlvo) + ') ÷ ' + _fmtNM(desc, 3) + ' = ' + _fmtBR(justo)
    ].join('\n');
    cells[16].innerHTML = '';
    const val = document.createElement('span');
    val.textContent = _fmtBR(justo);
    cells[16].appendChild(val);
    cells[16].appendChild(document.createTextNode(' '));
    cells[16].appendChild(_varTipBtn(tip));
  }
}

// ── Helpers de formatação e tooltip de variáveis ──
function _fmtBR(v){ return 'R$ ' + v.toFixed(2).replace('.', ','); }
function _fmtPC(v){ return (v * 100).toFixed(1).replace('.', ',') + '%'; }
function _fmtNM(v, d){ return v.toFixed(d == null ? 1 : d).replace('.', ','); }
function _varTipBtn(tip){
  const b = document.createElement('span');
  b.className = 'teto-tip';
  b.textContent = 'ⓘ';
  b.dataset.tip = tip;
  return b;
}

// Renderiza Margem (cell 20), Retorno Total (cell 21) e Retorno Real (cell 22)
// com botões de tooltip explicando as variáveis de cada coluna.
function renderMargemRetorno(cells, margemCell, precoJusto, cotacao, dyProj){
  if (!(precoJusto > 0) || !cotacao) return;
  const pct     = ((precoJusto - cotacao) / precoJusto) * 100;
  const valoriz = ((precoJusto - cotacao) / cotacao) * 100;
  const ret     = valoriz + (dyProj * 100);

  // Margem de Segurança
  if (margemCell) {
    margemCell.innerHTML = margemTag(pct);
    const tipM = [
      'MARGEM DE SEGURANÇA — variáveis','',
      'Preço Justo: ' + _fmtBR(precoJusto),
      'Cotação: ' + _fmtBR(cotacao),
      '──────────────',
      'Margem = (Justo − Cotação) ÷ Justo',
      '= (' + _fmtBR(precoJusto) + ' − ' + _fmtBR(cotacao) + ') ÷ ' + _fmtBR(precoJusto),
      '= ' + _fmtNM(pct) + '%',
      (pct >= 0 ? 'Positivo → cotação abaixo do justo' : 'Negativo → cotação acima do justo')
    ].join('\n');
    margemCell.appendChild(document.createTextNode(' '));
    margemCell.appendChild(_varTipBtn(tipM));
  }

  // Retorno Total
  if (cells[19]) {
    cells[19].innerHTML = '';
    const v = document.createElement('span');
    v.textContent = (ret >= 0 ? '+' : '') + ret.toFixed(1) + '%';
    const tipR = [
      'RETORNO TOTAL — variáveis','',
      'Preço Justo: ' + _fmtBR(precoJusto),
      'Cotação: ' + _fmtBR(cotacao),
      'DY proj.: ' + _fmtPC(dyProj),
      '──────────────',
      'Valorização = (Teto − Cotação) ÷ Cotação = ' + _fmtNM(valoriz) + '%',
      'Dividendos (DY proj.) = ' + _fmtPC(dyProj),
      '──────────────',
      'Retorno = Valorização + DY = ' + (ret >= 0 ? '+' : '') + _fmtNM(ret) + '%'
    ].join('\n');
    cells[19].appendChild(v);
    cells[19].appendChild(document.createTextNode(' '));
    cells[19].appendChild(_varTipBtn(tipR));
  }
}

// ── Tooltip flutuante (position:fixed no body) — evita clipping do overflow da tabela ──
(function initCellTooltip(){
  let pop = null;
  function ensure(){
    if(!pop){ pop = document.createElement('div'); pop.id = 'cellTipPop'; document.body.appendChild(pop); }
    return pop;
  }
  function show(btn){
    const p = ensure();
    p.textContent = btn.dataset.tip || '';
    p.classList.add('show');
    const r = btn.getBoundingClientRect();
    let left = r.left + r.width/2 - p.offsetWidth/2;
    left = Math.max(8, Math.min(left, window.innerWidth - p.offsetWidth - 8));
    let top = r.bottom + 6;
    if(top + p.offsetHeight > window.innerHeight - 8) top = r.top - p.offsetHeight - 6;
    p.style.left = left + 'px';
    p.style.top  = top + 'px';
  }
  function hide(){ if(pop) pop.classList.remove('show'); }
  document.addEventListener('mouseover', e => { const b = e.target.closest && e.target.closest('.teto-tip,.rank-badge[data-tip]'); if(b) show(b); });
  document.addEventListener('mouseout',  e => { const b = e.target.closest && e.target.closest('.teto-tip,.rank-badge[data-tip]'); if(b) hide(); });
  window.addEventListener('scroll', hide, true);
})();

// ⚠️ APOSENTADA EM 06/09/2026 — TERCEIRO MOTOR ESCREVENDO AS MESMAS CÉLULAS
// Esta função projetava o lucro por CAGR de 2 anos capado por setor e escrevia nas colunas 4
// e 5. Enquanto existia, disputava as células com scripts/gerar_colunas.py: a CPFE3 exibia
// R$5,7 bi / R$6,1 bi (CAGR) em vez dos R$6,29 bi / R$6,05 bi gerados pelo motor de setor,
// porque a linha dela não tinha data-lucro-manual e o sync ganhava.
//
// É a MESMA classe de bug do data-pl-hist (duas fontes de verdade para o preço-teto, ganhava
// a errada) e do payout duplicado dentro do teto_bazin. O padrão já se repetiu três vezes:
// quando duas rotinas podem escrever a mesma célula, a que sobrevive é a última a rodar, não
// a mais correta.
//
// As colunas 4 e 5 agora vêm de UMA fonte só: lucro LTM da base e lucro normalizado do motor
// de setor (METODOLOGIA_ANALISE.md seções 10 e 23). A projeção por CAGR não é usada em lugar
// nenhum da decisão — o preço-teto usa múltiplo sobre lucro realizado, e a TIR usa o lucro
// normalizado. Mantida como código morto documentado em vez de apagada, para o registro.
// ⚠️ REMOVIDA EM 13/09/2026. Era uma projeção de lucro por CAGR de dois pontos, capada por
// segmento, e já estava DESLIGADA (a função começava com `return;`) desde que o lucro
// normalizado passou a vir de scripts/gerar_colunas.py. As células em que ela escrevia — Lucro
// LTM e Lucro normalizado — deixaram de existir quando a coluna Lucro Projetado 2026 entrou, e
// a projeção agora é gerada no Python, com taxa vinda do lucro recorrente por regressão log.
function applyMobileColHide(){
  // No mobile as colunas ficam todas visíveis via CSS (scroll horizontal)
  // Esta função só aplica classes para referência — CSS mobile sobrescreve com display:table-cell
  const MOB_HIDE_COLS = [3,5,6,7,8,9,12,13,14,15,18];
  document.querySelectorAll('#tableBody tr').forEach(row=>{
    const cells = row.querySelectorAll('td');
    MOB_HIDE_COLS.forEach(i=>{ if(cells[i]) cells[i].classList.add('col-mob-hide'); });
  });
}

// ── MOBILE: cards de posição ──
function renderMobileCards(){
  const container = document.getElementById('mobilePosCards');
  if(!container) return;
  // Só renderiza no mobile
  if(window.innerWidth > 768){
    container.innerHTML = '';
    container.style.display = 'none';
    return;
  }
  container.style.display = 'flex';
  container.style.flexDirection = 'column';
  container.style.gap = '0.6rem';
  const rows = getCarteiraRows();
  let totalSaldo = 0;
  rows.forEach(r => totalSaldo += parseFloat(r.dataset.saldo)||0);
  rows.sort((a,b)=>(parseFloat(b.dataset.saldo)||0)-(parseFloat(a.dataset.saldo)||0));
  let html = '';
  rows.forEach(row=>{
    const ticker = (row.dataset.ticker||'').replace('.SA','');
    const nome = row.querySelector('.empresa-name')?.textContent||'';
    const qtd = parseFloat(row.dataset.qtd)||0;
    const pm = parseFloat(row.dataset.pm)||0;
    const saldo = parseFloat(row.dataset.saldo)||0;
    const prov = parseFloat(row.dataset.proventos12m)||0;
    const dyAtual = parseFloat(row.dataset.dyAtual)||0;
    const rent = parseFloat(row.dataset.rent)||0;
    const varPct = parseFloat(row.dataset.var)||0;
    const pctCart = totalSaldo>0?(saldo/totalSaldo)*100:0;
    const cotacaoCell = row.querySelector('.cotacao-cell');
    const cotTxt = cotacaoCell?.textContent||'—';
    const rentClass = rent>=0?'rent-pos':'rent-neg';
    const varClass = varPct>=0?'rent-pos':'rent-neg';
    const veredicto = row.dataset.veredicto||'';
    const verd = veredicto==='compra'?'🟢':'veredicto'==='aguardar'?'🟡':'';
    const barW = Math.min(pctCart*4,100);
    html += `<div class="mob-card">
      <div class="mob-card-top">
        <div>
          <div class="mob-card-ticker">${ticker}</div>
          <div class="mob-card-nome">${nome}</div>
        </div>
        <div class="mob-card-saldo">R$ ${saldo.toLocaleString('pt-BR',{maximumFractionDigits:0})}</div>
      </div>
      <div class="mob-card-grid">
        <div class="mob-card-item">
          <span class="mob-card-label">Cotação</span>
          <span class="mob-card-value num-blue">${cotTxt}</span>
        </div>
        <div class="mob-card-item">
          <span class="mob-card-label">Variação</span>
          <span class="mob-card-value ${varClass}">${varPct>=0?'+':''}${varPct.toFixed(1)}%</span>
        </div>
        <div class="mob-card-item">
          <span class="mob-card-label">Rentab.</span>
          <span class="mob-card-value ${rentClass}">${rent>=0?'+':''}${rent.toFixed(1)}%</span>
        </div>
        <div class="mob-card-item">
          <span class="mob-card-label">Qtd</span>
          <span class="mob-card-value">${qtd.toLocaleString('pt-BR')}</span>
        </div>
        <div class="mob-card-item">
          <span class="mob-card-label">Prov. 12M</span>
          <span class="mob-card-value num-green">R$ ${prov.toLocaleString('pt-BR',{maximumFractionDigits:0})}</span>
        </div>
        <div class="mob-card-item">
          <span class="mob-card-label">DY Atual</span>
          <span class="mob-card-value">${dyAtual.toFixed(2)}%</span>
        </div>
      </div>
      <div class="mob-pct-bar"><div class="mob-pct-bar-fill" style="width:${barW}%"></div></div>
      <div style="font-size:10px;color:var(--text3);margin-top:4px;text-align:right;">${pctCart.toFixed(1)}% da carteira</div>
    </div>`;
  });
  container.innerHTML = html;
}

