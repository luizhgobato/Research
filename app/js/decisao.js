// ══════════════════════════════════════════════════════════════════════════════════════════
// MOTOR DE DECISÃO — "esta empresa está barata?" traduzido em colunas do Radar
// ══════════════════════════════════════════════════════════════════════════════════════════
// O Radar tinha 20 colunas de DADO e nenhuma de DECISÃO: para saber se um ativo passava no
// crivo era preciso ler seis colunas e fazer a conta de cabeça. Este arquivo aplica os quatro
// critérios da METODOLOGIA_ANALISE.md (seção 9) e devolve DUAS colunas novas:
//
//   20 · Prêmio Selic  = earnings yield (L/P) − Selic, em pontos percentuais.
//                        É a pergunta central: "se esta empresa nunca mais crescer e eu
//                        comprar por este preço, quanto rende por ano — e isso ganha do
//                        CDI?" Positivo = a ação paga para você correr risco.
//   21 · Critérios     = quantos dos 4 testes a empresa passa (n/N). Tooltip lista cada um.
//                        O 5º (margem de segurança) virou REFERÊNCIA em 06/09/2026 — ver bloco 3.
//
// POR QUE AS COLUNAS SÃO ACRESCENTADAS NO FIM E NÃO NO MEIO:
// meia dúzia de arquivos indexam células por posição (cells[7] = LPA, cells[16] = cotação,
// sortTable(12) = P/L…). Inserir coluna no meio deslocaria TODOS esses índices e quebraria
// preço-teto, margem de segurança e ordenação de uma vez. Acrescentar no fim é aditivo:
// nenhum índice existente muda. O ranking no topo da aba resolve a visibilidade.
//
// RECÁLCULO AO VIVO: segue o padrão de atualizarPLAtualLinha() (js/fundamentos.js) — o
// earnings yield depende da cotação, então tudo é recalculado a cada atualização de preço.
// Nada aqui é hardcodado.

const DEC_COL_PREMIO = 20, DEC_COL_SCORE = 21, DEC_COL_TIR = 22, DEC_COL_G = 23;

// ── COLUNA 23 · CRESCIMENTO (g) — 07/09/2026 ──────────────────────────────────────────────
// O `g` já existia e movia a TIR inteira, mas só aparecia dentro de uma tooltip. Ele é a
// premissa mais influente da TIR real depois do próprio lucro, e estava invisível.
//
// g = MENOR entre  ROE × retenção  e  crescimento do lucro recorrente por regressão log,
//     com piso em 0% e teto em 15%.
//
// A coluna mostra o g USADO e, quando o bruto é diferente, o bruto entre parênteses. Isso
// existe porque o piso e o teto ESCONDEM informação relevante:
//   · BBSE3 aparece com 15% e o dado diz 23,1% — o teto está cortando
//   · PASS3 aparece com 0% e o dado diz −16,4% — a empresa está ENCOLHENDO
//   · SHUL4 aparece com 0% e o dado diz −3,2% — estagnada, não encolhendo
// Sem o bruto, PASS3 e SHUL4 pareciam idênticas na tela, e não são: uma anda de lado, a
// outra perdeu metade do lucro recorrente em quatro anos.

// ══════════════════════════════════════════════════════════════════════════════════════════
// A "Nota 0-100" foi REMOVIDA daqui. Não porque estava quebrada — porque não tinha evidência.
// O backtest sobre os dados deste projeto (130 obs., 2021-2026) não achou poder discriminante
// nos 5 critérios, e os eixos de "qualidade" (ROE, alavancagem) PIORARAM o retorno. Uma nota
// de 0 a 100 comunica precisão que o método não tinha. No lugar entra a TIR real de
// data/tir.data.js — três medidas independentes, cada uma auditável até a DFP.
// Os critérios (coluna 21) FICAM, rebaixados a triagem: dizem onde olhar, não o que comprar.
// ══════════════════════════════════════════════════════════════════════════════════════════

function _tirDe(row) {
  const t = (row.dataset.ticker || '').replace(/\.SA$/i, '');
  return (typeof TIR_SEED !== 'undefined') ? TIR_SEED[t] : null;
}

// ── TIR AO VIVO — item #8 do punch-list de 06/09/2026 ─────────────────────────────────────
// data/tir.data.js é gerado por scripts/gerar_tir.py com o preço do data-base do HIST_SEED
// (`precoBase`), não a cotação de hoje. Medido em 07/09/2026, um dia depois de gerado, isso
// já defasava IRBR3 em -9,9%, BBSE3 em -8,1%, PASS3 em -6,3%, CPFE3 em -5,5% — e piora
// sozinho a cada dia sem que nada avise, o mesmo padrão que motivou o próprio gerar_tir.py.
//
// `cx` (caixa), `div` (dividendos) e `luc` (lucro) dependem do preço só através do valor de
// mercado (cotação × papéis); `g` não depende de preço. Por isso o gerador passou a exportar
// `pap`, `d0` (dividendo/papel) e `fcfe` (FCO−capex nominal) — os insumos que sobrevivem à
// mudança de cotação — e esta função recompõe as três medidas com a cotação do DOM, espelho
// exato das fórmulas de scripts/gerar_tir.py (mesma constante IPCA, mesmo DDM de 2 estágios).
const _TIR_IPCA = 0.0444;                 // igual a IPCA em scripts/motor_teto.py
const _TIR_GT = _TIR_IPCA + 0.02;         // perpetuidade: IPCA + 2%, igual ao gerador
const _TIR_ANOS_G1 = 10;

// ── POR QUE A TIR REAL DEIXOU DE ORDENAR A FILA (13/09/2026) ────────────────────────────
// Ela ordenava desde a seção 24 sem nunca ter sido testada contra retorno futuro — herdou o
// lugar da Nota 0-100 por ser melhor construída, não por ter medido melhor.
// `scripts/backtest_ranking.py` mediu, nos setores defensivos:
//     L/P puro              +20,3 p.p. · 5 de 5 anos · t +2,52
//     TIR real (ey + g)     +11,4 p.p. · 3 de 5 anos · t +1,04
//     `g` isolado            +8,3 p.p. · 2 de 5 anos
// Somar `g` ao earnings yield PIORA o spread em 8,9 p.p. — o componente que a TIR acrescenta
// não tem sinal próprio nesses setores. A TIR continua na tabela: ela responde "quanto rende
// acima da NTN-B", pergunta diferente de "qual está mais barata". Só deixou de ordenar.
// ── SCORE COMPOSTO DE VALOR + QUALIDADE (13/09/2026) ────────────────────────────────────
// SUBSTITUIU o critério único por grupo (L/P nas defensivas, DY nas demais) que durou um dia.
// O que derrubou aquele: `backtest_metricas.py` mediu DY com corte na MEDIANA e deu p=0,62
// nos setores defensivos — spread NEGATIVO. O resultado anterior, favorável ao DY, vinha de
// corte em TERCIS. Sinal que muda de veredicto conforme você corta em tercis ou em metades
// não é sinal; é ruído com sorte de amostragem. DY saiu de régua de barateza e voltou a ser
// o que sempre foi: medida de RENDA.
//
// POR QUE COMPOSTO, e não a melhor métrica isolada:
// cada múltiplo tem um jeito próprio de ser enganado — lucro por contabilidade, patrimônio
// por reavaliação, EBITDA por capex escondido, receita por margem que não existe. Quatro
// medindo a mesma coisa por caminhos diferentes cancelam parte do erro individual. O teste
// de conjuntos (`backtest_conjunto.py`) confirmou: o conjunto de 3-4 bateu qualquer métrica
// sozinha, e — contraintuitivo — o conjunto de 10 foi o PIOR de todos (p=0,36), porque
// indicador ruim contamina a média. O ponto ideal é poucos e bons.
//
// ⚠️ OS PESOS SÃO PREMISSA, NÃO RESULTADO. 70% valor / 30% qualidade não sai de calibração:
// com 5 transições anuais não há amostra para calibrar peso nenhum, e fingir que há seria
// exatamente o superajuste que o teste de permutação existe para denunciar. É juízo
// declarado, na mesma prateleira do juro real normalizado de 5,5% (seção 25.3).
const RANK_PESO_VALOR = 0.70;
const RANK_PESO_QUALIDADE = 0.30;

