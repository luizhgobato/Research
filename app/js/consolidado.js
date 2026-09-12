// ══════════════════════════════════════════════════════════════════════════════════════════
// CARTEIRA CONSOLIDADA — Luiz + Flavia (#page-familia)
// ══════════════════════════════════════════════════════════════════════════════════════════
// As duas carteiras existem e continuam existindo, cada uma com sua página. Esta é a visão
// do CASAL: o patrimônio somado, e — mais importante — os riscos que só aparecem quando se
// soma. BBSE3 pesa 16,9% na carteira do Luiz e 5,7% na da Flavia; nenhuma das duas páginas
// consegue dizer quanto o casal tem em BBSE3. Esta diz.
//
// PRINCÍPIO: zero número hardcodado. Tudo é lido das tabelas de posição já renderizadas
// (flaviaPosBody / luizPosBody), mesma filosofia de js/graficos-resumo.js. Consequência
// prática: editar uma Qtd na página do Luiz muda esta página sozinho, e uma atualização de
// cotação reflete aqui na hora. Duplicar os números aqui seria criar uma terceira fonte de
// verdade para dessincronizar — foi exatamente esse erro que gerou os bugs do Radar.

const CONS_CARTEIRAS = [
  { nome: 'Luiz',   prefix: 'Luiz',   bodyId: 'luizPosBody',   classeTableId: 'tblLuizClasse',   cor: '#2a78d6' },
  { nome: 'Flavia', prefix: 'Flavia', bodyId: 'flaviaPosBody', classeTableId: 'tblFlaviaClasse', cor: '#eb6834' },
];

// Alvo de alocação do casal. Os dois planos individuais usam 65/20/15 — como são iguais, a
// meta consolidada é a mesma, sem precisar de média ponderada. Se um dia divergirem, é AQUI
// que a ponderação por patrimônio precisa entrar (e o comentário deixa de valer).
const CONS_ALVO = { dividendos: 65, crescimento: 20, rf: 15 };

// Marco de patrimônio e meta de renda: são do CASAL, não por pessoa — o objetivo escrito nas
// duas páginas é o mesmo ("viver de dividendos, renda mínima R$20.000/mês"). Premissa
// explícita, não dado: se a intenção for R$20k por pessoa, é este número que muda.
const CONS_MARCO = 2000000;
const CONS_META_RENDA = 20000;

// Parser de número em formato BR. O ponto é ambíguo: "R$ 3.186" são três mil e cento e
// oitenta e seis, mas "1.05" seria um decimal. A regra abaixo resolve pelo FORMATO — ponto
// seguido de exatamente 3 dígitos, em grupos, é separador de milhar.
// (Sem isso a renda estimada "R$ 3.186/mês" virava R$ 3,186 e o card mostrava "R$ 4/mês".)
function _consNum(s) {
  if (s === null || s === undefined) return 0;
  const c = String(s).replace(/−/g, '-').replace(/[^\d,.-]/g, '');
  if (!c) return 0;
  let t;
  if (c.includes(',')) t = c.replace(/\./g, '').replace(',', '.');       // 1.234,56
  else if (/^-?\d{1,3}(\.\d{3})+$/.test(c)) t = c.replace(/\./g, '');    // 3.186 → milhar
  else t = c;                                                            // 26.02 → decimal
  const n = parseFloat(t);
  return isNaN(n) ? 0 : n;
}
function _consR(v) { return 'R$ ' + v.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }); }
function _consR0(v) { return 'R$ ' + Math.round(v).toLocaleString('pt-BR'); }
function _consPct(v) { return v.toFixed(2).replace('.', ',') + '%'; }

