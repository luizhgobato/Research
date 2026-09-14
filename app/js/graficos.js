function buildRentAcumChart(){
  const el = document.getElementById('chartRentAcum');
  if(!el) return;
  // Pontos: jan/2020 até mai/2026 — rentabilidade acumulada mensal
  const pontos = [
    // 2020
    {l:'Jan/20', v:-5.50},  {l:'Fev/20', v:-14.74},{l:'Mar/20', v:-43.22},{l:'Abr/20', v:-33.69},
    {l:'Mai/20', v:-28.79}, {l:'Jun/20', v:-22.58}, {l:'Jul/20', v:-20.83},{l:'Ago/20', v:-20.68},
    {l:'Set/20', v:-25.82}, {l:'Out/20', v:-30.18}, {l:'Nov/20', v:-30.04},{l:'Dez/20', v:-28.99},
    // 2021
    {l:'Jan/21', v:-29.07}, {l:'Fev/21', v:-28.99},{l:'Mar/21', v:-27.65},{l:'Abr/21', v:-28.27},
    {l:'Mai/21', v:-25.76},{l:'Jun/21', v:-27.85},{l:'Jul/21', v:-29.31},{l:'Ago/21', v:-30.41},
    {l:'Set/21', v:-45.73},{l:'Out/21', v:-48.41},{l:'Nov/21', v:-49.53},{l:'Dez/21', v:-49.17},
    // 2022
    {l:'Jan/22', v:-48.22},{l:'Fev/22', v:-49.90},{l:'Mar/22', v:-47.45},{l:'Abr/22', v:-52.62},
    {l:'Mai/22', v:-52.37},{l:'Jun/22', v:-58.45},{l:'Jul/22', v:-56.77},{l:'Ago/22', v:-53.12},
    {l:'Set/22', v:-54.60},{l:'Out/22', v:-54.21},{l:'Nov/22', v:-55.82},{l:'Dez/22', v:-57.04},
    // 2023
    {l:'Jan/23', v:-55.02},{l:'Fev/23', v:-56.32},{l:'Mar/23', v:-56.55},{l:'Abr/23', v:-53.82},
    {l:'Mai/23', v:-49.62},{l:'Jun/23', v:-44.67},{l:'Jul/23', v:-43.92},{l:'Ago/23', v:-43.27},
    {l:'Set/23', v:-42.52},{l:'Out/23', v:-46.95},{l:'Nov/23', v:-40.78},{l:'Dez/23', v:-40.11},
    // 2024
    {l:'Jan/24', v:-42.89},{l:'Fev/24', v:-42.79},{l:'Mar/24', v:-43.07},{l:'Abr/24', v:-43.34},
    {l:'Mai/24', v:-46.27},{l:'Jun/24', v:-45.55},{l:'Jul/24', v:-45.67},{l:'Ago/24', v:-39.77},
    {l:'Set/24', v:-43.05},{l:'Out/24', v:-44.27},{l:'Nov/24', v:-45.71},{l:'Dez/24', v:-45.65},
    // 2025
    {l:'Jan/25', v:-41.07},{l:'Fev/25', v:-43.02},{l:'Mar/25', v:-40.05},{l:'Abr/25', v:-37.53},
    {l:'Mai/25', v:-40.12},{l:'Jun/25', v:-41.83},{l:'Jul/25', v:-44.12},{l:'Ago/25', v:-40.47},
    {l:'Set/25', v:-39.42},{l:'Out/25', v:-38.31},{l:'Nov/25', v:-35.27},{l:'Dez/25', v:-33.17},
    // 2026
    {l:'Jan/26', v:-29.73},{l:'Fev/26', v:-28.90},{l:'Mar/26', v:-30.28},{l:'Abr/26', v:-32.27},{l:'Mai/26', v:-31.91},
  ];
  // Mostra só rótulos de ano
  const labels_ano = ['2020','2021','2022','2023','2024','2025','2026'];
  const W = Math.max(el.offsetWidth||600, 400);
  const H = 160, pad = {t:20,r:20,b:30,l:55};
  const cW = W-pad.l-pad.r, cH = H-pad.t-pad.b;
  const vals = pontos.map(p=>p.v);
  const minV = Math.min(...vals)-5, maxV = Math.max(...vals)+5;
  const range = maxV-minV;
  const xScale = i => pad.l + (i/(pontos.length-1))*cW;
  const yScale = v => pad.t + cH*(1-(v-minV)/range);
  const zeroY = yScale(0);
  // Área sob a curva (fill)
  let areaPath = `M${xScale(0)},${zeroY}`;
  pontos.forEach((p,i) => { areaPath += ` L${xScale(i)},${yScale(p.v)}`; });
  areaPath += ` L${xScale(pontos.length-1)},${zeroY} Z`;
  // Linha
  let linePath = pontos.map((p,i) => `${i===0?'M':'L'}${xScale(i)},${yScale(p.v)}`).join(' ');
  // Grid lines
  let grid = '', yLabels = '';
  [-60,-40,-20,0].forEach(v => {
    const y = yScale(v);
    if(y>=pad.t && y<=pad.t+cH) {
      grid += `<line x1="${pad.l}" y1="${y}" x2="${pad.l+cW}" y2="${y}" stroke="${v===0?'#999':'#eee'}" stroke-width="${v===0?1.5:1}" stroke-dasharray="${v===0?'':'4,3'}"/>`;
      yLabels += `<text x="${pad.l-6}" y="${y+4}" text-anchor="end" font-size="9" fill="#aaa">${v}%</text>`;
    }
  });
  // Rótulos de ano
  let xLabels = '';
  labels_ano.forEach((ano, i) => {
    const mesIdx = i * 12;
    if(mesIdx < pontos.length) {
      const x = xScale(mesIdx);
      xLabels += `<text x="${x}" y="${H-pad.b+14}" text-anchor="middle" font-size="9" fill="#888">${ano}</text>`;
      xLabels += `<line x1="${x}" y1="${pad.t}" x2="${x}" y2="${pad.t+cH}" stroke="#f0f0f0" stroke-width="1"/>`;
    }
  });
  // Ponto final
  const lastX = xScale(pontos.length-1), lastY = yScale(pontos[pontos.length-1].v);
  const lastVal = pontos[pontos.length-1].v;
  const lastColor = lastVal >= 0 ? '#16a34a' : '#dc2626';
  el.innerHTML = `<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible;">
    <defs>
      <linearGradient id="rentGrad" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#dc2626" stop-opacity="0.15"/>
        <stop offset="100%" stop-color="#dc2626" stop-opacity="0.02"/>
      </linearGradient>
    </defs>
    ${grid}${yLabels}${xLabels}
    <path d="${areaPath}" fill="url(#rentGrad)"/>
    <path d="${linePath}" fill="none" stroke="#dc2626" stroke-width="2" stroke-linejoin="round"/>
    <circle cx="${lastX}" cy="${lastY}" r="4" fill="${lastColor}"/>
    <text x="${lastX+6}" y="${lastY+4}" font-size="10" font-weight="bold" fill="${lastColor}">${lastVal.toFixed(1)}%</text>
  </svg>`;
}
function buildChartClasse(){
  const el = document.getElementById('chartClasse');
  if(!el) return;
  const classes = [
    { label: 'Ações B3',           valor: 628826, cor: '#4f46e5' },
    { label: 'Previdência',         valor: 126826, cor: '#7c3aed' },
    { label: 'Renda Fixa',          valor: 72076,  cor: '#0891b2' },
    { label: 'ETFs Internacionais', valor: 9695,   cor: '#2563eb' },
  ];
  makeSVGDonut(el, classes.map(c=>c.label), classes.map(c=>c.valor), classes.map(c=>c.cor));
}
// opts.amounts: array de valores em R$ (mesma ordem de labels). Quando presente, a legenda
// e o tooltip passam a mostrar "R$ X · Y%" em vez de só o percentual — os gráficos das
// carteiras usam isso para o usuário ver quanto dinheiro há em cada fatia, não só a fração.
function makeSVGDonut(el, labels, values, colors, opts){
  if(!el)return;
  opts=opts||{};
  const amounts=Array.isArray(opts.amounts)?opts.amounts:null;
  const fmtR=v=>'R$ '+Math.round(v).toLocaleString('pt-BR');
  const amt=i=>(amounts&&isFinite(amounts[i]))?fmtR(amounts[i]):null;
  const total=values.reduce((a,b)=>a+b,0);
  if(total===0){el.innerHTML='<p style="color:#aaa;text-align:center;padding:2rem;font-size:12px;">Sem dados</p>';return;}
  const H=220,cx=100,cy=110,R=80,r=52;
  let paths='',startAngle=-Math.PI/2;
  values.forEach((v,i)=>{
    const angle=(v/total)*2*Math.PI;
    const x1=cx+R*Math.cos(startAngle),y1=cy+R*Math.sin(startAngle);
    const x2=cx+R*Math.cos(startAngle+angle),y2=cy+R*Math.sin(startAngle+angle);
    const xi1=cx+r*Math.cos(startAngle),yi1=cy+r*Math.sin(startAngle);
    const xi2=cx+r*Math.cos(startAngle+angle),yi2=cy+r*Math.sin(startAngle+angle);
    const lg=angle>Math.PI?1:0;
    const pct=((v/total)*100).toFixed(1).replace('.',',');
    const _a=amt(i);
    paths+=`<path d="M${xi1},${yi1} L${x1},${y1} A${R},${R} 0 ${lg},1 ${x2},${y2} L${xi2},${yi2} A${r},${r} 0 ${lg},0 ${xi1},${yi1}" fill="${colors[i%colors.length]}" opacity="0.9"><title>${labels[i]}: ${_a?_a+' · ':''}${pct}%</title></path>`;
    startAngle+=angle;
  });
  let legend='';
  labels.forEach((l,i)=>{
    const pct=((values[i]/total)*100).toFixed(1).replace('.',',');
    const a=amt(i);
    const valTxt=a?`<span style="font-weight:700;color:#333;margin-left:6px;white-space:nowrap;">${a}</span><span style="color:#888;margin-left:5px;white-space:nowrap;">${pct}%</span>`
                 :`<span style="font-weight:700;color:#333;margin-left:6px;">${pct}%</span>`;
    legend+=`<div class="svg-donut-leg-item" style="display:flex;align-items:center;gap:6px;margin-bottom:6px;font-size:11px;color:#555;"><div style="width:9px;height:9px;border-radius:2px;background:${colors[i%colors.length]};flex-shrink:0;"></div><span style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${l}</span>${valTxt}</div>`;
  });
  // As classes existem para o CSS poder empilhar rosca e legenda quando não cabem lado a lado.
  // Sem isso a legenda ficava espremida numa coluna de 82px no celular e os valores (que são
  // white-space:nowrap, senão "R$ 244.074" quebraria no meio) vazavam para fora da tela — era
  // esse vazamento que fazia a página inteira rolar 49px de lado sem ter nada lá.
  el.innerHTML=`<div class="svg-donut-row"><svg class="svg-donut-svg" width="210" height="${H}" viewBox="0 0 210 ${H}">${paths}</svg><div class="svg-donut-legend">${legend}</div></div>`;
}

