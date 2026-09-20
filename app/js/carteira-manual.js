// ── Atualização manual de cotação para as páginas "Carteira Luiz" / "Carteira Flavia" ──
// Tabelas estáticas (não fazem parte do motor do Radar) com Qtd/PM editáveis pelo usuário.
// O botão busca preço em tempo real (brapi.dev, reaproveita fetchCotacoesBatch de js/cotacoes.js)
// e recalcula Saldo/Result./subtotal/total a partir dos campos preenchidos.

function _cwParseNum(str) {
  if (str === null || str === undefined) return 0;
  const clean = String(str).trim().replace(/[^\d,.-]/g, '');
  if (!clean) return 0;
  // formato BR: milhar com ponto, decimal com vírgula
  const normalized = clean.includes(',') ? clean.replace(/\./g, '').replace(',', '.') : clean;
  const n = parseFloat(normalized);
  return isNaN(n) ? 0 : n;
}

function _cwFmtR(n) {
  return 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function _cwFmtResult(saldo, investido, cellEl, positiveColor, negativeColor) {
  if (!cellEl) return;
  const result = saldo - investido;
  const pct = investido > 0 ? (result / investido * 100) : null;
  // pt-BR usa vírgula decimal. Esta era a ÚNICA das cinco formatações de percentual do
  // arquivo sem o `.replace`, então a página mostrava "+9.23%" na coluna Result. e
  // "4,20%" na coluna ao lado — duas convenções na mesma linha da tabela.
  const pctTxt = pct !== null ? ` (${pct >= 0 ? '+' : ''}${pct.toFixed(2).replace('.', ',')}%)` : '';
  cellEl.textContent = (result >= 0 ? '+' : '') + result.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) + pctTxt;
  cellEl.style.color = result >= 0 ? (positiveColor || '#0a5c35') : (negativeColor || '#9c1c1c');
}

async function atualizarCotacaoCarteira(tbodyId, statusId, outrosFixos) {
  outrosFixos = outrosFixos || 0;
  const tbody = document.getElementById(tbodyId);
  const statusEl = statusId ? document.getElementById(statusId) : null;
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr[data-ticker]'));
  if (rows.length === 0) return;

  if (statusEl) statusEl.textContent = 'Buscando cotações...';

  // 17/09/2026 — mesma correção de js/cotacoes.js: Yahoo primeiro (sem teto mensal de
  // requisições), brapi.dev só como fallback do que faltar (o free dela tem limite de
  // 15.000 req/mês e falhava em silêncio quando estourava).
  const tickers = rows.map(r => r.dataset.ticker);
  let map = {};
  try {
    map = await fetchCotacoesBatchYahoo(tickers);
    const faltando = tickers.filter(t => !map[t]);
    if (faltando.length) {
      const brapiMap = await fetchCotacoesBatch(faltando);
      map = { ...map, ...brapiMap };
    }
  } catch (e) { /* segue com map vazio, trata como erro por linha */ }

  _cwCalcular(tbodyId, outrosFixos, map, statusEl);
}

// Recalcula a carteira SEM buscar cotação — reaproveita o preço já exibido em cada linha.
// É isto que roda quando o usuário digita uma Qtd ou um PM: o número entra na conta na hora,
// sem depender de rede nem de clicar em "Atualizar Cotação".
function recalcularCarteiraManual(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  const outrosFixos = parseFloat(tbody.dataset.outrosFixos || '0') || 0;
  _cwCalcular(tbodyId, outrosFixos, null, null);
}