// ── COLETA ────────────────────────────────────────────────────────────────────────────────
// Devolve a fotografia consolidada. Tudo o que as seções desenham sai daqui — uma leitura só,
// para que nenhuma seção possa discordar de outra sobre quanto o casal tem.
function coletarConsolidado() {
  const porTitular = {}, porTicker = {}, porSegmento = {}, porClasse = {}, porGrupo = {};
  let totalGeral = 0;

  CONS_CARTEIRAS.forEach(c => {
    const tbody = document.getElementById(c.bodyId);
    if (!tbody) return;
    let subtotal = 0;

    tbody.querySelectorAll('tr[data-ticker]').forEach(tr => {
      const saldo = _consNum(tr.querySelector('.cw-saldo')?.textContent);
      if (!(saldo > 0)) return;
      const ticker = (tr.dataset.ticker || '').replace(/\.SA$/i, '');
      const qtd = _consNum(tr.querySelector('.cw-qtd')?.value);
      const preco = parseFloat(tr.dataset.preco) || _consNum(tr.querySelector('.cw-preco')?.textContent);
      const investido = qtd * _consNum(tr.querySelector('.cw-pm')?.value);
      const classe = tr.dataset.classe === 'rf' ? 'Renda Fixa' : 'Ações BR';
      const seg = tr.dataset.segmento || 'Sem segmento';
      const grupo = tr.dataset.classe === 'rf' ? 'rf' : (tr.dataset.grupo || 'sem-grupo');

      subtotal += saldo;
      porTicker[ticker] = porTicker[ticker] || { ticker, saldo: 0, investido: 0, preco, seg, grupo, classe, donos: {} };
      const t = porTicker[ticker];
      t.saldo += saldo; t.investido += investido; t.donos[c.nome] = (t.donos[c.nome] || 0) + saldo;
      if (preco > 0) t.preco = preco;
      porSegmento[seg] = (porSegmento[seg] || 0) + saldo;
      porClasse[classe] = (porClasse[classe] || 0) + saldo;
      porGrupo[grupo] = (porGrupo[grupo] || 0) + saldo;
    });

    // Classes que NÃO existem como linha de posição (Previdência, ETFs do Luiz): vêm da
    // configuração de patrimônio já usada pelas páginas individuais, para não recadastrar
    // esses valores num terceiro lugar.
    const fixos = (typeof RP_PATRIMONIO_CFG !== 'undefined' && RP_PATRIMONIO_CFG[c.prefix])
      ? RP_PATRIMONIO_CFG[c.prefix].fixos : [];
    fixos.forEach(f => {
      subtotal += f.valor;
      porClasse[f.label] = (porClasse[f.label] || 0) + f.valor;
      porSegmento[f.label] = (porSegmento[f.label] || 0) + f.valor;
      porGrupo['fora'] = (porGrupo['fora'] || 0) + f.valor;
    });

    porTitular[c.nome] = subtotal;
    totalGeral += subtotal;
  });

  // Renda mensal estimada: lida do card já calculado em cada página individual, para não
  // criar uma segunda projeção de dividendos que possa divergir da de lá.
  let rendaMes = 0;
  CONS_CARTEIRAS.forEach(c => {
    const cfg = (typeof RP_PATRIMONIO_CFG !== 'undefined') ? RP_PATRIMONIO_CFG[c.prefix] : null;
    if (!cfg) return;
    document.querySelectorAll(`#${cfg.pageId} .rp-exec-item`).forEach(item => {
      const lbl = (item.querySelector('.rp-exec-label')?.textContent || '').trim();
      if (lbl.indexOf('Renda ações') === 0) rendaMes += _consNum(item.querySelector('.rp-exec-value')?.textContent);
    });
  });

  const ativos = Object.values(porTicker).sort((a, b) => b.saldo - a.saldo);
  return { porTitular, porSegmento, porClasse, porGrupo, ativos, totalGeral, rendaMes };
}

// ── RENDER ────────────────────────────────────────────────────────────────────────────────
function _consDonut(containerId, mapa, total) {
  const el = document.getElementById(containerId);
  if (!el) return;
  const rows = Object.entries(mapa).map(([label, value]) => ({ label, value }))
    .filter(r => r.value > 0).sort((a, b) => b.value - a.value);
  if (!rows.length || typeof makeSVGDonut !== 'function') { if (el) el.innerHTML = ''; return; }
  const vals = rows.map(r => r.value);
  makeSVGDonut(el, rows.map(r => r.label), vals, RP_COLORS, { amounts: vals });
}