// Percentil dentro do grupo de motor. Comparar P/L de banco com P/L de software não diz nada
// sobre qual está barata — múltiplo só é comparável dentro de negócios parecidos. Grupo com
// menos de 4 empresas não forma percentil (com 2 elementos o percentil é sempre 0 ou 1), e aí
// cai para o universo inteiro, que é pior mas não é ruído.
const RANK_MIN_GRUPO = 4;

function _rankPercentis(linhas, chave) {
  // Devolve Map ticker → percentil (0 = pior, 1 = melhor) entre quem TEM o dado.
  const com = linhas.filter(l => l[chave] != null && isFinite(l[chave]));
  const out = new Map();
  if (com.length < 2) return out;
  const ord = [...com].sort((a, b) => a[chave] - b[chave]);
  ord.forEach((l, i) => out.set(l.ticker, i / (ord.length - 1)));
  return out;
}

const RANK_VALOR = ['ey', 'recPreco', 'ebitEv', 'vpPreco'];
const RANK_QUALIDADE = ['roe', 'mgBruta'];

function _calcularScores(linhas) {
  // Agrupa por motor; grupo pequeno demais usa o universo inteiro como referência.
  const porGrupo = new Map();
  linhas.forEach(l => {
    const g = l.seg || '—';
    if (!porGrupo.has(g)) porGrupo.set(g, []);
    porGrupo.get(g).push(l);
  });
  linhas.forEach(l => {
    const grupo = porGrupo.get(l.seg || '—') || [];
    const ref = grupo.length >= RANK_MIN_GRUPO ? grupo : linhas;
    l.rankRef = grupo.length >= RANK_MIN_GRUPO ? (l.seg || '—') : 'todos';
    const pct = (chaves) => {
      const vs = [];
      chaves.forEach(c => {
        const p = _rankPercentis(ref, c).get(l.ticker);
        if (p != null) vs.push(p);
      });
      return vs.length ? vs.reduce((a, b) => a + b, 0) / vs.length : null;
    };
    const pv = pct(RANK_VALOR);
    const pq = pct(RANK_QUALIDADE);
    l.pctValor = pv;
    l.pctQualidade = pq;
    // Sem nenhuma métrica de valor a linha não entra na fila — não dá para ordenar por
    // barateza quem não tem nenhuma medida de barateza. Sem qualidade, o valor responde
    // sozinho, em vez de a linha sumir.
    l.score = pv == null ? null
      : (pq == null ? pv : RANK_PESO_VALOR * pv + RANK_PESO_QUALIDADE * pq);
  });
}

function _tirReal(nom) {
  return ((1 + nom) / (1 + _TIR_IPCA) - 1) * 100;
}

// Mesmo binary search de tir_ddm() em scripts/gerar_tir.py: TIR que iguala o preço ao fluxo
// de dividendos (10 anos a g, depois perpetuidade a gt).
function _tirDdm(preco, d0, g1, gt, anos) {
  if (!preco || preco <= 0 || !d0 || d0 <= 0) return null;
  const vp = r => {
    if (r <= gt) return Infinity;
    let s = 0, d = d0;
    for (let i = 0; i < anos; i++) { d *= (1 + g1); s += d / Math.pow(1 + r, i) / (1 + r); }
    return s + (d * (1 + gt) / (r - gt)) / Math.pow(1 + r, anos);
  };
  let lo = gt + 1e-4, hi = 3.0;
  if (vp(hi) > preco) return null;
  for (let i = 0; i < 200; i++) {
    const mid = (lo + hi) / 2;
    if (vp(mid) > preco) lo = mid; else hi = mid;
  }
  return (lo + hi) / 2;
}

// Recompõe cx/div/luc/med/lo/hi com a cotação ao vivo da linha. Devolve o objeto do seed
// (TIR_SEED) com esses campos substituídos — g, payout, lucroNorm, motor, fonte etc. não
// dependem de preço e ficam como vieram. Cai para os valores estáticos do seed só quando a
// linha ainda não tem cotação (primeira renderização, antes do preço carregar).
function _tirAoVivo(T, cotacao) {
  if (!T) return null;
  if (!(cotacao > 0) || T.pap == null) return T;
  const mcap = cotacao * T.pap;
  if (!(mcap > 0)) return T;
  const g = T.g / 100;

  let cx = null;
  if (T.fcfe != null && T.fcfe > 0) cx = _tirReal(T.fcfe / mcap);

  let luc = null;
  if (T.lucroNorm != null) luc = _tirReal(T.lucroNorm / mcap + g);

  let div = null;
  if (T.d0 != null && T.d0 > 0) {
    const r = _tirDdm(cotacao, T.d0, g, _TIR_GT, _TIR_ANOS_G1);
    if (r != null) div = _tirReal(r);
  }

  const ms = [cx, div, luc].filter(v => v != null);
  if (!ms.length) return T;
  ms.sort((a, b) => a - b);
  const mid = ms.length >> 1;
  const med = ms.length % 2 ? ms[mid] : (ms[mid - 1] + ms[mid]) / 2;
  return Object.assign({}, T, {
    med, lo: ms[0], hi: ms[ms.length - 1], cx, div, luc,
    amp: ms[ms.length - 1] - ms[0], _aoVivo: true, _cotacaoUsada: cotacao,
  });
}
function _decCorTir(v) {
  if (v == null) return '#9ca3af';
  if (v >= TIR_NTNB) return '#0a5c35';          // bate a NTN-B
  if (v >= 0) return '#7a5c00';                 // positivo, mas perde da renda fixa
  return '#9c1c1c';
}
// A faixa inteira acima da barra = ganha da renda fixa em QUALQUER das três medidas.
// A faixa cruzando a barra = depende de qual medida acertar: é pedido de análise, não veredicto.
function _decCorFaixa(T) {
  if (!T || T.lo == null) return '#9ca3af';
  if (T.lo >= TIR_NTNB) return '#0a5c35';
  if (T.hi < TIR_NTNB) return '#9c1c1c';
  return '#7a5c00';
}

// Financeiras: dív. líq./EBITDA não se aplica (o passivo É a matéria-prima do negócio).
// Nesses casos o critério de alavancagem sai do denominador em vez de contar como falha.
const DEC_SEG_FINANCEIRO = ['Bancos', 'Bancos digitais', 'Seguros', 'Resseguros', 'Holding'];

function _decEhFinanceira(row) {
  return DEC_SEG_FINANCEIRO.includes(row.dataset.segmento || '');
}