// map = null → usa o preço já na célula (modo recálculo). map = {ticker: preço} → modo cotação.
function _cwCalcular(tbodyId, outrosFixos, map, statusEl) {
  const semFetch = !map;
  map = map || {};
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  const rows = Array.from(tbody.querySelectorAll('tr[data-ticker]'));
  if (!rows.length) return;

  let ok = 0, err = 0;
  let subAcaoInvestido = 0, subAcaoSaldo = 0, temSubtotal = false;
  let totInvestido = 0, totSaldo = 0;
  const classeTotais = {}; // classe -> saldo somado (para % da Classe)
  const rowSaldos = []; // {row, saldo, classe} para segunda passada

  rows.forEach(row => {
    const ticker = row.dataset.ticker;
    const preco = map[ticker];
    const qtdInput = row.querySelector('.cw-qtd');
    const pmInput = row.querySelector('.cw-pm');
    const qtd = qtdInput ? _cwParseNum(qtdInput.value) : 0;
    const pm = pmInput ? _cwParseNum(pmInput.value) : 0;
    const precoCell = row.querySelector('.cw-preco');
    const investidoCell = row.querySelector('.cw-investido');
    const saldoCell = row.querySelector('.cw-saldo');
    const resultCell = row.querySelector('.cw-result');

    if (qtd <= 0) {
      // sem Qtd preenchida: linha ignorada no cálculo, mas ainda tenta mostrar preço se veio
      if (preco && precoCell) { precoCell.textContent = _cwFmtR(preco); ok++; }
      else if (precoCell) { precoCell.textContent = preco ? _cwFmtR(preco) : precoCell.textContent; }
      return;
    }

    const investido = qtd * pm;
    let saldo;
    if (preco) {
      ok++;
      if (precoCell) precoCell.textContent = _cwFmtR(preco);
      row.dataset.preco = String(preco); // valor exato, sem o arredondamento do texto exibido
      saldo = qtd * preco;
    } else {
      // sem cotação nova: mantém saldo baseado no último preço exibido, se numérico —
      // precisa ler o texto ANTES de sobrescrever, senão o parse sempre dá 0
      // (bug: sobrescrevia primeiro e tentava reler o próprio texto 'Erro' depois).
      const prevPreco = parseFloat(row.dataset.preco) > 0
        ? parseFloat(row.dataset.preco)
        : (precoCell ? _cwParseNum(precoCell.textContent) : 0);
      // No modo recálculo (semFetch) não houve tentativa de busca: não é erro, e a célula
      // de preço não deve ganhar o ⚠️ nem virar 'Erro'.
      if (!semFetch) {
        err++;
        if (precoCell) precoCell.textContent = prevPreco > 0 ? _cwFmtR(prevPreco) + ' ⚠️' : 'Erro';
      }
      saldo = qtd * prevPreco;
    }

    if (investidoCell) investidoCell.textContent = _cwFmtR(investido);
    if (saldoCell) saldoCell.textContent = _cwFmtR(saldo);
    if (resultCell) _cwFmtResult(saldo, investido, resultCell);

    totInvestido += investido;
    totSaldo += saldo;
    if (row.dataset.classe === 'acao') {
      subAcaoInvestido += investido;
      subAcaoSaldo += saldo;
      temSubtotal = true;
    }
    const classe = row.dataset.classe || '_';
    classeTotais[classe] = (classeTotais[classe] || 0) + saldo;
    rowSaldos.push({ row, saldo, classe });
  });

  const subRow = tbody.querySelector('tr[data-role="subtotal-acoes"]');
  if (subRow && temSubtotal) {
    const investCell = subRow.querySelector('.cw-sub-investido');
    const saldoCell = subRow.querySelector('.cw-sub-saldo');
    const resultCell = subRow.querySelector('.cw-sub-result');
    if (investCell) investCell.textContent = _cwFmtR(subAcaoInvestido);
    if (saldoCell) saldoCell.textContent = _cwFmtR(subAcaoSaldo);
    if (resultCell) _cwFmtResult(subAcaoSaldo, subAcaoInvestido, resultCell);
  }

  const totRow = document.querySelector(`[data-role="total-${tbodyId}"]`);
  if (totRow) {
    const investCell = totRow.querySelector('.cw-tot-investido');
    const saldoCell = totRow.querySelector('.cw-tot-saldo');
    const resultCell = totRow.querySelector('.cw-tot-result');
    if (investCell) investCell.textContent = _cwFmtR(totInvestido);
    if (saldoCell) saldoCell.textContent = totSaldo > 0 ? _cwFmtR(totSaldo) : '—';
    if (resultCell) _cwFmtResult(totSaldo, totInvestido, resultCell, '#4ecdc4', '#ff6b6b');
  }

  // % Cart. / % Classe — só recalcula se as colunas existirem na tabela (cw-pct-cart/.cw-pct-classe)
  const totGeral = totSaldo + outrosFixos;
  if (totGeral > 0) {
    rowSaldos.forEach(({ row, saldo, classe }) => {
      const pctCartCell = row.querySelector('.cw-pct-cart');
      const pctClasseCell = row.querySelector('.cw-pct-classe');
      if (pctCartCell) pctCartCell.textContent = (saldo / totGeral * 100).toFixed(2).replace('.', ',') + '%';
      if (pctClasseCell) {
        const classeTot = classeTotais[classe] || 0;
        pctClasseCell.textContent = classeTot > 0 ? (saldo / classeTot * 100).toFixed(2).replace('.', ',') + '%' : '—';
      }
    });
    if (subRow) {
      const pctCartCell = subRow.querySelector('.cw-pct-cart') || subRow.children[subRow.children.length - 2];
      if (pctCartCell) pctCartCell.textContent = (subAcaoSaldo / totGeral * 100).toFixed(2).replace('.', ',') + '%';
    }
    // linha fixa fora da tabela dinâmica (ex.: Academia) — atualiza seu % Cart. se outrosFixos > 0
    const fixedRow = tbody.querySelector('tr[data-classe="outros"]:not([data-ticker])');
    if (fixedRow && outrosFixos > 0) {
      const pctCartCell = fixedRow.querySelector('.cw-pct-cart');
      if (pctCartCell) pctCartCell.textContent = (outrosFixos / totGeral * 100).toFixed(2).replace('.', ',') + '%';
    }
  }

  // Só grava cotação quando ela veio de uma busca de verdade (não no modo recálculo).
  if (!semFetch) _cwGravarCotacoes(tbody);

  if (statusEl) {
    const agora = new Date().toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const msg = err === 0
      ? `${ok} cotações atualizadas às ${agora}`
      : `${ok} ok · ${err} erro(s) às ${agora}`;
    statusEl.textContent = msg;
  }

  _cwPropagar(tbodyId);
}