function makeSVGBar(el, labels, values, colors, fmt){
  if(!el)return;
  // Percorre a árvore buscando a primeira largura real
  let W=0;
  let node=el;
  while(node&&W<10){W=node.offsetWidth||node.clientWidth||0;node=node.parentElement;}
  if(W<10)W=500; // fallback fixo
  W=Math.min(W,700);
  const H=200,pad={t:10,r:10,b:40,l:55};
  const cW=W-pad.l-pad.r,cH=H-pad.t-pad.b;
  const barW=Math.max(8,cW/labels.length-6);
  let bars='',xLabels='',yLines='';
  const maxVal=Math.max(...values,0),minVal=Math.min(...values,0);
  const range=maxVal-minVal||1;
  const zeroY=pad.t+cH*(maxVal/range);
  [0,25,50,75,100].forEach(p=>{
    const v=minVal+(range*p/100);
    const y=pad.t+cH*(1-p/100);
    yLines+=`<line x1="${pad.l}" y1="${y}" x2="${pad.l+cW}" y2="${y}" stroke="#f0f0f0" stroke-width="1"/>`;
    yLines+=`<text x="${pad.l-4}" y="${y+3}" text-anchor="end" font-size="9" fill="#aaa">${fmt?fmt(v):v.toFixed(0)}</text>`;
  });
  labels.forEach((l,i)=>{
    const x=pad.l+(i*(cW/labels.length))+(cW/labels.length-barW)/2;
    const v=values[i];
    const barH=Math.max(Math.abs(v/range)*cH,1);
    const y=v>=0?zeroY-barH:zeroY;
    const col=Array.isArray(colors)?colors[i%colors.length]:colors;
    bars+=`<rect x="${x}" y="${y}" width="${barW}" height="${barH}" fill="${col}" rx="3" opacity="0.85"><title>${l}: ${fmt?fmt(v):v}</title></rect>`;
    xLabels+=`<text x="${x+barW/2}" y="${H-pad.b+14}" text-anchor="middle" font-size="9" fill="#888">${l}</text>`;
  });
  el.innerHTML=`<svg width="100%" height="${H}" viewBox="0 0 ${W} ${H}" style="overflow:visible;">${yLines}${bars}${xLabels}<line x1="${pad.l}" y1="${zeroY}" x2="${pad.l+cW}" y2="${zeroY}" stroke="#ddd" stroke-width="1"/></svg>`;
}

