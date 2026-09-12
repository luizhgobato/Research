// ══════════════════════════════════════════════════════
// GRÁFICOS — Carteira Luiz (#page-resumoluiz) e Carteira da Flavia (#page-flavia)
// ══════════════════════════════════════════════════════
// Essas duas páginas são relatórios estáticos (rp-table), diferentes do motor do Radar.
// Em vez de hardcodar os números dos gráficos (duplicando os das tabelas — foi assim que
// vários bugs de dessincronia apareceram no Radar), os gráficos aqui LEEM as próprias
// tabelas já renderizadas no HTML e desenham em cima. Editar uma tabela em index.html
// atualiza o gráfico correspondente automaticamente, sem precisar tocar em JS.
//
// Paleta categórica validada (dataviz skill, references/palette.md) — 8 cores, ordem fixa,
// testada contra confusão de daltonismo (ΔE CVD ≥8, ΔE visão normal ≥15 entre vizinhas).
const RP_COLORS = ['#2a78d6','#eb6834','#1baf7a','#eda100','#e87ba4','#008300','#4a3aa7','#e34948'];

function _rpParseNum(str) {
  if (str === null || str === undefined) return 0;
  const clean = String(str).replace(/−/g, '-').replace(/[^\d,.-]/g, '');
  if (!clean) return 0;
  const norm = clean.includes(',') ? clean.replace(/\./g, '').replace(',', '.') : clean;
  const n = parseFloat(norm);
  return isNaN(n) ? 0 : n;
}
function _rpParsePP(text) {
  if (!text || String(text).indexOf('pp') === -1) return null;
  return _rpParseNum(text);
}
// Extrai {label, value} das linhas de um <table class="rp-table">, pulando totais/subtotais
// (identificados pelo fundo escuro/cinza padrão usado nessas tabelas para totalizadores).
function _rpTableRows(table, labelIdx, valueIdx, parseFn) {
  if (!table) return [];
  const parse = parseFn || _rpParseNum;
  return Array.from(table.querySelectorAll('tbody tr'))
    .filter(tr => {
      const style = tr.getAttribute('style') || '';
      return style.indexOf('#1e1a2e') === -1 && style.indexOf('#f7f7f5') === -1;
    })
    .map(tr => {
      const cells = tr.querySelectorAll('td');
      const label = (cells[labelIdx]?.textContent || '').trim();
      const value = parse(cells[valueIdx]?.textContent);
      return { label, value };
    })
    .filter(r => r.label);
}

// ── Donut genérico (reaproveita makeSVGDonut de js/graficos.js) ────────────────────────
// A coluna lida (valueIdx) já é o valor em R$, então serve tanto de fatia quanto de "amounts"
// — a legenda mostra "R$ X · Y%".
function renderRpDonut(tableId, containerId, labelIdx, valueIdx) {
  const table = document.getElementById(tableId), el = document.getElementById(containerId);
  if (!table || !el) return;
  const rows = _rpTableRows(table, labelIdx, valueIdx).filter(r => r.value > 0);
  if (!rows.length) { el.innerHTML = ''; return; }
  const vals = rows.map(r => r.value);
  makeSVGDonut(el, rows.map(r => r.label), vals, RP_COLORS, { amounts: vals });
}

// Patrimônio total da carteira, lido da linha de total da tabela de Patrimônio (fundo #1e1a2e).
// Usado para converter os gráficos que trabalham em % (Segmento, Posição) de volta para R$.
function _rpTotalPatrimonio(classeTableId) {
  const table = document.getElementById(classeTableId);
  if (!table) return 0;
  const totalRow = Array.from(table.querySelectorAll('tbody tr'))
    .find(tr => (tr.getAttribute('style') || '').indexOf('#1e1a2e') !== -1);
  return totalRow ? _rpParseNum(totalRow.querySelectorAll('td')[1]?.textContent) : 0;
}

