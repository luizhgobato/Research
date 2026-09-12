// ── DICA DE SCROLL HORIZONTAL (MOBILE) ───────────────────────────────────────────────────
// A página inteira rola de lado quando a tabela ativa é mais larga que a viewport (ver
// comentário em #mainTable thead / .table-wrap, css/styles.css). No iOS a barra de rolagem
// some em repouso, então sem isso nada avisa que dá pra arrastar. Mostra o selo quando há
// overflow horizontal e a página ainda está no início do scroll; some ao rolar, ou sozinho
// depois de alguns segundos, e reaparece se o usuário voltar pro início com overflow ainda
// presente (troca de aba/página pode reduzir ou aumentar a largura do conteúdo).
(function () {
  const hint = document.getElementById('scrollHintMobile');
  if (!hint) return;
  let autoHideTimer = null;

  function hasOverflow() {
    return document.documentElement.scrollWidth > window.innerWidth + 4;
  }
  function show() {
    hint.classList.add('show');
    clearTimeout(autoHideTimer);
    autoHideTimer = setTimeout(() => hint.classList.remove('show'), 3500);
  }
  function hide() {
    hint.classList.remove('show');
    clearTimeout(autoHideTimer);
  }
  function evaluate() {
    if (hasOverflow() && window.scrollX < 20) show();
    else hide();
  }

  window.addEventListener('scroll', () => {
    if (window.scrollX > 20) hide();
  }, { passive: true });
  window.addEventListener('resize', evaluate);
  // Trocar de aba (Radar/Base de Dados/Carteiras) muda a tabela ativa e sua largura — reavalia
  // depois do reflow do showPage().
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => setTimeout(evaluate, 150));
  });
  setTimeout(evaluate, 600);
})();