// ══════════════════════════════════════════════════════════════════════════════════════════
// GRAVAÇÃO DAS COTAÇÕES
// ══════════════════════════════════════════════════════════════════════════════════════════
// As cotações buscadas ficavam só na tela: ao recarregar o arquivo (ou ao receber uma versão
// nova), as células voltavam ao preço estático do HTML e o patrimônio "andava para trás".
// Agora o preço buscado é gravado no navegador por ticker e reaplicado na abertura, antes do
// primeiro cálculo — o patrimônio abre já no último valor conhecido, não no da data-base.
const CW_COT_KEY = 'carteira_cotacoes_v1';
const CW_COT_MAX_DIAS = 30; // acima disso o preço é velho demais para ser reaplicado

function _cwGravarCotacoes(tbody) {
  let store = {};
  try { store = JSON.parse(localStorage.getItem(CW_COT_KEY) || '{}') || {}; } catch { store = {}; }
  const data = store.data || {};
  let n = 0;
  tbody.querySelectorAll('tr[data-ticker]').forEach(row => {
    const preco = parseFloat(row.dataset.preco) || 0;
    // ⚠️ na célula = preço antigo reaproveitado após falha de busca: não regrava
    const falhou = (row.querySelector('.cw-preco')?.textContent || '').indexOf('⚠️') !== -1;
    if (preco > 0 && !falhou) { data[row.dataset.ticker] = preco; n++; }
  });
  if (!n) return;
  try { localStorage.setItem(CW_COT_KEY, JSON.stringify({ ts: Date.now(), data })); } catch { /* sem storage */ }
}