// ── Barra horizontal (magnitude, todas positivas) — ideal p/ listas de tickers ─────────
// wideLabels: reserva mais espaço à direita quando o rótulo do valor traz R$ + % (texto longo),
// senão a barra mais comprida empurra o texto para fora do SVG.
function makeSVGHBar(el, labels, values, colors, fmt, wideLabels) {
  if (!el || !labels.length) { if (el) el.innerHTML = ''; return; }
  let W = el.offsetWidth || el.parentElement?.offsetWidth || 600;
  W = Math.max(Math.min(W, 720), 320);
  const rowH = 30, padL = 70, padR = wideLabels ? 170 : 90, padT = 4, padB = 4;
  const H = labels.length * rowH + padT + padB;
  const cW = W - padL - padR;
  const maxV = Math.max(...values, 0.0001);
  let bars = '';
  labels.forEach((l, i) => {
    const v = values[i];
    const y = padT + i * rowH;
    const w = Math.max((v / maxV) * cW, 2);
    const col = Array.isArray(colors) ? colors[i % colors.length] : colors;
    const txt = fmt ? fmt(v, i) : v;
    bars += `<text x="${padL - 8}" y="${y + rowH / 2 + 4}" text-anchor="end" font-size="13" fill="#555">${l}</text>`;
    bars += `<rect x="${padL}" y="${y + 6}" width="${w}" height="${rowH - 12}" rx="3" fill="${col}" opacity="0.88"><title>${l}: ${txt}</title></rect>`;
    bars += `<text x="${padL + w + 7}" y="${y + rowH / 2 + 4}" font-size="12.5" font-weight="700" fill="#333">${txt}</text>`;
  });
  el.innerHTML = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible;">${bars}</svg>`;
}
// Lê % Carteira (posição atual) por ativo de uma tabela de posição e desenha barra horizontal.
// pctSelector: '.cw-pct-cart' (Flavia, dinâmico) ou 'td:nth-child(2)' (Luiz, texto estático).
// O rótulo de cada barra mostra "R$ X · Y%" quando a linha já tem saldo calculado (cw-saldo);
// se a Qtd/PM ainda não foram preenchidos, cai de volta para só o percentual.
function renderRpPosicaoBar(tbodyId, containerId, pctSelector) {
  const tbody = document.getElementById(tbodyId), el = document.getElementById(containerId);
  if (!tbody || !el) return;
  const rows = Array.from(tbody.querySelectorAll('tr[data-ticker]'))
    .map(tr => {
      const ticker = (tr.dataset.ticker || '').replace('.SA', '');
      const pctCell = tr.querySelector(pctSelector);
      return {
        label: ticker,
        value: _rpParseNum(pctCell?.textContent),
        amount: _rpParseNum(tr.querySelector('.cw-saldo')?.textContent),
      };
    })
    .filter(r => r.value > 0)
    .sort((a, b) => b.value - a.value);
  renderRpHBarFmt(el, rows, v => v.toFixed(2).replace('.', ',') + '%');
}
function renderRpHBarFmt(el, rows, fmt) {
  const anyAmount = rows.some(r => r.amount > 0);
  const fmtFinal = anyAmount
    ? (v, i) => {
        const a = rows[i] && rows[i].amount > 0 ? 'R$ ' + Math.round(rows[i].amount).toLocaleString('pt-BR') + ' · ' : '';
        return a + fmt(v);
      }
    : fmt;
  makeSVGHBar(el, rows.map(r => r.label), rows.map(r => r.value), RP_COLORS, fmtFinal, anyAmount);
}
// Lê qualquer coluna numérica de uma rp-table (ex.: "Div. 2026" da tabela Renda Esperada)
// e desenha barra horizontal ordenada por magnitude — pula linhas de total/subtotal.
function renderRpTableHBar(tableId, containerId, labelIdx, valueIdx, fmt) {
  const table = document.getElementById(tableId), el = document.getElementById(containerId);
  if (!table || !el) return;
  const rows = _rpTableRows(table, labelIdx, valueIdx).filter(r => r.value > 0).sort((a, b) => b.value - a.value);
  renderRpHBarFmt(el, rows, fmt);
}

