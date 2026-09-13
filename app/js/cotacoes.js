async function fetchCotacao(ticker){
  const chartUrls=[
    `https://query1.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=1d`,
    `https://query2.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=1d`,
  ];
  const proxies=[
    u=>`https://corsproxy.io/?${encodeURIComponent(u)}`,
    u=>`https://api.codetabs.com/v1/proxy?quest=${encodeURIComponent(u)}`,
    u=>`https://api.allorigins.win/get?url=${encodeURIComponent(u)}`,
  ];
  for(const proxyFn of proxies){
    for(const yUrl of chartUrls){
      try{
        const isAO=proxyFn===proxies[2];
        const res=await fetch(proxyFn(yUrl),{signal:AbortSignal.timeout(7000)});
        if(!res.ok)continue;
        const raw=await res.text();
        let json;try{json=isAO?JSON.parse(JSON.parse(raw).contents):JSON.parse(raw);}catch{continue;}
        const m=json?.chart?.result?.[0]?.meta;
        const p=m?.regularMarketPrice||m?.previousClose;
        if(p&&p>0)return p;
      }catch{continue;}
    }
  }
  return null;
}

// Fetch via brapi.dev — 1 ticker por requisição (plano free NÃO aceita batch),
// em paralelo via Promise.all. Nome mantido p/ compatibilidade com atualizarCotacoes.
async function fetchCotacoesBatch(tickers){
  const map={};
  await Promise.all(tickers.map(async t=>{
    const clean=t.replace('.SA','');
    try{
      const res=await fetch(`https://brapi.dev/api/quote/${clean}?token=${BRAPI_TOKEN}`,{signal:AbortSignal.timeout(12000)});
      if(!res.ok)return;
      const json=await res.json();
      const r=json?.results?.[0];
      if(r&&r.regularMarketPrice>0)map[t]=r.regularMarketPrice;
    }catch{}
  }));
  return map;
}
function margemTag(pct){
  if(pct===null) return '<span class="muted">—</span>';
  const fmt=(pct>=0?'+':'')+pct.toFixed(0)+'%';
  if(pct>=10) return `<span class="tag tag-green">${fmt}</span>`;
  if(pct>=0)  return `<span class="tag tag-blue">${fmt}</span>`;
  return `<span class="tag tag-red">${fmt}</span>`;
}
// Aplica o preço numa linha do radar e recalcula todos os indicadores derivados
function aplicarPrecoRadar(row, preco){
  const ticker=row.dataset.ticker;
  const cotacaoCell=row.querySelector('.cotacao-cell'),margemCell=row.querySelector('.margem-cell'),cells=row.querySelectorAll('td');
  // Captura cotação e DY antigos ANTES de atualizar a célula
  const _oldCot=parseFloat((cells[17]?.textContent||'').replace(/[^0-9,.]/g,'').replace(',','.')) || 0;
  const _oldDy =parseFloat(row.dataset.dyProj) || 0;
  cotacaoCell.classList.remove('loading','error');
  cotacaoCell.classList.add('updated');
  cotacaoCell.textContent=`R$ ${preco.toFixed(2).replace('.',',')}`;
  // Preserva DPS real: novo DY% = DPS / novo preço (DPS = dyProj_antigo × cotacao_antiga)
  if(_oldDy>0&&_oldCot>0&&preco>0) row.dataset.dyProj=(_oldDy*_oldCot/preco).toFixed(4);
  // Atualiza células de DY proj
  atualizarDivDY(row, preco);   // DPS = LPA × payout; DY = DPS ÷ preço (js/calculos.js)
  calcularPrecoTeto(row,preco);
  const precoTeto=parseFloat(row.dataset.precoTeto)||null;
  const qtd=parseFloat(row.dataset.qtd)||0,pm=parseFloat(row.dataset.pm)||0;
  if(qtd>0){
    row.dataset.saldo=(qtd*preco).toFixed(2);
    if(pm>0)row.dataset.rent=(((preco-pm)/pm)*100>=0?'+':'')+((preco-pm)/pm*100).toFixed(2);
  }
  if(margemCell&&precoTeto){
    renderMargemRetorno(cells, margemCell, precoTeto, preco, dyProj);
  }
  if(typeof atualizarPLAtualLinha==='function') atualizarPLAtualLinha(row);
}