let charts={};
function buildCharts(){
  buildChartClasse();
  buildRentAcumChart();
  const rows=getCarteiraRows().filter(r=>parseFloat(r.dataset.saldo)>0);
  rows.sort((a,b)=>(parseFloat(b.dataset.saldo)||0)-(parseFloat(a.dataset.saldo)||0));
  const labels=rows.map(r=>(r.dataset.ticker||'').replace('.SA',''));
  const saldos=rows.map(r=>parseFloat(r.dataset.saldo)||0);
  const segMap={};
  rows.forEach(r=>{const seg=r.dataset.segmento||'Outros';segMap[seg]=(segMap[seg]||0)+(parseFloat(r.dataset.saldo)||0);});
  const segLabels=Object.keys(segMap),segVals=segLabels.map(s=>segMap[s]);
  makeSVGDonut(document.getElementById('chartComposicao'),labels,saldos,COLORS);
  makeSVGDonut(document.getElementById('chartSegmento'),segLabels,segVals,COLORS.slice(2));
  // Gráfico de Proventos 12M por ativo
  const provLabels=rows.map(r=>(r.dataset.ticker||'').replace('.SA',''));
  const provVals=rows.map(r=>parseFloat(r.dataset.proventos12m)||0);
  makeSVGBar(document.getElementById('chartRent'),provLabels,provVals,
    provVals.map(()=>'#0891b2'),
    v=>`R$${(v/1000).toFixed(0)}k`);
  buildDivProjChart();
  buildDivHistChart();
}