function _decNum(txt) {
  if (!txt) return NaN;
  const t = String(txt).replace(/[^0-9,.\-]/g, '').replace(/\./g, '').replace(',', '.');
  return parseFloat(t);
}

// Cotação ao vivo da linha: prioriza o valor exato guardado no dataset (mesmo motivo da
// carteira manual — reler o texto renderizado perde casas decimais e o número derrete a
// cada reload). Cai para o texto da célula quando o dataset ainda não foi preenchido.
function _decCotacao(row) {
  const c = row.querySelector('.cotacao-cell');
  const v = parseFloat((c?.textContent || '').replace(/[^0-9,.]/g, '').replace(',', '.'));
  return v > 0 ? v : NaN;
}

// ── OS QUATRO CRITÉRIOS (+1 referência) ────────────────────────────────────────────────────────────────────
// Cada um devolve {ok, texto, na}. "na" = não se aplica (sai do denominador, não conta falha).
// ══════════════════════════════════════════════════════════════════════════════════════════
// VEREDICTO DERIVADO — era o último campo de opinião escrita à mão (06/09/2026)
// ══════════════════════════════════════════════════════════════════════════════════════════
// `data-veredicto` valia 'compra' | 'aguardar' | 'acima' e vinha DIGITADO em cada linha, de
// análises escritas em datas diferentes. Depois que margem, TIR real e critérios passaram a
// ser todos calculados, ele virou a única opinião solta da tabela — e podia CONTRADIZER as
// colunas sem nada avisar: um 'compra' escrito em agosto ao lado de uma margem de −40%
// calculada hoje.
//
// Agora ele deriva de três coisas que a própria tabela já calcula:
//   🟢 COMPRA    margem ≥ MARGEM_MIN_COMPRA  E  piso da TIR real ≥ NTN-B  E  passa em tudo
//   🟡 AGUARDAR  a faixa da TIR cruza a NTN-B, ou passa nos critérios sem margem suficiente
//   🔴 ACIMA     faixa inteira da TIR abaixo da NTN-B, ou reprova em critério
//
// É deliberadamente EXIGENTE no verde: as três condições juntas. Um número que autoriza
// compra tem que ser difícil de acender.
// ⚠️ 13/09/2026 — A MARGEM MÍNIMA PASSOU A SER EXPLÍCITA. O preço-teto saiu da planilha
// (decisão do usuário: um número de valor por linha, não dois), e com ele saiu a margem que
// ele embutia sem dizer: o teto era o piso da faixa, e a distância dele até o justo variava
// de 4% (KLBN11) a 28% (CLSC4) conforme o múltiplo da empresa tivesse oscilado mais ou menos.
// Exigir `margem ≥ 0` contra o JUSTO seria afrouxar o verde — o justo é maior que o teto era,
// então a mesma cotação passa a mostrar margem maior. Este número devolve a exigência, agora
// como uma linha que se lê, igual para todas as empresas e fácil de mudar.
const MARGEM_MIN_COMPRA = 0.15;

function veredictoDerivado(row, r, T) {
  const justo = parseFloat(row.dataset.precoJusto);
  const cot = _decCotacao(row);
  const mg = (justo > 0 && cot > 0) ? (justo - cot) / justo : null;
  const passaTudo = r.total > 0 && r.passa === r.total;
  const lo = T && T.lo != null ? T.lo : null;
  const hi = T && T.hi != null ? T.hi : null;

  // A régua do amarelo usa a MEDIANA das três medidas, não o topo. Com o topo (`hi`),
  // 23 de 30 caíam em "aguardar" — uma classificação que não classifica nada, porque `hi` é
  // sempre a medida mais otimista das três. A mediana é o consenso, e separa 18 de 12.
  const med = T && T.med != null ? T.med : null;
  if (mg != null && mg >= MARGEM_MIN_COMPRA && med != null && med >= TIR_NTNB && passaTudo) return 'compra';
  if (med != null && med >= TIR_NTNB) return 'aguardar';
  return 'acima';
}

