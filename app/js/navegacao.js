// ── REPORTS DATA ──
let REPORTS = {};
try {
  const raw = document.getElementById('reportsData').textContent;
  REPORTS = JSON.parse(raw);
} catch(e) {
  console.warn('[Reports] Erro ao parsear JSON:', e);
}

// ── NAVEGAÇÃO SPA ──
let _paginaAnterior = 'radar';
function showPage(id){
  document.querySelectorAll('.page, .page-report').forEach(p=>p.classList.remove('active'));
  document.querySelectorAll('.nav-tab').forEach(t=>t.classList.remove('active'));
  const pg = document.getElementById('page-'+id);
  if(pg) pg.classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(t=>{
    const txt = t.textContent.toLowerCase();
    if(id==='carteira'&&txt.includes('minha carteira')) t.classList.add('active');
    if(id==='radar'&&txt.includes('radar')) t.classList.add('active');
    if(id==='dados'&&txt.includes('base de dados')) t.classList.add('active');
    if(id==='flavia'&&txt.includes('carteira da flavia')) t.classList.add('active');
    if(id==='resumoluiz'&&txt.includes('carteira luiz')) t.classList.add('active');
  });
  _paginaAnterior = id;
  window.scrollTo(0,0);
  if(id==='carteira') setTimeout(tryBuildCharts, 100);
}

function abrirReport(ticker, nome, data, veredicto) {
  // Esconde todas as páginas
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  // Mostra a página de report
  document.getElementById('page-report').classList.add('active');
  // Atualiza topbar
  document.getElementById('reportTicker').textContent = ticker;
  document.getElementById('reportNome').textContent = nome;
  document.getElementById('reportData').textContent = data ? `Atualizado em ${data}` : '';
  const vEl = document.getElementById('reportVerd');
  if(veredicto==='compra'){vEl.textContent='🟢 Compra';vEl.style.cssText='background:#f0fdf4;color:#16a34a;border:1px solid #bbf7d0;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;';}
  else if(veredicto==='aguardar'){vEl.textContent='🟡 Aguardar';vEl.style.cssText='background:#fffbeb;color:#d97706;border:1px solid #fde68a;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;';}
  else if(veredicto==='acima'){vEl.textContent='🔴 Acima do teto';vEl.style.cssText='background:#fef2f2;color:#dc2626;border:1px solid #fecaca;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;';}
  else if(veredicto==='saida'){vEl.textContent='⚫ Saída';vEl.style.cssText='background:#f3f4f6;color:#111827;border:1px solid #d1d5db;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;';}
  else{vEl.textContent='⚪ Pendente';vEl.style.cssText='background:#f9fafb;color:#9ca3af;border:1px solid #e5e7eb;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;';}
  // Render conteúdo
  const body = document.getElementById('reportBody');
  const data_report = REPORTS[ticker];
  if(!data_report){ renderReportVazio(body, ticker); return; }
  renderReportCompleto(body, data_report);
  window.scrollTo(0,0);
}

function fecharReport(){
  document.getElementById('page-report').classList.remove('active');
  document.getElementById('page-'+_paginaAnterior).classList.add('active');
  document.querySelectorAll('.nav-tab').forEach(t=>{
    if(t.textContent.toLowerCase().includes(_paginaAnterior==='carteira'?'carteira':_paginaAnterior==='dados'?'base de dados':'radar'))t.classList.add('active');
  });
  window.scrollTo(0,0);
}

function renderReportVazio(body, ticker){
  body.innerHTML=`<div class="rp-empty">
    <div class="rp-empty-icon">📋</div>
    <div class="rp-empty-title">Research de ${ticker} em produção</div>
    <div class="rp-empty-sub">Este relatório ainda não foi gerado. Solicite no chat do Claude para priorizar a análise.</div>
    <button class="rp-empty-btn" onclick="solicitarRelatorio('${ticker}')">✦ Solicitar Research</button>
  </div>`;
}

function copiarBloco(btnEl, raw){
  navigator.clipboard.writeText(raw).then(()=>{
    showToast('✓ Bloco de veredito copiado');
  }).catch(()=>{});
}

// ══════════════════════════════════════════════════════
// RENDER DO REPORT — ordem pensada pra ler o essencial primeiro:
// 1 Veredicto · 2 Pontos a favor/Riscos · 3 Encaixe na carteira ·
// 4 Classificação setorial · 5 Contexto de preço · 6 Descobertas ·
// 7 Projeção de lucro · 8 Valuation · 9 Quanto posso ganhar (retorno
// total simplificado, com detalhamento técnico dentro de um <details>) ·
// 10 Projeção de dividendos (5 anos) · 11 Composição da receita ·
// 12 Teste do payout · 13 Dados coletados · 14 Bloco copiável
// ══════════════════════════════════════════════════════
function renderReportCompleto(body, r){
  // ⚠️ GATE DO MODELO NOVO (14/09/2026). Só quem tem `valuation.serieMultiplo` — hoje apenas
  // a ALOS3, porque o gerador roda com argumento — entra no layout novo. Os outros 13
  // continuam exatamente como estavam, para dar para comparar os dois lado a lado antes de
  // replicar. Ver o cabeçalho de renderReportV2.
  if (r && r.valuation && r.valuation.serieMultiplo) return renderReportV2(body, r);
  body.innerHTML = `
    ${secHeader(r)}
    ${secVeredicto(r)}
    ${secTeseRiscos(r)}
    ${secLeituraDados(r)}
    ${secEncaixeCarteira(r)}
    ${secClassificacao(r)}
    ${secContextoPreco(r)}
    ${secDescobertas(r)}
    ${secProjecaoLucro(r)}
    ${secValuation(r)}
    ${secRegraMultiplo(r)}
    ${secRetornoTotal(r)}
    ${secDividendos(r)}
    ${secReceita(r)}
    ${secTestePayout(r)}
    ${secDadosColetados(r)}
    ${secBlocoCopiavel(r)}
    <p style="font-size:10px;color:#aaa;text-align:center;padding:0.5rem 0 1rem;">Research para uso pessoal · Não constitui recomendação de investimento</p>
  `;
}

function esc(s){ return (s==null?'':String(s)); }