function buildDivProjChart(){
  const rows=getCarteiraRows().filter(r=>parseFloat(r.dataset.qtd)>0);
  let anos=[2026,2027,2028,2029,2030],totais=anos.map(()=>0);
  rows.forEach(row=>{
    const qtd=parseFloat(row.dataset.qtd)||0,dyProj=parseFloat(row.dataset.dyProj)||0,divAcao=parseFloat(row.dataset.divAcao)||0;
    const cotacaoCell=row.querySelector('.cotacao-cell');
    let cot=parseFloat(row.dataset.pm)||0;
    if(cotacaoCell){const t=cotacaoCell.textContent.replace(/[^0-9,.]/g,'').replace(',','.');const p=parseFloat(t);if(p>0)cot=p;}
    const base=divAcao>0?qtd*divAcao:qtd*cot*dyProj;
    anos.forEach((_,i)=>{totais[i]+=base*Math.pow(1+DIV_GROWTH,i);});
  });
  makeSVGBar(document.getElementById('chartDivProj'),anos.map(String),totais.map(v=>Math.round(v)),'#0891b2',v=>`R$${(v/1000).toFixed(0)}k`);
  const t0=Math.round(totais[0]);
  document.getElementById('kpi-div2026').textContent=`R$ ${t0.toLocaleString('pt-BR')}`;
  document.getElementById('kpi-div2026-mes').textContent=`~R$ ${Math.round(t0/12).toLocaleString('pt-BR')}/mês`;
  const acum=totais.reduce((a,b)=>a+b,0),totalSaldo=getCarteiraRows().reduce((a,r)=>a+(parseFloat(r.dataset.saldo)||0),0);
  document.getElementById('divKpisRow').innerHTML=`
    <div class="div-kpi-sm"><div class="div-kpi-sm-val">R$ ${t0.toLocaleString('pt-BR')}</div><div class="div-kpi-sm-label">2026</div></div>
    <div class="div-kpi-sm"><div class="div-kpi-sm-val">R$ ${Math.round(t0/12).toLocaleString('pt-BR')}/mês</div><div class="div-kpi-sm-label">Média mensal</div></div>
    <div class="div-kpi-sm"><div class="div-kpi-sm-val">R$ ${Math.round(acum).toLocaleString('pt-BR')}</div><div class="div-kpi-sm-label">Acum. 5 anos</div></div>
    <div class="div-kpi-sm"><div class="div-kpi-sm-val">${totalSaldo>0?((acum/totalSaldo)*100).toFixed(1).replace('.',','):0}%</div><div class="div-kpi-sm-label">% Cap. Recup.</div></div>`;
}