function calcularCriterios(row) {
  const ticker = (row.dataset.ticker || '').replace(/\.SA$/i, '');
  const seed = (typeof histSeedUltimoAno === 'function') ? histSeedUltimoAno(ticker) : null;
  const cot = _decCotacao(row);
  const cells = row.querySelectorAll('td');
  const fin = _decEhFinanceira(row);
  const criterios = [];
  // Valores crus de cada teste, guardados para a NOTA (0-100). Os critérios respondem
  // "passa ou não"; a nota precisa de "por quanto" — o mesmo dado, sem o corte binário.
  const bruto = { premio: null, margem: null, roe: null, alav: null, cresc: null, dyLtm: null };

  // DY REALIZADO, recalculado com a cotação ao vivo. É o insumo do ranking dos grupos não
  // defensivos (ver o score composto no topo) e precisa ser o MESMO conceito que o teste mediu:
  // `dy` do HIST_SEED, que é dividendo pago ÷ preço do fechamento daquele exercício — provento
  // que a empresa JÁ distribuiu, não o DY projetado da coluna 10 (que sai do lucro normalizado
  // e é estimativa). Como o `dy` da base está preso ao preço do data-base, reconstituímos o
  // dividendo por ação em reais e dividimos pela cotação de agora — mesmo padrão de
  // _tirAoVivo() e calcularPrecoTeto(): nada que dependa de preço fica travado no dia da carga.
  if (seed && seed.dy != null && seed.preco > 0 && cot > 0) {
    bruto.dyLtm = ((seed.dy / 100) * seed.preco) / cot * 100;
  }

  // 1 · Earnings yield (L/P) ≥ Selic ────────────────────────────────────────────────────
  // L/P = LPA LTM ÷ cotação ao vivo. NÃO usa o LPA projetado da coluna 7: o teste é sobre o
  // que a empresa já entrega, não sobre o que se espera dela.
  //
  // Qual LPA usar — a ordem importa e já custou um erro:
  //  1º  LPA IMPLÍCITO da base Partnr = preço do fechamento ÷ P/L do mesmo ano. É a opção
  //      preferida por dois motivos: (a) vem da mesma fonte única do resto do projeto e não
  //      envelhece separadamente — o data-lpa-ltm da linha do Radar é curado à mão e pode
  //      ficar defasado (LEVE3 carregava 2,82 quando o LPA TTM da base já era 5,14, um P/L
  //      quase 2x errado); (b) é seguro para UNITS. O campo `lpa` cru do Partnr é POR AÇÃO,
  //      mas KLBN11/SANB11/BPAC11 negociam pacotes de várias ações — dividir preço da unit
  //      por LPA por ação dá P/L errado por um fator inteiro. O `pl` do valuationRatios já
  //      vem na base certa, então o LPA implícito herda essa correção automaticamente.
  //  2º  data-lpa-ltm da linha, quando a base não tem P/L para o ticker.
  const lpaLtm = parseFloat(row.dataset.lpaLtm);
  const lpaImplicito = (seed && seed.pl > 0 && seed.preco > 0) ? seed.preco / seed.pl : null;
  const lpaUso = lpaImplicito != null ? lpaImplicito : (lpaLtm > 0 ? lpaLtm : null);
  let ey = null;
  if (lpaUso > 0 && cot > 0) ey = lpaUso / cot;
  if (ey != null && isFinite(ey)) {
    criterios.push({
      ok: ey >= SELIC,
      texto: `L/P ${(ey * 100).toFixed(1).replace('.', ',')}% ${ey >= SELIC ? '≥' : '<'} Selic ${(SELIC * 100).toFixed(2).replace('.', ',')}%`
    });
  } else {
    criterios.push({ na: true, texto: 'L/P — sem LPA LTM disponível' });
  }

  // 2 · ROE acima do custo de capital ───────────────────────────────────────────────────
  const roe = seed && seed.roe != null ? seed.roe : null;
  bruto.roe = roe;
  if (roe != null) {
    criterios.push({
      ok: roe >= ROE_MINIMO,
      texto: `ROE ${roe.toFixed(1).replace('.', ',')}% ${roe >= ROE_MINIMO ? '≥' : '<'} ${ROE_MINIMO}%`
    });
  } else {
    criterios.push({ na: true, texto: 'ROE — sem dado na base' });
  }

  // 3 · Margem de segurança — REFERÊNCIA, NÃO CRITÉRIO (06/09/2026) ─────────────────────
  // Era o 3º dos cinco testes e REPROVAVA empresa. Rebaixado a informativo por decisão do
  // usuário, com três evidências contra ele:
  //  (a) INSTABILIDADE PRÓPRIA. Medi o efeito de uma troca de motor minha: mediana de 23%
  //      de variação no teto EM UM DIA, SANB11 +98%, 14 de 24 acima de 20% — com o preço
  //      de mercado parado. Número que se move 23% por premissa minha não pode decidir se
  //      a empresa entra na carteira.
  //  (b) DEFEITOS ESTRUTURAIS AINDA APARECENDO. Em dois dias, dois bugs de primeira ordem:
  //      mediana contra tendência (reprovava 9 de 9 financeiras) e mediana contra quebra de
  //      série (SAUD3 dava teto de R$ 3,71 contra cotação de R$ 14,60). Metodologia com bug
  //      de primeira ordem não tem autoridade de veto.
  //  (c) NENHUM TESTE CONTRA RETORNO FUTURO. Os seis motores foram escolhidos por argumento
  //      econômico, não por evidência. O único critério que passou por backtest foi o L/P
  //      vs Selic (nº 1), e com margem modesta: +21,9% contra +19,0% do baseline.
  // O PREÇO JUSTO continua na tabela, na coluna própria, com tooltip de auditoria. Serve para
  // disciplina (número declarado antes de comprar) e para detectar absurdo de dado — foi ele
  // que expôs a incorporação da Bradsaúde. Só não pontua.
  const justo = parseFloat(row.dataset.precoJusto);
  if (justo > 0 && cot > 0) {
    const mg = ((justo - cot) / justo) * 100;
    bruto.margem = mg;
    criterios.push({
      ref: true, na: true,
      texto: `[referência, não pontua] Margem de segurança ${mg >= 0 ? '+' : ''}${mg.toFixed(1).replace('.', ',')}% — cotação R$ ${cot.toFixed(2).replace('.', ',')} vs justo R$ ${justo.toFixed(2).replace('.', ',')}`
    });
  } else {
    criterios.push({ ref: true, na: true, texto: '[referência, não pontua] Margem de segurança — sem preço justo ou cotação' });
  }

  // 4 · Alavancagem sob controle (não se aplica a financeiras) ──────────────────────────
  if (fin) {
    criterios.push({ na: true, texto: 'Dív. líq./EBITDA — não se aplica a instituição financeira' });
  } else {
    const de = seed && seed.divEbitda != null ? seed.divEbitda : null;
    bruto.alav = de;
    if (de != null) {
      criterios.push({
        ok: de < ALAVANCAGEM_MAX,
        texto: `Dív. líq./EBITDA ${de.toFixed(1).replace('.', ',')}x ${de < ALAVANCAGEM_MAX ? '<' : '≥'} ${ALAVANCAGEM_MAX}x`
      });
    } else {
      criterios.push({ na: true, texto: 'Dív. líq./EBITDA — sem dado na base' });
    }
  }

  // 5 · Lucro projetado 2026 não encolhe ────────────────────────────────────────────────
  const l25 = _decNumLucro(cells[4]), l26 = _decNumLucro(cells[5]);
  // Crescimento só é comparável com base positiva: sair de prejuízo para lucro dá um
  // percentual sem significado (base negativa), então nesse caso a nota não usa este eixo.
  if (l25 > 0 && l26 != null) bruto.cresc = (l26 - l25) / l25 * 100;
  if (l25 != null && l26 != null) {
    criterios.push({
      ok: l26 >= l25 && l26 > 0,
      texto: l26 >= l25 && l26 > 0 ? 'Lucro projetado 2026 cresce sobre 2025' : 'Lucro projetado 2026 encolhe ou é negativo'
    });
  } else {
    criterios.push({ na: true, texto: 'Crescimento de lucro — projeção 2026 ausente' });
  }

  const valem = criterios.filter(c => !c.na);
  bruto.premio = ey != null && isFinite(ey) ? (ey - SELIC) * 100 : null;
  return {
    ey, criterios, lpaUso, bruto,
    lpaFonte: lpaImplicito != null ? 'base Partnr (preço ÷ P/L do último exercício)' : 'data-lpa-ltm da linha',
    passa: valem.filter(c => c.ok).length,
    total: valem.length,
    premio: bruto.premio
  };
}

// Os quatro critérios continuam calculados porque a coluna 21 os mostra — mas o motor de
// NOTA 0-100 que ficava aqui foi removido junto com a coluna. O `bruto` sobrevive apenas
// como material das tooltips; se algum dia voltar a ideia de pontuar, leia antes a seção 10
// da METODOLOGIA_ANALISE.md, que registra por que a primeira tentativa não se sustentou.

// Lucro vem como "R$ 1,36 bi" / "R$ 940 mi" / "-R$ 210 mi" — converte para número comparável.
function _decNumLucro(td) {
  if (!td) return null;
  const txt = (td.textContent || '').replace(/ⓘ.*$/, '');
  const m = txt.match(/(-?\s*R\$\s*)?(-?[\d.]+(?:,\d+)?)\s*(bi|mi|mil)?/i);
  if (!m) return null;
  let v = parseFloat(m[2].replace(/\./g, '').replace(',', '.'));
  if (isNaN(v)) return null;
  const u = (m[3] || '').toLowerCase();
  if (u === 'bi') v *= 1e9; else if (u === 'mi') v *= 1e6; else if (u === 'mil') v *= 1e3;
  if (/^-|^\s*-\s*R\$/.test(txt.trim())) v = -Math.abs(v);
  return v;
}

// ── RENDER ────────────────────────────────────────────────────────────────────────────────
function _decCorPremio(p) {
  if (p == null) return '#9ca3af';
  if (p >= 5) return '#0a5c35';   // ganha da Selic com folga
  if (p >= 0) return '#2563eb';   // empata ou ganha pouco
  if (p >= -5) return '#7a5c00';  // perde por pouco
  return '#9c1c1c';               // perde feio
}

function _decCorScore(passa, total) {
  if (!total) return '#9ca3af';
  const r = passa / total;
  if (r >= 0.8) return '#0a5c35';
  if (r >= 0.6) return '#2563eb';
  if (r >= 0.4) return '#7a5c00';
  return '#9c1c1c';
}