// ── Barra divergente (desvio +/- vs. Ideal) ─────────────────────────────────────────────
function makeSVGDivergingBar(el, labels, values, fmt, wideLabels) {
  if (!el || !labels.length) { if (el) el.innerHTML = ''; return; }
  let W = el.offsetWidth || el.parentElement?.offsetWidth || 600;
  W = Math.max(Math.min(W, 720), 360);
  // wideLabels: o texto do valor ("−39,8pp · −R$ 286.360") é longo demais para caber na ponta
  // da barra sem esbarrar no rótulo da categoria do lado oposto. Nesse modo o valor vai para
  // uma COLUNA FIXA na direita, alinhada para todas as linhas — some a colisão e fica mais
  // fácil de comparar linha a linha. No modo normal (só "pp") ele continua na ponta da barra.
  const valCol = wideLabels ? 168 : 0;
  const rowH = 36, padL = 234, padR = (wideLabels ? valCol : 70), padT = 6, padB = 6;
  const H = labels.length * rowH + padT + padB;
  const cW = W - padL - padR;
  const maxAbs = Math.max(...values.map(v => Math.abs(v)), 0.0001);
  const half = cW / 2, midX = padL + half;
  // Reserva um espaço fixo (labelSpace) na ponta de fora de cada lado para o texto do valor —
  // sem isso, a barra do maior |valor| encosta no rótulo da categoria (colisão de texto).
  const labelSpace = wideLabels ? 6 : 60, barMax = Math.max(half - labelSpace, 10);
  let bars = '';
  labels.forEach((l, i) => {
    const v = values[i];
    const y = padT + i * rowH;
    const w = (Math.abs(v) / maxAbs) * barMax;
    const x = v >= 0 ? midX : midX - w;
    const color = v >= 0 ? '#16a34a' : '#dc2626';
    const txt = fmt ? fmt(v, i) : v;
    bars += `<text x="${padL - 10}" y="${y + rowH / 2 + 4}" text-anchor="end" font-size="13" fill="#555">${l}</text>`;
    bars += `<rect x="${x}" y="${y + 7}" width="${Math.max(w, 1.5)}" height="${rowH - 14}" rx="3" fill="${color}" opacity="0.85"><title>${l}: ${txt}</title></rect>`;
    const vx = wideLabels ? W - 4 : (v >= 0 ? x + w + 7 : x - 7);
    const anchor = wideLabels ? 'end' : (v >= 0 ? 'start' : 'end');
    bars += `<text x="${vx}" y="${y + rowH / 2 + 4}" text-anchor="${anchor}" font-size="12.5" font-weight="700" fill="${color}">${txt}</text>`;
  });
  el.innerHTML = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible;">
    <line x1="${midX}" y1="${padT}" x2="${midX}" y2="${H - padB}" stroke="#ddd" stroke-width="1"/>
    <text x="${midX}" y="${padT - 2 < 8 ? 8 : padT}" text-anchor="middle" font-size="9" fill="#bbb"></text>
    ${bars}
  </svg>`;
}
// Lê a coluna "Desvio" (ex.: "−16,08pp"/"+10,46pp") da tabela Carteira Ideal e desenha
// a barra divergente. Pula linhas sem pp (ex.: "Fora da régua", sem % Ideal definido).
// Além do desvio em pp, mostra o desvio em R$ (Valor Atual − Valor-alvo) — é o número que
// diz quanto falta comprar / quanto sobra em cada grupo, mais acionável que o pp sozinho.
function renderRpDesvioChart(tableId, containerId) {
  const table = document.getElementById(tableId), el = document.getElementById(containerId);
  if (!table || !el) return;
  const trs = Array.from(table.querySelectorAll('tbody tr')).filter(tr => {
    const style = tr.getAttribute('style') || '';
    return style.indexOf('#1e1a2e') === -1 && style.indexOf('#f7f7f5') === -1;
  });
  const rows = trs.map(tr => {
    const c = tr.querySelectorAll('td');
    return {
      label: (c[0]?.textContent || '').trim(),
      pp: _rpParsePP(c[5]?.textContent),
      gap: _rpParseNum(c[3]?.textContent) - _rpParseNum(c[2]?.textContent),
    };
  }).filter(r => r.label && r.pp !== null);
  const fmtGap = g => (g >= 0 ? '+' : '−') + 'R$ ' + Math.round(Math.abs(g)).toLocaleString('pt-BR');
  makeSVGDivergingBar(
    el,
    rows.map(r => r.label),
    rows.map(r => r.pp),
    (v, i) => {
      const pp = (v >= 0 ? '+' : '') + v.toFixed(1).replace('.', ',').replace('-', '−') + 'pp';
      const r = rows[i];
      return r && isFinite(r.gap) && r.gap !== 0 ? pp + ' · ' + fmtGap(r.gap) : pp;
    },
    true
  );
}

// ── Barra de progresso (Tempo até o Objetivo) ───────────────────────────────────────────
function renderRpProgress(tableId, containerId) {
  const table = document.getElementById(tableId), el = document.getElementById(containerId);
  if (!table || !el) return;
  // Sem o filtro de total/subtotal de _rpTableRows: aqui a linha "Tempo estimado" É o dado
  // que precisamos, mesmo estilizada como destaque (fundo escuro igual a um total).
  const rows = Array.from(table.querySelectorAll('tbody tr')).map(tr => {
    const cells = tr.querySelectorAll('td');
    return { label: (cells[0]?.textContent || '').trim(), value: (cells[1]?.textContent || '').trim() };
  });
  const get = label => rows.find(r => r.label.indexOf(label) === 0)?.value || '';
  const atual = _rpParseNum(get('Renda mensal atual'));
  const meta = _rpParseNum(get('Meta de renda mensal'));
  const tempoRaw = get('Tempo estimado');
  if (!atual || !meta) { el.innerHTML = ''; return; }
  const pct = Math.min(100, (atual / meta) * 100);
  const fmtR = v => 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  el.innerHTML = `
    <div style="display:flex;justify-content:space-between;font-size:11px;color:#666;margin-bottom:5px;">
      <span><b style="color:#333;">${fmtR(atual)}</b>/mês hoje</span>
      <span>Meta <b style="color:#333;">${fmtR(meta)}</b>/mês</span>
    </div>
    <div style="background:#ececec;border-radius:8px;height:16px;overflow:hidden;">
      <div style="background:linear-gradient(90deg,#2a78d6,#4a3aa7);height:100%;width:${pct}%;border-radius:8px;min-width:${pct > 0 ? 10 : 0}px;"></div>
    </div>
    <div style="text-align:center;margin-top:7px;font-size:12px;color:#333;">
      <b>${pct.toFixed(1).replace('.', ',')}%</b> da meta atingido${tempoRaw ? ' · tempo estimado: <b>' + tempoRaw + '</b>' : ''}
    </div>`;
}

// ── Donut de Segmento (setor de atuação) — agrupa as linhas de posição por data-segmento ──
// Lê % Carteira já calculado em cada linha (mesma fonte de dados de renderRpPosicaoBar,
// sem duplicar números). Para Luiz, as classes não-ações (Fundos/ETFs) não existem como
// linhas individuais em luizPosBody — mescla-as a partir da tabela de Patrimônio via
// opts.classeTableId, pulando os rótulos já cobertos pelas linhas de ações (opts.skipLabels).
function renderRpSegmentoChart(tbodyId, containerId, opts) {
  opts = opts || {};
  const tbody = document.getElementById(tbodyId), el = document.getElementById(containerId);
  if (!tbody || !el) return;
  const pctSelector = opts.pctSelector || '.cw-pct-cart';
  const map = {};
  Array.from(tbody.querySelectorAll('tr[data-segmento]')).forEach(tr => {
    const seg = tr.dataset.segmento;
    if (!seg) return;
    const cell = tr.querySelector(pctSelector);
    const v = _rpParseNum(cell?.textContent);
    if (v > 0) map[seg] = (map[seg] || 0) + v;
  });
  if (opts.classeTableId && opts.skipLabels) {
    const table = document.getElementById(opts.classeTableId);
    if (table) {
      _rpTableRows(table, 0, 2, _rpParseNum).forEach(r => {
        if (opts.skipLabels.indexOf(r.label) !== -1) return;
        map[r.label] = (map[r.label] || 0) + r.value;
      });
    }
  }
  const rows = Object.entries(map)
    .map(([label, value]) => ({ label, value }))
    .filter(r => r.value > 0)
    .sort((a, b) => b.value - a.value);
  if (!rows.length) { el.innerHTML = ''; return; }
  // As fatias aqui são % da carteira; converte para R$ usando o patrimônio total para que a
  // legenda mostre também quanto dinheiro há em cada segmento.
  const total = _rpTotalPatrimonio(opts.totalTableId);
  const amounts = total > 0 ? rows.map(r => r.value / 100 * total) : null;
  makeSVGDonut(el, rows.map(r => r.label), rows.map(r => r.value), RP_COLORS, { amounts });
}

// ── Recalcula Patrimônio total / Carteira Ideal / stats do topo após "Atualizar Cotação" ──
// A tabela de posição (flaviaPosBody/luizPosBody) já é recalculada pelo motor genérico de
// js/carteira-manual.js, mas o resto da página (tabela Patrimônio, donut, Carteira Ideal,
// resumo do topo) eram números estáticos do HTML — não reagiam à atualização de cotação.
// Esta função lê os saldos já recalculados na tabela de posição (cw-saldo) e propaga pro
// resto da página, mesmo princípio de "ler do DOM, não duplicar dado" das demais funções
// deste arquivo. Só roda depois de Qtd/PM preenchidos (senão não há saldo pra ler).
const RP_PATRIMONIO_CFG = {
  Flavia: {
    pageId: 'page-flavia',
    posBodyId: 'flaviaPosBody',
    classeTableId: 'tblFlaviaClasse',
    idealTableId: 'tblFlaviaIdeal',
    fixos: [], // R$200k da academia está DENTRO do saldo do LFTB11, não é classe à parte
    // FIQE3 é Crescimento (telecom em expansão), não Dividendos — reclassificado a pedido do usuário
    dividendosBaseline: 153582.85,
    crescimentoBaseline: 60200.00,
  },
  Luiz: {
    pageId: 'page-resumoluiz',
    posBodyId: 'luizPosBody',
    classeTableId: 'tblLuizClasse',
    idealTableId: 'tblLuizIdeal',
    fixos: [
      { label: 'Previdência Privada', valor: 131616.44 },
      { label: 'ETFs BR', valor: 8521.76 },
      { label: 'ETFs Internacionais', valor: 6630.02 },
    ],
    dividendosBaseline: 348189.43,
    crescimentoBaseline: 216799.87,
  },
};
function _rpFmtR(v) { return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function _rpFmtPct(v) { return v.toFixed(2).replace('.', ',') + '%'; }

function atualizarResumoPatrimonio(prefix) {
  const cfg = RP_PATRIMONIO_CFG[prefix];
  if (!cfg) return;
  const tbody = document.getElementById(cfg.posBodyId);
  if (!tbody) return;

  let acoesTotal = 0;
  tbody.querySelectorAll('tr[data-classe="acao"]').forEach(tr => {
    acoesTotal += _rpParseNum(tr.querySelector('.cw-saldo')?.textContent);
  });
  if (!(acoesTotal > 0)) return; // Qtd/PM ainda não preenchidos — nada a propagar

  const lftbRow = tbody.querySelector('tr[data-ticker="LFTB11.SA"]');
  const lftbTotal = lftbRow ? _rpParseNum(lftbRow.querySelector('.cw-saldo')?.textContent) : 0;
  const fixosTotal = cfg.fixos.reduce((s, f) => s + f.valor, 0);
  const novoTotal = acoesTotal + lftbTotal + fixosTotal;
  if (!(novoTotal > 0)) return;

  // ── Tabela Patrimônio + donut ──
  const classeTable = document.getElementById(cfg.classeTableId);
  if (classeTable) {
    Array.from(classeTable.querySelectorAll('tbody tr')).forEach(tr => {
      const cells = tr.querySelectorAll('td');
      const label = (cells[0]?.textContent || '').trim();
      const isTotal = (tr.getAttribute('style') || '').indexOf('#1e1a2e') !== -1;
      if (isTotal) {
        if (cells[1]) cells[1].textContent = _rpFmtR(novoTotal);
        if (cells[2]) cells[2].textContent = '100%';
        return;
      }
      let valor = null;
      if (label.indexOf('Ações') === 0) valor = acoesTotal;
      else if (label.indexOf('Renda Fixa') === 0) valor = lftbTotal;
      else { const f = cfg.fixos.find(f => f.label === label); if (f) valor = f.valor; }
      if (valor === null) return;
      if (cells[1]) cells[1].textContent = _rpFmtR(valor);
      if (cells[2]) cells[2].textContent = _rpFmtPct(valor / novoTotal * 100);
    });
    if (typeof renderRpDonut === 'function') renderRpDonut(cfg.classeTableId, `chart${prefix}Classe`, 0, 1);
  }

  // ── Resumo-grid do topo da "Posição Atual" (só existe na página do Luiz) ──
  const grid = document.querySelector(`#${cfg.pageId} .rp-resumo-grid`);
  if (grid) {
    Array.from(grid.querySelectorAll('.rp-resumo-item')).forEach(item => {
      const label = (item.querySelector('.rp-r-label')?.textContent || '').trim();
      const vals = item.querySelectorAll('.rp-r-value');
      let valor = null;
      if (label.indexOf('Ações') === 0) valor = acoesTotal;
      else if (label.indexOf('Renda Fixa') === 0) valor = lftbTotal;
      else { const f = cfg.fixos.find(f => f.label === label); if (f) valor = f.valor; }
      if (valor === null) return;
      if (vals[0]) vals[0].textContent = _rpFmtR(valor);
      if (vals[1]) vals[1].textContent = _rpFmtPct(valor / novoTotal * 100);
    });
  }

  // ── Stats do topo (rp-exec-grid) ──
  document.querySelectorAll(`#${cfg.pageId} .rp-exec-item`).forEach(item => {
    const label = (item.querySelector('.rp-exec-label')?.textContent || '').trim();
    const valEl = item.querySelector('.rp-exec-value');
    if (!valEl) return;
    if (label.indexOf('Patrimônio total') === 0) {
      valEl.textContent = _rpFmtR(novoTotal);
    } else if (label.indexOf('Progresso vs. marco') === 0) {
      valEl.textContent = (novoTotal / 2000000 * 100).toFixed(1).replace('.', ',') + '%';
    } else if (label.indexOf('Financeiro/seguros') === 0) {
      const finTickers = ['IRBR3.SA', 'BBSE3.SA', 'CXSE3.SA', 'ITUB3.SA', 'BBAS3.SA'];
      let finTotal = 0;
      finTickers.forEach(t => {
        const r = tbody.querySelector(`tr[data-ticker="${t}"]`);
        if (r) finTotal += _rpParseNum(r.querySelector('.cw-saldo')?.textContent);
      });
      valEl.textContent = _rpFmtPct(finTotal / novoTotal * 100);
      const irbrRow = tbody.querySelector('tr[data-ticker="IRBR3.SA"]');
      const alertEl = document.querySelector(`#${cfg.pageId} .rp-exec-alert`);
      if (irbrRow && alertEl) {
        const irbrPct = _rpParseNum(irbrRow.querySelector('.cw-saldo')?.textContent) / novoTotal * 100;
        const ratio = irbrPct / 12.5;
        alertEl.innerHTML = `⚠️ Maior risco agora: IRBR3 em ${_rpFmtPct(irbrPct)} da carteira (~${ratio.toFixed(1).replace('.', ',')}x o % Ideal) com veredicto 🟡 Aguardar/acima do teto — ver Diagnóstico.`;
      }
    }
  });

  // ── Carteira Ideal ──
  // Cada linha de ação carrega data-grupo="dividendos|crescimento", então Dividendos e
  // Crescimento são somados DIRETO dos saldos já atualizados — exato, e reage a
  // reclassificações (ex.: FIQE3 movida para Crescimento) sem tocar em JS.
  // Os *Baseline do cfg ficam só como fallback caso alguma linha não esteja marcada.
  const idealTable = document.getElementById(cfg.idealTableId);
  if (idealTable) {
    const somaGrupo = g => {
      let t = 0;
      tbody.querySelectorAll(`tr[data-grupo="${g}"]`).forEach(tr => {
        t += _rpParseNum(tr.querySelector('.cw-saldo')?.textContent);
      });
      return t;
    };
    let dividVal = somaGrupo('dividendos');
    let crescVal = somaGrupo('crescimento');
    if (!(dividVal + crescVal > 0)) { // nenhuma linha marcada — cai no rateio antigo
      const baseAcoes = cfg.dividendosBaseline + cfg.crescimentoBaseline;
      const scale = baseAcoes > 0 ? acoesTotal / baseAcoes : 1;
      dividVal = cfg.dividendosBaseline * scale;
      crescVal = cfg.crescimentoBaseline * scale;
    }
    Array.from(idealTable.querySelectorAll('tbody tr')).forEach(tr => {
      const cells = tr.querySelectorAll('td');
      const label = (cells[0]?.textContent || '').trim();
      const isTotal = (tr.getAttribute('style') || '').indexOf('#f7f7f5') !== -1;
      if (isTotal) {
        if (cells[2]) cells[2].textContent = _rpFmtR(novoTotal);
        if (cells[3]) cells[3].textContent = _rpFmtR(novoTotal);
        return;
      }
      let valor = null, idealPct = null;
      if (label.indexOf('Dividendos') !== -1) { valor = dividVal; idealPct = 65; }
      else if (label.indexOf('Crescimento') !== -1) { valor = crescVal; idealPct = 20; }
      else if (label.indexOf('Renda Fixa') === 0) { valor = lftbTotal; idealPct = 15; }
      else if (label.indexOf('Fora da régua') === 0) { valor = fixosTotal; }
      if (valor === null) return;
      const pct = valor / novoTotal * 100;
      if (cells[3]) cells[3].textContent = _rpFmtR(valor);
      if (cells[4]) cells[4].textContent = _rpFmtPct(pct);
      if (idealPct !== null) {
        if (cells[2]) cells[2].textContent = _rpFmtR(idealPct / 100 * novoTotal);
        if (cells[5]) {
          const desvio = pct - idealPct;
          const cls = desvio < 0 ? 'rp-tag-red' : 'rp-tag-yellow';
          const sign = desvio >= 0 ? '+' : '−';
          cells[5].innerHTML = `<span class="rp-tag ${cls}">${sign}${Math.abs(desvio).toFixed(2).replace('.', ',')}pp</span>`;
        }
      }
    });
    if (typeof renderRpDesvioChart === 'function') renderRpDesvioChart(cfg.idealTableId, `chart${prefix}Ideal`);
  }

  // ── Segmento (mescla Renda Fixa/fixos, já lê % Carteira atualizado dos data-segmento) ──
  if (typeof renderRpSegmentoChart === 'function') {
    if (prefix === 'Flavia') {
      renderRpSegmentoChart('flaviaPosBody', 'chartFlaviaSegmento', { pctSelector: '.cw-pct-cart', totalTableId: 'tblFlaviaClasse' });
    } else {
      renderRpSegmentoChart('luizPosBody', 'chartLuizSegmento', {
        pctSelector: 'td:nth-child(2)',
        classeTableId: 'tblLuizClasse',
        totalTableId: 'tblLuizClasse',
        skipLabels: ['Ações BR', 'Renda Fixa (LFTB11)']
      });
    }
  }
}

