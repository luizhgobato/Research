// Indicadores SETORIAIS — bancos, seguradoras e resseguradora.
// Linhas da DRE que a tabela industrial da Base de Dados não tem coluna para exibir.
// Fonte: MCP Partnr (B3/CVM), companies_reports/INCOME_STATEMENT/CONSOLIDATED — 01/09/2026.
// 2021-2025 = exercício fechado (ANNUAL); 2026 = LTM/TTM até 30/06/2026.
//
// POR QUE ESTE BLOCO EXISTE: CXSE3 e BBSE3 são holdings puras — as operadoras de seguro são
// joint ventures (CNP, Tokio Marine, Icatu) que NÃO são consolidadas linha a linha, entram por
// equivalência patrimonial. Por isso receita líquida, custos e lucro bruto valem ZERO de verdade
// na DRE delas: o prêmio está no balanço da investida, não no da holding.
//
// CAMPOS SUPRIMIDOS DE PROPÓSITO (a fonte devolve, mas o valor não fecha):
//  · lucroRecorrente só é publicado para CXSE3 e BBSE3, onde a série é coerente (0,47-0,66x do
//    lucro líquido). Nos bancos a fonte devolve valores impossíveis — ITUB3 2021 daria
//    R$112,5 bi contra lucro líquido de R$28,4 bi (4x) e BMEB4 fica 2-5x acima em todos os anos.
//  · aliquota é anulada quando fica fora de 0-50%: acontece quando o EBT é quase zero e o
//    quociente explode (BMEB4 2025 daria -21.679%). É o dado real da fonte, mas não é legível.
const SETORIAL_SEED = {
  CXSE3: {
    2026: { equivPatrimonial:3502145000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:1876228000, receitaFinanceira:194143000, despAdmin:-165431000, ebt:5067864000, aliquota:10.75, lucroRecorrente:2975392000, coreEbit:-165431000 },
    2025: { equivPatrimonial:3279914000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:1838846000, receitaFinanceira:193094000, despAdmin:-149421000, ebt:4829789000, aliquota:11.14, lucroRecorrente:2774799000, coreEbit:-149421000 },
    2024: { equivPatrimonial:2683337000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:1963980000, receitaFinanceira:172227000, despAdmin:-126617000, ebt:4336515000, aliquota:13.17, lucroRecorrente:2098998000, coreEbit:-126617000 },
    2023: { equivPatrimonial:2669450000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:1638983000, receitaFinanceira:147813000, despAdmin:-110036000, ebt:4065096000, aliquota:11.88, lucroRecorrente:2190471000, coreEbit:-110036000 },
    2022: { equivPatrimonial:1938126000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:1382246000, receitaFinanceira:98182000, despAdmin:-100302000, ebt:3419109000, aliquota:15.01, lucroRecorrente:1422307000, coreEbit:-100302000 },
    2021: { equivPatrimonial:1327737000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:1048434000, receitaFinanceira:15583000, despAdmin:-69563000, ebt:2196235000, aliquota:13.66, lucroRecorrente:968663000, coreEbit:-69563000 },
  },
  BBSE3: {
    2026: { equivPatrimonial:5471842000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:4844115000, receitaFinanceira:1289853000, despAdmin:-341985000, ebt:11128400000, aliquota:17.42, lucroRecorrente:4345202000, coreEbit:null },
    2025: { equivPatrimonial:5340918000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:4812035000, receitaFinanceira:1174046000, despAdmin:-287185000, ebt:10941368000, aliquota:17.58, lucroRecorrente:4205294000, coreEbit:null },
    2024: { equivPatrimonial:5311964000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:4695854000, receitaFinanceira:696360000, despAdmin:-250551000, ebt:10410989000, aliquota:16.4, lucroRecorrente:4007499000, coreEbit:null },
    2023: { equivPatrimonial:4890458000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:4235610000, receitaFinanceira:670933000, despAdmin:-220301000, ebt:9493312000, aliquota:16.29, lucroRecorrente:3711593000, coreEbit:null },
    2022: { equivPatrimonial:3363765000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:3681904000, receitaFinanceira:532063000, despAdmin:null, ebt:7548231000, aliquota:19.92, lucroRecorrente:2362667000, coreEbit:null },
    2021: { equivPatrimonial:1830355000, receitaInterm:null, resultBrutoInterm:null, sinistros:null, outrasRecOper:3101845000, receitaFinanceira:151739000, despAdmin:null, ebt:5079424000, aliquota:22.57, lucroRecorrente:831372000, coreEbit:null },
  },
  IRBR3: {
    2026: { equivPatrimonial:null, receitaInterm:4461289000, resultBrutoInterm:106676000, sinistros:-4354613000, outrasRecOper:50832000, receitaFinanceira:520570000, despAdmin:-35472000, ebt:322771000, aliquota:25.46, lucroRecorrente:null, coreEbit:null },
    2025: { equivPatrimonial:null, receitaInterm:5211349000, resultBrutoInterm:578687000, sinistros:-4632662000, outrasRecOper:10788000, receitaFinanceira:468253000, despAdmin:-29559000, ebt:602561000, aliquota:35.12, lucroRecorrente:null, coreEbit:null },
    2024: { equivPatrimonial:null, receitaInterm:6057974000, resultBrutoInterm:776731000, sinistros:-5281243000, outrasRecOper:37167000, receitaFinanceira:1783139000, despAdmin:-23535000, ebt:1196546000, aliquota:32.66, lucroRecorrente:null, coreEbit:null },
    2023: { equivPatrimonial:null, receitaInterm:5794710000, resultBrutoInterm:-325688000, sinistros:-6120398000, outrasRecOper:614000, receitaFinanceira:412897000, despAdmin:-53743000, ebt:-257678000, aliquota:null, lucroRecorrente:null, coreEbit:null },
    2022: { equivPatrimonial:null, receitaInterm:7047042000, resultBrutoInterm:-1439154000, sinistros:-8486196000, outrasRecOper:65169000, receitaFinanceira:2334708000, despAdmin:-421237000, ebt:-1180761000, aliquota:46.62, lucroRecorrente:null, coreEbit:null },
    2021: { equivPatrimonial:null, receitaInterm:7987428000, resultBrutoInterm:-1576708000, sinistros:-9564136000, outrasRecOper:-9161000, receitaFinanceira:2038700000, despAdmin:-419685000, ebt:-1395465000, aliquota:null, lucroRecorrente:null, coreEbit:null },
  },
  ITUB3: {
    2026: { equivPatrimonial:2663000000, receitaInterm:385985000000, resultBrutoInterm:143714000000, sinistros:null, outrasRecOper:null, receitaFinanceira:null, despAdmin:-80695000000, ebt:54689000000, aliquota:12.34, lucroRecorrente:null, coreEbit:null },
    2025: { equivPatrimonial:1417000000, receitaInterm:387118000000, resultBrutoInterm:138947000000, sinistros:null, outrasRecOper:null, receitaFinanceira:null, despAdmin:-79176000000, ebt:50250000000, aliquota:8.76, lucroRecorrente:null, coreEbit:null },
    2024: { equivPatrimonial:1047000000, receitaInterm:335328000000, resultBrutoInterm:135739000000, sinistros:null, outrasRecOper:null, receitaFinanceira:null, despAdmin:-79416000000, ebt:47556000000, aliquota:11.41, lucroRecorrente:null, coreEbit:null },
    2023: { equivPatrimonial:920000000, receitaInterm:313221000000, resultBrutoInterm:124526000000, sinistros:null, outrasRecOper:null, receitaFinanceira:null, despAdmin:-75759000000, ebt:39700000000, aliquota:14.67, lucroRecorrente:null, coreEbit:null },
    2022: { equivPatrimonial:672000000, receitaInterm:283372000000, resultBrutoInterm:115570000000, sinistros:null, outrasRecOper:null, receitaFinanceira:null, despAdmin:-69164000000, ebt:37533000000, aliquota:18.11, lucroRecorrente:null, coreEbit:null },
    2021: { equivPatrimonial:1164000000, receitaInterm:195679000000, resultBrutoInterm:126374000000, sinistros:null, outrasRecOper:-14379000000, receitaFinanceira:null, despAdmin:null, ebt:42231000000, aliquota:32.79, lucroRecorrente:null, coreEbit:null },
  },
  BMEB4: {
    2026: { equivPatrimonial:null, receitaInterm:9537345000, resultBrutoInterm:4316407000, sinistros:null, outrasRecOper:252972000, receitaFinanceira:null, despAdmin:-1613744000, ebt:315143000, aliquota:null, lucroRecorrente:null, coreEbit:null },
    2025: { equivPatrimonial:null, receitaInterm:8259120000, resultBrutoInterm:3968680000, sinistros:null, outrasRecOper:145069000, receitaFinanceira:null, despAdmin:-1399354000, ebt:2942000, aliquota:null, lucroRecorrente:null, coreEbit:null },
    2024: { equivPatrimonial:null, receitaInterm:5913694000, resultBrutoInterm:3128765000, sinistros:null, outrasRecOper:105182000, receitaFinanceira:null, despAdmin:-994009000, ebt:575525000, aliquota:11.28, lucroRecorrente:null, coreEbit:null },
    2023: { equivPatrimonial:null, receitaInterm:4707585000, resultBrutoInterm:2575249000, sinistros:null, outrasRecOper:86406000, receitaFinanceira:null, despAdmin:-783947000, ebt:492888000, aliquota:19.78, lucroRecorrente:null, coreEbit:null },
    2022: { equivPatrimonial:null, receitaInterm:3661460000, resultBrutoInterm:1970970000, sinistros:null, outrasRecOper:154699000, receitaFinanceira:null, despAdmin:-731133000, ebt:263382000, aliquota:24.12, lucroRecorrente:null, coreEbit:null },
    2021: { equivPatrimonial:null, receitaInterm:2510145000, resultBrutoInterm:1564164000, sinistros:null, outrasRecOper:293544000, receitaFinanceira:null, despAdmin:-742506000, ebt:160405000, aliquota:null, lucroRecorrente:null, coreEbit:null },
  },
};

