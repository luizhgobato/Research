function getCarteiraRows(){return Array.from(document.querySelectorAll('#tableBody tr[data-carteira="true"]'));}
function renderPosicoes(){
  const rows=getCarteiraRows();const tbody=document.getElementById('posTableBody');
  let html='',totalSaldo=0;
  rows.forEach(r=>totalSaldo+=(parseFloat(r.dataset.saldo)||0));
  rows.sort((a,b)=>(parseFloat(b.dataset.saldo)||0)-(parseFloat(a.dataset.saldo)||0));
  rows.forEach((row)=>{
    const ticker=(row.dataset.ticker||'').replace('.SA','');
    const qtd=parseFloat(row.dataset.qtd)||0;
    const pm=parseFloat(row.dataset.pm)||0;
    const saldo=parseFloat(row.dataset.saldo)||0;
    const dyAtual=parseFloat(row.dataset.dyAtual)||0;
    const varPct=parseFloat(row.dataset.var)||0;
    const pctCart=totalSaldo>0?(saldo/totalSaldo)*100:0;
    const cotacaoCell=row.querySelector('.cotacao-cell');
    let cotacaoTxt='—';
    if(cotacaoCell&&cotacaoCell.textContent!=='...'&&cotacaoCell.textContent!=='Erro')cotacaoTxt=cotacaoCell.textContent;
    const varClass=varPct>=0?'rent-pos':'rent-neg';
    const barW=Math.min(pctCart*3,100);
    const nome=row.querySelector('.empresa-name')?.textContent||'';
    html+=`<tr>
      <td><div class="pos-ticker">${ticker}</div><div class="pos-name">${nome}</div></td>
      <td>${qtd.toLocaleString('pt-BR')}</td>
      <td>R$ ${pm.toFixed(2).replace('.',',')}</td>
      <td class="num-blue">${cotacaoTxt}</td>
      <td class="${varClass}">${varPct>=0?'+':''}${varPct.toFixed(2).replace('.',',')}%</td>
      <td>${dyAtual.toFixed(2).replace('.',',')}%</td>
      <td>${pctCart.toFixed(1).replace('.',',')}%<div class="progress-bar-wrap"><div class="progress-bar" style="width:${barW}%"></div></div></td>
    </tr>`;
  });
  tbody.innerHTML=html;
}
// ── PRIVACIDADE ──
let _privado = false;
function togglePrivacy(){
  _privado = !_privado;
  document.body.classList.toggle('privado', _privado);
  document.getElementById('olhoIcon').textContent = _privado ? '🙈' : '👁';
  document.getElementById('olhoLabel').textContent = _privado ? 'Mostrar valores' : 'Ocultar valores';
  document.getElementById('btnOlho').classList.toggle('oculto', _privado);
  // Reconstrói cards e tabela com modo certo
  renderPosicoes();
  renderMobileCards();
}