// Reaplica os preços gravados nas células. Devolve o timestamp usado (ou 0 se não havia nada).
function _cwAplicarCotacoesSalvas(tbody) {
  let store;
  try { store = JSON.parse(localStorage.getItem(CW_COT_KEY) || 'null'); } catch { return 0; }
  if (!store || !store.data || !store.ts) return 0;
  if (Date.now() - store.ts > CW_COT_MAX_DIAS * 86400000) return 0;
  let n = 0;
  tbody.querySelectorAll('tr[data-ticker]').forEach(row => {
    const p = store.data[row.dataset.ticker];
    const cell = row.querySelector('.cw-preco');
    if (p > 0 && cell) { cell.textContent = _cwFmtR(p); row.dataset.preco = String(p); n++; }
  });
  return n ? store.ts : 0;
}

// ── Propagação para o resto da página ────────────────────────────────────────────────────
// Um único ponto de entrada para tudo que depende do valor da carteira: gráfico de posição,
// Patrimônio (tabela/donut), Carteira Ideal, Segmento e os números do topo. Fica aqui — e não
// no wrapper de main.js — para que TODO caminho que altera saldo (cotação nova OU edição de
// Qtd/PM) atualize a página inteira, e não só a tabela.
function _cwPropagar(tbodyId) {
  const prefix = tbodyId === 'flaviaPosBody' ? 'Flavia' : (tbodyId === 'luizPosBody' ? 'Luiz' : null);
  if (!prefix) return;
  if (typeof renderRpPosicaoBar === 'function') {
    renderRpPosicaoBar(tbodyId, `chart${prefix}Pos`, prefix === 'Flavia' ? '.cw-pct-cart' : 'td:nth-child(2)');
  }
  if (typeof atualizarResumoPatrimonio === 'function') atualizarResumoPatrimonio(prefix);
}

// ══════════════════════════════════════════════════════════════════════════════════════════
// GRAVAÇÃO DAS POSIÇÕES (Qtd / PM)
// ══════════════════════════════════════════════════════════════════════════════════════════
// Os campos Qtd e PM são editáveis, mas o arquivo HTML é estático — não há servidor para
// gravar. A persistência é feita no localStorage do próprio navegador: o que o usuário digita
// fica salvo naquele navegador e volta sozinho ao reabrir o arquivo. Guardamos por
// carteira → ticker, e só o que o usuário de fato alterou; o resto continua vindo do HTML,
// então uma atualização futura do arquivo não fica presa a valores velhos.
const CW_POS_KEY = 'carteira_posicoes_v1';

function _cwLerStore() {
  try { return JSON.parse(localStorage.getItem(CW_POS_KEY) || '{}') || {}; }
  catch { return {}; }
}
function _cwGravarStore(store) {
  try { localStorage.setItem(CW_POS_KEY, JSON.stringify(store)); return true; }
  catch { return false; } // modo anônimo / storage cheio: segue funcionando, só não persiste
}

// Salva Qtd/PM de uma linha. Se o valor voltar a ser igual ao original do HTML, remove a
// entrada — assim o usuário "desfaz" simplesmente digitando o número de volta.
function _cwSalvarLinha(tbodyId, row) {
  const ticker = row.dataset.ticker;
  if (!ticker) return;
  const qtdInput = row.querySelector('.cw-qtd');
  const pmInput = row.querySelector('.cw-pm');
  const qtd = qtdInput ? qtdInput.value.trim() : '';
  const pm = pmInput ? pmInput.value.trim() : '';
  const origQtd = qtdInput ? (qtdInput.dataset.original || '') : '';
  const origPm = pmInput ? (pmInput.dataset.original || '') : '';

  const store = _cwLerStore();
  store[tbodyId] = store[tbodyId] || {};
  if (qtd === origQtd && pm === origPm) delete store[tbodyId][ticker];
  else store[tbodyId][ticker] = { qtd, pm };
  if (!Object.keys(store[tbodyId]).length) delete store[tbodyId];
  return _cwGravarStore(store);
}