const SETORIAL_LABELS = {
  equivPatrimonial:  ['Equiv. patrimonial', 'Resultado das participações em joint ventures (CNP, Tokio Marine, Icatu...). Numa holding pura é o motor do lucro.'],
  receitaInterm:     ['Rec. intermediação', 'Banco: receita de intermediação financeira. Resseguradora: prêmios ganhos. NÃO é comparável com a receita de uma empresa industrial.'],
  resultBrutoInterm: ['Result. bruto interm.', 'Receita de intermediação menos as despesas de intermediação / sinistros.'],
  sinistros:         ['Sinistros e desp. oper.', 'Despesas com sinistros e operações de resseguro.'],
  outrasRecOper:     ['Outras rec. oper.', 'Inclui a corretagem (ex.: Caixa Corretora), que na CXSE3 é a segunda maior fonte de resultado.'],
  receitaFinanceira: ['Receita financeira', 'Rendimento das aplicações da própria holding.'],
  despAdmin:         ['Desp. administrativas', 'Custo da estrutura própria.'],
  ebt:               ['EBT (lucro antes do IR)', 'Lucro antes do imposto de renda e contribuição social.'],
  aliquota:          ['Alíquota efetiva', 'Imposto dividido pelo EBT. Anulada quando o EBT é quase zero e o quociente explode.'],
  lucroRecorrente:   ['Lucro recorrente', 'Lucro excluindo itens não recorrentes. Só publicado para CXSE3 e BBSE3 — nos bancos a fonte devolve valor incoerente.'],
  coreEbit:          ['Core EBIT', 'EBIT SEM a equivalência patrimonial: o que a holding gera por operação própria. Negativo na CXSE3 — sozinha, ela é um centro de custo administrativo.'],
};

const SETORIAL_NOTES = {
  CXSE3: 'Holding pura de seguros. Receita/custos/lucro bruto = zero por desenho societário (JVs entram por equivalência). Core EBIT negativo é característico, não um problema: a operação própria é só a estrutura administrativa.',
  BBSE3: 'Mesma estrutura da CXSE3. Sem despesa administrativa reportada em 2021-2022 na fonte. Sem Core EBIT na base.',
  IRBR3: 'Resseguradora — opera DIRETO, por isso tem prêmios (em "Rec. intermediação") e sinistros de verdade, diferente das holdings. Prejuízo de 2021 a 2023.',
  ITUB3: 'Banco. "Rec. intermediação" é receita de intermediação financeira — base totalmente diferente da receita de uma empresa não-financeira, não comparar. Sem receita financeira nem Core EBIT separados na base.',
  BMEB4: 'Banco. Alíquota efetiva fica anulada em 2021, 2025 e 2026: o EBT é quase zero e/ou o IR é positivo (crédito tributário), o que faz o quociente explodir.',
};