// ══════════════════════════════════════════════════════════════════════════════════════════
// MODELO NOVO DE RELATÓRIO — 14/09/2026
//
// Pedido do usuário, ponto a ponto, e onde cada um foi atendido:
//
//   "temos muitos blocos no relatório, precisamos organizar melhor" / "tem itens que são
//   parecidos e podem ser melhor organizados: projeção de lucro, valuation, a regra, quanto
//   posso ganhar"  →  de 15 blocos para 7. Os quatro que ele citou eram QUATRO CAIXAS
//   contando a MESMA história em pedaços — viraram duas: "O múltiplo" e "Do lucro ao preço".
//
//   "o racional do múltiplo está pequeno como uma observação, mas é uma informação
//   extremamente relevante"  →  ganhou SEÇÃO PRÓPRIA, a primeira depois da tese, com caixa
//   de destaque e corpo de texto de leitura em vez de nota de rodapé.
//
//   "quero acrescentar o ROE e P/L histórico que está sendo utilizado, quebrado por ano"
//   →  tabela ano a ano dentro da seção do múltiplo, com a mediana conferível na tela.
//
//   "os cenários estão muito próximos... dois centavos de diferença não faz diferença"
//   →  os cenários passaram a mover o múltiplo TAMBÉM (ver faixa_do_multiplo no gerador).
//   Na ALOS3 a amplitude foi de 12% para 71%.
//
//   "sinto falta de uma análise qualitativa, já havia pedido, e também comparação com os
//   concorrentes"  →  seção 1 (qualitativa, escrita) e seção 2 (tabela de pares, derivada).
//
//   "as letras estão pequenas, quase não dá para enxergar"  →  css/styles.css, bloco
//   #page-report.
//
// ⚠️ SÓ A ALOS3 ENTRA AQUI, e é de propósito: "faça essas alterações somente na Allos,
// depois replicaremos". O gate é `valuation.serieMultiplo`, que só o gerador rodado com
// argumento produz. Os outros 13 relatórios caem em renderReportCompleto, intactos, para dar
// para comparar os dois modelos lado a lado.
// ══════════════════════════════════════════════════════════════════════════════════════════

// Renumera o título de uma seção REAPROVEITADA do modelo antigo. Elas trazem a numeração
// de lá (9, 10, 14) e são compartilhadas com os 13 relatórios que ainda usam o layout
// original — mexer no título na origem quebraria aqueles. A troca é feita aqui, na montagem.
function _v2num(html, de, para){ return html ? html.replace(de, para) : ''; }

function renderReportV2(body, r){
  body.innerHTML = `
    ${secHeader(r)}
    ${secVeredicto(r)}
    ${v2Tese(r)}
    ${v2Pares(r)}
    ${v2Multiplo(r)}
    ${v2LucroPreco(r)}
    ${v2Cenarios(r)}
    ${_v2num(v2Retorno(r), '9 · Quanto posso ganhar', '7 · Quanto posso ganhar')}
    ${_v2num(v2Dividendos(r), '10 · 💰 Projeção de dividendos', '8 · 💰 Projeção de dividendos')}
    ${v2Testes(r)}
    ${_v2num(secBlocoCopiavel(r), '14 · Bloco de veredito copiável', '10 · Bloco de veredito copiável')}
    <p style="font-size:11px;color:#999;text-align:center;padding:0.5rem 0 1rem;">Research para uso pessoal · Não constitui recomendação de investimento</p>
  `;
}

// ── 1 · A TESE ────────────────────────────────────────────────────────────────────────────
// Junta o que antes eram quatro caixas separadas (Pontos a favor/Riscos, Encaixe na carteira,
// Classificação setorial e a análise qualitativa nova). São todas resposta à mesma pergunta:
// que empresa é esta e por que ela estaria na carteira.
function v2Tese(r){
  const q = r.qualitativa;
  const tese = (r.tese||[]).map(x => `<li>${esc(x)}</li>`).join('');
  const riscos = (r.riscos||[]).map(x => `<li>${esc(x)}</li>`).join('');
  const cl = r.classificacao || {};
  const blocosQ = q ? (q.blocos||[]).map(b => `
      <div style="margin-bottom:1.1rem;">
        <div style="font-size:14px;font-weight:700;color:#1a1a2e;margin-bottom:5px;">${esc(b.titulo)}</div>
        <p style="margin:0;color:#3a3a4a;">${esc(b.texto)}</p>
      </div>`).join('') : '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">2 · A tese</div>
      ${q ? `<p style="font-size:16px;line-height:1.65;color:#1a1a2e;font-weight:600;margin:0 0 1.2rem;">${esc(q.resumo)}</p>` : ''}
      ${blocosQ}
      <div class="rp-bull-bear">
        <div class="rp-bull"><div class="rp-bb-title">A favor</div><ul>${tese}</ul></div>
        <div class="rp-bear"><div class="rp-bb-title">Riscos</div><ul>${riscos}</ul></div>
      </div>
      ${r.encaixeCarteira ? `<p class="rp-note"><strong>Encaixe na carteira:</strong> ${esc(r.encaixeCarteira)}</p>` : ''}
      ${cl.setor ? `<p class="rp-note"><strong>Classificação:</strong> ${esc(cl.setor)}${cl.perfil ? ' · ' + esc(cl.perfil) : ''}${cl.racional ? ' — ' + esc(cl.racional) : ''}</p>` : ''}
    </div>`;
}

// ── 2 · COMO ELA SE COMPARA ───────────────────────────────────────────────────────────────
function v2Pares(r){
  const p = (r.valuation||{}).pares;
  if(!p || !(p.linhas||[]).length) return '';
  const linhas = p.linhas.map(l => `
      <tr${l.eu ? ' style="background:#f0fdf6;font-weight:700;"' : ''}>
        <td class="left">${esc(l.ativo)}${l.eu ? ' ←' : ''}</td>
        <td class="rp-mono">${esc(l.multiplo)}</td>
        <td class="left" style="font-size:12px;color:#666;">${esc(l.metodo)}</td>
        <td class="rp-mono">${esc(l.roe)}</td>
        <td class="rp-mono">${esc(l.roeMed)}</td>
        <td class="rp-mono">${esc(l.mgLiq)}</td>
        <td class="rp-mono">${esc(l.divEbitda)}</td>
        <td class="rp-mono">${esc(l.valorMercado)}</td>
      </tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">3 · Como ela se compara com os concorrentes</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Ativo</th><th>Múltiplo aplicado</th><th>Método</th>
          <th>${esc(p.metricaRoe)} hoje</th><th>mediano</th><th>Margem líq.</th>
          <th>Dív.Líq/EBITDA</th><th>Valor de mercado</th></tr></thead>
        <tbody>${linhas}</tbody>
      </table></div>
      <p class="rp-note">Todos do grupo <strong>${esc(p.grupo)}</strong> do motor, com a rentabilidade medida
        na <strong>mesma definição</strong> (em shopping o numerador é o FFO, não o lucro contábil — por isso
        a linha lê alto para os dois). Não há coluna de preço justo aqui de propósito: cada empresa tem o seu,
        calculado sobre um fundamento diferente, e comparar dois desses números não diz nada.</p>
    </div>`;
}

// ── 3 · O MÚLTIPLO ────────────────────────────────────────────────────────────────────────
// A seção que o usuário pediu para destacar. Era uma linha de observação dentro de "8b".
function v2Multiplo(r){
  const v = r.valuation || {};
  const s = v.serieMultiplo;
  if(!s) return '';
  const linhas = (s.linhas||[]).map(l => `
      <tr>
        <td class="left"><strong>${esc(l.ano)}</strong></td>
        <td class="rp-mono">${esc(l.preco)}</td>
        <td class="rp-mono">${esc(l.fundamento)}</td>
        <td class="rp-mono" style="font-weight:700;">${esc(l.multiplo)}</td>
        <td class="rp-mono">${esc(l.roe)}</td>
      </tr>`).join('');
  const conta = (v.metodos||[{}])[0].metodo || '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">4 · O múltiplo — a variável que define metade do preço</div>

      <div class="rp-destaque">
        <div class="rp-destaque-topo">Múltiplo aplicado</div>
        <div class="rp-conta">${esc(conta)} = <span style="color:#0a5c35;">${esc(v.precoJusto)}</span></div>
        <p>${esc(v.origemMult)}</p>
      </div>

      <p style="margin-top:1.3rem;"><strong>Por que ${esc(v.regraMetodo)} e não outro múltiplo:</strong>
        ${esc(v.regraPorque)}</p>

      <div class="rp-section-title" style="margin-top:1.4rem;">A série que produz a âncora, ano a ano</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Exercício</th><th>Preço</th><th>${esc(s.metrica === 'P/FFO' ? 'FFO' : 'Lucro')}</th>
          <th>${esc(s.metrica)}</th><th>${esc(s.metricaRoe)}</th></tr></thead>
        <tbody>${linhas}</tbody>
        <tfoot><tr style="background:#f7f7f5;font-weight:700;">
          <td class="left">Mediana</td><td>—</td><td>—</td>
          <td class="rp-mono">${esc(s.mediana)}</td><td class="rp-mono">${esc(s.roeMediano)}</td>
        </tr></tfoot>
      </table></div>
      <p class="rp-note">É esta mediana que ancora o preço justo, corrigida pela rentabilidade de hoje
        (<strong>${esc(s.roeHoje)}</strong> contra <strong>${esc(s.roeMediano)}</strong> de mediana do período).
        O múltiplo do setor <strong>não entra</strong> desde 14/09/2026 — quem faz esse papel é o ajuste de ROE.</p>
      ${s.quebra ? `<p class="rp-note">⚠️ ${esc(s.quebra)}</p>` : ''}
    </div>`;
}

