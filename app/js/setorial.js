// ══════════════════════════════════════════════════════════════════════════════════════════
// TABELA SETORIAL — bancos, seguradoras e resseguradora (aba Base de Dados)
// ══════════════════════════════════════════════════════════════════════════════════════════
// A tabela principal da Base de Dados tem 20 colunas desenhadas para empresa industrial:
// receita líquida, CPV, lucro bruto, EBITDA, margens. Uma holding de seguros que opera por
// equivalência patrimonial não tem NENHUMA dessas linhas — não por falta de dado, mas porque
// a DRE dela é outra. Este bloco existe para mostrar as linhas que essas empresas realmente
// têm, e que a grade industrial não comporta.
//
// Reaproveita fmtMoney() de js/fundamentos.js e as classes .fund-* já existentes.

// Uma coluna só é desenhada se ALGUM ticker tiver valor nela em ALGUM ano — evita coluna
// inteira de "—" quando o campo não existe para nenhuma das empresas listadas.
function _setColunasUteis() {
  return Object.keys(SETORIAL_LABELS).filter(k =>
    Object.values(SETORIAL_SEED).some(anos =>
      Object.values(anos).some(d => d[k] !== null && d[k] !== undefined)
    )
  );
}

function _setUltimoAno(t) {
  const anos = Object.keys(SETORIAL_SEED[t] || {}).map(Number).filter(n => !isNaN(n));
  return anos.length ? String(Math.max(...anos)) : null;
}

function _setCel(campo, v) {
  if (v === null || v === undefined || isNaN(v)) return '<span class="fund-val gray">—</span>';
  if (campo === 'aliquota') return `<span class="fund-val">${v.toFixed(1).replace('.', ',')}%</span>`;
  // Core EBIT negativo é a informação, não um erro: destaca em vermelho para não passar batido.
  const cor = (campo === 'coreEbit' || v < 0) && v < 0 ? ' style="color:#9c1c1c;"' : '';
  return fmtMoney(v).replace('<span class="fund-val"', `<span class="fund-val"${cor}`);
}

function buildSetorialTable() {
  const wrap = document.getElementById('setorialWrap');
  if (!wrap || typeof SETORIAL_SEED === 'undefined') return;

  const cols = _setColunasUteis();
  const th = cols.map(c => {
    const [rot, tip] = SETORIAL_LABELS[c];
    return `<th style="min-width:110px;">${rot}<span class="col-tip" data-tip="${tip.replace(/"/g, '&quot;')}">ⓘ</span></th>`;
  }).join('');

  const linhas = Object.keys(SETORIAL_SEED).map(t => {
    const ultimo = _setUltimoAno(t);
    if (!ultimo) return '';
    const d = SETORIAL_SEED[t][ultimo];
    const tds = cols.map(c => `<td>${_setCel(c, d[c])}</td>`).join('');
    const nota = SETORIAL_NOTES[t] || '';
    // Histórico por ticker, no mesmo padrão de expandir da tabela principal
    const anos = Object.keys(SETORIAL_SEED[t]).sort().reverse();
    const hist = anos.map(y => {
      const h = SETORIAL_SEED[t][y];
      return `<tr class="set-hist set-hist-${t}" style="display:none;background:#fafafa;">
        <td class="left" style="padding-left:34px;color:#888;">${y}</td>
        ${cols.map(c => `<td>${_setCel(c, h[c])}</td>`).join('')}
      </tr>`;
    }).join('') + `<tr class="set-hist set-hist-${t}" style="display:none;background:#fafafa;">
        <td class="left" colspan="${cols.length + 1}" style="padding-left:34px;font-size:11px;color:#777;line-height:1.6;">${nota}</td>
      </tr>`;

    return `<tr data-set-ticker="${t}">
      <td class="left"><div style="display:flex;align-items:center;gap:6px;">
        <button class="expand-btn" onclick="toggleSetorial('${t}')" title="Ver histórico e nota">▶</button>
        <span class="ticker-badge">${t}</span>
      </div></td>
      ${tds}
    </tr>${hist}`;
  }).join('');

  wrap.innerHTML = `
    <div class="rp-table-wrap" style="overflow-x:auto;">
      <table class="fund-table">
        <thead><tr><th class="left" style="min-width:120px;">Ativo</th>${th}</tr></thead>
        <tbody>${linhas}</tbody>
      </table>
    </div>`;
}

function toggleSetorial(t) {
  const linhas = document.querySelectorAll('.set-hist-' + t);
  if (!linhas.length) return;
  const abrindo = linhas[0].style.display === 'none';
  linhas.forEach(l => { l.style.display = abrindo ? 'table-row' : 'none'; });
  const btn = document.querySelector(`tr[data-set-ticker="${t}"] .expand-btn`);
  if (btn) btn.textContent = abrindo ? '▼' : '▶';
}