function atualizarDecisaoLinha(row) {
  const r = calcularCriterios(row);
  row.dataset.decScore = r.total ? (r.passa / r.total).toFixed(3) : '';
  row.dataset.decPassa = r.passa;
  row.dataset.decTotal = r.total;
  row.dataset.decPremio = r.premio != null ? r.premio.toFixed(2) : '';

  const cells = row.querySelectorAll('td');
  const cPrem = cells[DEC_COL_PREMIO], cScore = cells[DEC_COL_SCORE];
  const cTir = cells[DEC_COL_TIR];

  if (cPrem) {
    const tip = r.ey != null
      ? `Earnings yield (L/P) = LPA LTM R$ ${r.lpaUso.toFixed(2).replace('.', ',')} ÷ cotação = ${(r.ey * 100).toFixed(1).replace('.', ',')}%.&#10;LPA obtido de: ${r.lpaFonte}.&#10;Selic ${(SELIC * 100).toFixed(2).replace('.', ',')}% (Copom ${SELIC_DATA}).&#10;Prêmio = L/P − Selic. Positivo significa que o lucro que a empresa já gera, ao preço de hoje, rende mais que a renda fixa — antes de qualquer crescimento.`
      : 'Sem LPA LTM confiável nesta linha (a base não traz P/L e a linha não tem data-lpa-ltm): o prêmio não pode ser calculado sem inventar lucro.';
    cPrem.innerHTML = r.premio == null
      ? `<span style="color:#9ca3af;">—</span><span class="col-tip" data-tip="${tip}">ⓘ</span>`
      : `<span style="color:${_decCorPremio(r.premio)};font-weight:600;">${r.premio >= 0 ? '+' : ''}${r.premio.toFixed(1).replace('.', ',')} p.p.</span><span class="col-tip" data-tip="${tip}">ⓘ</span>`;
  }

  if (cScore) {
    const lista = r.criterios.map(c =>
      `${c.ref ? '🔵' : (c.na ? '⚪' : (c.ok ? '🟢' : '🔴'))} ${c.texto}`).join('&#10;');
    const tip = `${lista}&#10;&#10;⚪ = critério não se aplica ou falta dado — sai do denominador em vez de contar como reprovação (empresa sem dado não é empresa ruim).&#10;🔵 = referência, fora da pontuação. A margem de segurança saiu dos critérios em 06/09/2026: o preço justo se move por mudança de premissa e nunca foi testado como régua de ordenação. Ele continua na coluna Preço Justo, como disciplina e detector de absurdo — mas não reprova mais empresa nenhuma.`;
    cScore.innerHTML = r.total
      ? `<span style="color:${_decCorScore(r.passa, r.total)};font-weight:700;">${r.passa}/${r.total}</span><span class="col-tip" data-tip="${tip}">ⓘ</span>`
      : `<span style="color:#9ca3af;">—</span><span class="col-tip" data-tip="${tip}">ⓘ</span>`;
  }
  // ── TIR real e convergência (data/tir.data.js) ──────────────────────────────────────
  const T = _tirAoVivo(_tirDe(row), _decCotacao(row));
  // VEREDICTO: derivado das colunas, sobrescrevendo o valor escrito à mão. Ver
  // veredictoDerivado() — desde 06/09/2026 nenhuma opinião solta sobrevive na tabela.
  row.dataset.veredicto = veredictoDerivado(row, r, T);
  row.dataset.decTir = T && T.med != null ? T.med.toFixed(2) : '';

  // ── INSUMOS DO SCORE COMPOSTO ────────────────────────────────────────────────────────
  // Todos recalculados com a COTAÇÃO AO VIVO, não travados no preço do data-base — mesma
  // disciplina de _tirAoVivo() e calcularPrecoTeto(). O denominador (lucro, receita, EBIT,
  // patrimônio) não depende de preço; só o numerador muda, então basta dividir de novo.
  const seed = (typeof histSeedUltimoAno === 'function')
    ? histSeedUltimoAno((row.dataset.ticker || '').replace(/\.SA$/i, '')) : null;
  const cot = _decCotacao(row);
  // Papéis: prefere `pap` de data/tir.data.js, que é a contagem já corrigida para units
  // (KLBN11 ÷5, SANB11 ÷2, BPAC11 ÷3). Sem ela, deriva de lucro ÷ LPA como o motor faz.
  const pap = (T && T.pap) ? T.pap
    : (seed && seed.lucrolin && seed.lpa ? Math.abs(seed.lucrolin / seed.lpa) : null);
  const mcap = (pap && cot > 0) ? pap * cot : null;
  row.dataset.decEy = r.ey != null && isFinite(r.ey) ? (r.ey * 100).toFixed(3) : '';
  row.dataset.decRecPreco = (seed && seed.receita && mcap) ? (seed.receita / mcap).toFixed(4) : '';
  // EBIT/EV — EV = valor de mercado + dívida líquida. Dívida líquida negativa (caixa) reduz
  // o EV, que é o comportamento certo: quem tem caixa vale menos do que o preço sugere.
  const ev = (mcap != null && seed && seed.divliq != null) ? mcap + seed.divliq : null;
  row.dataset.decEbitEv = (seed && seed.ebit && ev && ev > 0) ? (seed.ebit / ev).toFixed(4) : '';
  // VP/P ao vivo: o `pvp` da base está preso ao preço do data-base, então reescala pela razão
  // entre aquele preço e a cotação de agora.
  row.dataset.decVpPreco = (seed && seed.pvp > 0 && seed.preco > 0 && cot > 0)
    ? ((1 / seed.pvp) * (seed.preco / cot)).toFixed(4) : '';
  row.dataset.decRoe = (seed && seed.roe != null) ? seed.roe.toFixed(2) : '';
  row.dataset.decMgBruta = (seed && seed.mgBruta != null) ? seed.mgBruta.toFixed(2) : '';
  row.dataset.decDyLtm = r.bruto.dyLtm != null ? r.bruto.dyLtm.toFixed(2) : '';
  // Coluna 23 · crescimento
  const cG = cells[DEC_COL_G];
  if (cG) {
    if (!T || T.g == null) {
      cG.innerHTML = '<span style="color:#9ca3af;">—</span><span class="col-tip" data-tip="Sem crescimento calculável: a empresa não tem série de lucro recorrente nem ROE utilizável na base.">ⓘ</span>';
      row.dataset.decG = '';
    } else {
      const br = T.gBruto != null ? T.gBruto : T.g;
      const cortado = Math.abs(br - T.g) > 0.05;
      const cor = T.g >= 10 ? '#0a5c35' : T.g >= 4 ? '#7a5c00' : '#9c1c1c';
      const extra = cortado
        ? ` <span style="color:#b45309;font-size:11px;">(${br >= 0 ? '+' : ''}${br.toFixed(1).replace('.', ',')}%)</span>` : '';
      const tip = `CRESCIMENTO ANUAL (g) = ${T.g.toFixed(1).replace('.', ',')}%&#10;&#10;`
        + (T.gRoe != null ? `ROE × retenção: ${T.gRoe.toFixed(1).replace('.', ',')}%&#10;` : '')
        + (T.gCagr != null ? `Lucro recorrente (regressão log de 5 anos): ${T.gCagr.toFixed(1).replace('.', ',')}%&#10;` : 'Crescimento do lucro recorrente: não aplicável (financeira, holding ou cíclica — ver metodologia)&#10;')
        + `Regra: usa o MENOR dos dois, com piso 0% e teto 15%.&#10;&#10;`
        + (cortado
            ? `⚠️ VALOR BRUTO ${br.toFixed(1).replace('.', ',')}% — ${br < 0 ? 'a série de lucro recorrente está CAINDO. O piso de zero é premissa do modelo (crescer negativo por 10 anos e depois voltar a crescer com a economia seria incoerente), mas o dado diz outra coisa e está aqui para você ver.' : 'o teto de 15% está cortando. Crescimento acima disso por 10 anos seguidos é raro o suficiente para eu não projetar.'}&#10;&#10;`
            : '')
        + `Este g move as três medidas da TIR real.&#10;⚠️ São 5 pontos de série — estimativa, não medida.`;
      cG.innerHTML = `<span style="color:${cor};font-weight:600;">${T.g >= 0 ? '+' : ''}${T.g.toFixed(1).replace('.', ',')}%</span>${extra}<span class="col-tip" data-tip="${tip}">ⓘ</span>`;
      row.dataset.decG = T.g.toFixed(2);
    }
  }
  row.dataset.decAmp = T && T.amp != null ? T.amp.toFixed(2) : '';
  row.dataset.decLo = T && T.lo != null ? T.lo.toFixed(2) : '';
  if (cTir) {
    if (!T || T.med == null) {
      cTir.innerHTML = '<span style="color:#9ca3af;">—</span><span class="col-tip" data-tip="Sem TIR calculada: o payout está fora de 0-110% (a empresa distribui mais do que lucra) ou falta dado para qualquer uma das três medidas. Preferimos vazio a um número inventado.">ⓘ</span>';
    } else {
      const f = v => v == null ? '—' : (v >= 0 ? '+' : '') + v.toFixed(1).replace('.', ',') + '%';
      const tip = [
        `TIR REAL (acima do IPCA) — mediana de ${[T.cx, T.div, T.luc].filter(v => v != null).length} medidas independentes.`,
        `Barra: NTN-B 2035 = IPCA + ${TIR_NTNB.toFixed(2).replace('.', ',')}%`,
        '',
        `Caixa (FCFE):        ${f(T.cx)}   — (FCO − capex${T.fcfeAjustada ? ' + Δdívida bruta' : ''}) ÷ valor de mercado${T.fcfeAjustada ? '' : ' ⚠️ sem dívida de 2 anos consecutivos — FCFF, não FCFE'}`,
        `Dividendos (DDM):    ${f(T.div)}   — DY futuro ${T.payout.toFixed(0)}% payout mediano, g ${T.g.toFixed(1).replace('.', ',')}%`,
        `Lucro normalizado:   ${f(T.luc)}   — ${T.motor}`,
        '',
        T.amp != null ? `Amplitude ${T.amp.toFixed(1).replace('.', ',')} p.p. — ${T.amp <= 4 ? 'as medidas CONCORDAM, leitura robusta' : T.amp <= 9 ? 'divergência moderada' : 'DIVERGEM MUITO: a leitura depende de qual régua você acredita'}` : 'Só uma medida disponível.',
        `g usado: ${T.g.toFixed(1).replace('.', ',')}% = menor entre CAGR 5a do lucro recorrente (${T.gCagr == null ? 'não existe p/ financeira' : T.gCagr.toFixed(1).replace('.', ',') + '%'}) e ROE × retenção (${T.gRoe.toFixed(1).replace('.', ',')}%), limitado a 15%.`,
        T._aoVivo
          ? `Recalculado com a cotação ao vivo (R$ ${T._cotacaoUsada.toFixed(2).replace('.', ',')}). g, payout e lucro normalizado vêm do motor de ${TIR_DATA_EM}; caixa/dividendos/lucro reagem ao preço a cada atualização.`
          : `Sem cotação ao vivo nesta linha ainda — mostrando o valor do motor de ${TIR_DATA_EM} (preço R$ ${T.precoBase != null ? T.precoBase.toFixed(2).replace('.', ',') : '?'}).`
      ].join('&#10;');
      const n1 = v => (v >= 0 ? '' : '−') + Math.abs(v).toFixed(1).replace('.', ',');
      const veredicto = T.lo >= TIR_NTNB
        ? 'Toda a faixa supera a NTN-B: ganha da renda fixa por qualquer das três medidas.'
        : (T.hi < TIR_NTNB
          ? 'Toda a faixa fica abaixo da NTN-B: perde da renda fixa por qualquer medida.'
          : 'A faixa CRUZA a NTN-B: ganha por uma medida e perde por outra — precisa de análise, a tabela não decide.');
      cTir.innerHTML = `<span style="color:${_decCorFaixa(T)};font-weight:700;font-size:11.5px;">${n1(T.lo)} → ${n1(T.hi)}%</span><span class="col-tip" data-tip="${tip}&#10;&#10;${veredicto}">ⓘ</span>`;
    }
  }
  return r;
}