function _cwStatusSalvo(tbodyId, txt, cor) {
  const el = document.getElementById(tbodyId === 'flaviaPosBody' ? 'flaviaSaveStatus' : 'luizSaveStatus');
  if (!el) return;
  el.textContent = txt;
  el.style.color = cor || '#0a5c35';
  clearTimeout(el._t);
  el._t = setTimeout(() => { el.textContent = ''; }, 4000);
}

// Guarda o valor original de cada campo (para o "restaurar") e aplica o que estiver salvo.
function restaurarPosicoesSalvas(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  const salvos = (_cwLerStore()[tbodyId]) || {};
  let n = 0;
  tbody.querySelectorAll('tr[data-ticker]').forEach(row => {
    const ticker = row.dataset.ticker;
    ['cw-qtd', 'cw-pm'].forEach(cls => {
      const inp = row.querySelector('.' + cls);
      if (!inp) return;
      if (inp.dataset.original === undefined) inp.dataset.original = inp.value;
    });
    const s = salvos[ticker];
    if (!s) return;
    const q = row.querySelector('.cw-qtd'), p = row.querySelector('.cw-pm');
    if (q && s.qtd !== undefined) q.value = s.qtd;
    if (p && s.pm !== undefined) p.value = s.pm;
    n++;
  });
  return n;
}

// Volta Qtd/PM para os valores que vieram no arquivo e limpa o que estava gravado.
function restaurarPosicoesOriginais(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody) return;
  tbody.querySelectorAll('tr[data-ticker]').forEach(row => {
    ['cw-qtd', 'cw-pm'].forEach(cls => {
      const inp = row.querySelector('.' + cls);
      if (inp && inp.dataset.original !== undefined) inp.value = inp.dataset.original;
    });
  });
  const store = _cwLerStore();
  delete store[tbodyId];
  _cwGravarStore(store);
  recalcularCarteiraManual(tbodyId);
  _cwStatusSalvo(tbodyId, '↩️ valores originais restaurados', '#7a5c00');
}

// Liga os campos: digitou → recalcula a página toda e grava. O debounce evita recalcular a
// cada tecla enquanto o número ainda está sendo digitado (ex.: "1", "15", "150").
function initCarteiraEditavel(tbodyId) {
  const tbody = document.getElementById(tbodyId);
  if (!tbody || tbody.dataset.editavelPronto) return;
  tbody.dataset.editavelPronto = '1';

  restaurarPosicoesSalvas(tbodyId);
  // Preço gravado ANTES do primeiro cálculo, senão a página abre com o preço da data-base
  // e o patrimônio aparece desatualizado até o usuário clicar em "Atualizar Cotação".
  const tsCot = _cwAplicarCotacoesSalvas(tbody);
  recalcularCarteiraManual(tbodyId);
  if (tsCot) {
    const st = document.getElementById(tbodyId === 'flaviaPosBody' ? 'flaviaUpdateStatus' : 'luizUpdateStatus');
    if (st) {
      const d = new Date(tsCot).toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' });
      st.textContent = `Cotações de ${d} (salvas) · clique para atualizar`;
    }
  }

  let t = null;
  tbody.addEventListener('input', e => {
    const inp = e.target;
    if (!inp.classList || (!inp.classList.contains('cw-qtd') && !inp.classList.contains('cw-pm'))) return;
    const row = inp.closest('tr[data-ticker]');
    if (!row) return;
    clearTimeout(t);
    t = setTimeout(() => {
      recalcularCarteiraManual(tbodyId);
      const ok = _cwSalvarLinha(tbodyId, row);
      _cwStatusSalvo(tbodyId,
        ok ? '✅ salvo neste navegador' : '⚠️ não foi possível salvar (navegação anônima?)',
        ok ? '#0a5c35' : '#9c1c1c');
    }, 400);
  });
}
