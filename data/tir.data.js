// ══════════════════════════════════════════════════════════════════════════════════════════
// TIR REAL — faixa de três medidas independentes   ·   GERADO por scripts/gerar_tir.py · 06/09/2026
// ══════════════════════════════════════════════════════════════════════════════════════════
// SUBSTITUI a "Nota 0-100". Motivo: o backtest sobre os dados deste projeto (130 obs.,
// 2021-2026) não achou poder discriminante nos 5 critérios, e os eixos de qualidade (ROE,
// alavancagem) PIORARAM o resultado. Ver METODOLOGIA_ANALISE.md seção 10.
//
// A COLUNA MOSTRA A FAIXA (lo → hi), NÃO A MEDIANA. Isto é correção de um erro de desenho:
// exibir só a mediana obrigava a cruzar com uma segunda coluna de convergência para não ler
// errado — e um número que precisa de outro para não enganar está mal apresentado. A faixa
// carrega as duas informações de uma vez: onde está o retorno E quanto as medidas discordam.
//   BRSR6 "16,9%"  parece resposta.
//   BRSR6 "10,2 → 23,5%"  mostra que não é: pode ser ótimo ou medíocre, vá investigar.
//
// As três medidas, todas em RETORNO REAL comparável com a NTN-B:
//   cx   CAIXA        (FCO − capex) ÷ valor de mercado. Imune a lucro contábil. 11 de 25.
//   div  DIVIDENDOS   DDM 2 estágios: 10 anos a g, depois perpetuidade a IPCA+2%.
//                     DY futuro = lucro normalizado × payout MEDIANO de 5 anos.
//   luc  LUCRO        lucro normalizado ÷ valor de mercado + g.
//
// ⚠️ FISHER: retorno real é DIVISÃO, não subtração — real = (1+nominal)/(1+IPCA) − 1.
// A versão anterior subtraía, o que superestimava em ~0,8 p.p. na PETR4 e mais nos retornos
// altos. Não mudava a ordem do ranking, mas era erro de método.
//
// `g` = MENOR entre CAGR 5a do lucro recorrente e ROE × retenção, limitado a 15%.
// ⚠️ Financeiras NÃO têm CAGR de lucro recorrente na base (testado em ITUB e BBSE): nelas o g
// vem só de ROE × retenção, e o teto de 15% ainda é premissa arbitrária.
//
// Patrimônio das financeiras vem do BALANÇO (CONTROLLING_SHAREHOLDERS_EQUITY), não de
// valor de mercado ÷ P/VP — o P/VP do Partnr erra em units (BPAC11: 6,96x reportado contra
// 2,70x real, porque divide preço da unit por valor patrimonial por ação).
// ⚠️ REGERADO EM 06/09/2026. Este arquivo era um SNAPSHOT ESTÁTICO escrito à mão em
// 05/09, antes das correções de payout daquele dia — e por isso ficou com premissas de
// duas versões atrás sem que nada quebrasse. Doze empresas divergiam mais de 5 p.p. do
// que o motor calcula (AXIA3 43%→93%, SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo
// estático não briga com o motor: ele envelhece em silêncio, que é o modo mais
// perigoso da falha. Agora é gerado, e o payout vem de payout_final() — a mesma função
// que alimenta o preço-teto e a coluna de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
// ⚠️ REGERADO EM 06/09/2026. Este arquivo era um SNAPSHOT ESTÁTICO escrito à mão em
// 05/09, antes das correções de payout daquele dia — e por isso ficou com premissas de
// duas versões atrás sem que nada quebrasse. Doze empresas divergiam mais de 5 p.p. do
// que o motor calcula (AXIA3 43%→93%, SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo
// estático não briga com o motor: ele envelhece em silêncio, que é o modo mais
// perigoso da falha. Agora é gerado, e o payout vem de payout_final() — a mesma função
// que alimenta o preço-teto e a coluna de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
// ⚠️ REGERADO EM 06/09/2026. Este arquivo era um SNAPSHOT ESTÁTICO escrito à mão em
// 05/09, antes das correções de payout daquele dia — e por isso ficou com premissas de
// duas versões atrás sem que nada quebrasse. Doze empresas divergiam mais de 5 p.p. do
// que o motor calcula (AXIA3 43%→93%, SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo
// estático não briga com o motor: ele envelhece em silêncio, que é o modo mais
// perigoso da falha. Agora é gerado, e o payout vem de payout_final() — a mesma função
// que alimenta o preço-teto e a coluna de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
// ⚠️ REGERADO EM 06/09/2026. Este arquivo era um SNAPSHOT ESTÁTICO escrito à mão em
// 05/09, antes das correções de payout daquele dia — e por isso ficou com premissas de
// duas versões atrás sem que nada quebrasse. Doze empresas divergiam mais de 5 p.p. do
// que o motor calcula (AXIA3 43%→93%, SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo
// estático não briga com o motor: ele envelhece em silêncio, que é o modo mais
// perigoso da falha. Agora é gerado, e o payout vem de payout_final() — a mesma função
// que alimenta o preço-teto e a coluna de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
// ⚠️ REGERADO EM 06/09/2026. Este arquivo era um SNAPSHOT ESTÁTICO escrito à mão em
// 05/09, antes das correções de payout daquele dia — e por isso ficou com premissas de
// duas versões atrás sem que nada quebrasse. Doze empresas divergiam mais de 5 p.p. do
// que o motor calcula (AXIA3 43%→93%, SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo
// estático não briga com o motor: ele envelhece em silêncio, que é o modo mais
// perigoso da falha. Agora é gerado, e o payout vem de payout_final() — a mesma função
// que alimenta o preço-teto e a coluna de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
// ⚠️ REGERADO EM 06/09/2026. Este arquivo era um SNAPSHOT ESTÁTICO escrito à mão em
// 05/09, antes das correções de payout daquele dia — e por isso ficou com premissas de
// duas versões atrás sem que nada quebrasse. Doze empresas divergiam mais de 5 p.p. do
// que o motor calcula (AXIA3 43%→93%, SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo
// estático não briga com o motor: ele envelhece em silêncio, que é o modo mais
// perigoso da falha. Agora é gerado, e o payout vem de payout_final() — a mesma função
// que alimenta o preço-teto e a coluna de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
// ⚠️ REGERADO EM 06/09/2026, campos ao-vivo acrescentados 07/09/2026. Este arquivo era
// um SNAPSHOT ESTÁTICO escrito à mão em 05/09, antes das correções de payout daquele
// dia — e por isso ficou com premissas de duas versões atrás sem que nada quebrasse.
// Doze empresas divergiam mais de 5 p.p. do que o motor calcula (AXIA3 43%→93%,
// SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo estático não briga com o motor: ele
// envelhece em silêncio, que é o modo mais perigoso da falha. Agora é gerado, e o
// payout vem de payout_final() — a mesma função que alimenta o preço-teto e a coluna
// de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
//
// ⚠️ `med/lo/hi/cx/div/luc` NESTE ARQUIVO SÃO CALCULADOS COM O PREÇO DO DATA-BASE
// (`precoBase`), NÃO com a cotação ao vivo — igual ao preço-teto ANTES de recalcular
// em cada atualização de página. Por isso `pap`, `d0` e `fcfe` também estão aqui: são
// os insumos que não dependem de preço, e js/decisao.js usa `_tirAoVivo()` para
// recompor cx/div/luc com a cotação do DOM a cada render — os três campos estáticos
// ficam só como fallback caso a cotação da linha ainda não tenha carregado.
// ⚠️ REGERADO EM 06/09/2026, campos ao-vivo acrescentados 07/09/2026. Este arquivo era
// um SNAPSHOT ESTÁTICO escrito à mão em 05/09, antes das correções de payout daquele
// dia — e por isso ficou com premissas de duas versões atrás sem que nada quebrasse.
// Doze empresas divergiam mais de 5 p.p. do que o motor calcula (AXIA3 43%→93%,
// SBSP3 19%→50%, LEVE3 57%→86%). Um arquivo estático não briga com o motor: ele
// envelhece em silêncio, que é o modo mais perigoso da falha. Agora é gerado, e o
// payout vem de payout_final() — a mesma função que alimenta o preço-teto e a coluna
// de payout do Radar.
//
// `cx` e `gCagr` são HERDADOS do snapshot: dependem de FCO, capex e lucro recorrente,
// campos que não estão no HIST_SEED. Nenhum dos dois depende de payout, então a
// correção não os afeta. O campo `fonte` diz de onde veio o payout de cada linha.
//
// ⚠️ `med/lo/hi/cx/div/luc` NESTE ARQUIVO SÃO CALCULADOS COM O PREÇO DO DATA-BASE
// (`precoBase`), NÃO com a cotação ao vivo — igual ao preço-teto ANTES de recalcular
// em cada atualização de página. Por isso `pap`, `d0` e `fcfe` também estão aqui: são
// os insumos que não dependem de preço, e js/decisao.js usa `_tirAoVivo()` para
// recompor cx/div/luc com a cotação do DOM a cada render — os três campos estáticos
// ficam só como fallback caso a cotação da linha ainda não tenha carregado.
const TIR_DATA_EM = '06/09/2026';
const TIR_NTNB = 7.70;   // NTN-B 2035 (IPCA + %). Atualizar junto com os dados.
const TIR_SEED = {
  FIQE3:    { med: 19.19, lo:  8.48, hi: 33.33, cx: 33.33, div:  8.48, luc: 19.19, amp: 24.85, g: 11.27, gBruto:  11.27, gRoe: 11.27, gCagr: 25.57, payout: 34.3, lucroNorm:229282836, motor:'receita × margem líquida mediana', seg:'IND', fonte:'realizado', pap:363679167, d0:0.2164, fcfe:680831000, fcfeAjustada:true, precoBase:4.77 },
  BRSR6:    { med: 18.71, lo: 12.25, hi: 25.16, cx:  null, div: 12.25, luc: 25.16, amp: 12.91, g:  8.56, gBruto:   8.56, gRoe:  8.56, gCagr:  null, payout: 40.0, lucroNorm:1358314878, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'piso', pap:408865310, d0:1.3289, fcfe:null, fcfeAjustada:false, precoBase:14.99 },
  PETR4:    { med: 18.10, lo:  9.85, hi: 22.35, cx:  9.85, div: 18.10, luc: 22.35, amp: 12.50, g:  6.95, gBruto:   6.95, gRoe:  6.95, gCagr:  null, payout: 74.2, lucroNorm:129992841000, motor:'receita × margem líquida mediana', seg:'IND', fonte:'outra_base', pap:12966623476, d0:7.4405, fcfe:91894000000, fcfeAjustada:true, precoBase:48.13 },
  BBSE3:    { med: 17.62, lo: 14.85, hi: 20.39, cx:  null, div: 14.85, luc: 20.39, amp:  5.54, g: 15.00, gBruto:  23.12, gRoe: 23.12, gCagr:  null, payout: 70.8, lucroNorm:8693797041, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'estatutario', pap:2000089283, d0:3.0758, fcfe:null, fcfeAjustada:false, precoBase:40.48 },
  BMEB4:    { med: 15.79, lo:  8.79, hi: 22.80, cx:  null, div:  8.79, luc: 22.80, amp: 14.01, g: 15.00, gBruto:  19.61, gRoe: 19.61, gCagr:  null, payout: 27.5, lucroNorm:841830215, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'realizado', pap:104930497, d0:2.2074, fcfe:null, fcfeAjustada:false, precoBase:60.55 },
  PSSA3:    { med: 13.59, lo:  9.18, hi: 18.00, cx:  null, div:  9.18, luc: 18.00, amp:  8.81, g: 12.99, gBruto:  12.99, gRoe: 12.99, gCagr:  null, payout: 43.8, lucroNorm:3360915162, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'realizado', pap:646537442, d0:2.2750, fcfe:null, fcfeAjustada:false, precoBase:50.74 },
  ITSA4:    { med: 13.25, lo: 10.12, hi: 16.38, cx:  null, div: 10.12, luc: 16.38, amp:  6.26, g:  8.50, gBruto:   8.50, gRoe:  8.50, gCagr:  null, payout: 53.6, lucroNorm:19080998282, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'realizado', pap:10690740741, d0:0.9570, fcfe:null, fcfeAjustada:false, precoBase:13.68 },
  BRAP4:    { med: 12.92, lo: 10.45, hi: 15.39, cx:  null, div: 10.45, luc: 15.39, amp:  4.93, g:  2.85, gBruto:   2.85, gRoe:  2.85, gCagr:  null, payout: 60.2, lucroNorm:1594332571, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'realizado', pap:393341325, d0:2.4411, fcfe:null, fcfeAjustada:false, precoBase:22.95 },
  RANI3:    { med: 12.05, lo:  9.55, hi: 20.47, cx:  9.55, div: 12.05, luc: 20.47, amp: 10.92, g:  8.40, gBruto:   8.40, gRoe:  8.40, gCagr:  null, payout: 50.4, lucroNorm:316421836, motor:'receita × margem líquida mediana', seg:'IND', fonte:'realizado', pap:239712495, d0:0.6648, fcfe:261833000, fcfeAjustada:true, precoBase:7.58 },
  LEVE3:    { med: 11.92, lo: 10.73, hi: 12.10, cx: 10.73, div: 11.92, luc: 12.10, amp:  1.38, g:  0.26, gBruto:   0.26, gRoe: 10.21, gCagr:  0.26, payout: 85.9, lucroNorm:741336000, motor:'lucro recorrente (campo Partnr)', seg:'IND', fonte:'realizado', pap:135523715, d0:4.6964, fcfe:689393000, fcfeAjustada:true, precoBase:32.52 },
  KLBN11:   { med: 11.86, lo:  9.18, hi: 14.54, cx:  null, div:  9.18, luc: 14.54, amp:  5.36, g:  5.75, gBruto:   5.75, gRoe:  5.75, gCagr:  null, payout: 53.9, lucroNorm:3268773520, motor:'receita × margem líquida mediana', seg:'IND', fonte:'outra_base', pap:1214609111, d0:1.4504, fcfe:-1012710000, fcfeAjustada:true, precoBase:19.40 },
  SBSP3:    { med: 11.64, lo:  6.25, hi: 13.61, cx: 13.61, div:  6.25, luc: 11.64, amp:  7.36, g: 10.32, gBruto:  10.32, gRoe: 10.32, gCagr:  null, payout: 50.0, lucroNorm:5783821556, motor:'receita × margem líquida mediana', seg:'IND', fonte:'teto', pap:3518545415, d0:0.8219, fcfe:17187887000, fcfeAjustada:true, precoBase:26.19 },
  ITUB3:    { med: 11.48, lo:  8.27, hi: 14.69, cx:  null, div:  8.27, luc: 14.69, amp:  6.42, g: 10.52, gBruto:  10.52, gRoe: 10.52, gCagr:  null, payout: 50.0, lucroNorm:39059965264, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'estatutario', pap:9794124882, d0:1.9929, fcfe:null, fcfeAjustada:false, precoBase:43.07 },
  SANB11:   { med: 10.49, lo:  8.18, hi: 12.81, cx:  null, div:  8.18, luc: 12.81, amp:  4.62, g:  4.88, gBruto:   4.88, gRoe:  4.88, gCagr:  null, payout: 53.3, lucroNorm:14496584457, motor:'ROE mediano × patrimônio líquido (balanço)', seg:'FIN', fonte:'realizado', pap:3754909464, d0:2.0558, fcfe:null, fcfeAjustada:false, precoBase:29.85 },
  VALE3:    { med: 10.41, lo:  2.44, hi: 13.81, cx:  2.44, div: 10.41, luc: 13.81, amp: 11.38, g:  1.88, gBruto:   1.88, gRoe:  1.88, gCagr:  null, payout: 66.4, lucroNorm:62027000000, motor:'lucro recorrente (campo Partnr)', seg:'IND', fonte:'outra_base', pap:4542316303, d0:9.0647, fcfe:25516000000, fcfeAjustada:true, precoBase:80.40 },
  BPAC11:   { med:  9.72, lo:  4.41, hi: 15.03, cx:  null, div:  4.41, luc: 15.03, amp: 10.62, g: 15.00, gBruto:  17.12, gRoe: 17.12, gCagr:  null, payout: 23.4, lucroNorm:11421058000, motor:'lucro recorrente (campo Partnr)', seg:'FIN', fonte:'realizado', pap:3847053872, d0:0.6952, fcfe:null, fcfeAjustada:false, precoBase:57.80 },
  CPFE3:    { med:  8.48, lo:  8.36, hi:  9.96, cx:  8.48, div:  8.36, luc:  9.96, amp:  1.60, g:  3.12, gBruto:   3.12, gRoe:  8.22, gCagr:  3.12, payout: 68.6, lucroNorm:6048203710, motor:'receita × margem líquida mediana', seg:'IND', fonte:'piso', pap:1152183325, d0:3.5985, fcfe:6861067000, fcfeAjustada:true, precoBase:44.79 },
  CXSE3:    { med:  7.95, lo:  7.49, hi:  8.41, cx:  null, div:  7.49, luc:  8.41, amp:  0.92, g:  6.32, gBruto:   6.32, gRoe:  6.32, gCagr:  null, payout: 80.0, lucroNorm:4024087388, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'realizado', pap:3005427994, d0:1.0708, fcfe:null, fcfeAjustada:false, precoBase:19.40 },
  SAUD3:    { med:  7.93, lo:  5.39, hi: 10.48, cx:  null, div:  5.39, luc: 10.48, amp:  5.08, g:  9.86, gBruto:   9.86, gRoe:  9.86, gCagr:  null, payout: 46.9, lucroNorm:2358835563, motor:'receita × margem líquida mediana', seg:'IND', fonte:'pares', pap:2927105556, d0:0.3777, fcfe:null, fcfeAjustada:false, precoBase:14.60 },
  MULT3:    { med:  7.52, lo:  2.52, hi: 17.19, cx:  2.52, div:  7.52, luc: 17.19, amp: 14.67, g: 12.69, gBruto:  12.69, gRoe: 12.69, gCagr: 26.21, payout: 35.5, lucroNorm:1409011000, motor:'FFO (FCO − capex)', seg:'SHOP', fonte:'realizado', pap:519762016, d0:0.9633, fcfe:1027126000, fcfeAjustada:true, precoBase:27.95 },
  TIMS3:    { med:  6.77, lo:  6.18, hi: 10.56, cx: 10.56, div:  6.77, luc:  6.18, amp:  4.38, g:  3.44, gBruto:   3.44, gRoe:  3.44, gCagr: 15.55, payout: 80.3, lucroNorm:3382496391, motor:'receita × margem líquida mediana', seg:'IND', fonte:'outra_base', pap:2422648586, d0:1.1214, fcfe:7013735000, fcfeAjustada:true, precoBase:18.71 },
  SHUL4:    { med:  6.70, lo:  2.42, hi: 10.98, cx:  null, div:  2.42, luc: 10.98, amp:  8.56, g:  0.00, gBruto:  -3.18, gRoe: 17.46, gCagr: -3.18, payout:  5.8, lucroNorm:252232383, motor:'receita × margem líquida mediana', seg:'IND', fonte:'realizado', pap:356271795, d0:0.0408, fcfe:-1080000, fcfeAjustada:true, precoBase:4.45 },
  ALOS3:    { med:  5.97, lo:  5.74, hi: 10.25, cx: 10.25, div:  5.74, luc:  5.97, amp:  4.50, g:  2.62, gBruto:   2.62, gRoe:  2.62, gCagr: 17.90, payout: 63.3, lucroNorm:1127358000, motor:'FFO (FCO − capex)', seg:'SHOP', fonte:'realizado', pap:523411472, d0:1.3642, fcfe:2119208000, fcfeAjustada:true, precoBase:26.74 },
  FLRY3:    { med:  5.26, lo:  4.07, hi:  7.64, cx:  7.64, div:  5.26, luc:  4.07, amp:  3.57, g:  2.80, gBruto:   2.80, gRoe:  2.80, gCagr: 27.52, payout: 75.0, lucroNorm:632977056, motor:'receita × margem líquida mediana', seg:'IND', fonte:'realizado', pap:546963982, d0:0.8680, fcfe:1334861000, fcfeAjustada:true, precoBase:19.65 },
  CLSC4:    { med:  5.20, lo:  4.37, hi:  9.17, cx:  5.20, div:  4.37, luc:  9.17, amp:  4.80, g:  2.75, gBruto:   2.75, gRoe: 14.10, gCagr:  2.75, payout: 29.3, lucroNorm:677687000, motor:'lucro recorrente (campo Partnr)', seg:'IND', fonte:'realizado', pap:38574593, d0:5.1394, fcfe:594033000, fcfeAjustada:true, precoBase:156.00 },
  PASS3:    { med:  4.73, lo:  4.57, hi: 15.72, cx: 15.72, div:  4.73, luc:  4.57, amp: 11.15, g:  0.00, gBruto: -16.35, gRoe:  9.44, gCagr:-16.35, payout: 51.4, lucroNorm:1512254377, motor:'receita × margem líquida mediana', seg:'UTIL', fonte:'pares', pap:714288216, d0:1.0891, fcfe:3425021000, fcfeAjustada:true, precoBase:22.99 },
  IRBR3:    { med:  4.27, lo:  3.95, hi:  4.60, cx:  null, div:  3.95, luc:  4.60, amp:  0.65, g:  3.97, gBruto:   3.97, gRoe:  3.97, gCagr:  null, payout: 46.9, lucroNorm:244749476, motor:'ROE mediano × patrimônio líquido', seg:'FIN', fonte:'pares', pap:81832653, d0:1.4017, fcfe:null, fcfeAjustada:false, precoBase:56.78 },
  AXIA3:    { med:  0.81, lo:  0.29, hi:  4.30, cx:  0.81, div:  4.30, luc:  0.29, amp:  4.01, g:  0.58, gBruto:   0.58, gRoe:  0.58, gCagr:  9.96, payout: 92.7, lucroNorm:6769932213, motor:'receita × margem líquida mediana', seg:'IND', fonte:'realizado', pap:2928410780, d0:2.1439, fcfe:8594080000, fcfeAjustada:true, precoBase:55.52 },
};