function atualizarTodasDecisoes() {
  document.querySelectorAll('#tableBody tr[data-ticker]').forEach(atualizarDecisaoLinha);
  if (typeof renderRankingDecisao === 'function') renderRankingDecisao();
}

// ── INJEÇÃO DAS COLUNAS ───────────────────────────────────────────────────────────────────
function initColunasDecisao() {
  const table = document.getElementById('mainTable');
  if (!table || table.dataset.decisaoOk === '1') return;
  table.dataset.decisaoOk = '1';

  const colgroup = table.querySelector('colgroup');
  if (colgroup) {
    colgroup.insertAdjacentHTML('beforeend',
      '<col style="width:95px"><!-- Prêmio Selic --><col style="width:85px"><!-- Critérios --><col style="width:112px"><!-- TIR real (faixa) --><col style="width:118px"><!-- Crescimento g -->');
  }

  const head = table.querySelector('thead tr.col-header');
  if (head) {
    head.insertAdjacentHTML('beforeend', `
      <th data-col="${DEC_COL_PREMIO}" class="sep gh-ret sortable" onclick="sortTable(${DEC_COL_PREMIO})"><div class="th-inner">Prêmio Selic<span class="sort-arrow"></span><span class="col-tag proj">decisão</span></div><span class="col-tip" data-tip="Fonte: Calculado&#10;Earnings yield (LPA LTM ÷ cotação) − Selic ${(SELIC * 100).toFixed(2).replace('.', ',')}%&#10;Positivo = o lucro atual da empresa, ao preço de hoje, rende mais que a renda fixa">ⓘ</span></th>
      <th data-col="${DEC_COL_SCORE}" class="gh-ret sortable" onclick="sortTable(${DEC_COL_SCORE})"><div class="th-inner">Critérios<span class="sort-arrow"></span><span class="col-tag proj">decisão</span></div><span class="col-tip" data-tip="Fonte: Calculado&#10;Quantos dos 4 testes de qualidade+preço a empresa passa (METODOLOGIA_ANALISE.md, seção 9)&#10;&#10;⚠️ A margem de segurança contra o preço justo SAIU da pontuação em 06/09/2026 e aparece como 🔵 referência: o valor justo oscila por mudança de premissa e nunca foi validado como régua de ordenação.&#10;&#10;Passe o mouse no ⓘ de cada linha para ver critério a critério">ⓘ</span></th>
      <th data-col="${DEC_COL_TIR}" class="gh-ret sortable" onclick="sortTable(${DEC_COL_TIR})"><div class="th-inner">TIR real<span class="sort-arrow"></span><span class="col-tag proj">decisão</span></div><span class="col-tip" data-tip="Fonte: Análise própria sobre MCP Partnr&#10;FAIXA de retorno anual REAL (acima do IPCA) das três medidas: caixa (FCFE), dividendos (DDM) e lucro normalizado&#10;&#10;Barra: NTN-B 2035 = IPCA + ${TIR_NTNB.toFixed(2).replace('.', ',')}%&#10;VERDE = faixa inteira acima da barra&#10;ÂMBAR = a faixa cruza a barra: depende de qual medida acertar&#10;VERMELHO = faixa inteira abaixo&#10;&#10;A largura da faixa É a informação: estreita = as três réguas concordam; larga = a leitura depende de qual você acredita&#10;Substituiu a Nota 0-100, que o backtest do projeto não validou&#10;&#10;⚠️ DEIXOU DE ORDENAR A FILA em 13/09/2026. Quando foi finalmente testada contra retorno futuro (scripts/backtest_ranking.py), ordenou pior que o L/P puro nos setores defensivos: spread barato−caro de +11,4 p.p. acertando 3 de 5 anos, contra +20,3 p.p. e 5 de 5 do L/P. O componente que ela acrescenta ao earnings yield (o crescimento g) não teve sinal próprio — somá-lo PIOROU o spread em 8,9 p.p. A TIR continua aqui porque responde a outra pergunta: quanto rende acima da NTN-B, não qual está mais barata&#10;Caixa/dividendos/lucro recalculam com a cotação ao vivo a cada atualização (motor de ${TIR_DATA_EM}; g/payout/lucro normalizado fixos até a próxima regeração)">ⓘ</span></th>
      <th data-col="${DEC_COL_G}" class="gh-ret sortable" onclick="sortTable(${DEC_COL_G})"><div class="th-inner">Crescimento<span class="sort-arrow"></span><span class="col-tag proj">decisão</span></div><span class="col-tip" data-tip="Fonte: Análise própria sobre MCP Partnr&#10;g = crescimento anual usado na TIR real&#10;&#10;É o MENOR entre:&#10;· ROE × retenção — quanto a empresa cresce com o lucro que NÃO distribui&#10;· crescimento do lucro recorrente, por REGRESSÃO LOG sobre a série (não CAGR de pontas: o CAGR usa só 2 pontos e a CLSC4 saía com −0,7% num período em que a receita subiu 10% e o lucro contábil 57%)&#10;&#10;Piso 0% e teto 15%. Quando o valor bruto difere, ele aparece entre parênteses — é aí que está a informação que o corte esconde:&#10;· BBSE3 mostra 15% e o dado diz 23,1%&#10;· PASS3 mostra 0% e o dado diz −16,4% (encolhendo)&#10;· SHUL4 mostra 0% e o dado diz −3,2% (estagnada)&#10;&#10;⚠️ São 5 pontos de série. É estimativa, não medida.">ⓘ</span></th>`);
  }

  document.querySelectorAll('#tableBody tr[data-ticker]').forEach(row => {
    row.insertAdjacentHTML('beforeend',
      '<td class="sep dec-premio-cell"></td><td class="dec-score-cell"></td><td class="dec-tir-cell"></td><td class="dec-g-cell"></td>');
  });

  atualizarTodasDecisoes();
}