function buildDivHistChart(){
  const anos = ['2022','2023','2024','2025','2026*'];
  const vals = [2101, 13175, 25308, 34266, 15774];
  const colors = [
    'rgba(156,163,175,0.7)',
    'rgba(96,165,250,0.75)',
    'rgba(52,211,153,0.75)',
    'rgba(22,163,74,0.85)',
    'rgba(79,70,229,0.75)'
  ];
  makeSVGBar(document.getElementById('chartDivHist'), anos, vals, colors,
    v => `R$${(v/1000).toFixed(0)}k`);
}
function renderDivProjTable(){const rows=getCarteiraRows().filter(r=>parseFloat(r.dataset.qtd)>0);rows.sort((a,b)=>(parseFloat(b.dataset.saldo)||0)-(parseFloat(a.dataset.saldo)||0));const tbody=document.getElementById('divProjBody');let html='',tots=[0,0,0,0,0];rows.forEach(row=>{const ticker=(row.dataset.ticker||'').replace('.SA',''),qtd=parseFloat(row.dataset.qtd)||0,divAcao=parseFloat(row.dataset.divAcao)||0,dyProj=parseFloat(row.dataset.dyProj)||0,saldo=parseFloat(row.dataset.saldo)||0;const cotacaoCell=row.querySelector('.cotacao-cell');let cot=parseFloat(row.dataset.pm)||0;if(cotacaoCell){const t=cotacaoCell.textContent.replace(/[^0-9,.]/g,'').replace(',','.');const p=parseFloat(t);if(p>0)cot=p;}const base=divAcao>0?qtd*divAcao:qtd*cot*dyProj,divs=[0,1,2,3,4].map(i=>base*Math.pow(1+DIV_GROWTH,i));divs.forEach((v,i)=>tots[i]+=v);const acum=divs.reduce((a,b)=>a+b,0),pctCap=saldo>0?(acum/saldo)*100:0;const divAcaoStr=divAcao>0?`R$ ${divAcao.toFixed(2).replace('.',',')}`:`<span style="color:var(--text3)">~R$ ${(cot*dyProj).toFixed(2).replace('.',',')}*</span>`;html+=`<tr><td><strong>${ticker}</strong></td><td>${qtd.toLocaleString('pt-BR')}</td><td>${divAcaoStr}</td>${divs.map(v=>`<td style="color:var(--teal);font-weight:600;">R$ ${Math.round(v).toLocaleString('pt-BR')}</td>`).join('')}<td style="font-weight:700;">R$ ${Math.round(acum).toLocaleString('pt-BR')}</td><td>${pctCap.toFixed(1).replace('.',',')}%</td></tr>`;});const acumTotal=tots.reduce((a,b)=>a+b,0),totalSaldo=getCarteiraRows().reduce((s,r)=>s+(parseFloat(r.dataset.saldo)||0),0);html+=`<tr><td>TOTAL</td><td>—</td><td>—</td>${tots.map(v=>`<td>R$ ${Math.round(v).toLocaleString('pt-BR')}</td>`).join('')}<td>R$ ${Math.round(acumTotal).toLocaleString('pt-BR')}</td><td>${totalSaldo>0?((acumTotal/totalSaldo)*100).toFixed(1).replace('.',',')+' %':'—'}</td></tr>`;tbody.innerHTML=html;}
// ══ TOGGLE DE CARTEIRA — 14/09/2026 ═══════════════════════════════════════════════════════
// Relato do usuário: "marquei umas ações que estão na minha carteira, e o formulário apagou".
// Eram DOIS defeitos na mesma função, e os dois perdiam a marcação:
//
//  1 · NADA ERA GRAVADO. `toggleCarteira` escrevia só `row.dataset.carteira`, que vive na
//      memória da página. Qualquer recarga, F5 ou versão nova do arquivo zerava tudo, e as
//      33 linhas do radar-rows.data.js nascem com data-carteira="false". O trabalho de marcar
//      a carteira inteira se perdia sem aviso nenhum.
//
//  2 · A LINHA ERA IDENTIFICADA PELO ÍNDICE NO DOM. O handler recebia `i` da ordem de
//      renderização e depois fazia querySelectorAll(...)[i]. Só que a tabela ORDENA: clicar
//      em qualquer cabeçalho reordena o tbody e o índice passa a apontar para outra empresa.
//      Marcar o ITUB3 depois de ordenar por margem marcava a linha que estivesse naquela
//      posição. A identidade certa é o TICKER, que não muda de valor quando a ordem muda.
//
// A gravação é por ticker, no localStorage do próprio navegador (não sai do aparelho, não
// acompanha outro computador nem aba anônima). Se o storage estiver bloqueado, a marcação
// ainda funciona na sessão e o usuário é avisado uma vez — calar seria repetir o defeito.
const CART_KEY = 'radar_carteira_v1';
let _cartAvisou = false;