function renderConsolidado() {
  const d = coletarConsolidado();
  if (!(d.totalGeral > 0)) return;

  // ── Cards do topo ──
  const exec = document.getElementById('consExec');
  if (exec) {
    const luiz = d.porTitular['Luiz'] || 0, flavia = d.porTitular['Flavia'] || 0;
    // Maior AÇÃO, não maior ativo: o LFTB11 seria sempre o topo e o card viraria "reserva de
    // liquidez é grande" — verdade, mas não é o risco que o card precisa vigiar.
    const maior = d.ativos.find(a => a.classe === 'Ações BR');
    exec.innerHTML = `
      <div class="rp-exec-item"><div class="rp-exec-label">Patrimônio do casal</div><div class="rp-exec-value">${_consR(d.totalGeral)}</div></div>
      <div class="rp-exec-item"><div class="rp-exec-label">Luiz / Flavia</div><div class="rp-exec-value">${_consPct(luiz / d.totalGeral * 100)} / ${_consPct(flavia / d.totalGeral * 100)}</div></div>
      <div class="rp-exec-item"><div class="rp-exec-label">Progresso vs. marco R$ 2MM</div><div class="rp-exec-value yellow">${(d.totalGeral / CONS_MARCO * 100).toFixed(1).replace('.', ',')}%</div></div>
      <div class="rp-exec-item"><div class="rp-exec-label">Renda ações 2026 (est.)</div><div class="rp-exec-value">${_consR0(d.rendaMes)}/mês</div></div>
      <div class="rp-exec-item"><div class="rp-exec-label">Maior ação única</div><div class="rp-exec-value ${maior && maior.saldo / d.totalGeral > 0.15 ? 'red' : ''}">${maior ? maior.ticker + ' ' + _consPct(maior.saldo / d.totalGeral * 100) : '—'}</div></div>`;
  }

  // ── Donuts ──
  _consDonut('chartConsTitular', d.porTitular, d.totalGeral);
  _consDonut('chartConsClasse', d.porClasse, d.totalGeral);
  _consDonut('chartConsSegmento', d.porSegmento, d.totalGeral);

  // ── Barras por ativo ──
  const barEl = document.getElementById('chartConsAtivo');
  if (barEl && typeof renderRpHBarFmt === 'function') {
    renderRpHBarFmt(
      barEl,
      d.ativos.map(a => ({ label: a.ticker, value: a.saldo / d.totalGeral * 100, amount: a.saldo })),
      v => v.toFixed(2).replace('.', ',') + '%'
    );
  }

  // ── Tabela por ativo, com quem detém o quê ──
  const tb = document.querySelector('#tblConsAtivos tbody');
  if (tb) {
    tb.innerHTML = d.ativos.map(a => {
      const donos = Object.entries(a.donos).sort((x, y) => y[1] - x[1]);
      const ambos = donos.length > 1;
      const res = a.investido > 0 ? (a.saldo - a.investido) / a.investido * 100 : null;
      return `<tr>
        <td class="rp-bold">${a.ticker}</td>
        <td>${a.seg}</td>
        <td>${donos.map(([n, v]) => `<span style="display:inline-block;background:${ambos ? '#eef3fb' : '#fff'};border:1px solid #e0e0e0;border-radius:6px;padding:2px 7px;margin:0 4px 3px 0;font-size:11px;white-space:nowrap;"><b>${n}</b> ${_consR0(v)}</span>`).join('')}${ambos ? '<span class="rp-tag rp-tag-yellow" style="font-size:10px;">nos dois</span>' : ''}</td>
        <td>${_consR(a.saldo)}</td>
        <td>${_consPct(a.saldo / d.totalGeral * 100)}</td>
        <td style="color:${res === null ? '#888' : (res >= 0 ? '#0a5c35' : '#9c1c1c')};">${res === null ? '—' : (res >= 0 ? '+' : '') + res.toFixed(2).replace('.', ',') + '%'}</td>
      </tr>`;
    }).join('') + `<tr style="background:#1e1a2e;color:#fff;font-weight:700;">
        <td>Total</td><td></td><td></td><td>${_consR(d.totalGeral)}</td><td>100%</td><td></td></tr>`;
  }

  // ── Carteira Ideal do casal ──
  // Mesma régua 65/20/15 das páginas individuais, aplicada sobre o patrimônio somado. Os
  // grupos vêm de data-grupo em cada linha — reclassificar um ativo lá reflete aqui sozinho.
  const ti = document.querySelector('#tblConsIdeal tbody');
  if (ti) {
    const linhas = [
      { label: 'Ações — Dividendos', valor: d.porGrupo['dividendos'] || 0, alvo: CONS_ALVO.dividendos },
      { label: 'Ações — Crescimento', valor: d.porGrupo['crescimento'] || 0, alvo: CONS_ALVO.crescimento },
      { label: 'Renda Fixa / Reserva Estratégica', valor: d.porGrupo['rf'] || 0, alvo: CONS_ALVO.rf },
      { label: 'Fora da régua — Previdência/ETFs', valor: d.porGrupo['fora'] || 0, alvo: null },
    ];
    ti.innerHTML = linhas.map(l => {
      const pct = l.valor / d.totalGeral * 100;
      if (l.alvo === null) {
        return `<tr><td class="rp-bold">${l.label}</td><td>—</td><td>—</td><td>${_consR(l.valor)}</td><td>${_consPct(pct)}</td><td>—</td></tr>`;
      }
      const desvio = pct - l.alvo;
      const cls = desvio < 0 ? 'rp-tag-red' : 'rp-tag-yellow';
      return `<tr><td class="rp-bold">${l.label}</td><td>${l.alvo}%</td><td>${_consR(l.alvo / 100 * d.totalGeral)}</td><td>${_consR(l.valor)}</td><td>${_consPct(pct)}</td>
        <td><span class="rp-tag ${cls}">${desvio >= 0 ? '+' : '−'}${Math.abs(desvio).toFixed(2).replace('.', ',')}pp</span></td></tr>`;
    }).join('') + `<tr style="background:#f7f7f5;font-weight:700;"><td>Total</td><td>100%</td><td>${_consR(d.totalGeral)}</td><td>${_consR(d.totalGeral)}</td><td>100%</td><td></td></tr>`;
    if (typeof renderRpDesvioChart === 'function') renderRpDesvioChart('tblConsIdeal', 'chartConsIdeal');
  }

  // ── Riscos que só aparecem somando ──
  renderConsRiscos(d);

  // ── Rodapé de sincronia ──
  const st = document.getElementById('consStatus');
  if (st) st.textContent = `Somando ${d.ativos.length} ativos das duas carteiras · atualizado às ${new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
}

// A seção que justifica a página existir: concentração e sobreposição são invisíveis nas
// páginas individuais por construção — cada uma só enxerga a própria metade.
function renderConsRiscos(d) {
  const el = document.getElementById('consRiscos');
  if (!el) return;
  const itens = [];

  // 1 · Ativos presentes nas DUAS carteiras
  const dobrados = d.ativos.filter(a => Object.keys(a.donos).length > 1).sort((a, b) => b.saldo - a.saldo);
  if (dobrados.length) {
    itens.push(`<b>${dobrados.length} ativos aparecem nas duas carteiras</b>, somando ${_consR0(dobrados.reduce((s, a) => s + a.saldo, 0))} (${_consPct(dobrados.reduce((s, a) => s + a.saldo, 0) / d.totalGeral * 100)} do patrimônio do casal): ${dobrados.map(a => `<b>${a.ticker}</b> ${_consPct(a.saldo / d.totalGeral * 100)}`).join(' · ')}. Separadas, cada posição parece pequena; somadas, não.`);
  }

  // 2 · Concentração por ativo — limite prático de 15% por posição única
  // Só AÇÕES entram no teste: o LFTB11 concentra 38% e isso é reserva de liquidez, não risco
  // de tese. Contá-lo aqui dispararia um alerta vermelho permanente sobre a parte mais
  // conservadora da carteira — alarme que ninguém lê depois da terceira vez.
  const grandes = d.ativos.filter(a => a.classe === 'Ações BR' && a.saldo / d.totalGeral > 0.15);
  if (grandes.length) {
    itens.push(`<b style="color:#9c1c1c;">Concentração acima de 15% em uma única ação:</b> ${grandes.map(a => `${a.ticker} ${_consPct(a.saldo / d.totalGeral * 100)}`).join(' · ')}. Um erro de tese aqui move o patrimônio do casal inteiro.`);
  }
  // Peso da renda fixa: informação, não alerta vermelho.
  const rf = d.porGrupo['rf'] || 0;
  if (rf / d.totalGeral > CONS_ALVO.rf / 100) {
    itens.push(`Renda fixa em <b>${_consPct(rf / d.totalGeral * 100)}</b> contra alvo de ${CONS_ALVO.rf}% — ${_consR0(rf - CONS_ALVO.rf / 100 * d.totalGeral)} acima da régua. Não é risco de perda; é <b>custo de oportunidade</b>: esse dinheiro rende Selic enquanto o plano pede que ele esteja comprando renda futura.`);
  }

  // 3 · Concentração setorial — financeiro/seguros é a exposição estrutural das duas carteiras
  const finSegs = ['Bancos', 'Bancos digitais', 'Seguros', 'Resseguros'];
  const fin = finSegs.reduce((s, k) => s + (d.porSegmento[k] || 0), 0);
  if (fin > 0) {
    const pct = fin / d.totalGeral * 100;
    itens.push(`<b${pct > 40 ? ' style="color:#9c1c1c;"' : ''}>Financeiro/seguros: ${_consPct(pct)}</b> do patrimônio do casal (${_consR0(fin)}). Bancos e seguradoras reagem ao mesmo ciclo de juro e crédito — não são quatro apostas independentes.`);
  }

  // 4 · Renda vs. meta
  if (d.rendaMes > 0) {
    itens.push(`Renda estimada de <b>${_consR0(d.rendaMes)}/mês</b> contra a meta de <b>${_consR0(CONS_META_RENDA)}/mês</b> — <b>${(d.rendaMes / CONS_META_RENDA * 100).toFixed(1).replace('.', ',')}%</b> do objetivo. A meta é tratada aqui como sendo <b>do casal</b>, não por pessoa; se for por pessoa, o alvo dobra.`);
  }

  el.innerHTML = itens.map(t =>
    `<li style="margin-bottom:10px;font-size:12px;line-height:1.65;">${t}</li>`).join('');
}

// ── ATUALIZAR COTAÇÃO DAS DUAS DE UMA VEZ ────────────────────────────────────────────────
async function atualizarCotacaoFamilia() {
  const st = document.getElementById('consUpdateStatus');
  if (st) st.textContent = 'Buscando cotações das duas carteiras...';
  for (const c of CONS_CARTEIRAS) {
    const cfg = (typeof RP_PATRIMONIO_CFG !== 'undefined') ? RP_PATRIMONIO_CFG[c.prefix] : null;
    const outros = document.getElementById(c.bodyId)?.dataset.outrosFixos || 0;
    try { await atualizarCotacaoCarteira(c.bodyId, null, parseFloat(outros) || 0); } catch { /* segue para a outra */ }
    if (cfg && typeof atualizarResumoPatrimonio === 'function') atualizarResumoPatrimonio(c.prefix);
  }
  renderConsolidado();
  if (st) st.textContent = `Atualizado às ${new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })}`;
}

// ── INICIALIZAÇÃO ─────────────────────────────────────────────────────────────────────────
// Os gráficos são SVG dimensionados por offsetWidth: desenhar com a aba ainda oculta produz
// um SVG de largura zero. Por isso o primeiro render acontece na primeira abertura da aba —
// mesmo motivo já documentado em js/main.js para as páginas individuais.
let _consIniciado = false;
(function patchShowPageFamilia() {
  const orig = window.showPage;
  if (typeof orig !== 'function') return;
  window.showPage = function (id) {
    orig(id);
    if (id !== 'familia') return;
    // As duas tabelas precisam estar calculadas antes de somar. initCarteiraEditavel é
    // idempotente e faz o pacote completo (Qtd/PM salvos + cotações salvas + recálculo),
    // então a consolidada abre correta mesmo que o usuário nunca tenha aberto as outras abas.
    CONS_CARTEIRAS.forEach(c => {
      if (typeof initCarteiraEditavel === 'function') initCarteiraEditavel(c.bodyId);
      else if (typeof recalcularCarteiraManual === 'function') recalcularCarteiraManual(c.bodyId);
    });
    _consIniciado = true;
    renderConsolidado();
  };
})();

// Qualquer alteração nas carteiras individuais (cotação nova OU edição de Qtd/PM) passa por
// _cwPropagar. Enganchar aqui garante que a consolidada nunca fique exibindo um total velho.
(function patchPropagarFamilia() {
  const orig = window._cwPropagar;
  if (typeof orig !== 'function') return;
  window._cwPropagar = function (tbodyId) {
    orig(tbodyId);
    if (_consIniciado) renderConsolidado();
  };
})();