// ── RANKING NO TOPO DA ABA ────────────────────────────────────────────────────────────────
// A coluna resolve "esta empresa passa?". O ranking resolve "por onde começo?" — que era a
// pergunta do usuário. Ordena por critérios aprovados e, no empate, por prêmio sobre a Selic.
function renderRankingDecisao() {
  const wrap = document.getElementById('rankingDecisao');
  if (!wrap) return;

  const linhas = Array.from(document.querySelectorAll('#tableBody tr[data-ticker]')).map(row => ({
    ticker: (row.dataset.ticker || '').replace(/\.SA$/i, ''),
    empresa: (row.querySelector('.empresa-name')?.textContent || '').trim(),
    seg: row.dataset.segmento || '',
    passa: parseInt(row.dataset.decPassa) || 0,
    total: parseInt(row.dataset.decTotal) || 0,
    premio: row.dataset.decPremio === '' ? null : parseFloat(row.dataset.decPremio),
    ratio: parseFloat(row.dataset.decScore) || 0,
    tir: row.dataset.decTir === '' ? null : parseFloat(row.dataset.decTir),
    amp: row.dataset.decAmp === '' ? null : parseFloat(row.dataset.decAmp),
    lo: row.dataset.decLo === '' ? null : parseFloat(row.dataset.decLo),
    ey: row.dataset.decEy === '' ? null : parseFloat(row.dataset.decEy),
    recPreco: row.dataset.decRecPreco === '' ? null : parseFloat(row.dataset.decRecPreco),
    ebitEv: row.dataset.decEbitEv === '' ? null : parseFloat(row.dataset.decEbitEv),
    vpPreco: row.dataset.decVpPreco === '' ? null : parseFloat(row.dataset.decVpPreco),
    roe: row.dataset.decRoe === '' ? null : parseFloat(row.dataset.decRoe),
    mgBruta: row.dataset.decMgBruta === '' ? null : parseFloat(row.dataset.decMgBruta),
    dyLtm: row.dataset.decDyLtm === '' ? null : parseFloat(row.dataset.decDyLtm)
  })).filter(l => l.total > 0);

  _calcularScores(linhas);

  // Ordenação: SCORE COMPOSTO de valor + qualidade, por grupo de motor (ver _calcularScores).
  //
  // Histórico curto e instrutivo desta linha: até 12/09 ordenava pela TIR real, que nunca
  // tinha sido testada; em 13/09 passou ao yield validado por grupo (L/P nas defensivas, DY
  // nas demais); e no mesmo dia o DY caiu, porque o teste por MEDIANA o reprovou (p=0,62)
  // depois de o teste por TERCIS o ter aprovado. Métrica isolada é frágil a como você corta
  // a amostra — o composto é justamente a resposta a isso.
  //
  // Quem não tem NENHUMA métrica de valor cai para o fim: não dá para ordenar por barateza
  // quem não tem medida de barateza. Desempate: critérios de qualidade, depois convergência
  // das medidas da TIR.
  linhas.sort((a, b) =>
    ((b.score != null) - (a.score != null)) ||
    ((b.score ?? -99) - (a.score ?? -99)) ||
    (b.ratio - a.ratio) ||
    ((a.amp ?? 99) - (b.amp ?? 99)));

  const top = linhas.slice(0, 8);
  const comPremio = linhas.filter(l => l.premio != null && l.premio >= 0).length;
  const batemNtnb = linhas.filter(l => l.tir != null && l.tir >= TIR_NTNB).length;
  const comTir = linhas.filter(l => l.tir != null).length;

  wrap.innerHTML = `
    <div style="display:flex;flex-wrap:wrap;gap:8px;align-items:baseline;margin-bottom:8px;">
      <strong style="font-size:13px;">🎯 Por onde começar</strong>
      <span style="font-size:11px;color:#666;">ordenado por <b>score composto</b> — 70% valor (L/P · Receita/Preço · EBIT/EV · VP/P) + 30% qualidade (ROE · margem bruta), comparado dentro do grupo</span>
    </div>
    <div style="display:flex;flex-wrap:wrap;gap:6px;">
      ${top.map((l, i) => `
        <div style="border:1px solid #e3e3e3;border-radius:8px;padding:6px 10px;background:#fff;min-width:132px;">
          <div style="font-size:10px;color:#999;">${i + 1}º · ${l.seg}</div>
          <div style="font-weight:600;font-size:12px;">${l.ticker}</div>
          <div style="font-size:13px;color:#0a5c35;font-weight:700;">${l.score == null ? '—' : 'score ' + (l.score * 100).toFixed(0)}</div>
          <div style="font-size:10px;color:#888;">${l.ey == null ? '' : 'L/P ' + l.ey.toFixed(1).replace('.', ',') + '%'}${l.pctQualidade != null ? ' · qual. ' + (l.pctQualidade * 100).toFixed(0) : ''}</div>
          <div style="font-size:10.5px;color:${l.tir != null && l.tir >= TIR_NTNB ? '#0a5c35' : '#888'};">${l.tir == null ? 'TIR —' : 'TIR ' + l.tir.toFixed(1).replace('.', ',') + '%'}</div>
          <div style="font-size:10.5px;color:#888;">${l.passa}/${l.total} critérios</div>
        </div>`).join('')}
    </div>
    <div style="font-size:11px;color:#666;margin-top:8px;line-height:1.6;">
      O <b>score</b> é o percentil médio de quatro réguas de preço e duas de qualidade, comparado <b>dentro do grupo de motor</b> — P/L de banco
      não se compara com P/L de telecom. Composto e não métrica única porque cada múltiplo tem um jeito próprio de ser enganado (lucro por contabilidade,
      patrimônio por reavaliação, EBITDA por capex escondido); quatro medindo o mesmo por caminhos diferentes cancelam parte do erro individual.
      <b>Os pesos 70/30 são premissa declarada, não calibração</b> — com 5 anos de amostra não há como calibrar peso, e fingir que há seria o superajuste
      que o teste de permutação existe para denunciar.
      <br>
      <strong>${batemNtnb}</strong> de <strong>${comTir}</strong> ativos com TIR calculada superam a NTN-B (IPCA + ${TIR_NTNB.toFixed(2).replace('.', ',')}%) — a TIR continua na tabela
      respondendo "quanto rende acima da renda fixa", que é pergunta diferente de "qual está mais barata". Ranking alto não é ordem de compra: é a fila para ler o relatório.
    </div>`;
}