async function atualizarCotacoes(){
  const btn=document.getElementById('btnUpdate'),statusEl=document.getElementById('updateStatus'),statusText=document.getElementById('updateText');
  btn.disabled=true;btn.classList.add('loading');statusText.textContent='Buscando...';statusEl.className='update-status';
  const arr=Array.from(document.querySelectorAll('#tableBody tr[data-ticker]'));
  arr.forEach(r=>{const c=r.querySelector('.cotacao-cell');if(c){c.classList.add('loading');c.textContent='...';}});
  let ok=0,errs=0;

  // brapi primeiro (1 ticker/req em paralelo — plano free não aceita batch);
  // Yahoo via proxies só como fallback (proxies gratuitos estão instáveis)
  statusText.textContent='Buscando cotações...';
  const batchMap=await fetchCotacoesBatch(arr.map(r=>r.dataset.ticker));
  const fallbackRows=[];
  for(const row of arr){
    const p=batchMap[row.dataset.ticker];
    if(p){aplicarPrecoRadar(row,p);ok++;}
    else fallbackRows.push(row);
  }
  if(fallbackRows.length>0){
    await Promise.all(fallbackRows.map(async row=>{
      const p=await fetchCotacao(row.dataset.ticker);
      if(p){aplicarPrecoRadar(row,p);ok++;}
      else{row.querySelector('.cotacao-cell').classList.add('error');row.querySelector('.cotacao-cell').textContent='Erro';errs++;}
    }));
  }
  // ── RECALCULA KPI CARDS ──
  recalcularKPIs();
  btn.disabled=false;btn.classList.remove('loading');
  const agora=new Date().toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  statusEl.className=errs===0?'update-status ok':'update-status err';
  const msg=errs===0?`${ok} cotações às ${agora}`:`${ok} ok · ${errs} erros · ${agora}`;
  statusText.textContent=msg;
  const lu=document.getElementById('lastUpdate');const sd=document.getElementById('statusDot');
  if(lu)lu.textContent=msg;
  if(sd){sd.className='nav-status-dot '+(errs===0?'ok':'err');}
  // ── RERENDER TUDO ──
  renderPosicoes();renderMobileCards();
  buildCharts();buildDivProjChart();renderDivProjTable();
  calcularDerivadosRadar();
  // Salvar cache
  const cache={};document.querySelectorAll('#tableBody tr[data-ticker]').forEach(r=>{const c=r.querySelector('.cotacao-cell');if(c&&c.textContent!=='...'&&c.textContent!=='Erro'&&c.textContent!=='—')cache[r.dataset.ticker]=c.textContent;});
  try{localStorage.setItem('cotacoes_cache',JSON.stringify({ts:Date.now(),data:cache}));}catch(e){sessionStorage.setItem('cotacoes_cache',JSON.stringify({ts:Date.now(),data:cache}));}
}

function recalcularKPIs(){
  // Soma saldos de ações B3 (data-carteira=true, são ações)
  const carteiraRows = getCarteiraRows();
  const totalAcoes = carteiraRows.reduce((s,r)=>s+(parseFloat(r.dataset.saldo)||0),0);
  // Patrimônio total = ações + outros investimentos fixos
  const outrosFixo = 126826 + 72076 + 9695; // Previdência + RF + ETF Int.
  const totalPatr = totalAcoes + outrosFixo;
  // Atualiza KPI Ações B3
  const kpiAcoes = document.querySelector('.kpi-card:nth-child(2) .kpi-val');
  if(kpiAcoes){
    const pctAcoes=(totalAcoes/totalPatr*100).toFixed(1);
    kpiAcoes.innerHTML=`<span class="valor-rs">R$ ${Math.round(totalAcoes).toLocaleString('pt-BR')}</span><span class="valor-pct">${pctAcoes}%</span>`;
  }
  // Atualiza KPI Patrimônio Total
  const kpiPatr = document.querySelector('.kpi-card.accent .kpi-val');
  if(kpiPatr){
    kpiPatr.innerHTML=`<span class="valor-rs">R$ ${Math.round(totalPatr).toLocaleString('pt-BR')}</span><span class="valor-pct">100%</span>`;
  }
  // Atualiza subtítulo do header
  const sub = document.querySelector('.carteira-header p');
  if(sub) sub.textContent=`Patrimônio total: R$ ${Math.round(totalPatr).toLocaleString('pt-BR')} · Ações + Prev. + Renda Fixa + ETFs · Atualizado agora`;
}