// ── 4 · DO LUCRO AO PREÇO ─────────────────────────────────────────────────────────────────
// Funde "7 · Projeção de lucro" e "8 · Valuation". "Precisamos ter clareza na projeção de
// lucro, o LPA e o múltiplo" — a fórmula aparece inteira, com cada peça nomeada.
function v2LucroPreco(r){
  const v = r.valuation || {};
  const c = v.cenariosLpa || {};
  const pl = r.projecaoLucro || {};
  const base = (c.cenarios||[]).find(x => x.cenario === 'Base') || {};
  const fund = (c.fundamento||'LPA').replace(' (fixo)','');
  const verif = (v.verificacao||[]).map(m => `
      <tr><td class="left">${esc(m.metodo)}</td><td class="rp-mono">${esc(m.precoJusto)}</td></tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">5 · Do lucro projetado ao preço justo</div>

      <div class="rp-formula">
        <div><b>1.</b> Ponto de partida &nbsp;→&nbsp; <strong>${esc(c.base||'—')}</strong></div>
        <div><b>2.</b> Crescimento aplicado &nbsp;→&nbsp; <strong>${esc(base.crescimento||'—')}</strong></div>
        <div><b>3.</b> ${esc(fund)} projetado &nbsp;→&nbsp; <strong>${esc(base.lpa||'—')}</strong></div>
        <div><b>4.</b> Múltiplo &nbsp;→&nbsp; <strong>${esc(c.multiplo||'—')}</strong></div>
        <div style="border-top:1px solid #e8e8f0;margin-top:8px;padding-top:8px;">
          <b>=</b> Preço justo &nbsp;→&nbsp; <strong style="font-size:19px;color:#0a5c35;">${esc(v.precoJusto)}</strong></div>
      </div>
      ${v2Crescimento(c.origemCrescimento)}
      <p class="rp-note"><strong>Premissa declarada:</strong> ${esc(base.premissa||'—')}</p>
      ${pl.nota ? `<p class="rp-note">${esc(pl.nota)}</p>` : ''}

      ${verif ? `
      <div class="rp-section-title" style="margin-top:1.4rem;">Verificação — não entra na conta</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Método</th><th>Daria</th></tr></thead><tbody>${verif}</tbody>
      </table></div>
      <p class="rp-note">Réguas diferentes, calculadas só para comparação. O preço justo usa
        <strong>um</strong> método, nunca a mediana de vários — ver METODOLOGIA_ANALISE.md seção 31.</p>` : ''}
    </div>`;
}

// ── 5 · CENÁRIOS ──────────────────────────────────────────────────────────────────────────
function v2Cenarios(r){
  const c = (r.valuation||{}).cenariosLpa;
  if(!c || !(c.cenarios||[]).length) return '';
  const fund = (c.fundamento||'LPA').replace(' (fixo)','');
  const cen = c.cenarios;
  const lo = cen.find(x=>x.cenario==='Conservador')||{}, md = cen.find(x=>x.cenario==='Base')||{},
        hi = cen.find(x=>x.cenario==='Otimista')||{};
  const linhas = cen.map(x => `
      <tr${x.cenario==='Base' ? ' style="background:#f0fdf6;font-weight:600;"' : ''}>
        <td class="left"><strong>${esc(x.cenario)}</strong></td>
        <td class="rp-mono">${esc(x.crescimento)}</td>
        <td class="rp-mono">${esc(x.total||'—')}</td>
        <td class="rp-mono">${esc(x.lpa)}</td>
        <td class="rp-mono">${esc(x.multiplo||c.multiplo)}</td>
        <td class="rp-mono" style="font-weight:700;">${esc(x.precoJusto)}</td>
      </tr>
      <tr><td colspan="6" class="left" style="padding-top:0;border-bottom:1px solid #f0f0f0;">
        <span style="font-size:13px;color:#666;line-height:1.6;">${esc(x.premissa)}</span></td></tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">6 · Cenários${c.amplitude ? ` — amplitude de ${esc(c.amplitude)}` : ''}</div>
      <div class="rp-faixa">
        <div class="fx-lo">Conservador<b>${esc(lo.precoJusto||'—')}</b></div>
        <div class="fx-md">Base<b>${esc(md.precoJusto||'—')}</b></div>
        <div class="fx-hi">Otimista<b>${esc(hi.precoJusto||'—')}</b></div>
      </div>
      <p class="rp-note">${c.variaMultiplo
        ? 'Os três cenários movem <strong>as duas</strong> variáveis juntas — o fundamento e o múltiplo —, '
          + 'porque é assim que o mercado se move: múltiplo comprime justamente quando o resultado decepciona. '
          + 'As pontas do múltiplo são o percentil 25 e 75 do que a <strong>própria empresa já negociou</strong>, '
          + 'não número inventado.'
        : 'Os três cenários variam só o crescimento; o múltiplo é o mesmo nos três.'}</p>
      <div class="rp-table-wrap" style="margin-top:0.9rem;"><table class="rp-table">
        <thead><tr><th>Cenário</th><th>Crescimento</th><th>${esc(fund.replace(' por ação',''))} total</th><th>${esc(fund)}</th><th>Múltiplo</th><th>Preço justo</th></tr></thead>
        <tbody>${linhas}</tbody>
      </table></div>
    </div>`;
}

// ── 6 · RETORNO ───────────────────────────────────────────────────────────────────────────
function v2Retorno(r){ return secRetornoTotal(r); }

// A conta da taxa de crescimento, aberta. "Na imagem não consigo ver como você chegou no
// crescimento de 7,7, qual o racional?" — a taxa é metade do preço justo e aparecia como
// rodapé de uma linha.
function v2Crescimento(oc){
  if(!oc) return '';
  const linhas = (oc.linhas||[]).map(l => `
      <tr><td class="left"><strong>${esc(l.ano)}</strong></td>
          <td class="rp-mono">${esc(l.valor)}</td>
          <td class="rp-mono">${esc(l.variacao)}</td></tr>`).join('');
  return `
      <div class="rp-section-title" style="margin-top:1.4rem;">De onde vem o crescimento de ${esc(oc.taxa)}</div>
      <div class="rp-table-wrap" style="max-width:520px;"><table class="rp-table">
        <thead><tr><th>Exercício</th><th>${esc(oc.rotulo)}</th><th>Variação a/a</th></tr></thead>
        <tbody>${linhas}</tbody>
        <tfoot><tr style="background:#f7f7f5;font-weight:700;">
          <td class="left">Taxa aplicada</td><td class="rp-mono">${esc(oc.taxa)}</td>
          <td style="font-size:12px;color:#666;">regressão log</td></tr></tfoot>
      </table></div>
      <p class="rp-note">${esc(oc.porQue)}</p>
      ${oc.limitado ? `<p class="rp-note">⚠️ A regressão deu ${esc(oc.taxaBruta)} e foi <strong>limitada ao teto de ${esc(oc.teto)}</strong> — premissa declarada, não calibração.</p>` : ''}`;
}

// Tabela de dividendos com o fundamento do ano e o payout implícito. "No item 8 faltou o LPA
// dos anos" — sem ele não dá para ver QUE FRAÇÃO do resultado está sendo distribuída, que é
// a única pergunta que importa numa projeção de dividendo de 5 anos.
function v2Dividendos(r){
  const html = secDividendos(r);
  const fpa = (r.valuation||{}).fundamentoPorAno;
  const pd = r.projecaoDividendos;
  if(!html || !fpa || !pd || !pd.tabela) return html;
  const porAno = {}; (fpa.linhas||[]).forEach(l => porAno[l.ano] = l);
  const linhas = (pd.tabela.linhas||[]).map(l => {
    const f = porAno[l.ano];
    const dv = _parseNumBR(l.divAcao);
    const po = (f && f.bruto && dv) ? Math.round(dv/f.bruto*100) + '%' : '—';
    return `<tr><td class="left"><strong>${esc(l.ano)}</strong></td>
      <td class="rp-mono">${esc(f ? f.valor : '—')}</td>
      <td class="rp-mono">${esc(l.divAcao)}</td>
      <td class="rp-mono">${po}</td>
      <td class="rp-mono">${esc(l.dy)}</td>
      <td class="left" style="font-size:13px;color:#666;">${esc(l.premissa)}</td></tr>`;
  }).join('');
  const tabela = `
      <div class="rp-table-wrap" style="margin-top:1rem;"><table class="rp-table">
        <thead><tr><th>Ano</th><th>${esc(fpa.rotulo)}</th><th>Dividendo/ação</th>
          <th>Payout implícito</th><th>DY</th><th>Premissa</th></tr></thead>
        <tbody>${linhas}</tbody>
      </table></div>
      <p class="rp-note"><strong>${esc(fpa.rotulo)}</strong> projetado à taxa do cenário base
        (${esc(fpa.taxa)} a.a.), a mesma da seção 6 — não é número novo. O <strong>payout
        implícito</strong> é o dividendo dividido por ele.</p>
      <p class="rp-note">⚠️ <strong>Confira contra o alerta acima.</strong> O payout implícito
        desta tabela cai de 77% para 54% do FFO ao longo dos 5 anos. O alerta, escrito à mão em
        15/08/2026, fala em normalizar a ~90% do AFFO — que, pelos próprios números dele
        (135% sobre FFO = 152% sobre AFFO, logo AFFO ≈ 0,89 × FFO), daria ~80% do FFO. As duas
        coisas não fecham: ou os dividendos projetados estão baixos, ou a referência de
        normalização está. Os valores de dividendo são premissa escrita, não saída do motor.</p>`;
  // Troca a tabela antiga pela nova, mantendo alerta, cards e o resto da seção.
  // ⚠️ A classe é `rp-div-table-wrap`, não `rp-table-wrap` — a seção de dividendos tem estilo
  // próprio. A primeira versão procurou a classe genérica, não achou nada, e devolveu o HTML
  // intacto: a tabela continuou com a coluna "LPA estimado" vazia, exatamente o que o usuário
  // tinha apontado. Falha silenciosa de `String.replace`, que não reclama quando não casa.
  const novo = html.replace(/<div class="rp-div-table-wrap">[\s\S]*?<\/table><\/div>/,
                            tabela.replace('rp-table-wrap', 'rp-div-table-wrap')
                                  .replace('class="rp-table"', 'class="rp-div-table"'));
  if (novo === html) return html;
  // A nota de rodapé dizia "coluna LPA não se aplica" — agora aplica, com FFO por ação.
  return novo.replace(/ALOS3 não opera com LPA como motor[^<]*—\s*coluna LPA não se aplica\./,
    'A coluna traz o FFO por ação, não o LPA: shopping não se mede por lucro contábil (ver seção 4).');
}


// ── 7 · TESTES E DADOS ────────────────────────────────────────────────────────────────────
// Recolhe num acordeão o que era bloco solto: descobertas, payout, receita, contexto de preço,
// leitura dos dados e dados coletados. Continua tudo lá — deixa de disputar a atenção.
function v2Testes(r){
  const partes = [secDescobertas(r), secTestePayout(r), secReceita(r), secContextoPreco(r),
                  secLeituraDados(r), secDadosColetados(r)].filter(Boolean).join('');
  if(!partes) return '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">9 · Testes, dados e verificações</div>
      <p class="rp-note" style="margin-top:0;">Tudo o que sustenta os números acima, recolhido aqui para não
        disputar atenção com a tese. Clique para abrir.</p>
      <details style="margin-top:0.6rem;">
        <summary style="cursor:pointer;font-size:14px;font-weight:600;color:#4f46e5;padding:6px 0;">
          Abrir testes de qualidade, payout, receita, contexto de preço e dados coletados</summary>
        <div style="margin-top:0.8rem;">${partes}</div>
      </details>
    </div>`;
}


function secHeader(r){
  return `
    <div class="rp-header">
      <div class="rp-header-left">
        <h1>${esc(r.ticker)} — ${esc(r.nome)}</h1>
        <p>Research · ${esc(r.segmento)} · ${esc(r.data)} · Fontes: ${esc(r.fontes)}</p>
      </div>
      <div style="text-align:right;">
        <div class="rp-cotacao">${esc(r.cotacao)}</div>
        <div style="font-size:11px;color:#aaa;margin-top:4px;">Preço justo ${esc(r.precoJusto||r.precoTeto||'—')} · Máx 52s ${esc(r.max52||'—')} · Mín 52s ${esc(r.min52||'—')}</div>
      </div>
    </div>`;
}

function secClassificacao(r){
  const c = r.classificacao || {};
  return `
    <div class="rp-section">
      <div class="rp-section-title">4 · Classificação setorial</div>
      <p style="font-size:12px;line-height:1.7;color:#333;">
        <strong>Setor:</strong> ${esc(c.setor)} &nbsp;|&nbsp; <strong>Motor de valuation:</strong> ${esc(c.motorPrimario)} &nbsp;|&nbsp;
        <span style="color:#888;"><strong>Descartado:</strong> ${esc(c.motorDescartado)}</span>
      </p>
      ${c.justificativa ? `<p style="font-size:12px;line-height:1.7;color:#555;margin-top:8px;">${esc(c.justificativa)}</p>` : ''}
    </div>`;
}

function secDadosColetados(r){
  const linhas = r.dadosColetados || [];
  if(!linhas.length) return '';
  const rows = linhas.map(d => `<tr><td class="rp-bold">${esc(d.bloco)}</td><td>${esc(d.dado)}</td><td class="rp-mono">${esc(d.valor)}</td><td>${esc(d.fonte)}</td><td>${esc(d.data)}</td></tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">13 · Dados coletados</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Bloco</th><th>Dado</th><th>Valor</th><th>Fonte</th><th>Data</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
    </div>`;
}

function secContextoPreco(r){
  if(!r.contextoPreco) return '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">5 · Contexto de preço</div>
      <p style="font-size:12px;line-height:1.75;color:#333;">${esc(r.contextoPreco)}</p>
    </div>`;
}

function secDescobertas(r){
  const items = r.descobertas || [];
  if(!items.length) return '';
  const cards = items.map(d => `
    <div class="rp-resumo-item" style="background:#f7f7f5;">
      <div class="rp-r-label">${esc(d.titulo)}</div>
      <div class="rp-r-value" style="line-height:1.7;">${esc(d.texto)}</div>
    </div>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">6 · Descobertas (testes de qualidade)</div>
      <div class="rp-resumo-grid" style="grid-template-columns:1fr;">${cards}</div>
    </div>`;
}

function secProjecaoLucro(r){
  const p = r.projecaoLucro;
  if(!p || !p.cenarios || !p.cenarios.length) return '';
  const rows = p.cenarios.map(c=>`<tr><td class="rp-bold">${esc(c.cenario)}</td><td>${esc(c.premissa)}</td><td class="rp-mono">${esc(c.valor)}</td></tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">7 · Projeção de lucro</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Cenário</th><th>Premissa</th><th>Resultado</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
      ${p.nota ? `<p class="rp-note">${esc(p.nota)}</p>` : ''}
    </div>`;
}

// ⚠️ REESCRITA EM 13/09/2026. Esta seção mostrava uma TABELA DE MÉTODOS, uma "dispersão"
// entre eles e um "preço justo (ponderado)" — a arquitetura de consenso que o Radar abandonou.
// O usuário abriu um relatório, leu "média dos 2 métodos" e disse: "eu já disse que não quero
// dessa forma, você precisa entender o que estou pedindo e implementar".
// Agora: UM método decide e aparece como conta; os demais aparecem separados e rotulados como
// verificação que NÃO entra no cálculo. Ver METODOLOGIA_ANALISE.md seção 31.
function secValuation(r){
  const v = r.valuation;
  if(!v) return '';
  const decide = (v.metodos||[])[0];
  const verif = v.verificacao||[];
  const linhasVerif = verif.map(m=>`<tr><td>${esc(m.metodo)}</td><td class="rp-mono">${esc(m.precoJusto)}</td></tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">8 · Valuation</div>
      ${decide ? `
      <div class="rp-info-grid">
        <div class="rp-info-item"><div class="rp-info-label">Critério</div><div class="rp-info-value">${esc(v.criterio||'—')}</div></div>
        <div class="rp-info-item"><div class="rp-info-label">Preço justo</div><div class="rp-info-value">${esc(v.precoJusto||'—')}</div></div>
      </div>
      <p class="rp-note" style="font-size:13px;color:#1a1a1a;margin-top:0.9rem;">
        <strong>${esc(decide.metodo)} = ${esc(decide.precoJusto)}</strong>
      </p>
      ${v.origemMult ? `<p class="rp-note">O múltiplo é ${esc(v.origemMult)}.</p>` : ''}
      ` : '<p class="rp-note">Sem preço justo calculável — ver a nota abaixo.</p>'}
      ${verif.length ? `
      <div class="rp-section-title" style="font-size:12px;margin-top:1.2rem;">Verificação — não entra na conta</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Outra régua</th><th>Daria</th></tr></thead>
        <tbody>${linhasVerif}</tbody>
      </table></div>` : ''}
      ${v.nota ? `<p class="rp-note">${esc(v.nota)}</p>` : ''}
    </div>`;
}

// ── 8b · A REGRA DESTA EMPRESA + LPA EM TRÊS CENÁRIOS ─────────────────────────────────────
// Pedido do usuário: "quero ver o cálculo de múltiplo e a regra que adotamos para cada empresa,
// e também um detalhamento do LPA projetado considerando 3 cenários". A regra que rege o que
// entra aqui está escrita no topo de scripts/gerar_relatorio_valuation.py — este render só
// exibe o que o gerador produziu, para não haver duas definições da mesma coisa.
function secRegraMultiplo(r){
  const v = r.valuation; if(!v || !v.regraMetodo) return '';
  const c = v.cenariosLpa;
  const linhas = c ? c.cenarios.map(x => `
    <tr${x.cenario === 'Base' ? ' style="background:#f0fdf6;font-weight:600;"' : ''}>
      <td class="left">${esc(x.cenario)}</td>
      <td class="rp-mono">${esc(x.crescimento)}</td>
      <td class="rp-mono">${esc(x.lpa)}</td>
      <td class="rp-mono rp-bold">${esc(x.precoJusto)}</td>
      <td class="left" style="font-size:11px;color:#666;">${esc(x.premissa)}</td>
    </tr>`).join('') : '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">8b · A regra desta empresa</div>
      <div class="rp-info-grid">
        <div class="rp-info-item"><div class="rp-info-label">Método que decide</div><div class="rp-info-value">${esc(v.regraMetodo)}</div></div>
        <div class="rp-info-item"><div class="rp-info-label">Grupo (só fallback)</div><div class="rp-info-value">${esc(v.regraGrupo)}</div></div>
      </div>
      <p class="rp-note" style="margin-top:0.8rem;"><strong>Por que este método:</strong> ${esc(v.regraPorque)}</p>
      ${v.origemMult ? `<p class="rp-note"><strong>De onde vem o múltiplo:</strong> ${esc(v.origemMult.replace(/\.$/, ''))}.</p>` : ''}
      <p class="rp-note" style="font-size:11px;color:#666;">${/DECLARADO/.test(v.origemMult || '')
        ? 'Este múltiplo foi DECLARADO no relatório e prevalece sobre a estatística — é a única exceção à regra geral. Nas demais empresas a âncora é a mediana do próprio múltiplo na janela 2021→, corrigida por (ROE atual ÷ ROE mediano do período), limitada a ±30%.'
        : 'Desde 14/09/2026 o múltiplo do SETOR não entra no preço justo. A âncora é a mediana do próprio múltiplo na janela 2021→, corrigida por (ROE atual ÷ ROE mediano do período), limitada a ±30%. O grupo acima só é usado como fallback quando a empresa não tem série própria utilizável.'}</p>
      ${c ? `
      <div class="rp-section-title" style="font-size:12px;margin-top:1.2rem;">${/fixo/.test(c.fundamento||'') ? esc(c.fundamento.replace(' (fixo)','')) + ' — três cenários de múltiplo' : esc(c.fundamento||'LPA') + ' projetado 2026 — três cenários'}</div>
      <p class="rp-note" style="margin-bottom:0.6rem;">Todos partem do mesmo lucro-base (<strong>${esc(c.base)}</strong>)
         e do mesmo múltiplo (<strong>${esc(c.multiplo)}</strong>). O que muda é só o crescimento.</p>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Cenário</th><th>${/fixo/.test(c.fundamento||'') ? 'Múltiplo' : 'Crescimento'}</th><th>${esc((c.fundamento||'LPA').replace(' (fixo)',''))} 2026</th><th>Preço justo</th><th>Premissa</th></tr></thead>
        <tbody>${linhas}</tbody>
      </table></div>` : `
      <p class="rp-note" style="margin-top:1rem;"><strong>Sem os três cenários nesta empresa.</strong>
         Eles exigem um fundamento em reais e uma contagem de papéis que reconcilie com ele — a base
         não tem os dois para esta linha, e projetar sobre um número que não fecha produziria três
         preços justos com aparência de precisão. O preço justo da coluna continua valendo: ele usa
         o LPA que a base traz, sem projeção.</p>`}
    </div>`;
}

// ── 2b · LEITURA DOS DADOS ────────────────────────────────────────────────────────────────
// ⚠️ NÃO É TESE. São fatos do HIST_SEED traduzidos para frase — rentabilidade, alavancagem,
// consistência do lucro, sustentabilidade do dividendo, quebra de série. O rótulo diz isso,
// porque dezenove das trinta e três empresas não têm análise escrita e um texto plausível
// gerado do nada seria pior que a ausência dele.
function secLeituraDados(r){
  const v = r.valuation; if(!v || !(v.leituraDados||[]).length) return '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">2b · Leitura dos dados</div>
      <p class="rp-note" style="margin-bottom:0.6rem;">Derivado da série do HIST_SEED, não é tese de
         analista — os pontos abaixo são o que os números dizem sozinhos.</p>
      <ul style="margin:0;padding-left:1.1rem;font-size:12.5px;line-height:1.75;">
        ${v.leituraDados.map(x => `<li>${esc(x)}</li>`).join('')}
      </ul>
    </div>`;
}

// Extrai o valor numérico de strings tipo "R$ 26,02" / "+19,1%" / "R$ 1.300.000"
function _parseNumBR(s){
  if(s==null) return null;
  const m = String(s).match(/-?\d[\d.]*,\d+|-?\d+/);
  if(!m) return null;
  const v = parseFloat(m[0].replace(/\./g,'').replace(',','.'));
  return isNaN(v) ? null : v;
}
function _fmtR$(v){
  if(v==null || isNaN(v)) return null;
  return 'R$ ' + v.toLocaleString('pt-BR', {minimumFractionDigits:2, maximumFractionDigits:2});
}
function _fmtPct(v){
  if(v==null || isNaN(v)) return null;
  return (v>=0?'+':'') + v.toLocaleString('pt-BR', {minimumFractionDigits:1, maximumFractionDigits:1}) + '%';
}

function secRetornoTotal(r){
  const rt = r.retornoTotal;
  if(!rt) return '';
  const doze = rt.doze || {};
  const v = r.valuation || {};

  const cotNum = _parseNumBR(r.cotacao);
  const precoJustoNum = _parseNumBR(v.precoJusto);
  // Não existe mais "preço teto" no relatório: a segunda leitura de valor é a MARGEM DE
  // SEGURANÇA contra o preço justo, exatamente como na coluna do Radar.
  const margemPct = (cotNum && precoJustoNum) ? _fmtPct((precoJustoNum - cotNum)/precoJustoNum*100) : null;

  let valorJustoPct = null, valorJustoR$ = null;
  if(cotNum && precoJustoNum){
    valorJustoPct = _fmtPct((precoJustoNum/cotNum - 1) * 100);
    valorJustoR$ = _fmtR$(precoJustoNum - cotNum);
  }
  // tenta achar o dividendo/ação (cenário base) na tabela embutida, se existir
  let divPorAcao = null;
  const linhasEmb = (rt.embutido && rt.embutido.tabelaProjecao) || [];
  const linhaDiv = linhasEmb.find(l => /dividendo/i.test(l.label||''));
  if(linhaDiv && linhaDiv.valores && linhaDiv.valores.length){
    divPorAcao = linhaDiv.valores[Math.floor(linhaDiv.valores.length/2)];
  }

  const ganhoGrid = `
    <div class="rp-ganho-grid">
      <div class="rp-ganho-item">
        <div class="rp-ganho-label">💰 Dividendos (12m)</div>
        <div class="rp-ganho-value">${esc(doze.dy || '—')}</div>
        ${divPorAcao ? `<div class="rp-ganho-sub">${esc(divPorAcao)}/ação</div>` : ''}
      </div>
      <div class="rp-ganho-item">
        <div class="rp-ganho-label">📈 Até o preço justo</div>
        <div class="rp-ganho-value">${esc(valorJustoPct || '—')}</div>
        ${valorJustoR$ ? `<div class="rp-ganho-sub">${esc(valorJustoR$)}/ação · justo ${esc(v.precoJusto||'—')}</div>` : ''}
      </div>
      <div class="rp-ganho-item">
        <div class="rp-ganho-label">🛡️ Margem de segurança</div>
        <div class="rp-ganho-value">${esc(margemPct || '—')}</div>
        <div class="rp-ganho-sub">(preço justo − cotação) ÷ preço justo</div>
      </div>
      <div class="rp-ganho-item rp-ganho-neutro">
        <div class="rp-ganho-label">🏆 Retorno total (12m)</div>
        <div class="rp-ganho-value">${esc(doze.total || '—')}</div>
        <div class="rp-ganho-sub">dividendos + valorização até o preço justo</div>
      </div>
    </div>`;

  const emb = rt.embutido;
  let embHtml = '';
  if(emb){
    const tA = (emb.tabelaProjecao||[]).map(row=>`<tr><td class="rp-bold">${esc(row.label)}</td>${(row.valores||[]).map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('');
    const tB = (emb.tabelaRetorno||[]).map(row=>`<tr><td class="rp-bold">${esc(row.label)}</td>${(row.valores||[]).map(v=>`<td>${esc(v)}</td>`).join('')}</tr>`).join('');
    embHtml = `
      <div style="margin-top:1rem;">
        <div class="rp-r-label" style="margin-bottom:6px;">Retorno embutido (múltiplo/cap rate constante)</div>
        <div class="rp-table-wrap"><table class="rp-table">
          <thead><tr><th>Tabela A — Projeção</th><th>Pessimista</th><th>Média</th><th>Otimista</th></tr></thead>
          <tbody>${tA}</tbody>
        </table></div>
        <div class="rp-table-wrap" style="margin-top:0.6rem;"><table class="rp-table">
          <thead><tr><th>Tabela B — Retorno embutido</th><th>Pessimista</th><th>Média</th><th>Otimista</th></tr></thead>
          <tbody>${tB}</tbody>
        </table></div>
        ${emb.leitura ? `<p class="rp-note">${esc(emb.leitura)}</p>` : ''}
      </div>`;
  }

  const cinco = rt.cincoAnos;
  let cincoHtml = '';
  if(cinco){
    const rows = (cinco.cenarios||[]).map(c=>`<tr class="${c.rowClass||''}"><td class="rp-bold">${esc(c.cenario)}</td><td>${esc(c.peso)}</td><td>${esc(c.acumulado)}</td><td>${esc(c.anualizado)}</td><td>${esc(c.realAnualizado)}</td></tr>`).join('');
    cincoHtml = `
      <div style="margin-top:1rem;">
        <div class="rp-r-label" style="margin-bottom:6px;">Retorno plurianual — 5 anos</div>
        <div class="rp-table-wrap"><table class="rp-table">
          <thead><tr><th>Cenário</th><th>Peso</th><th>Ret. acumulado</th><th>Anualizado</th><th>Real anualizado</th></tr></thead>
          <tbody>${rows}</tbody>
        </table></div>
        <div class="rp-info-grid" style="margin-top:0.75rem;">
          <div class="rp-info-item"><div class="rp-info-label">Ponderado (real a.a.)</div><div class="rp-info-value">${esc(cinco.ponderadoReal)}</div></div>
          <div class="rp-info-item"><div class="rp-info-label">Selic real 5a</div><div class="rp-info-value">${esc(cinco.selicReal)}</div></div>
          <div class="rp-info-item"><div class="rp-info-label">Tese sustenta?</div><div class="rp-info-value">${esc(cinco.sustentaTese)}</div></div>
        </div>
      </div>`;
  }

  const temDetalhe = embHtml || cincoHtml || doze.premioSelic || doze.realFisher;

  return `
    <div class="rp-section">
      <div class="rp-section-title">9 · Quanto posso ganhar</div>
      ${ganhoGrid}
      ${rt.interpretacao ? `<p class="rp-note" style="margin-top:0.85rem;">${esc(rt.interpretacao)}</p>` : ''}
      ${temDetalhe ? `
      <details class="rp-details" style="margin:1rem 0 0;padding:0.85rem 1rem;">
        <summary>Ver detalhamento (prêmio s/ Selic, cenários embutido e 5 anos)</summary>
        <div class="rp-details-body">
          <div class="rp-info-grid">
            <div class="rp-info-item"><div class="rp-info-label">Prêmio s/ Selic (12m)</div><div class="rp-info-value">${esc(doze.premioSelic||'—')}</div></div>
            <div class="rp-info-item"><div class="rp-info-label">Retorno real (Fisher, 12m)</div><div class="rp-info-value">${esc(doze.realFisher||'—')}</div></div>
          </div>
          ${embHtml}
          ${cincoHtml}
        </div>
      </details>` : ''}
    </div>`;
}

function secReceita(r){
  const rec = r.receita;
  if(!rec || !rec.itens || !rec.itens.length) return '';
  const rows = rec.itens.map(i=>`<tr><td class="rp-bold">${esc(i.item)}</td><td>${esc(i.pct)}</td><td>${esc(i.valor||'')}</td></tr>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">11 · Composição da receita</div>
      <div class="rp-table-wrap"><table class="rp-table">
        <thead><tr><th>Produto / Segmento</th><th>% da receita</th><th>Valor</th></tr></thead>
        <tbody>${rows}</tbody>
      </table></div>
      ${rec.nota ? `<p class="rp-note" style="margin-top:0.75rem;">${esc(rec.nota)}</p>` : ''}
      ${rec.fonte ? `<p class="rp-note">Fonte: ${esc(rec.fonte)}</p>` : ''}
    </div>`;
}

function secDividendos(r){
  const pd = r.projecaoDividendos;
  if(!pd) return '';
  const alerta = pd.alerta ? `
      <div class="rp-div-alert">
        <div class="rp-div-alert-title">⚠️ ${esc(pd.alerta.titulo)}</div>
        <div class="rp-div-alert-body">${esc(pd.alerta.texto)}</div>
      </div>` : '';

  const cardCls = {Conservador:'cons', Base:'base', Otimista:'otim'};
  const cenarios = (pd.cenarios||[]).map(c => `
      <div class="rp-div-card ${cardCls[c.nome]||'base'}">
        <div class="rp-div-card-label">${esc(c.nome)}</div>
        <div class="rp-div-card-value">${esc(c.divAcao)}</div>
        ${c.sub ? `<div class="rp-div-card-sub">${esc(c.sub)}</div>` : ''}
        ${c.dy ? `<div class="rp-div-card-dy">${esc(c.dy)}</div>` : ''}
      </div>`).join('');
  const cenariosHtml = cenarios ? `<div class="rp-div-cenarios">${cenarios}</div>` : '';

  const linhas = (pd.tabela && pd.tabela.linhas) || [];
  const tabelaHtml = linhas.length ? `
      <div class="rp-div-table-wrap"><table class="rp-div-table">
        <thead><tr><th>Ano</th><th>LPA estimado</th><th>Div./ação (Base)</th><th>DY (cotação atual)</th><th>Premissa</th></tr></thead>
        <tbody>${linhas.map(l=>`<tr><td>${esc(l.ano)}</td><td>${esc(l.lpa||'—')}</td><td>${esc(l.divAcao||'—')}</td><td>${esc(l.dy||'—')}</td><td>${esc(l.premissa||'')}</td></tr>`).join('')}</tbody>
      </table></div>` : '';

  if(!alerta && !cenariosHtml && !tabelaHtml) return '';

  return `
    <div class="rp-section">
      <div class="rp-section-title">10 · 💰 Projeção de dividendos — próximos 5 anos</div>
      ${alerta}
      ${cenariosHtml}
      ${tabelaHtml}
      ${pd.nota ? `<p class="rp-note" style="margin-top:0.75rem;">${esc(pd.nota)}</p>` : ''}
    </div>`;
}

function secTestePayout(r){
  const p = r.testePayout;
  if(!p) return '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">12 · Teste do payout</div>
      <div class="rp-info-grid">
        <div class="rp-info-item"><div class="rp-info-label">Payout / FFO</div><div class="rp-info-value">${esc(p.payoutFFO)}</div></div>
        <div class="rp-info-item"><div class="rp-info-label">Payout / AFFO</div><div class="rp-info-value">${esc(p.payoutAFFO)}</div></div>
        <div class="rp-info-item"><div class="rp-info-label">Origem do excedente</div><div class="rp-info-value">${esc(p.origem)}</div></div>
        <div class="rp-info-item"><div class="rp-info-label">Gravidade</div><div class="rp-info-value">${esc(p.gravidade)}</div></div>
      </div>
      ${p.texto ? `<p style="font-size:12px;line-height:1.7;color:#333;margin-top:0.75rem;">${esc(p.texto)}</p>` : ''}
    </div>`;
}

function secTeseRiscos(r){
  const teseItems = (r.tese||[]).map(t=>`<li>${esc(t)}</li>`).join('');
  const riscoItems = (r.riscos||[]).map(t=>`<li>${esc(t)}</li>`).join('');
  return `
    <div class="rp-section">
      <div class="rp-section-title">2 · Pontos a favor &nbsp;/&nbsp; Riscos</div>
      <div class="rp-bull-bear">
        <div class="rp-bull"><h3>🟢 Sustenta a tese</h3><ul>${teseItems}</ul></div>
        <div class="rp-bear"><h3>🔴 Riscos (por gravidade)</h3><ol style="padding-left:16px;">${riscoItems}</ol></div>
      </div>
    </div>`;
}

// Converte "★★★☆☆" em algo lível tipo "★★★☆☆ 3/5 · Moderada" — a nota
// numérica/qualitativa é derivada da própria contagem de estrelas (escala
// 1-5 já usada na metodologia), não é um dado novo inventado.
const _CONV_LABELS = {1:'Baixa', 2:'Baixa-moderada', 3:'Moderada', 4:'Alta', 5:'Muito alta'};
function _convComNota(s){
  if(!s) return '';
  const cheias = (String(s).match(/★/g)||[]).length;
  if(!cheias) return esc(s);
  return `${esc(s)} <span style="font-size:12px;font-weight:600;opacity:0.85;">${cheias}/5 · ${_CONV_LABELS[cheias]||''}</span>`;
}

// Valor curto no campo + ⓘ com a explicação completa em tooltip (mesmo padrão do
// Radar) — evita empilhar frase longa dentro do card.
function _valComTip(val, nota){
  if(!val) return '—';
  if(!nota) return esc(val);
  return `${esc(val)} <span class="col-tip" data-tip="${esc(nota).replace(/"/g,'&quot;')}">ⓘ</span>`;
}

function secVeredicto(r){
  const v = r.veredicto;
  if(!v) return '';
  const precoJusto = (r.valuation && r.valuation.precoJusto) || null;
  const retornoTotalProjetado = (r.retornoTotal && r.retornoTotal.doze && r.retornoTotal.doze.total) || null;
  const lucroTxt = (v.lucro2025 || v.lucroProjetado2026)
    ? `${esc(v.lucro2025||'—')} → ${esc(v.lucroProjetado2026||'—')}`
    : '—';
  return `
    <div class="rp-veredito-final">
      <h2>1 · Veredicto</h2>
      <div class="rp-vf-grid">
        <div class="rp-vf-item"><div class="rp-vf-label">Veredicto</div><div class="rp-vf-value ${v.class||''}">${esc(v.emoji)} ${esc(v.label)}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Convicção</div><div class="rp-vf-value yellow">${_convComNota(v.conviccao)}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Cotação</div><div class="rp-vf-value">${esc(v.cotacao)}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Preço justo</div><div class="rp-vf-value">${esc(precoJusto||v.precoJusto||'—')}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Margem de segurança (cotação → preço justo)</div><div class="rp-vf-value green">${esc(v.margem)}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Retorno total projetado (12m)</div><div class="rp-vf-value yellow">${esc(retornoTotalProjetado||'—')}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">DY projetado</div><div class="rp-vf-value yellow">${esc(v.dyProjetado||'—')}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">P/L atual</div><div class="rp-vf-value">${_valComTip(v.plAtual, v.plAtualNota)}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Payout utilizado no cálculo</div><div class="rp-vf-value">${_valComTip(v.payoutUsado, v.payoutUsadoNota)}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Lucro 2025 → 2026E</div><div class="rp-vf-value">${v.lucroNota ? `${lucroTxt} <span class="col-tip" data-tip="${esc(v.lucroNota).replace(/"/g,'&quot;')}">ⓘ</span>` : lucroTxt}</div></div>
        <div class="rp-vf-item"><div class="rp-vf-label">Dív. líquida / EBITDA</div><div class="rp-vf-value">${_valComTip(v.divLiqEbitda, v.divLiqEbitdaNota)}</div></div>
      </div>
      ${(v.gatilhos&&v.gatilhos.length) ? `<p style="font-size:12px;color:#ddd;margin-top:1.25rem;line-height:1.7;border-top:1px solid #ffffff22;padding-top:1rem;"><strong style="color:#ffd93d;">Gatilhos de monitoramento:</strong> ${v.gatilhos.map(esc).join(' · ')}</p>` : ''}
    </div>`;
}

function secEncaixeCarteira(r){
  if(!r.encaixeCarteira) return '';
  return `
    <div class="rp-section">
      <div class="rp-section-title">3 · Encaixe na carteira</div>
      <p style="font-size:12px;line-height:1.75;color:#333;">${esc(r.encaixeCarteira)}</p>
    </div>`;
}

function secBlocoCopiavel(r){
  if(!r.blocoCopiavel) return '';
  const raw = r.blocoCopiavel.replace(/`/g,'\\`');
  return `
    <div class="rp-section">
      <div class="rp-section-title">14 · Bloco de veredito copiável</div>
      <div style="position:relative;">
        <button class="rp-empty-btn" style="position:absolute;top:8px;right:8px;margin:0;padding:5px 12px;font-size:10px;" onclick='copiarBloco(this, ${JSON.stringify(r.blocoCopiavel)})'>⧉ Copiar</button>
        <pre class="rp-code">${esc(r.blocoCopiavel)}</pre>
      </div>
      ${r.ressalvas ? `<p class="rp-note" style="margin-top:0.75rem;">⚠️ Ressalvas: ${esc(r.ressalvas)}</p>` : ''}
    </div>`;
}