// ── FILTRO ────────────────────────────────────────────────────────────────────────────────
let filterCriterios = false;
function toggleCriteriosFilter() {
  filterCriterios = !filterCriterios;
  const btn = document.getElementById('btnCriterios');
  if (btn) {
    btn.classList.toggle('cart-active', filterCriterios);
    btn.textContent = filterCriterios ? '✅ Passa no filtro ✓' : '✅ Passa no filtro';
  }
  applyFilters();
}

// applyFilters() vive em js/radar.js e não conhece este critério. Em vez de duplicar a função
// (que ia sair de sincronia na primeira alteração), embrulhamos: roda a original e depois
// esconde o que não passa no score. Mesmo padrão do patch de atualizarCotacoes em main.js.
(function patchFiltros() {
  const orig = window.applyFilters;
  if (typeof orig !== 'function') return;
  window.applyFilters = function () {
    orig();
    if (!filterCriterios) return;
    let cT = 0, cC = 0, cA = 0, cCart = 0;
    document.querySelectorAll('#tableBody tr[data-ticker]').forEach(row => {
      if (row.classList.contains('hidden')) return;
      const ratio = parseFloat(row.dataset.decScore) || 0;
      const premio = row.dataset.decPremio === '' ? null : parseFloat(row.dataset.decPremio);
      // Passa no filtro = aprova em pelo menos 3/4 dos critérios aplicáveis E não perde da Selic.
      const ok = ratio >= 0.75 && premio != null && premio >= 0;
      row.classList.toggle('hidden', !ok);
      if (ok) {
        cT++;
        if (row.dataset.veredicto === 'compra') cC++;
        if (row.dataset.veredicto === 'aguardar') cA++;
        if (row.dataset.carteira === 'true') cCart++;
      }
    });
    const set = (id, v) => { const e = document.getElementById(id); if (e) e.textContent = v; };
    set('cnt-compra', cC); set('cnt-aguardar', cA); set('cnt-carteira', cCart); set('cnt-total', cT);
  };
})();

// Recalcula tudo depois de cada atualização de cotação — o prêmio sobre a Selic e a margem
// de segurança mudam com o preço, então deixá-los estáticos seria mentir por omissão.
(function patchCotacoesDecisao() {
  const orig = window.atualizarCotacoes;
  if (typeof orig !== 'function') return;
  window.atualizarCotacoes = async function () {
    await orig();
    atualizarTodasDecisoes();
  };
})();

initColunasDecisao();

// ── SYNC DO CABEÇALHO STICKY COM A ALTURA DA BARRA DE CONTROLES — 07/09/2026 ─────────────
// .table-wrap deixou de ter overflow/max-height próprios (pedido do usuário: só a barra de
// rolagem da PÁGINA, não uma da tabela dentro de outra da página). Isso move o "container de
// rolagem" do thead sticky de .table-wrap para a página inteira — e o thead precisa parar
// exatamente sob .nav + .radar-controls, não sob a viewport inteira. A .radar-controls quebra
// linha em telas estreitas (flex-wrap), então a altura dela não é uma constante: mede-se e
// escreve-se em --radar-controls-h no :root, que #mainTable thead (css/styles.css) já lê.
// .nav e .radar-controls são position:fixed (ver o porquê em css/styles.css, na .nav): saem do
// fluxo, então o conteúdo abaixo precisa de um respiro EXATO do tamanho delas. As duas mudam de
// altura sozinhas — a nav encolhe no mobile, os controles quebram em duas ou três linhas conforme
// a largura — e não dá para fixar os números no CSS sem sobrar buraco ou faltar espaço. Mede as
// duas aqui e escreve nas variáveis que o CSS consome.
function _syncTheadSticky() {
  const nav = document.querySelector('.nav');
  const controls = document.querySelector('.radar-controls');
  const raiz = document.documentElement;
  if (nav) {
    const h = nav.getBoundingClientRect().height;
    if (h > 0) raiz.style.setProperty('--nav-h', h + 'px');
  }
  if (!controls) return;
  const hc = controls.getBoundingClientRect().height;
  // Aba não-Radar deixa os controles em display:none (altura 0). Guardar esse 0 colapsaria o
  // padding e, na volta para o Radar, a tabela subiria por baixo da barra por um quadro.
  if (hc > 0) raiz.style.setProperty('--radar-controls-h', hc + 'px');
}
_syncTheadSticky();
window.addEventListener('resize', _syncTheadSticky);
// Trocar de aba remonta a barra (os controles só existem visíveis no Radar) — remede depois que
// o navegador aplicou o display novo.
document.addEventListener('click', (e) => {
  if (e.target.closest('.nav-tab, .nav-tabs a, [data-page]')) requestAnimationFrame(_syncTheadSticky);
}, true);
// A barra também muda de altura quando o usuário alterna carteira/filtros (mesmos controles,
// conteúdo condicional) — reobserva no próprio elemento em vez de só no resize da janela.
(function () {
  const controls = document.querySelector('.radar-controls');
  if (!controls || typeof ResizeObserver === 'undefined') return;
  new ResizeObserver(_syncTheadSticky).observe(controls);
})();