// Devolve null quando NUNCA foi gravado — diferente de gravado-e-vazio. A distinção importa:
// sem chave vale o padrão do HTML (RANI3, CXSE3, BBSE3 e IRBR3 nascem marcadas); com chave,
// vale o que está gravado, inclusive lista vazia.
function _cartLer(){
  try {
    const raw = localStorage.getItem(CART_KEY);
    if (raw === null) return null;
    const v = JSON.parse(raw);
    return new Set(Array.isArray(v) ? v : []);
  } catch { return null; }
}
function _cartGravar(set){
  try { localStorage.setItem(CART_KEY, JSON.stringify([...set])); return true; }
  catch { return false; }
}
function _cartAtual(){
  return new Set(Array.from(document.querySelectorAll('#tableBody tr[data-carteira="true"]'))
                      .map(r => r.dataset.ticker).filter(Boolean));
}

// Chamado no boot ANTES de renderToggles, para os checkboxes já nascerem no estado certo.
//
// ⚠️ APLICA O CONJUNTO GRAVADO DE FORMA AUTORITÁRIA — marca E DESMARCA. A primeira versão só
// adicionava, e aí desmarcar uma linha que vem marcada no HTML não sobrevivia à recarga: o
// usuário tirava a BBSE3, dava F5 e ela voltava, porque o padrão do arquivo se reimpunha.
// Quando não há chave gravada (primeira visita), o padrão do HTML vale e é GRAVADO na hora —
// a partir daí o navegador do usuário é a fonte da verdade, não o arquivo.
function restaurarCarteira(){
  const salvos = _cartLer();
  if (salvos === null) { _cartGravar(_cartAtual()); return; }
  document.querySelectorAll('#tableBody tr[data-ticker]').forEach(r => {
    const dentro = salvos.has(r.dataset.ticker);
    r.dataset.carteira = dentro ? 'true' : 'false';
    r.classList.toggle('in-carteira', dentro);
  });
}

function renderToggles(){
  document.querySelectorAll('#tableBody tr').forEach(row => {
    const cell = row.querySelector('.toggle-col');
    if (!cell) return;
    const tk = row.dataset.ticker || '';
    const inCart = row.dataset.carteira === 'true';
    const id = 'tog_' + tk.replace(/[^A-Za-z0-9]/g, '');
    cell.innerHTML = `<div class="toggle-cart"><input type="checkbox" id="${id}" ${inCart ? 'checked' : ''} `
                   + `onchange="toggleCarteira(this,'${tk}')"><label for="${id}"></label></div>`;
    row.classList.toggle('in-carteira', inCart);
  });
}

function toggleCarteira(cb, tk){
  const row = document.querySelector(`#tableBody tr[data-ticker="${tk}"]`);
  if (!row) return;
  row.dataset.carteira = cb.checked ? 'true' : 'false';
  row.classList.toggle('in-carteira', cb.checked);
  if (!_cartGravar(_cartAtual()) && !_cartAvisou) {
    _cartAvisou = true;
    if (typeof showToast === 'function')
      showToast('⚠️ Sem acesso ao armazenamento do navegador — a marcação vale só nesta sessão.');
  }
  refreshCarteira();
}
function refreshCarteira(){renderPosicoes();renderMobileCards();buildCharts();renderDivProjTable();applyFilters();}