// ── Orquestrador — chamado uma vez, na primeira abertura de cada aba (showPage) ────────
function initRpCharts(prefix) {
  const P = prefix; // 'Flavia' | 'Luiz'
  renderRpDonut(`tbl${P}Classe`, `chart${P}Classe`, 0, 1);
  renderRpDesvioChart(`tbl${P}Ideal`, `chart${P}Ideal`);
  const pctSel = P === 'Flavia' ? '.cw-pct-cart' : 'td:nth-child(2)';
  renderRpPosicaoBar(`${prefix.toLowerCase()}PosBody`, `chart${P}Pos`, pctSel);
  renderRpTableHBar(`tbl${P}Renda`, `chart${P}Renda`, 0, 4, v => 'R$ ' + Math.round(v).toLocaleString('pt-BR'));
  renderRpProgress(`tbl${P}Tempo`, `prog${P}Tempo`);
  if (P === 'Flavia') {
    renderRpSegmentoChart('flaviaPosBody', 'chartFlaviaSegmento', { pctSelector: '.cw-pct-cart', totalTableId: 'tblFlaviaClasse' });
  } else {
    renderRpSegmentoChart('luizPosBody', 'chartLuizSegmento', {
      pctSelector: 'td:nth-child(2)',
      classeTableId: 'tblLuizClasse',
      totalTableId: 'tblLuizClasse',
      skipLabels: ['Ações BR', 'Renda Fixa (LFTB11)']
    });
  }
}
