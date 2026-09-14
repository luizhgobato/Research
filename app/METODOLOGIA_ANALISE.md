# Metodologia de Análise — motor de valuation por setor

> **Regra número 1: TODO ativo tem preço-teto.**
> Não existe "análise pendente" como resultado final. Se o motor genérico não serve, o certo é
> usar o motor do setor — não deixar em branco. Um teto com premissa explícita e sensibilizada
> é sempre melhor que nenhum teto: você pode discordar da premissa, mas não pode decidir sem número.
>
> A única coisa que pode ficar vazia é uma **premissa que ainda não foi pesquisada** — e nesse
> caso o teto sai marcado como preliminar (★☆☆), nunca ausente.

## 0. Como escolher o motor

Escolha pelo **modelo de negócio**, não pelo rótulo do setor na B3.

| Se a empresa… | Motor primário | Motor de validação |
|---|---|---|
| é banco ou seguradora (lucro nasce de capital alocado) | **P/VP × ROE** | Gordon (DDM) |
| é **holding pura** (lucro é equivalência patrimonial) | **NAV com desconto de holding** | DY sobre proventos recebidos |
| tem receita de aluguel/imóvel (shopping, logística) | **Cap rate / NAV** | P/FFO de pares + Bazin |
| é **cíclica de commodity** (minério, papel, petróleo, aço) | **EV/EBITDA meio-de-ciclo** | P/VP no fundo do ciclo |
| é utility regulada (energia, saneamento, gás) | **EV/EBITDA** | Bazin sobre dividendo sustentável |
| é industrial/serviço com lucro estável | **E/P histórico** (LPA × P/L médio) | EV/EBITDA setorial |
| está em prejuízo ou reestruturação | **P/VP × ROE normalizado** | EV/EBITDA sobre EBITDA recorrente |

**Preço-teto = preço justo × 0,85** (margem de segurança de 15%) em todos os motores.
Quando há dois métodos, o preço justo é a **média simples**, e a dispersão entre eles vira a
convicção (abaixo de 15% = ★★★, 15-35% = ★★☆, acima de 35% = ★☆☆ e revisar as premissas).

---

## 1. P/VP × ROE — bancos e seguradoras

Usado hoje em: ITUB3, BMEB4, ROXO34, CXSE3, BBSE3, IRBR3.

```
P/VP justo = (ROE − g) / (Ke − g)
Preço justo = P/VP justo × VPA
```

- `Ke` = 16% (custo de capital próprio padrão do projeto para financeiras)
- `g` = 8% (crescimento financeiro de longo prazo)
- `VPA` = cotação ÷ P/VP de mercado (quando o VPA não vier direto da fonte)

**Por que não P/L:** o lucro de um banco depende da alavancagem escolhida. P/VP × ROE captura
retorno sobre o capital que sustenta o balanço, que é o que limita o crescimento.

**Validação (Gordon):** `Preço = DPS sustentável ÷ (Ke − g)`, com DPS = payout × LPA.

---

## 2. NAV com desconto de holding — holdings puras

**Motor que faltava.** Aplicar a: ITSA4, BRAP4.

Uma holding não tem operação própria (ver o `Core EBIT` negativo da CXSE3 no bloco setorial).
Avaliar pelo P/L dela é avaliar o lucro das investidas duas vezes.

```
NAV por ação = Σ (participação % × valor de mercado da investida) ÷ nº de ações da holding
Preço justo  = NAV por ação × (1 − desconto de holding)
```

- **Desconto de holding**: 15% a 25%. Reflete custo da estrutura, tributação em cascata e
  falta de controle direto do minoritário. Use **20%** como padrão e sensibilize 15%/25%.
- Se a holding tem dívida líquida própria, subtraia antes de dividir pelas ações.

**Validação:** DY sobre os proventos que a holding **efetivamente recebe e repassa** —
não sobre o lucro de equivalência, que é contábil e não vira caixa integralmente.

**Ressalva obrigatória:** informe o desconto de holding **corrente de mercado** (NAV vs. cotação
hoje) ao lado do assumido. Se a ação já negocia com desconto maior que o assumido, o teto pelo
NAV vai parecer generoso — diga isso explicitamente.

---

## 3. EV/EBITDA meio-de-ciclo — cíclicas de commodity

Usado hoje em: RANI3. Aplicar também a: VALE3, PETR4, KLBN11.

**Este é o motor que resolve o caso "lucro LTM deprimido".** A Vale teve lucro de R$96 bi em
2022 e R$8,7 bi no LTM 2026 — usar o LPA atual × P/L histórico dá um teto sem sentido
(o cálculo produziu R$18,46 contra cotação de R$80,40). O ciclo é o dado, não o ruído.

```
EBITDA meio-de-ciclo = média do EBITDA dos últimos 5-7 anos (cobrindo pico E fundo)
EV justo             = EBITDA meio-de-ciclo × múltiplo-alvo do setor
Preço justo          = (EV justo − dívida líquida atual) ÷ nº de ações
```

- Use a **média**, não o LTM, e não o pico. A série 2021-2026 da Base de Dados já dá isso.
- **Múltiplo-alvo**: mediana do próprio EV/EBITDA histórico da empresa. Se a série tiver
  menos de 4 anos úteis, use referência setorial e marque como ⚠️ estimativa própria.
- Dívida líquida é a **atual**, não a média — ela não é cíclica da mesma forma.

**Validação:** P/VP no fundo do ciclo. Cíclica raramente cai abaixo do P/VP mínimo histórico.

**Ressalva obrigatória:** diga em que ponto do ciclo a empresa está hoje (EBITDA atual vs. média)
e o que o preço embute.

---

## 4. EV/EBITDA + Bazin — utilities reguladas

Usado hoje em: CPFE3, PASS3. Aplicar também a: SBSP3, CLSC4, AXIA3, AURE3.

```
EV justo    = EBITDA recorrente × múltiplo-alvo
Preço justo = (EV justo − dívida líquida) ÷ ações
Bazin       = dividendo sustentável ÷ yield exigido (8% a 9%)
```

- Utility tem receita previsível: use **EBITDA recorrente**, expurgando provisões e itens
  não recorrentes (a AXIA3, por exemplo, teve EBITDA de R$8,5 bi em 2025 contra R$26,2 bi
  em 2024 por provisões — normalize).
- **Empresa em prejuízo** (AURE3): não invalida o motor. EV/EBITDA funciona porque o EBITDA
  segue positivo; o prejuízo vem de despesa financeira e depreciação. Só marque a alavancagem
  como risco central e reduza o múltiplo-alvo.

---

## 5. E/P histórico + EV/EBITDA — industriais e serviços de lucro estável

Usado hoje em: LEVE3. Aplicar também a: SHUL4, FLRY3, SAUD3.

```
Preço justo = LPA (normalizado) × P/L médio histórico da própria empresa
```

- **P/L médio**: mediana de 5 anos, excluindo anos de prejuízo e outliers acima de 2 desvios.
- **LPA normalizado**: se houve incorporação ou desdobramento no período (SAUD3, SBSP3),
  use o LPA pró-forma e **declare a quebra de série** — não misture bases.
- Se os múltiplos da fonte estiverem quebrados (SHUL4: P/VP de 22x com VPA de R$5,08),
  **não use o múltiplo da fonte** — recalcule do balanço: `VPA = PL ÷ ações`.

---

## 6. Cap rate / NAV — shoppings e imobiliário

Usado hoje em: ALOS3, MULT3. Sem novas empresas neste motor.

```
NAV = NOI ÷ cap rate de mercado − dívida líquida
Preço justo = NAV ÷ ações, validado por P/FFO de pares e Bazin sobre FFO
```

Nunca usar P/L: o lucro contábil de shopping é distorcido por reavaliação de ativos.

---

## 7. Convicção e ressalvas

Todo relatório declara:

1. **Convicção** (★): dispersão entre os métodos, conforme a seção 0.
2. **Premissas próprias** marcadas com ⚠️ — múltiplo-alvo sem peer comp confirmado, yield
   exigido arbitrado, EBITDA normalizado por estimativa.
3. **Quebras de série** — desdobramento, grupamento, incorporação, mudança de norma contábil.
4. **O que faria a tese mudar** — gatilhos objetivos, não impressões.

## 8. Constantes do projeto

| Constante | Valor | Onde |
|---|---|---|
| Margem de segurança | 15% (teto = justo × 0,85) | todos os motores |
| Ke financeiras | 16% | seção 1 |
| g financeiro | 8% | seções 1 e 2 |
| Yield exigido Bazin | 8% a 9% | seções 4 e 6 |
| Desconto de holding | 20% (faixa 15-25%) | seção 2 |
| IPCA + prêmio (motor automático) | ver `js/config.js` | `calcularPrecoTeto` |
| Selic (taxa livre de risco) | 14,00% — Copom 05/08/2026 | seção 9, `js/decisao.js` |
| ROE mínimo do score | 15% | seção 9 |
| Alavancagem máxima do score | 3x dív. líq./EBITDA | seção 9 |

> O motor automático de `js/calculos.js` (LPA × P/L histórico + DY, descontado por IPCA+prêmio)
> é um **atalho válido apenas para a seção 5** — industriais e serviços de lucro estável.
> Para os demais setores, deixe `data-pl-hist` AUSENTE na linha do Radar e preencha
> `data-preco-teto` com o resultado do motor do setor. Isto está codificado nos comentários
> de `data/radar-rows.data.js`.

---

## 9. Motor de decisão — os quatro critérios do Radar

As seções 1 a 6 respondem "quanto vale". Esta responde **"compro?"**. Implementada em
`js/decisao.js`, colunas 20 (Prêmio Selic) e 21 (Critérios) do Radar.

### O teste central

> Se esta empresa **nunca mais crescer** e eu comprar por este preço, quanto rende por ano?

É o **earnings yield**: `L/P = LPA LTM ÷ cotação`. Se ele não ganha da **Selic**, a ação está
pedindo que você corra risco de renda variável por menos do que o Tesouro paga sem risco.
A coluna **Prêmio Selic** é exatamente `L/P − Selic`, em pontos percentuais.

**Qual LPA entra na conta** — nesta ordem, e a ordem não é cosmética:

1. **LPA implícito da base Partnr** = `preço do fechamento ÷ P/L do mesmo exercício`.
   Fonte única com o resto do projeto (não envelhece em paralelo) e **seguro para units**:
   o campo `lpa` cru do Partnr é por ação, mas KLBN11/SANB11/BPAC11 negociam pacotes de
   várias ações — o `pl` do `valuationRatios` já vem na base certa e o LPA implícito herda
   essa correção.
2. `data-lpa-ltm` da linha, só quando a base não tem P/L para o ticker.

> **Erro real corrigido por essa ordem:** a LEVE3 carregava `data-lpa-ltm="2.82"` enquanto o
> LPA TTM da base já era R$5,14 — um P/L quase 2x errado, que a jogava de 5/5 critérios para
> 4/5 e transformava um prêmio de +2 p.p. num −5,3 p.p. LPA curado à mão defasa; base não.

### Os quatro critérios

| # | Critério | Corte | Por quê |
|---|---|---|---|
| 1 | Earnings yield ≥ Selic | `SELIC` (`js/config.js`) | Custo de oportunidade zero-risco |
| 2 | ROE ≥ 15% | `ROE_MINIMO` | Abaixo do custo de capital, crescer destrói valor |
| 3 | Dív. líq./EBITDA < 3x | `ALAVANCAGEM_MAX` | Alavancagem transforma ciclo ruim em ruína |
| 4 | Lucro projetado 2026 ≥ 2025 | — | Barato + encolhendo é armadilha de valor |

**Critério que não se aplica sai do denominador — nunca conta como reprovação.** Alavancagem
não se mede em banco ou seguradora (o passivo é a matéria-prima), então essas empresas são
avaliadas em 3 critérios, não 4. Empresa sem dado não é empresa ruim; é empresa não medida.
Marcada ⚪ na tooltip, com o motivo escrito.

### 🔵 A margem de segurança saiu da pontuação (06/09/2026)

Era o critério nº 3 e **reprovava empresa**. Agora aparece na tooltip como 🔵 referência, fora
do denominador. Três razões, todas com evidência deste projeto:

**(a) O teto é instável por causa minha.** Medindo o efeito de uma troca de motor: **mediana de
23% de variação no teto em um dia**, SANB11 +98%, 14 de 24 acima de 20% — com o preço de
mercado parado. Um número que se move 23% por mudança de premissa minha não pode ser o que
decide se a empresa entra na carteira.

**(b) Ainda apareciam defeitos de primeira ordem.** Em dois dias: mediana contra tendência
(reprovava 9 de 9 financeiras) e mediana contra quebra de série (SAUD3 dava teto de R$ 3,71
contra cotação de R$ 14,60). Metodologia com bug de primeira ordem não tem autoridade de veto.

**(c) Nenhum dos seis motores foi testado contra retorno futuro.** Foram escolhidos por
argumento econômico. O único critério com backtest é o nº 1 (L/P vs Selic), e com margem
modesta: **+21,9% contra +19,0% do baseline**, em 130 observações.

⚠️ **O preço-teto NÃO foi removido do app.** Continua na sua coluna, com convicção ★ e tooltip
de auditoria, e serve para duas coisas reais: **disciplina** (obriga um número declarado antes
da compra) e **detecção de absurdo** — foi o teto absurdo que expôs a incorporação da
Bradsaúde e a quebra de série do IRB. Só não pontua mais.

### Nota 0-100 — o desempate entre duas aprovadas

O score `n/5` é um **portão**: responde *"é investível?"*. Ele não responde *"entre estas duas
5/5, qual eu compro?"* — porque **joga fora a magnitude**. Um prêmio de +0,5 p.p. e um de
+15 p.p. contam a mesma coisa: 🟢.

A nota recupera a magnitude. Cada eixo vira 0-100 por uma régua explícita, e os eixos são
combinados por peso:

| Eixo | Peso | Régua (0 → 50 → 100) |
|---|---|---|
| Prêmio sobre a Selic | **35%** | −10 p.p. → 0 p.p. → +10 p.p. |
| Margem de segurança | **25%** | −30% → 0% → +30% |
| ROE | **15%** | 0% → 15% → 30% |
| Crescimento do lucro | **15%** | −25% → 0% → +25% |
| Alavancagem (dív. líq./EBITDA) | **10%** | 6x → 3x → 0x |

**Os pesos são um julgamento, não um resultado de otimização.** O julgamento é: retorno
esperado pesa mais que qualidade, porque qualidade sem preço já está cara.

**Eixo sem dado sai e os pesos são renormalizados** — mesma regra do denominador dos
critérios. A nota então carrega um aviso de **cobertura** (ex.: "calculada sobre 75% dos
eixos"): uma nota de cobertura parcial não é comparável de igual para igual com uma completa.

**Crescimento com base negativa não entra.** Sair de prejuízo para lucro produz um percentual
sem significado; o eixo é omitido em vez de gerar um número inventado.

A tooltip da coluna mostra a conta inteira — valor cru → pontos → peso. Nota que não se
audita é palpite com aparência de precisão, e aí não serve para decidir.

### Ranking "Por onde começar"

Ordena em cinco níveis: **(1)** tem prêmio calculável, **(2)** prêmio ≥ 0, **(3)** proporção
de critérios aprovados, **(4)** **nota**, **(5)** prêmio.

**A ordem entre (3) e (4) é deliberada: o portão vem antes da magnitude.** Uma 5/5 com nota 78
fica à frente de uma 3/4 com nota 80 — a segunda tem mais retorno esperado, mas falha num
teste de qualidade, e nota alta não compra aprovação em critério reprovado. A nota desempata
*dentro* de cada faixa de aprovação, nunca por cima dela.

Os dois primeiros níveis existem por correções de resultados enganosos: sem o nível 1 a SHUL4
liderava com "4/4" — 4/4 porque o critério ausente era justamente o earnings yield; sem o
nível 2 o BRSR6 (+15 p.p., 3/4) ficava atrás do FIQE3 (−1,5 p.p., 4/5), ou seja, mais
critérios rendendo menos que a renda fixa.

**O ranking não é ordem de compra — é a fila para ler o relatório.**

### Atualização

Tudo é recalculado a cada atualização de cotação (o prêmio e a margem de segurança dependem
do preço). A única manutenção manual é a **Selic em `js/config.js` após cada Copom** —
a constante carrega a data da última reunião e a da próxima.

---

## 10. TIR real — três medidas independentes (substitui a Nota 0-100)

### Por que a nota saiu

A Nota 0-100 era média ponderada de 5 critérios, com pesos escolhidos por mim. Testada contra
os próprios dados do projeto — **130 observações, 27 empresas, 2021-2026**, retorno total 12
meses à frente:

| Filtro | n | Retorno médio |
|---|---|---|
| Todas (baseline) | 130 | **+19,0%** |
| L/P ≥ 14% | 41 | +21,9% |
| **Reprovadas** | 89 | **+17,7%** |
| L/P ≥ 14% **E** ROE ≥ 15% **E** dív/EBITDA < 3x | 35 | **+20,0%** |

Aprovar rendia +2,9 p.p. sobre a média — dentro da margem de erro — e **acrescentar os eixos
de qualidade PIOROU o resultado** (21,9% → 20,0%). O retorno também não era monotônico no L/P.
Bate com o estudo de 5 fatores Fama-French na B3, onde **HML é significante (t=2,02) e RMW
não é (t entre 0,60 e 1,17)**.

> **A lição:** um número de 0 a 100 comunica precisão que o método não tinha. Antes de publicar
> qualquer score novo, teste-o contra retorno futuro — e publique o resultado do teste na tela.

**Ressalvas do próprio backtest:** viés de sobrevivência (as 27 empresas existem hoje), amostra
pequena, janelas sobrepostas, um único regime de juro, horizonte de 12 meses. Ele **não prova
que o método não funciona** — prova que não há evidência de que funcione.

### As três medidas

Todas em **retorno real anual**, comparáveis com a **NTN-B 2035 (IPCA + 7,70%)**.

| Medida | Fórmula | Força | Limite |
|---|---|---|---|
| **Caixa (FCFE)** | `(FCO − capex) ÷ valor de mercado` | Imune a lucro contábil | Só onde a DFC é legível — 11 de 25 |
| **Dividendos (DDM)** | 10 anos a `g`, depois perpetuidade a IPCA+2% | Cobre financeiras | Depende do `g` |
| **Lucro normalizado** | `lucro norm. ÷ valor merc. + g − IPCA` | Existe para quase todas | Depende do motor de normalização |

**DY futuro = lucro normalizado × payout MEDIANO de 5 anos.** Payout de um ano é ruído — a
PETR4 varia de 26% a 266% em cinco anos.

### O normalizador é por setor

| Setor | Motor | Por quê |
|---|---|---|
| Indústria / serviço | `receita × margem líquida mediana` | Margem reverte à média |
| **Banco / seguradora** | `ROE mediano × patrimônio líquido` | Receita não existe (holdings lançam por equivalência) |
| **Shopping** | `FFO = FCO − capex` | Lucro contábil distorcido por reavaliação de imóvel (IFRS) |
| Qualquer uma | `RECURRING_NET_INCOME` do Partnr | Quando passa no teste de sanidade |

⚠️ **`RECURRING_NET_INCOME` é fórmula, não julgamento de analista.** O `name_pt` do campo é
"Resultado Líquido de Operações Descontinuadas" e a definição vem vazia. Reverso-engenhado, ele
remove: operações descontinuadas, outras receitas/despesas operacionais, IR diferido e
impairment. **Funciona na VALE3** (lucro de R$ 8,7 bi → R$ 62 bi, com impairment de −R$ 23,5 bi
e IR diferido de −R$ 15,4 bi explicando). **Destrói o SANB11** (R$ 14,5 bi → R$ 1,9 bi), porque
"outras receitas operacionais" num banco é operação normal, não evento. Regra: usar só quando
o campo `IMPAIRMENTS` explica a diferença, e sempre conferir contra ROE × patrimônio.

### O `g`

```
g = MENOR entre (CAGR 5a do lucro recorrente) e (ROE × retenção), limitado a 15%
```

`ROE × retenção` **infla sistematicamente**: assume reinvestimento do lucro retido ao mesmo ROE
para sempre. Na LEVE3 dava 23,2% ao ano; o lucro recorrente dela cresceu **8,9%** de fato.

⚠️ **Financeiras não têm `CAGR_*_RECURRING_NET_INCOME` na base** (testado em ITUB e BBSE). Para
BBSE3, ITUB3, BRSR6, CXSE3, PSSA3, SANB11, BPAC11 e ITSA4 o `g` vem só de `ROE × retenção`, e o
teto de 15% continua sendo premissa arbitrária.

### A coluna mostra a FAIXA, não a mediana

Correção de um erro de desenho. Exibir a mediana obrigava a cruzar com uma segunda coluna de
convergência para não ler errado — **um número que precisa de outro para não enganar está mal
apresentado**. A faixa `mín → máx` carrega as duas informações de uma vez.

| Você vê | Leitura |
|---|---|
| Faixa **inteira acima** de 7,70% | Ganha da renda fixa por qualquer medida → sinal mais forte da tabela |
| Faixa **inteira abaixo** | Perde por qualquer medida → descarta |
| Faixa **cruza** a barra | Depende de qual régua acertar → **precisa de análise, a tabela não decide** |
| Faixa estreita | As três concordam — número confiável, bom ou ruim |
| Faixa larga | A divergência é o assunto, não o ponto médio |

`BRSR6 16,9%` parecia resposta. `BRSR6 10,2 → 23,5%` mostra que não é.

### ⚠️ Fisher: retorno real é divisão, não subtração

```
errado:   nominal − IPCA
correto:  (1 + nominal) ÷ (1 + IPCA) − 1
```

A primeira versão subtraía, superestimando ~0,8 p.p. na PETR4 e mais nos retornos altos. Não
mudava a ordem do ranking, mas era erro de método. Corrigido em 05/09/2026.

Consequência para a medida de caixa: o FCFE yield **não é** o retorno real. Com `g = IPCA`,
o retorno nominal é `yield + IPCA` e o real vira `yield ÷ (1+IPCA)` — na PETR4, 17,6% → 16,9%.

### Armadilha recorrente: UNITS

KLBN11 (1 ON + 4 PN), SANB11 (1 ON + 1 PN), BPAC11 (1 ON + 2 PN). O `lpa` e o valor patrimonial
por ação do Partnr são **por ação**; o preço é **por unit**. O `pl` e o `pvp` reportados dividem
um pelo outro e saem errados por um fator inteiro. **Esse erro apareceu QUATRO vezes nesta
metodologia** — no payout (BPAC11 72% → 26%), no P/L (SANB11 15,5x → 7,7x), no patrimônio
(BTG R$ 32,3 bi → R$ 83,1 bi) e no **preço-teto do BPAC11** (R$ 13,50 → R$ 34,88, porque o
P/VP justo multiplicava o valor patrimonial por AÇÃO e era comparado com preço por UNIT —
a margem de segurança dizia −328% quando o correto é −66%).

Contraexemplo importante: o teto do **SANB11 não era erro de unit**. O VPA usado (R$ 37,03)
já estava em base de unit, só estava desatualizado contra o balanço (R$ 33,95). Diagnostiquei
errado da primeira vez — **conferir contra o balanço antes de atribuir a units**. Sempre multiplicar o LPA/VPA pelo fator da unit,
ou ler `UNIT_*` do balanço.

### Como atualizar

`data/tir.data.js` é um snapshot. Recalcular exige `companies_reports` (CASH_FLOW_STATEMENT +
INCOME_STATEMENT) e `companies_ratios` (CAGR do lucro recorrente) do Partnr — não há como fazer
em runtime, porque a API exige chave e um HTML estático não pode guardá-la em segurança.
Atualizar também `TIR_NTNB` junto, e a Selic em `js/config.js` após cada Copom.

### Lacunas conhecidas

- **CPFE3 tem `DIVIDEND_YIELD = 0`** na base em 2025 e 2026 — é dado ausente, não dividendo
  zero. A coluna do Radar mostra "—" em vez de "0,0%": publicar zero afirmaria algo falso.
  O payout mediano dela saiu de 4 anos, não 5.
- **VALE3 (+398%) e KLBN11 (+365%) na coluna Crescimento** comparam um lucro estimado já
  normalizado contra um 2025 deprimido de fundo de ciclo. O número está certo; o rótulo
  "crescimento" é que engana. Não é erro de dado — é limitação da coluna.

---

## 11. Motor de preço-teto — refeito em 06/09/2026

Antes: 16 tetos calculados à mão em momentos diferentes com parâmetros fixos, e 13 herdados de
análises antigas **sem motor declarado**. Agora `scripts/motor_teto.py` recalcula 24 dos 30 com
a mesma régua e gera a tooltip de auditoria. NAV (ITSA4, BRAP4) e shopping (ALOS3, MULT3)
seguem manuais — exigem valor de mercado das investidas e cap rate, que não estão na base.

### As seis mudanças de critério

**1 · Taxa livre de risco normalizada, não spot.** A NTN-B longa paga hoje IPCA+7,70%, nível
historicamente alto. Usá-la num modelo de **perpetuidade** congela o estresse de hoje para
sempre — o mesmo erro de avaliar cíclica pelo lucro de pico. Usamos **IPCA+5,5%** → 10,18%
nominal. ⚠️ **É o juízo mais influente do motor:** com a spot, praticamente toda a bolsa fica
acima do teto e o Radar não aponta nenhuma compra.

**2 · Ke variável por risco, mecânico.** `Ke = 15,18% base ± ajustes`, todos de dado observável:

| Ajuste | Regra | Faixa |
|---|---|---|
| Volatilidade do ROE | coef. de variação < 0,25 / 0,25-0,50 / > 0,50 | −1,0 / 0 / +1,5 |
| Tamanho | > R$ 50 bi / R$ 10-50 bi / < R$ 10 bi | −1,0 / 0 / +1,5 |
| Alavancagem | dív.líq/EBITDA < 1 / 1-3 / > 3 | −0,5 / 0 / +1,5 |

Limitado a 13-22%. Resultado: ITUB3 e BBSE3 a 13,2%; IRBR3 e KLBN11 a 18,2%. **Nenhum ajuste
é opinião** — todos saem da própria série.

**3 · `g` de 8% para IPCA+2% = 6,44%**, a mesma perpetuidade que a TIR real já usava. As duas
metodologias do projeto paravam de discordar sobre a mesma empresa.

**4 · Financeiras trocam P/VP×ROE de um estágio por DDM de dois estágios.** O motor de um
estágio **não comporta franquia que cresce acima do PIB**: testando o Ke implícito no preço de
mercado, ITUB3 e CXSE3 davam ~11,8%, **abaixo do juro longo** — sinal de que o `g` fixo é que
estava errado, não o preço. Agora a empresa cresce ao ritmo que ROE × retenção sustenta por
10 anos e só então converge. É o **mesmo DDM da TIR real, resolvido para preço em vez de taxa**.

**5 · Bazin vira Gordon.** Yield exigido = `Ke − g` da própria empresa, em vez da constante
arbitrária de 8-9%. Um só parâmetro governa dividendo e capital.

**6 · Margem de segurança escala com a convicção:** ★★★ 10% · ★★☆ 15% · ★☆☆ 25%. Antes eram
15% para todos e a estrela era decorativa.

### Duas travas que existem por erro cometido

**`g1` não pode alcançar o Ke.** A BBSE3 (ROE 78,8%) saiu com crescimento de 15% contra Ke de
13,2%: o valor presente explodiu e o teto deu R$ 79,30 contra cotação de R$ 40,48 — "+49% de
margem" numa ação a 7x o patrimônio. Agora `g1 ≤ Ke − 2 p.p.`, e quem bate na trava cai
para ★☆☆.

**Guarda de sanidade.** Teto que produz margem acima de |100%| quase sempre é o modelo sob
estresse, não a ação. Rebaixa a convicção automaticamente (o que aumenta a margem exigida) e
marca na tooltip. Atinge hoje: IRBR3, BPAC11, BMEB4, CLSC4, SAUD3, SBSP3, AXIA3.

### Financeiras: MEDIANA de três motores, não um só

**Diagnóstico do que estava errado.** Os tetos se moveram 23% na mediana num único dia — o
SANB11 dobrou — sem nenhuma notícia das empresas. A causa não era o teto ser instável em uso:
era **eu trocar o motor três vezes** (P/VP×ROE → DDM 2 estágios → lucro residual). Testando as
alternativas, a BBSE3 valia R$ 23 ou R$ 61 conforme a premissa de vantagem competitiva.

**Nenhum motor único resolve**, e a razão é honesta:

| Motor | Sensibilidade ao Ke | Viés |
|---|---|---|
| Gordon / P/VP×ROE | **1,46x** entre Ke 13% e 16% | Generoso: vantagem eterna. ROE baixo → valor negativo |
| Lucro residual com fade | **1,11x** | Duro: ITUB3 valeria 1,18x patrimônio com ROE de 18% sustentado |
| Múltiplo próprio (P/VP mediano × VPA) | **0** | Assume que o passado da empresa era justo |

**A regra já estava na seção 0 e eu não aplicava aqui: havendo mais de um método, o justo é o
consenso e a dispersão vira a convicção.** Financeiras passam a usar a **mediana dos três**.

Por que isso estabiliza: nenhum motor decide sozinho. Trocar um deles move pouco a mediana,
porque os outros dois seguram. E a dispersão entre eles — que é a incerteza real — deixa de ser
escondida e passa a governar a margem de segurança exigida.

**Não é abrir mão do teto por empresa.** Continua havendo um número por empresa, com critério
declarado. O que muda é que o número é consenso de três leituras em vez de aposta numa.

### O defeito que reprovava TODAS as financeiras: mediana contra tendência

Sintoma: as 9 financeiras davam margem negativa. Nove de nove não é resultado, é sintoma.

**Não era o Ke.** Invertendo o Gordon para achar o Ke que o preço de mercado pratica:

| Ativo | Ke implícito no mercado | Ke do motor |
|---|---|---|
| ITUB3 | 13,0% | 13,2% |
| CXSE3 | 12,8% | 13,0% |
| BPAC11 | 13,7% | 13,2% |
| BMEB4 | 15,4% | 15,7% |

**Era o ROE mediano.** Os bancos melhoraram de forma persistente na janela:

| Ativo | 1ª metade | 2ª metade | Δ |
|---|---|---|---|
| BBSE3 | 69,1% | 79,0% | **+9,9 p.p.** |
| BMEB4 | 18,6% | 27,2% | **+8,6 p.p.** |
| CXSE3 | 24,6% | 31,2% | **+6,6 p.p.** |
| PSSA3 | 16,1% | 22,3% | **+6,2 p.p.** |
| ITUB3 | 17,2% | 20,5% | +3,3 p.p. |
| **SANB11** | 17,6% | 10,6% | **−7,0 p.p.** |

> **A mediana é o instrumento certo para série que OSCILA e o errado para série que SOBE.**

Prova: ITUB3 com ROE **atual** de 21,0% e o Ke do motor dá P/VP justo de **2,16x** contra
**2,21x** negociado — praticamente o preço. Com a mediana de 18,2%, dá 1,74x, e daí vinha o −93%.

**Regra nova (`mediana_com_tendencia`):** compara a média das duas metades da série. Se
diferirem mais que o limiar (2 p.p. para ROE, 12% relativos para múltiplos), a série tem
tendência e vale a mediana **só da metade recente**. Vale nos dois sentidos — o SANB11
deteriorou e passa a usar o ROE menor, ficando **mais** conservador.

Resultado: BRSR6 passa a **+16%** de margem, e as demais ficam entre −14% e −52%, faixa
defensável, em vez de −35% a −93%.

⚠️ **Aplicado só a financeiras, de propósito.** Em cíclica de commodity a mediana da série
inteira é o ponto — ela precisa cobrir pico E fundo. Detectar "tendência" no EBITDA da Vale
seria confundir ciclo com trajetória e destruir o motor meio-de-ciclo.

### Correções de dado que entraram junto

**P/VP corrigido para units na série inteira.** O Partnr divide preço da UNIT por valor
patrimonial por AÇÃO: `pvp_real = pvp_reportado ÷ fator`. Conferido no SANB11 (1,74x ÷ 2 =
0,87x contra 0,88x do balanço). Sem isso o múltiplo próprio do BPAC11 dava teto de R$ 150.

**Um erro meu, para registro:** eu afirmei que o lucro residual na forma
`V = VPA × [1 + (ROE−Ke)/(Ke−g)]` seria mais estável que o Gordon. É **algebricamente idêntico**
a ele — `= VPA × (ROE−g)/(Ke−g)`. A saída denunciou: a faixa deu exatamente 1,46x para todos os
bancos, independente do ROE. Só a versão com **horizonte finito de retorno excedente** estabiliza.

### Terceira trava: reestruturação e ROE baixo (achada pelo usuário)

O IRBR3 saiu com teto de **R$ 8,18** contra cotação de R$ 56,78 — margem de −525%, absurda para
uma resseguradora que negocia a **0,86x o patrimônio** e voltou a pagar dividendo.

**Causa: eu perdi a trava do Gordon ao trocar o motor de financeiras.** Ela existia na versão
P/VP×ROE (bloqueava a fórmula quando `ROE < g + 3 p.p.`) e não foi transportada para o DDM.

Duas coisas se somam nesses casos:

**(a) A mediana atravessa a quebra de série.** O IRB teve ROE de −16,8%, −16,7% e −3,0% na crise
e 17,2%, 7,5%, 4,5% depois. A mediana da série inteira dá **0,8%**, que não descreve nem a
empresa velha nem a nova.

**(b) DDM sobre empresa que quase não distribui e rende pouco converge para zero**, mesmo com
patrimônio real de R$ 66/ação. Matematicamente correto, praticamente inútil.

**Regra restaurada:** se o ROE mediano não supera `g` em 3 p.p., abandona-se o fluxo e ancora-se
no **balanço** — `P/VP mínimo da própria série × VPA`, o menor múltiplo que o mercado já pagou
por aquele patrimônio. Convicção ★☆☆ obrigatória, e a tooltip marca a quebra de série quando há
anos de prejuízo na janela. IRBR3: **R$ 8,18 → R$ 25,75**.

**Quarta trava, do mesmo caso:** payout de **um ano só** não é política de dividendos, é um
ponto. O IRB retomou o pagamento em 2026 (payout 48%, DY 2,5%) e o motor tratava esse n=1 como
se fosse mediana de cinco anos. Agora `n < 3` força ★☆☆.

⚠️ **O que a correção NÃO diz:** que o IRB está barato. O lucro caiu de R$ 806 mi (2024) para
R$ 391 mi (2025) e R$ 241 mi (2026) — queda de 70% em dois anos. A retomada do dividendo é real;
a trajetória do lucro é o contrário. O teto corrigido continua abaixo da cotação.

### Telecom entra na tabela de motores

TIMS3 e FIQE3 não tinham motor em lugar nenhum. Passam a usar **EV/EBITDA + Gordon**, igual
utility: infraestrutura, receita recorrente, capex pesado — mesmo perfil econômico.

### `data-pl-hist` foi removido de todas as linhas cobertas

Enquanto existia, `calcularPrecoTeto()` em `js/calculos.js` **recalculava o teto no navegador
e sobrescrevia o valor do motor de setor**. A LEVE3 exibia R$ 45,54 (motor genérico
IPCA+prêmio) em vez dos R$ 30,83 corretos. Duas fontes de verdade para o mesmo número, e
ganhava a errada. **Regra: linha com teto do motor de setor não leva `data-pl-hist`.**

### Quinta trava: quebra de série societária (achada pelo usuário)

O SAUD3 saiu com teto de **R$ 3,71** contra cotação de R$ 14,60. O usuário recusou o número
antes de qualquer conta minha — e estava certo.

**Causa raiz: era outra empresa.** `companies_list` confirma `SAUD3 = BRADSAUDE S.A.`, ticker
anterior **ODPV3 (Odontoprev)**. Na incorporação dos ativos de saúde do Bradesco:

| | 2025 (Odontoprev) | 2026 (Bradsaúde) |
|---|---|---|
| Ações | 544 mi | **2.927 mi** |
| Lucro | R$ 583 mi | R$ 1.054 mi |
| LPA | 1,07 | **0,36** |
| Market cap | R$ 6,1 bi | **R$ 42,7 bi** |

O motor E/P multiplicava o **P/L mediano da Odontoprev** (13,7x) pelo **LPA da Bradsaúde**
(R$ 0,36). Duas empresas diferentes na mesma conta.

**Dois erros somados, e o segundo era de classificação.** O balanço mostra R$ 13,2 bi de
"caixa líquido" sobre R$ 9,9 bi de receita — isso não é caixa industrial, são **reservas
técnicas de seguradora**. A Bradsaúde estava no grupo `IND`. Reclassificada para `FIN`
(P/VP×ROE + Gordon + lucro residual, a mesma régua da PSSA3 e da CXSE3).

**Regra nova (`ano_quebra` / `anos_validos`):** salto de mais de **25% na quantidade de ações
em um ano** marca quebra societária; múltiplos e ROE passam a usar **só os anos posteriores**.
A varredura achou 7 casos: ALOS3 (2022), AXIA3 (2022 e 2025), FLRY3 (2023), IRBR3 (2022),
SAUD3 (2026), SBSP3 (2026), SHUL4 (2022).

Efeito nos tetos: **SAUD3 R$ 3,71 → R$ 8,37**, FLRY3 R$ 17,20 → R$ 16,25, SHUL4 R$ 5,02 →
R$ 3,65.

⚠️ **O que isto NÃO resolve.** Com um único ano válido, a série do SAUD3 não tem mediana — o
"múltiplo próprio" vira o preço de hoje, ou seja, circular. A dispersão entre os três motores
é de 43% e a convicção é ★☆☆ por isso. O teto de R$ 8,37 continua abaixo dos R$ 14,60, e a
leitura honesta é **"não sei precificar esta empresa ainda"**, não "está cara".

⚠️ **Rejeitado: fallback setorial.** Tentei substituir o múltiplo quebrado pela mediana de
pares. No grupo IND o único par sem quebra é a LEVE3 (autopeças, P/L 6,7x) — o teto do SAUD3
caiu para R$ 1,80. Um par não é setor. O fallback continua no código, mas só é acionado com
★☆☆ e depois de esgotada a série própria.

### O que ainda é premissa, não dado

- **IPCA+5,5%** como juro real normalizado e **5,0 p.p.** de prêmio de risco base
- Os **cortes dos ajustes de Ke** (0,25 / 0,50 de CV; R$ 10 bi e R$ 50 bi de tamanho)
- **10 anos** de estágio de crescimento
- As **margens de 10/15/25%** por convicção

Nenhuma dessas foi testada contra retorno futuro — valem as mesmas ressalvas da seção 10.


---

## 12. Corrida de múltiplos — o teste barato (06/09/2026)

`scripts/backtest_multiplos.py` · 30 tickers do Radar · 2021-2026 · 125 observações válidas ·
fonte `data/historico.data.js` (Partnr, B3/CVM), zero chamadas de rede.

**Pergunta:** qual medida de "barato" separou vencedor de perdedor — e o meu motor de
preço-teto ganha de um múltiplo simples?

### Resultado

Retorno total médio 12 meses à frente, terço barato vs terço caro, ranking refeito a cada ano:

| Métrica | n | BARATO | CARO | spread | ρ | t | anos + |
|---|---|---|---|---|---|---|---|
| **L/P (earnings yield)** | 120 | **24,9%** | 16,1% | **+8,8 p.p.** | +0,09 | **+2,63** | **4 de 5** |
| Dividend yield | 125 | 20,0% | 14,7% | +5,3 p.p. | +0,11 | +1,01 | 3 de 5 |
| MOTOR (margem s/ teto) | 42 | 27,4% | 22,3% | +5,1 p.p. | +0,26 | — | 1 de 2 |
| VP/P (book yield) | 122 | 19,0% | 16,3% | +2,6 p.p. | +0,06 | +0,81 | 3 de 5 |
| EBIT/EV | 89 | 18,2% | 15,7% | +2,5 p.p. | +0,05 | +0,87 | 3 de 5 |
| EBITDA/EV | 89 | 14,8% | 17,6% | **−2,8 p.p.** | +0,01 | −0,77 | 3 de 5 |
| *baseline (comprar as 30)* | 125 | *19,0%* | | | | | |

### Leitura

**O L/P venceu, e venceu com folga.** Maior spread, único com t acima de 2, e positivo em 4
dos 5 anos. É exatamente o critério nº 1 do Radar — o único que já tinha backtest.

**O EV/EBITDA foi o pior, e isso contradiz a literatura** (Gray & Vogel encontram EV/EBIT
vencendo nos EUA). O EBIT/EV também ficou fraco aqui. Hipótese honesta: com só 89 observações
e 13 financeiras fora (não têm EV), a amostra de EV/EBITDA é pequena e enviesada para cíclicas
e utilities, onde o múltiplo se move com o ciclo e não com o preço.

**O DY tem o maior spread MEDIANO (+13,5 p.p.)** contra +4,1 do L/P, apesar de um spread médio
menor. Isso significa que ele acerta com mais frequência e erra grande de vez em quando —
perfil compatível com carteira de dividendos.

**O MEU MOTOR NÃO GANHOU.** 42 observações, apenas 2 anos com dados suficientes, spread médio
de +5,1 p.p. mas spread mediano de +0,8 p.p., e positivo em 1 de 2 anos. O terço do meio rendeu
MAIS que o terço barato (33,9% contra 27,4%) — o ranking não é monotônico, que é o sintoma de
ruído. **Seis motores, um Ke ajustado por risco, fade de vantagem competitiva em 10 anos e
juro real normalizado não bateram `1 ÷ P/L`.**

### ⚠️ O que este teste NÃO prova

- **Viés de sobrevivência puro.** As 30 empresas foram escolhidas hoje. Nenhuma quebrou porque
  se tivesse quebrado não estaria no Radar.
- **n efetivo é 5, não 125.** As observações do mesmo ano pegam o mesmo mercado. Por isso o t
  é calculado sobre os SPREADS ANUAIS. Com 4 graus de liberdade, 5% exigiria |t| > 2,78 —
  **nem o L/P chega lá** (2,63).
- **Só 5 anos, todos de juro alto.** Não há um ciclo de queda de Selic completo na janela.

### Dois erros de dado achados pelo próprio teste

**(1) IRBR3 com +5.051% de retorno em 2022→2023.** Não foi retorno: foi **grupamento de ações**
(R$ 0,86 → R$ 44,30). O detector `ano_quebra` do motor só enxergava AUMENTO de ações
(incorporação, follow-on) e estava cego para grupamento, que é o caso que *explode* o retorno
em vez de amassar o múltiplo.

**(2) A quebra e o artefato de preço não caem no mesmo ano.** A CVM reapresenta o LPA na base
nova (IRB 2022: −7,66 contra −0,54 de 2021), então a quebra aparece em 2022 — mas a série de
preços do Partnr **não é ajustada retroativamente**, e o salto cai em 2022→2023.

Correções: a quantidade de ações passa a ser derivada de `lucro ÷ LPA` e testada em **ambas as
direções** (±25%), e a transição é descartada se houver quebra em **qualquer um dos dois anos**.
A mesma cegueira existe no `ano_quebra` de `scripts/motor_teto.py` — **ainda não corrigida lá**.

### Consequência prática

O L/P vs Selic (critério nº 1) é o único elo da metodologia com evidência a favor, e sai
reforçado. O preço-teto continua fora da pontuação — agora não só por instabilidade, mas
porque **foi medido e não venceu um múltiplo de uma linha**.


---

## 13. Duas correções que saíram do backtest (06/09/2026)

### 13.1 Cosmético vs real — eu tinha diagnosticado ao contrário

⚠️ **Registro de erro meu.** Eu disse ao usuário que `ano_quebra` era "cego para grupamento".
**Falso.** Ele usa `abs(b/a − 1)`, que é simétrico, e detecta o grupamento do IRBR3
(1.264 mi → 82 mi ações) sem dificuldade. O problema era outro.

**O bug real:** o detector tratava como iguais dois eventos que não são iguais.

| | Desdobramento / grupamento | Incorporação / emissão |
|---|---|---|
| Ações | mudam | mudam |
| Negócio | **igual no dia seguinte** | **outro** |
| Múltiplos históricos | **atravessam intactos** | **não descrevem nada** |
| Exemplo | SBSP3 5:1 — preço R$133,39→R$26,19, P/VP 2,59→1,96 | SAUD3 — ações +437%, lucro +81% |

Descartar o histórico no caso cosmético é **jogar dado bom fora**. O motor fazia isso.

**Teste novo, duas condições, ambas necessárias:**

1. **Negócio parado** — receita dentro de ±25% (lucro como segunda opção, para banco e
   seguradora sem linha de receita)
2. **Valor de mercado contínuo** — `(preço_novo/preço_velho) × (ações_novas/ações_velhas) ≈ 1`.
   O SBSP3 dá `0,196 × 4,99 = 0,98` ✓

A primeira versão usava só a condição (1) e classificou a **fusão Aliansce+brMalls** (ALOS3
2022, ações ×2,15) como cosmética — a receita subiu só 19% porque a fusão fechou no meio do
ano. Um teste que aprova uma fusão de R$ 10 bi como "só mudou a unidade" não serve. A condição
(2) reprova. O IRBR3 também é reprovado, e corretamente: foi grupamento **e** follow-on no
mesmo ano, e o produto dá 3,6 — entrou capital novo.

**Na dúvida o teste reprova.** Descartar história boa custa convicção (★☆☆); misturar duas
empresas na mesma conta custa um teto errado.

### 13.2 P/L derivado quando a base não traz o campo

O **SHUL4** não tem o campo `pl` na base Partnr em nenhum dos 6 anos. `teto_ep` caía direto no
fallback setorial — cujo único par sem quebra no grupo IND é a **LEVE3, autopeças**. O teto do
Schulz vinha de uma empresa que não é ele.

Mas `preco` e `lpa` estão lá, nos 6 anos: 8,41/1,08 = 7,8x · 4,71/0,76 = 6,2x · … A série
existia inteira, só não estava pré-calculada. **Derivar `preço ÷ (LPA × fator_unit)` é
aritmética sobre dado da mesma fonte, não estimativa.**

| | antes | depois |
|---|---|---|
| Âncora | P/L da LEVE3 (6,7x) | P/L do próprio SHUL4 (mediana de 6 anos) |
| Convicção | ★☆☆ | **★★★** |
| Teto | R$ 3,65 | **R$ 4,61** |
| Margem vs R$ 4,45 | −22% | **+3%** |

---

## 14. L/P + DY combinados — testado e REJEITADO

Hipótese: o L/P captura o lucro que a empresa **gera**, o DY o caixa que ela **entrega**.
Armadilha de valor (barata no lucro, mesquinha no dividendo) e payout insustentável (generosa
no dividendo, cara no lucro) são erros diferentes — em tese um filtro corrigiria o outro.

Combinação por **rank médio** (percentil dentro do ano em cada métrica, média dos dois). Sem
peso escolhido por mim, no espírito do Greenblatt — é por isso que é difícil de superajustar.

| Estratégia | BARATO | CARO | spread | spr. mediano | t | anos + |
|---|---|---|---|---|---|---|
| **L/P sozinho** | **24,9%** | 16,1% | **+8,8 p.p.** | +4,1 p.p. | **+2,63** | **4 de 5** |
| L/P + DY (rank médio) | 19,1% | 15,1% | +4,0 p.p. | +6,1 p.p. | +0,81 | 3 de 5 |

Ano a ano da combinação: `+13,9%` · `−5,6%` · `+0,5%` · `−7,1%` · `+20,3%`

**Rejeitado.** Acrescentar o DY **cortou o spread pela metade** e derrubou o t de 2,63 para
0,81. O terço barato da combinação rendeu MENOS (19,1%) que o terço barato do L/P sozinho
(24,9%), e o terço do meio rendeu mais que o barato — ranking não-monotônico, sintoma de ruído.

Isto repete o padrão do backtest anterior, em que somar ROE e alavancagem **piorou** o
resultado (21,9% → 20,0%), e a conclusão do estudo Fama-French da B3, em que o eixo valor é
significativo e o de rentabilidade não.

> **Três tentativas de acrescentar um segundo eixo ao L/P, três pioras.** O padrão já não é
> coincidência: nesta amostra, o que funciona é `1 ÷ P/L` sozinho.

⚠️ Continua valendo tudo da seção 12: viés de sobrevivência, n efetivo de 5 anos, e nem o
vencedor é estatisticamente significativo (t 2,63 contra 2,78 exigidos).


---

## 15. Dividendo por ação — a inversão (06/09/2026)

**Achado pelo usuário**, na ALOS3: *"o LPA é 2,04, o payout 84%, e o dividendo por ação 2,30 —
esse cálculo está certo?"* `2,04 × 0,84 = 1,71`. A conta dele estava certa; a tabela não fechava.

### A causa raiz era pior que a linha

O DPS não era calculado a partir do lucro. Era `data-dy-proj × cotação`. Três consequências:

1. **O dividendo por ação flutuava com o preço da ação.** Papel sobe 10%, a tabela passa a
   dizer que a empresa vai pagar 10% mais dividendo. É o mundo ao contrário — o dividendo é
   decisão da empresa sobre o lucro dela, não sobre a cotação.
2. **O DY ficava congelado**, quando é justamente ele que deve se mover com o preço.
3. **O payout era texto estático**, escrito na análise, sem relação viva com nenhum dos dois.

As três células falavam de bases diferentes e nada no app percebia.

### A regra nova

```
DPS = LPA exibido × payout      ← fundamento, NÃO depende do preço
DY  = DPS ÷ cotação             ← deriva, e varia com o preço, como deve
```

Implementada em `atualizarDivDY()` (`js/calculos.js`), chamada dos três pontos que antes
duplicavam a fórmula antiga (`calculos.js`, `cotacoes.js`, `main.js`).

A linha precisa declarar **`data-payout`**. Sem ele, a rota antiga continua valendo e a coluna
de payout mostra "—" em vez de mentir sobre uma relação que não existe.

### `data-lpa-manual` deixou de ser opcional

O payout de cada análise foi aplicado a **uma base específica** — FFO por ação no shopping,
LPA FY2025 na indústria, LPA 2026E na seguradora. Sem `data-lpa-manual="true"`, o sync do
HIST_SEED troca essa base por baixo e quebra a conta de novo. **Foi exatamente o que aconteceu
com a ALOS3:** o R$ 1,64 curado virou R$ 2,04 do Partnr, e o R$ 2,30 ficou órfão.

### As 12 linhas corrigidas

| Ativo | LPA (base declarada) | payout | DPS | DY |
|---|---|---|---|---|
| **ALOS3** | **2,73** ← FFO/ação, não lucro contábil | 84% | 2,29 | 8,81% |
| MULT3 | 2,70 | 50% | 1,35 | 5,03% |
| CPFE3 | 4,98 | 75% | 3,74 | 8,83% |
| LEVE3 | 2,82 | 85% | 2,40 | 7,44% |
| RANI3 | 0,65 | 35% | 0,23 | 2,92% |
| CXSE3 | 1,43 | 90% | 1,29 | 6,92% |
| BBSE3 | 4,46 | 90% | 4,01 | 10,79% |
| FIQE3 | 0,55 | 45% | 0,25 | 5,44% |
| ITUB3 | 4,25 | 74% | 3,15 | 7,55% |
| TIMS3 | 1,81 | 92% | 1,67 | 9,02% |
| BMEB4 | 6,50 | 28% | 1,82 | 3,01% |
| **IRBR3** | 2,94 | 25% | **0,73** | **1,44%** |

Todas fecham exatamente. A **ALOS3** passa a mostrar **FFO por ação (R$ 2,73)** na coluna 7 —
shopping não paga dividendo de lucro contábil, e o lucro contábil dela vai de R$ 0,39 a R$ 6,09
por ação em três anos. O lucro contábil continua visível no P/L, que a própria linha já marcava
como não-decisório.

⚠️ **O IRBR3 caiu de DY 3,5% para 1,44%** e é a mudança mais dura. O DY de 3,5% era premissa
publicada; `25% (payout mínimo estatutário) × LPA TTM R$ 2,94` dá R$ 0,73. Os dois números
nunca conviveram — agora um deles teve que ceder, e cedeu o que não tinha conta por trás.
Dividendos retomados em fev/2026 após 5,5 anos: **n=1**, sem histórico para testar nada.

### ⚠️ Dois defeitos que esta correção NÃO cobre

**(1) UNITS na coluna de LPA.** As 17 linhas sem `data-payout` continuam com o DPS derivado do
preço, e três delas são units, onde o LPA exibido é **por ação** e o DPS é **por unit**:

| Ativo | LPA na tela | DPS | payout aparente | payout real |
|---|---|---|---|---|
| KLBN11 | 0,42 | 0,98 | **233%** | ~47% (÷4 ações/unit) |
| SANB11 | 2,02 | 1,91 | **95%** | ~47% (÷2) |
| BPAC11 | 1,82 | 1,27 | **23%** | ~70% (÷3) |

É a **sexta** aparição do mesmo erro de units neste projeto. A correção definitiva é aplicar
`FATOR_UNIT` na coluna 7, não caso a caso.

**(2) SAUD3 com DPS R$ 0,76 sobre LPA R$ 0,38** — payout aparente de 200%, e o SAUD3 não é
unit. Ou o DY publicado está errado, ou o LPA pós-incorporação ainda não estabilizou. Não
resolvido.


---

## 16. Units na coluna de LPA, e o DY suprimido do SAUD3 (06/09/2026)

### 16.1 A sexta aparição do erro de units — corrigida no lugar certo

`FATOR_UNIT` agora existe em `js/config.js`, espelhando a tabela de `scripts/motor_teto.py`:

| Unit | Composição | Ações/unit |
|---|---|---|
| KLBN11 | 1 ON + 4 PN | **5** |
| SANB11 | 1 ON + 1 PN | **2** |
| BPAC11 | 1 ON + 2 PN | **3** |

O Partnr reporta LPA **por ação**; preço e dividendo negociados são **por unit**. A coluna 7
misturava as duas bases.

| Ativo | LPA antes | LPA agora | DPS | payout aparente antes | agora |
|---|---|---|---|---|---|
| SANB11 | 2,02 | **4,04** | 1,91 | **95%** | **47%** |
| KLBN11 | 0,42 | **2,10** | 0,98 | **233%** | **47%** |
| BPAC11 | 1,82 | **5,46** | 1,27 | 23% | **23%** |

O BPAC11 confirma por fora: o motor de preço-teto calcula payout mediano de **24%** direto da
DFP, e a coluna agora mostra 23%. Antes mostrava a mesma coisa por acidente — o erro de units
e o payout baixo se cancelavam.

A correção entrou em **dois lugares**, porque há dois caminhos até a célula:
- `js/fundamentos.js` — aplica o fator ao sincronizar com o HIST_SEED
- `data/radar-rows.data.js` — o valor estático das 3 linhas (elas têm `data-lpa-manual`, então
  o sync não passa por cima)

⚠️ E uma anotação **errada** foi corrigida: as três linhas diziam *"derivado do P/L da fonte —
resolve a base de units"*. Não resolvia. `29,85 ÷ 1,92 = 15,5x` é o P/L **não corrigido** do
SANB11; o corrigido é 7,7x. A nota afirmava uma correção que o número não tinha.

### 16.2 SAUD3 — DY e dividendo suprimidos

O DY de 5,21% da base implicava **R$ 0,76/ação de dividendo sobre LPA de R$ 0,38** — payout de
**200%**, e a Bradsaúde não é unit, então não havia fator inteiro para explicar.

**Causa: a mesma quebra de série.** Os dividendos do período foram pagos pela **ODONTOPREV**,
com 545 mi de ações; o DY os divide pelo preço da **BRADSAUDE**, com 2.927 mi. Numerador de uma
empresa, denominador de outra — exatamente o defeito que já tinha produzido o teto de R$ 3,71.

As duas células passam a mostrar **"—"** com a explicação na tooltip. **Célula vazia é melhor
que número errado.** O valor volta quando houver um exercício completo na base nova.

### 16.3 Estado final da auditoria — 30 de 30

Todas as linhas do Radar têm agora payout implícito (`DPS ÷ LPA`) dentro de faixa plausível.
As 12 com `data-payout` fecham exatamente; as demais declaram "—" no payout em vez de afirmar
uma relação que não existe.

⚠️ **Fica um caso não resolvido:** o **SHUL4** tem DPS de R$ 0,04 e DY de 0,94%, um payout
implícito de 5% — baixo demais para a Schulz. Provável DY desatualizado na linha, não erro
estrutural. Não investigado.


---

## 17. O motor passa a poder dizer "não sei" (06/09/2026)

Três correções, todas com causa nomeada antes de escrever uma linha de código.

### 17.1 A trava de quebra de série existia em 2 dos 6 motores

`teto_fin` e `teto_ep` chamavam `anos_validos()`. **`teto_ev`, `teto_bazin` e os motores de
holding e shopping usavam a série inteira** — privatização e incorporação incluídas.

⚠️ **Registro de erro meu:** eu disse ao usuário que o SBSP3 caía no fallback setorial por
quebra de série. Não caía. **O motor de utility nunca consultou a função** — sempre usou os 6
anos. A correção passa a restrição para dentro de `serie()`, que é por onde todos os motores
leem histórico.

### 17.2 `mediana_com_tendencia` chega ao motor de utility

Eu havia escrito nesta metodologia que **não** aplicaria a regra fora de financeiras,
argumentando que *"em cíclica a mediana precisa cobrir pico E fundo"*.

**O argumento vale para cíclica de commodity, e eu o estendi para utility sem verificar.**
Utility não oscila com preço de commodity — ela faz **re-rating estrutural** (privatização,
revisão tarifária). A CLSC4 é a prova: EV/EBITDA subiu **3,15x → 5,70x de forma monotônica**
em 6 anos. A mediana (≈4,2x) descreve uma empresa que deixou de existir.

Junto entrou uma segunda trava: **dispersão do EBITDA**. Se o EBITDA da própria empresa varia
mais de 2x dentro da janela, cada ano foi medido contra um denominador diferente e a mediana do
múltiplo não descreve nada. O AXIA3 é o caso — EBITDA de R$ 8,5 bi a R$ 26,2 bi, EV/EBITDA de
6,01x a 27,50x. O motor recusa em vez de devolver número.

### 17.3 `LIM_MARGEM` — recusar em vez de rebaixar

Existia uma guarda: margem além de ±100% rebaixava a convicção para ★☆☆. **Rebaixar não
resolve.** O leitor via `R$ 51,72 ★☆☆` e lia um preço. A guarda agora **recusa**:

> Margem além de ±100% não vira teto. Vira célula vazia, com o motivo escrito na tooltip.

É a regra que o resto do projeto já seguia — *célula vazia é melhor que número errado* — e que
só o preço-teto não obedecia.

⚠️ **O limite é arbitrário e eu o declaro como tal.** 100% de margem significa que o motor acha
que o papel vale metade (ou o dobro) do que o mercado paga. Divergências dessa ordem existem de
verdade; mas com 6 anos de série e um Ke estimado eu não distingo convicção contrária ao mercado
de motor quebrado — e **nas 5 vezes em que isso aconteceu neste projeto, era motor quebrado nas 5**.

⚠️ **Segundo erro meu, na própria trava:** a primeira versão dividia pela cotação em vez de pelo
teto. Dividir pelo preço limita a margem negativa a −100% por construção, e o SBSP3 (−512% na
régua certa) aparecia como −84% e passava direto. A trava existia e não travava nada.

### 17.4 Resultado

| | antes | depois |
|---|---|---|
| Tetos publicados | 25 | **20** |
| Recusas explícitas | 0 | **5** |
| Margens além de ±100% | **5** | **0** |

**Recusados:** SBSP3 (−512%), FIQE3 (−195%), IRBR3 (−121%), CLSC4 (−104%) e AURE3 (LPA negativo
em 3 dos 6 anos, dívida 3,2 → 20,0 bi numa aquisição).

**Corrigido sem recusa:** o **AXIA3** foi de −121% para **−23%** — a trava de quebra de série
cortou os anos pré-reestruturação, e o EV/EBITDA saiu de cena pela dispersão do EBITDA.

Distribuição final: **7 ★★★ · 6 ★★☆ · 7 ★☆☆ · 5 recusas.**

⚠️ **O que continua valendo da seção 12:** nenhum destes motores venceu `1 ÷ P/L` no backtest.
Esta seção deixa o motor **coerente**, não **validado**. O preço-teto segue fora dos critérios
de decisão — é disciplina e detector de absurdo, não veredicto.


---

## 18. Holdings ganham motor, e o EV/EBITDA fica mais exigente (06/09/2026)

Pergunta do usuário: *"o preço-teto de todas as ações está preenchido com metodologia
correta?"* A resposta era **não — 20 de 30**. Cinco eram manuais, herdadas de análises antigas
sem régua comum, e duas das 20 eu não defendia. Esta seção corrige as duas frentes.

### 18.1 Motor de holding — paridade com a investida principal

ITSA4 e BRAP4 estavam manuais, com a justificativa de que *"NAV exige o valor de mercado das
investidas, que a base não traz"*. **Traz, para estes dois casos: a investida principal está no
mesmo Radar.**

| Holding | Investida | Razão preço/preço, 2021→2026 |
|---|---|---|
| ITSA4 | ITUB3 | 0,468 · 0,389 · 0,360 · 0,328 · 0,321 · 0,318 ← **desconto abrindo** |
| BRAP4 | VALE3 | 0,321 · 0,334 · 0,332 · 0,304 · 0,277 · 0,285 ← estável |

Essa razão **é o desconto de holding medido pelo próprio mercado**, ano a ano, sem eu estimar
NAV nenhum. Ela passa por `mediana_com_tendencia` (a da Itaúsa tem tendência clara) e multiplica
o **preço justo da investida calculado pelo próprio motor** — não o preço de mercado dela. A
holding herda a avaliação fundamentalista da controlada, descontada pelo desconto que o mercado
historicamente pratica.

| Ativo | antes (manual) | agora | conv | cotação |
|---|---|---|---|---|
| ITSA4 | R$ 12,31 | **R$ 10,00** | ★☆☆ | R$ 13,68 |
| BRAP4 | R$ 19,30 | **R$ 16,59** | ★★☆ | R$ 22,95 |

⚠️ **Isto NÃO é um NAV, e a convicção é limitada a ★★☆ por isso.** Não enxerga os demais ativos
da Itaúsa (Alpargatas, Dexco, NTS, Copa), não enxerga a dívida da holding, e **não sabe dizer se
o par inteiro está caro**: se o motor errar no ITUB3, erra na ITSA4 junto, na mesma direção.

### 18.2 EV/EBITDA: mínimo de 3 anos e dispersão de 1,7x

O **AXIA3** tinha passado com teto de R$ 45,19 e **EV/EBITDA-alvo de 20,39x**, num setor cujos
pares rodam entre 5x e 9x. Como: a trava de quebra de série cortou a janela para **2 anos**, e
com dois pontos não existe mediana — existe extrapolação. Ele escapou da trava de dispersão por
**0,1** (EBITDA variou 1,9x; o limite era 2,0x).

Dois cortes novos, ambos só para não-cíclicas:
- **mínimo de 3 anos válidos** de múltiplo e de EBITDA
- **dispersão do EBITDA de 2,0x → 1,7x**

⚠️ **1,7x também é arbitrário e eu declaro:** é o valor que reprova o caso que eu já sabia estar
errado. Não foi testado contra retorno.

O AXIA3 passa a **recusa**. O **PASS3** perdeu o motor de EV/EBITDA pelo mesmo corte (IPO em
mai/2026, série curta) e ficou só com o Gordon: teto R$ 15,61 → **R$ 12,29**, ★☆☆.

### 18.3 Estado final do Radar

| Origem | Antes de hoje | Agora |
|---|---|---|
| ✅ Motor de setor, régua única | 20 | **21** |
| ⛔ Recusa explícita, motivo escrito | 5 | **6** |
| ⚠️ Manual, sem motor declarado | 5 | **3** |

**Os 3 manuais restantes:** ALOS3 e MULT3 (shopping — exige cap rate de transação, que não
existe em nenhuma base a que eu tenho acesso) e ROXO34 (BDR de banco digital sem histórico
comparável).

Convicção das 21: **7 ★★★ · 7 ★★☆ · 7 ★☆☆.**

⚠️ Continua valendo o de sempre: **coerente não é validado**. Nenhum destes motores venceu
`1 ÷ P/L` no backtest da seção 12, e o preço-teto segue fora dos critérios de decisão.


---

## 19. Consenso de N métodos — 30 de 30 (06/09/2026)

**O usuário desmontou a arquitetura anterior**, e estava certo:

> *"Não é porque o motor trouxe o número errado que vamos recusar. Toda ação tem que ter um
> jeito de calcular o preço justo. Precisamos identificar o melhor jeito pra cada empresa —
> por mais que o motor tenha mais de uma metodologia por empresa, pra uma validar a outra."*

Meu erro tinha dois níveis. **Recusar não ajuda quem decide** — "não sei" é honesto sobre a
minha incerteza e inútil para a pergunta que a tabela existe para responder. E o problema nunca
foi "esta empresa não tem valor calculável": foi **"o método que EU escolhi para ela não serve"**.
A resposta é trocar de método, não apagar a linha.

### A nova arquitetura

Todo ativo passa por **todos os métodos que o dado dele permite**, e o resultado é a **MEDIANA**:

| Método | Depende de | Serve quando |
|---|---|---|
| E/P histórico | lucro | lucro estável |
| EV/EBITDA | EBITDA | operação previsível |
| Gordon/Bazin | lucro + payout | distribui de forma constante |
| P/VP × ROE + lucro residual | patrimônio + ROE | financeiras |
| **P/VP** (novo, universal) | **só patrimônio** | **prejuízo, lucro contábil distorcido** |
| **EV/Receita** (novo, universal) | **só receita** | **margem colapsando, EBITDA volátil** |
| Paridade com a investida | preço da controlada | holdings |
| **Pares do setor** (novo, último recurso) | nada da empresa | série curta ou quebrada |

**Mediana, não média.** A mediana ignora o método que enlouqueceu; a média não ignorava — foi
assim que a CLSC4 saiu em R$ 102 (média de um EV/EBITDA de R$ 136 com um Gordon defeituoso de
R$ 68), um número que **nenhum dos dois métodos defendia**.

A convicção passa a medir **dispersão entre métodos**, que é a incerteza real: ★★★ = 3+ métodos
dentro de 20%; ★★☆ = 2+ ou até 40%; ★☆☆ = método único ou grande divergência.

### Quebra operacional — o buraco que a SBSP3 mostrou

`ano_quebra` só enxergava a base **acionária**. A privatização da Sabesp em 2024 não emitiu ação
nenhuma, e mesmo assim o EBITDA foi de **R$ 9,1 bi para R$ 18,2 bi (+99%)** e a receita de
R$ 25,6 bi para R$ 36,1 bi (+41%). Multiplicador mediano de 6 anos misturava estatal com privada.

Regra nova: salto de **+50% no EBITDA E +25% na receita** no mesmo ano marca mudança de regime.
Exigir os dois evita confundir com um ano bom de margem. SBSP3: teto **R$ 4,28 → R$ 21,05**.

### Três correções de conta que apareceram no caminho

**1 · Contagem de papéis explodindo.** `lucro ÷ LPA` é instável quando o lucro se aproxima de
zero. A KLBN11 tem LPA de R$ 0,09 em 2026 e o teto saiu em **R$ 3,46 contra cotação de R$ 19,40
(−460%)** — erro de contagem, não de valuation. Agora é a **mediana** da contagem ao longo dos
anos válidos.

**2 · Units, sétima aparição.** `vpa()` devolvia patrimônio por **ação**, e o P/VP-alvo já vinha
por **unit**. Multiplicar os dois errava por um fator inteiro (KLBN11: R$ 3,96 em vez de
R$ 19,80). **A conversão agora mora dentro de `vpa()`, e só ali.**

**3 · Método votando duas vezes.** `teto_fin` já usa P/VP como um dos seus três motores internos;
somar `teto_pvp` de novo era a mesma leitura contando dobrado — no ITUB3 os dois davam
exatamente R$ 41,51, o que denunciou a duplicata.

### Métodos excluídos de propósito, por tipo de empresa

**Cíclica de commodity — fora E/P e Gordon.** A KLBN11 tem LPA de R$ 0,09 no fundo do ciclo da
celulose; E/P e Gordon davam R$ 4,62 e R$ 2,21 contra cotação de R$ 19,40. Não é a Klabin valendo
um quarto — é o lucro de **um ano ruim** tratado como capacidade normal. Ficam EV/EBITDA sobre a
**média de 6 anos**, EV/Receita e P/VP.

**Holding — fora E/P e Gordon.** O "lucro" de holding é equivalência patrimonial e herda o ciclo
da controlada amplificado. A BRAP4 dava E/P R$ 7,23 e Gordon R$ 8,36 contra paridade R$ 19,05 e
P/VP R$ 22,95 — o lucro dela caiu de R$ 8,1 bi para R$ 0,6 bi acompanhando o minério.

**Peer comp só quando não sobrou nada.** A primeira versão acionava com menos de 2 métodos, e o
múltiplo de pares acabou votando nas financeiras — o BBSE3 caiu de R$ 29,04 para R$ 17,76 por um
P/VP mediano que nada tem a ver com uma seguradora de ROE 79%. **Último recurso quer dizer último.**

### Resultado

| | antes | agora |
|---|---|---|
| Com preço-teto calculado | 21 | **30 de 30** |
| Recusas | 6 | **0** |
| Manuais sem motor | 3 | **0** |

Convicção: **7 ★★★ · 8 ★★☆ · 15 ★☆☆.**

Casos resolvidos que estavam sem número: **SBSP3 R$ 21,05** · **CLSC4 R$ 90,32** ·
**AURE3 R$ 14,48** (P/VP dos pares — no múltiplo de EV a dívida de R$ 20 bi contra EBITDA de
R$ 3,2 bi consome o equity inteiro, o que é informação real sobre a empresa) · **FIQE3 R$ 3,66** ·
**AXIA3 R$ 22,61** · **IRBR3 R$ 25,75** · **ALOS3 R$ 19,61** · **MULT3 R$ 24,20** ·
**ROXO34 R$ 3,12**.

⚠️ **Três seguem com margem além de ±100%** — AXIA3 (−146%), IRBR3 (−121%) e ROXO34 (−297%).
Não são mais recusas: são números publicados com ★☆☆ e aviso de MARGEM EXTREMA na tooltip. O
ROXO34 é o mais frágil de todos: 1 ano de base, avaliado pelo P/VP mediano de bancos brasileiros
tradicionais, o que ignora o crescimento e o ROE que justificam o prêmio do Nubank.

⚠️ **E o de sempre:** nenhum destes métodos venceu `1 ÷ P/L` no backtest da seção 12. Agora o
motor é **completo e coerente**. Continua **não validado**.


---

## 20. Payout calculado para todas as empresas com série (06/09/2026)

Pergunta do usuário: *"por que tem empresa que não tem payout?"* — e depois: *"então calcule o
payout das que não têm e coloque isso no motor."*

### Como é calculado: por identidade, não por estimativa

```
DY × P/L = (DPS ÷ Preço) × (Preço ÷ LPA) = DPS ÷ LPA = payout
```

O preço **se cancela**. Uso DY e P/L porque os dois vêm prontos do Partnr — uma fonte, uma
conta, zero estimativa minha. ⚠️ Em units, o P/L do Partnr divide preço-da-unit por LPA-por-ação
e sai inflado pelo fator: sem corrigir, o BPAC11 dava **72%** em vez de 23%.

### Duas tentativas erradas antes da que ficou

**(1) Mediana simples** — tinha o mesmo defeito que eu já havia corrigido no ROE e no P/VP e
não tinha trazido para cá. O ITUB3 denuncia: `22% · 22% · 30% · 50% · 112% · 68%`. A mediana dá
**40%**; a análise da linha dizia 74%. O banco mudou de política no meio da série.

**(2) Mediana com correção de tendência** — piorou. Nas cíclicas a metade **recente** é
justamente onde estão os anos de lucro deprimido: KLBN11, VALE3, SBSP3, ALOS3 e BRAP4 todas
bateram no teto de 100%. A KLBN11 tem P/L de **43,67x** em 2026 (fundo do ciclo da celulose) e
isso devolve payout de **220%** sem a empresa ter distribuído nada de anormal — **o denominador
é que sumiu**.

**(3) Razão de ACUMULADOS — a que ficou.** `Σ dividendos ÷ Σ lucros` da janela válida. Um ano de
lucro perto de zero contribui pouco para os **dois** lados e não domina. É também como a política
é escrita na prática ("distribuímos X% do lucro"), medida ao longo do ciclo. Anos de prejuízo
saem dos dois lados. Teto de 100%.

### 13 linhas ganharam payout

| Ativo | Payout | Anos | DY antes | DY agora |
|---|---|---|---|---|
| **PETR4** | **74%** | 6 | 6,24% | **13,59%** |
| VALE3 | 66% | 6 | 6,26% | 8,06% |
| SBSP3 | 64% | 3 | 10,67% | 7,02% |
| BRAP4 | 60% | 6 | 9,53% | 11,07% |
| KLBN11 | 54% | 6 | 5,04% | 5,83% |
| ITSA4 | 54% | 6 | 9,94% | 6,78% |
| SANB11 | 53% | 6 | 6,39% | 7,21% |
| PSSA3 | 44% | 6 | 5,07% | 5,61% |
| FLRY3 | 75% | 4 | 4,59% | 4,96% |
| BRSR6 | 34% | 6 | 9,64% | 10,05% |
| CLSC4 | 29% | 6 | 5,19% | 4,15% |
| BPAC11 | 23% | 6 | 2,19% | 2,21% |
| SHUL4 | 6% | 6 | 0,94% | 0,95% |

⚠️ **O PETR4 é o caso a ler com cuidado.** Os 74% são o que a Petrobras **de fato** distribuiu
entre 2021 e 2026 — mas a janela inclui a distribuição extraordinária de 2022 (DY de **64,98%**
naquele ano). A política atual é ~45% de (FCO − capex). O DY de 13,59% descreve o passado
recente, não um compromisso da empresa.

⚠️ **O SHUL4 com 6% valida um alerta anterior.** Eu tinha flagrado o DPS de R$ 0,04 como
"provável DY desatualizado". Não era: a Schulz distribui mesmo ~6% do lucro.

### Cinco continuam sem payout, de propósito

AURE3 (0 anos utilizáveis — prejuízo em 3 dos 6), ROXO34 e SAUD3 e PASS3 (1 ano cada) e AXIA3
(2 anos). **Um ano não é política de dividendos, é um ponto.** Exijo 3 anos.

### O que mudou no motor

`payout_mediano()` é usada pelo **Gordon/Bazin** e pelo **P/VP×ROE** (via taxa de retenção), ou
seja, os preços-teto de utilities, telecom e financeiras herdam a correção automaticamente.


---

## 21. Política declarada como RESTRIÇÃO, e o bug do `dy = 0` (06/09/2026)

Proposta do usuário: *"a primeira regra do motor de payout deveria ser o que a empresa declara
em sua política, e depois a mediana entre o que se enquadra."* A intenção está certa — guidance
é compromisso e olha para frente; realizado é passado. **Mas a pesquisa nos RIs desmontou a
aplicação literal.**

### O que a pesquisa achou (06/09/2026, 30 empresas)

**Das 30, só 7 têm compromisso formal acima do mínimo legal. E 4 desses 7 nem usam lucro
líquido como base:**

| Empresa | Política declarada | Base |
|---|---|---|
| PETR4 | 45% | **FCO − capex**, não lucro |
| VALE3 | 30% | **EBITDA ajustado − investimento corrente** |
| KLBN11 | 10-20% | **EBITDA ajustado** |
| TIMS3 | R$ 5,3-5,5 bi (2026) | **valor absoluto em R$** |
| CPFE3 | mínimo 50% | lucro líquido ajustado |
| BRSR6 | 40% | lucro líquido |
| SBSP3 | até 50% (2026-27) | lucro líquido ajustado |

⚠️ **E quatro empresas têm documento chamado "política de dividendos" cujo conteúdo é o mínimo
estatutário de 25% da Lei 6.404** — que toda S.A. brasileira tem: **ITUB3, BBSE3, IRBR3, AURE3**.
Projetar o dividendo do Itaú por 25% seria usar a lei como se fosse a política da empresa.

### O desenho que ficou: restrição, não substituição

> A política entra como **piso ou teto** sobre o realizado, não no lugar dele. O realizado é a
> estimativa; a política é o limite que a empresa se comprometeu a respeitar.

| Tipo | Ação | Casos |
|---|---|---|
| **piso** | `max(realizado, política)` | CPFE3 (69% já acima do piso 50%), **BRSR6 34% → 40%** |
| **teto** | `min(realizado, política)` | **SBSP3 64% → 50%** |
| **estatutário** | usa realizado, marca que os 25% não são meta | ITUB3, BBSE3, IRBR3, AURE3 |
| **outra base** | usa realizado como proxy, declara a conversão impossível | PETR4, VALE3, KLBN11, TIMS3 |
| **não paga** | payout = 0 | ROXO34 |
| **sem política** | realizado puro | as outras 18 |

Cada linha ganhou `data-payout-fonte` e a tooltip diz **qual dos seis casos é**, com a fonte e a
data do documento.

### ⚠️ O bug que a pergunta expôs: `dy = 0` é dado faltando

Fui conferir a CPFE3 para responder e não fechava: **nenhum ano dela tem payout abaixo de 55%**
(110% · 72% · 60% · 55%) e o meu agregado dava **44%**.

Causa: o Partnr traz **DY = 0 em 2025 e 2026** para a CPFL, que **pagou nos dois anos**. O zero
entrava no numerador e o lucro inteiro no denominador.

⚠️ **Eu já tinha tropeçado nesse mesmo zero antes e corrigido só na EXIBIÇÃO** — `js/fundamentos.js`
mostra "—" em vez de "0,0%" justamente por causa da CPFE3. O cálculo continuou comendo o zero.
Agora ano sem DY sai dos dois lados. **CPFE3: 44% → 69%.**

⚠️ **Viés declarado:** empresa que genuinamente não pagou naquele ano também sai da conta, e o
payout fica mais alto que a realidade. É o lado errado menos ruim — tratar dado ausente como
zero produz números que nenhum ano da série sustenta.

### Três defeitos encontrados ao ligar isto no motor

**1 · `teto_bazin` tinha uma CÓPIA da lógica de payout**, com todos os defeitos já corrigidos na
função oficial: sem correção de units, mediana das razões anuais em vez de razão de acumulados,
e `dy=0` tratado como dividendo zero. **Duas fontes de verdade, e a errada alimentava o Gordon
de utilities e telecom.** Agora só existe uma.

**2 · Gordon precisa de piso de payout.** Com payout baixo o modelo desconta um dividendo
minúsculo e **ignora o que a empresa faz com o lucro retido**. O SHUL4 (payout 6%) despencou
para R$ 2,10 contra cotação de R$ 4,45 quando o método entrou na votação. **Abaixo de 20% o
Gordon se retira** em vez de poluir a mediana.

**3 · Sem série de dividendos, o motor inteiro morria.** O IRBR3 retomou dividendos há 1 ano;
`payout = None` matava `teto_fin` e a empresa caía no peer comp bruto (**R$ 84,67** contra
cotação de R$ 56,78). Agora falta de payout cai no **payout mediano dos pares** — premissa
fraca, mas muito menos destrutiva que perder os três motores de valuation por um campo. IRBR3
voltou a R$ 25,75.

### Tetos que se moveram

AXIA3 R$ 22,61 → **R$ 36,91** (★★☆) · ROXO34 R$ 3,12 → R$ 5,58 · LEVE3 R$ 28,04 → R$ 29,12 ·
CPFE3 R$ 40,36 → R$ 38,12 · TIMS3 R$ 18,02 → R$ 17,72 · PASS3 R$ 14,40 → R$ 12,80.


---

## 22. Payout completo — 30 de 30, com a base declarada (06/09/2026)

Pergunta do usuário: *"agora o payout está certo pra todas as empresas?"* A resposta era **não**,
e a auditoria achou três defeitos.

### ⚠️ Defeito 1 — a tela contradizia a metodologia (IRBR3)

A linha do IRB mostrava **25%**, herdado da análise antiga. Na seção 21 **eu mesmo** classifiquei
esses 25% como **mínimo estatutário da Lei 6.404, não política** — e o motor já tinha parado de
usá-los. A tela dizia uma coisa e o cálculo fazia outra.

É a pior categoria de erro deste projeto: **não parece errado.** Corrigido para **47%** (payout
mediano dos pares), com a premissa escrita na tooltip.

### ⚠️ Defeito 2 — 4 linhas escondiam uma premissa que o motor já usava

AURE3, AXIA3, PASS3 e SAUD3 apareciam com "—". Mas o motor **já usava um payout nelas** (dos
pares, ou de 2 anos de série). **Ou eu mostro, ou o motor não deveria usar.** As quatro passam
a exibir, com o rótulo do que são.

### ⚠️ Defeito 3 — payout de 2 anos parecia igual a payout de 6

Um número de 6 anos e um de 2 anos tinham a mesma aparência. É o mesmo problema que o preço-teto
tinha antes das estrelas de convicção. Agora **base com menos de 4 anos, ou vinda de pares,
leva ⚠️ na própria célula**.

### ⚠️ Defeito 4, achado ao implementar — precedência invertida no ROXO34

O Nu Holdings saiu com **47%**: a mediana do payout dos **bancos brasileiros**. O fallback de
pares era consultado **antes** da política declarada, e a Nu Holdings **não paga dividendo
nenhum** — reinveste 100% e, sediada nas Cayman, não está sujeita ao mínimo obrigatório da Lei
6.404. **Um fato declarado tem precedência sobre qualquer inferência por semelhança.** Corrigido
para 0%: o retorno do ROXO34 é integralmente ganho de capital.

### Estado final — hierarquia de confiança do payout

| Base | Quantas | Marca |
|---|---|---|
| Série própria, 4-6 anos | 17 | — |
| Política declarada como piso/teto | 3 | BRSR6, CPFE3, SBSP3 |
| Realizado, política em outra base | 4 | PETR4, VALE3, KLBN11, TIMS3 |
| Realizado, política só estatutária | 2 | ITUB3, BBSE3 |
| Fato declarado (não paga) | 1 | ROXO34 |
| **Base curta (2-3 anos)** | **2** | **⚠️ AXIA3, SBSP3** |
| **Payout dos pares — não é da empresa** | **4** | **⚠️ AURE3, IRBR3, PASS3, SAUD3** |

**6 das 30 carregam ⚠️.** As outras 24 têm base própria de 4 anos ou mais, ou um fato declarado.

⚠️ **O que continua sendo verdade e não some com correção:** o payout realizado descreve o que a
empresa **pagou**, não o que vai pagar. O caso mais gritante é o **PETR4 com 74%** — real para
2021-2026, mas a janela inclui a distribuição extraordinária de 2022 (DY de **64,98%**), e a
política atual é 45% de (FCO − capex). O DY de 13,59% descreve o passado recente, não um
compromisso.


---

## 23. Auditoria de todos os campos do Radar (06/09/2026)

Pedido do usuário: *"valide todos os campos da tabela e garanta que todos estejam de um motor
com racional declarado e que não tem nada na mão. E que esteja tudo preenchido."*

A auditoria varreu 30 linhas × 23 colunas. Achou quatro coisas, e três eram piores que "faltou
tooltip".

### ⚠️ 1 · O rótulo da coluna 4 mentia em 20 das 30 linhas

Ela se chamava **"Lucro 2025 REAL"** e a maioria das linhas trazia o **LTM de 2026**. PETR4
(R$ 133,76 bi), VALE3 (R$ 8,69 bi), KLBN11 (R$ 0,54 bi), SAUD3, AXIA3 e AURE3 batiam exatamente
com o TTM 2T26, não com o exercício fechado de 2025. **Quem lesse a coluna como "o que a empresa
ganhou em 2025" lia errado em dois terços da tabela.**

Renomeada para **Lucro LTM**, e gerada da base para todas.

### ⚠️ 2 · A coluna 5 empilhava duas grandezas diferentes

Em algumas linhas era projeção de 2026 (CPFE3 R$ 6,10 bi); em outras já era lucro **normalizado
de meio de ciclo** (VALE3 R$ 43,26 bi contra LTM de R$ 8,69 bi — **cinco vezes**; KLBN11
R$ 2,51 bi contra R$ 0,54 bi). Duas definições na mesma coluna, ordenáveis juntas.

Passa a ser **Lucro normalizado**, com um motor por setor — o mesmo que já alimentava a TIR real:

| Tipo | Motor |
|---|---|
| indústria / serviço | receita atual × **margem líquida mediana** da série |
| financeira | **ROE mediano × patrimônio líquido** |
| shopping | **FFO** (FCO − capex) |
| onde o Partnr publica lucro recorrente | usado direto |

E a coluna 6 muda com ela: era "crescimento projetado", vira **distância do normalizado**
(`LTM ÷ normalizado − 1`). **Não é previsão, é diagnóstico de ciclo.** A KLBN11 com −84% não vai
cair 84%: está 84% abaixo do próprio padrão. A BPAC11 com +69% está ganhando acima dele.

### ⚠️ 3 · Um TERCEIRO motor disputava as mesmas células

`calcularLucroEstimado()` projetava lucro por **CAGR de 2 anos capado por setor** e escrevia nas
colunas 4 e 5 sempre que a linha não tivesse `data-lucro-manual`. A CPFE3 exibia R$ 5,7 bi /
R$ 6,1 bi (CAGR) em vez dos R$ 6,29 bi / R$ 6,05 bi do motor de setor.

> **Terceira vez que este padrão aparece neste projeto.** Antes foi o `data-pl-hist`
> recalculando o preço-teto por cima do motor, e o payout duplicado dentro do `teto_bazin`.
> **Quando duas rotinas podem escrever a mesma célula, a que sobrevive é a última a rodar, não
> a mais correta.** A função foi aposentada (mantida como código morto documentado).

### ⚠️ 4 · O JS destruía as tooltips que o gerador escrevia

Várias colunas apareciam sem ⓘ **mesmo tendo tooltip no HTML**: `cell.textContent = ...` apaga o
`<span class="col-tip">` junto com o valor. **De nada adianta gerar o racional se o primeiro
recálculo o remove.** Entrou `_celTip()`, que guarda a tooltip original no dataset e a reanexa
em toda reescrita.

### O que passou a ser gerado por motor

`scripts/gerar_colunas.py` regenera as colunas **4, 5, 6, 7, 9 e 10** de duas fontes e só duas
— HIST_SEED (Partnr/B3/CVM) e o lucro normalizado com motor declarado. **Nenhum número digitado.**

Também passou a gerar o `data-lpa-ltm` de cada linha (lucro LTM ÷ papéis), que antes era curado
à mão e envelhecia sozinho — foi essa defasagem que já tinha dado um P/L quase 2x errado na LEVE3.

E as colunas 11 (DY realizado), 13 (ROE) e 14 (dívida/EBITDA) passaram a declarar fonte na
própria célula, incluindo a explicação de por que dívida/EBITDA é vazio nas 8 financeiras.

### Resultado

| | antes | depois |
|---|---|---|
| Células sem racional declarado | **~180** | **0** |
| Linhas com `data-lucro-manual` | 29 | **0** |
| Motores escrevendo as colunas 4-5 | **3** | **1** |
| Células vazias | 30 | **29, todas com o motivo escrito** |

As 29 vazias são todas declaradas: 8 são dívida/EBITDA em financeira (não se aplica), 5 são TIR
real sem base, e o resto se concentra em **ROXO34** (BDR com 1 ano de base, sem lucro consolidado
na fonte) e **AURE3** (margem líquida mediana negativa — prejuízo em mais da metade dos anos
válidos, então não existe "ano representativo" positivo para normalizar).

⚠️ **A coluna 16 (Cotação) é a única exceção deliberada:** a fonte é idêntica em todas as linhas
(cotação ao vivo) e a declaração está no cabeçalho. Anexar um `<span>` por célula quebraria as
seis rotinas que leem o preço por `textContent`. Foi troca consciente, não esquecimento.


---

## 24. A TIR real deixa de ser snapshot (06/09/2026)

Achado ao responder *"tem coisa pendente ainda?"*. A coluna 22 vinha de `data/tir.data.js`,
um arquivo **estático escrito à mão em 05/09** — antes de todas as correções de payout daquele
dia. **Doze empresas divergiam mais de 5 p.p.** do que o motor calculava:

| Ativo | TIR usava | Motor | Δ |
|---|---|---|---|
| **AXIA3** | 43% | 93% | **+50 p.p.** |
| **SBSP3** | 19% | 50% | **+31 p.p.** |
| **LEVE3** | 57% | 86% | **+29 p.p.** |
| SAUD3 · TIMS3 · ITSA4 | | | −16 a −17 |
| ALOS3 · ITUB3 · PETR4 | | | ±9 a 11 |

> **Quarta aparição do mesmo padrão: duas fontes de verdade para o mesmo conceito.** Antes foi
> `data-pl-hist` recalculando o teto por cima do motor, o payout duplicado dentro do
> `teto_bazin`, e `calcularLucroEstimado()` disputando as colunas de lucro. A diferença é que
> aqui a segunda fonte é um ARQUIVO ESTÁTICO — ela não briga com a primeira, **ela envelhece em
> silêncio**. É o modo mais perigoso da falha, porque nada quebra e nada avisa.

`scripts/gerar_tir.py` regenera o arquivo a partir do motor. O payout vem de `payout_final()`,
a mesma função que alimenta o preço-teto e a coluna de payout.

### Dois defeitos que a regeneração expôs

**1 · `g` negativo de −70% na KLBN11.** O CAGR do lucro herdado mede a queda até o fundo do
ciclo da celulose, e o modelo o projetava como crescimento por 10 anos: a faixa saía **−58,1%
a 3,5%**. **Cíclica não usa CAGR de lucro** — é o mesmo erro que já tirou o E/P e o Gordon do
motor de preço-teto delas. Nelas o `g` vem só de ROE × retenção, que é estrutural.
**KLBN11: 1,9% → 9,2%. VALE3: 3,7% → 10,4%.**

**2 · Crescimento nominal negativo seguido de perpetuidade positiva.** O modelo dizia que a
empresa encolhe por 10 anos e depois volta a crescer com a economia, sem nada explicando a
virada. Entrou **piso de zero** — "estagnada em termos nominais", a hipótese conservadora
defensável. ⚠️ É premissa, declarada como tal. CLSC4 e RANI3 subiram por causa dela.

### O que NÃO foi regenerado, e por quê

`cx` (medida de caixa: FCO − capex ÷ valor de mercado) e `gCagr` dependem de FCO, capex e lucro
recorrente — campos que **não estão no HIST_SEED**, vieram de chamadas ao Partnr na época.
São **herdados** do snapshot, e nenhum dos dois depende de payout. Cada linha ganhou um campo
`fonte` dizendo de onde veio o payout, para o próximo leitor saber o que é fresco.

### Resultado

**28 das 30 com TIR real** (eram 25). Só ROXO34 e AURE3 continuam sem, ambas declaradas.

| Maiores movimentos | antes | agora |
|---|---|---|
| VALE3 | 3,8% | **10,4%** |
| KLBN11 | 3,1% | **9,2%** |
| RANI3 | 11,8% | 13,8% |
| BRAP4 | 16,7% | 12,9% |
| SAUD3 | 11,5% | 7,9% |
| BRSR6 | 16,9% | **18,7%** (topo da lista) |
| SHUL4, PASS3, IRBR3 | *sem TIR* | **14,6% · 10,8% · 4,3%** |


---

## 25. Fim dos campos manuais (06/09/2026)

Três limpezas depois de listar o que ainda não tinha motor.

### 25.1 `cx` e `gCagr` deixam de ser herdados

`data/fluxo.json` passa a trazer **FCO, capex e lucro recorrente** de 30 empresas, coletados do
Partnr (`CASH_FLOW_STATEMENT` e `INCOME_STATEMENT`, TTM). A medida de caixa e o CAGR da TIR real
deixam de vir do snapshot antigo.

⚠️ **FCO − capex é calculado aqui, não lido do campo `FREE_CASH_FLOW`.** Esse campo é
inconsistente com ele mesmo: no LEVE3 devolve **R$ 641,1 mi**, enquanto
`OPERATING_CASH_FLOW (862,3) − CAPEX (114,1) = R$ 748,2 mi`, e o `FCF_PER_SHARE` do mesmo
registro implica um terceiro valor (**R$ 577 mi**). Três números para a mesma grandeza no mesmo
registro — usar as duas pontas e subtrair é a única forma auditável.

### ⚠️ Duas regras que existiam de fato e não estavam escritas

Ao trocar o herdado pelo calculado, as **financeiras ganharam `cx` e `gCagr` pela primeira vez**
— e o resultado denunciou por que o snapshot antigo não as tinha:

**`cx` não vale para banco.** BRSR6 saiu com faixa até **220,7%**, ITUB3 até 30,1%. O "fluxo de
caixa operacional" de um banco inclui variação de depósitos e da carteira de crédito: captar
R$ 10 bi entra como caixa gerado, e isso é **passivo novo, não lucro do acionista**.

**`gCagr` não vale para banco.** O campo `RECURRING_NET_INCOME` devolve **R$ 112,5 bi para o
ITUB3 em 2021** (o recorrente real foi ~R$ 26 bi) e vem **nulo em 2022 e 2024**. É a fórmula
mecânica do Partnr, que não descreve banco. Com esse 2021 inflado o CAGR saía em −23% ao ano, o
`g` do Itaú ia a zero e a TIR dele caía de 11,5% para **4,6%**.

> **As duas regras já eram praticadas — o snapshot antigo simplesmente não tinha esses campos
> nas financeiras. Mas não estavam escritas em lugar nenhum**, então sobreviveram por acidente
> até alguém regenerar o arquivo. Agora estão no código, com o motivo.

### 25.2 O veredicto deixa de ser opinião escrita à mão

`data-veredicto` era o **último campo de opinião** da tabela: digitado linha a linha, de análises
escritas em datas diferentes, e podia contradizer as colunas sem nada avisar — um "compra" de
agosto ao lado de uma margem de −40% calculada hoje.

Agora deriva do que a tabela já calcula:

| | Regra |
|---|---|
| 🟢 **COMPRA** | margem ≥ 0 **E** TIR real mediana ≥ NTN-B **E** passa em todos os critérios |
| 🟡 **AGUARDAR** | TIR real mediana ≥ NTN-B |
| 🔴 **ACIMA** | TIR real mediana < NTN-B |

⚠️ **A primeira versão usava o TOPO da faixa da TIR e classificou 23 de 30 como "aguardar"** —
uma classificação que não classifica nada, porque `hi` é sempre a mais otimista das três
medidas. Com a **mediana** (o consenso), a separação é 18 / 12.

⚠️ **Nenhuma empresa acende verde hoje**, e eu não afrouxei a regra para produzir uma. A que
chega mais perto é a **BRSR6**: margem +16% e TIR mediana de 18,7%, mas passa em 2 de 3
critérios. O verde exige as três condições de propósito — um número que autoriza compra tem que
ser difícil de acender.

### 25.3 `data-lucro-manual` removido das 30 linhas

Ele protegia as colunas de lucro contra a `calcularLucroEstimado()`, que foi aposentada.
**Atributo que não protege mais nada é pior que inútil:** sugere a quem for auditar que existe
um valor curado ali, e não existe.

### O que ainda NÃO tem motor — a lista honesta

| | O que é |
|---|---|
| `VPA_BALANCO` (BPAC11, SANB11) | lido à mão do balanço, porque o P/VP do Partnr erra em units |
| `FATOR_UNIT` | fato societário (1 ON + n PN), não muda |
| `MOTOR` | classificação minha de qual motor cada empresa usa — **já errei uma vez** (SAUD3) |
| `POLITICA` | pesquisa nos RIs, com fonte e data por linha |
| **Premissas** | juro real normalizado 5,5% · prêmio 5,0 p.p. · g = IPCA+2% · margens 10/15/25% · Ke 13-22% · cap de g 15% · LIM_MARGEM 100% · dispersão 1,7x · piso de payout do Gordon 20% |

A mais influente é o **juro real normalizado de 5,5%**: move todos os tetos em bloco, e com a
NTN-B spot de 7,70% eles cairiam ~25%. **Nenhuma dessas premissas foi testada contra retorno
futuro.** Motor sem premissa não existe; o que dá para exigir é que ela esteja declarada e
num lugar só — e está.


---

## 26. O `g` sai da tooltip e vira coluna, e o CAGR vira regressão (07/09/2026)

Pergunta do usuário: *"as que estão com g 0 não crescem?"* — e depois: *"não é mais fácil
calcular o g com base na média de crescimento dos últimos 5 anos?"*

### ⚠️ A CLSC4 provou que o meu CAGR estava errado

| Ano | Receita | Lucro contábil | Lucro recorrente |
|---|---|---|---|
| 2021 | 11,34 | 0,56 | 0,67 |
| 2022 | 10,08 | 0,54 | **0,47** ← ano ruim isolado |
| 2023 | 10,40 | 0,56 | 0,67 |
| 2024 | 10,66 | 0,72 | 0,65 |
| 2025 | 11,90 | 0,73 | 0,65 |
| 2026 LTM | **12,52** | **0,88** | — |

**Receita +10% e lucro contábil +57% em cinco anos.** A Celesc cresce. Mas o CAGR ponta-a-ponta
via só `0,67 → 0,65 = −0,72%`, que o piso zerava. **O motor dizia "não cresce" sobre uma empresa
que cresce.**

### A armadilha da palavra "média"

| Método | CLSC4 | SHUL4 | PASS3 | ALOS3 |
|---|---|---|---|---|
| CAGR de pontas | −0,7% | −3,1% | −14,2% | 29,8% |
| **Média geométrica** | **−0,7%** | **−3,1%** | **−14,2%** | **29,8%** |
| Média aritmética | +2,4% | +0,6% | −10,4% | **+59,7%** |
| Mediana das variações | −1,0% | −2,2% | −2,4% | 14,7% |
| **Regressão log** | **+2,8%** | −3,2% | −16,4% | 17,9% |

⚠️ **Média geométrica é IDÊNTICA ao CAGR de pontas — em todas as 11 empresas.** Não é
coincidência, é álgebra: o produto `(1+g₁)(1+g₂)…(1+gₙ)` **telescopa** para último÷primeiro.
Os anos do meio se cancelam. Trocar por ela não mudaria um número.

⚠️ **Média aritmética seria pior.** Viés de Jensen: subir 50% e cair 50% dá média zero e perda
de 25%. Foi **maior que o real nas 11 de 11**, e na ALOS3 deu **59,7% contra 29,8%** — o ano da
fusão puxa a média. Compondo 10 anos num DDM, é fantasia.

⚠️ **Mediana esconderia queda monotônica.** A PASS3 sairia de −14,2% para −2,4%, quando ela
perdeu **51% do lucro recorrente em quatro anos**. Robustez que apaga o fato não serve.

**Ficou a regressão log**: usa todos os pontos, não telescopa, não tem viés de composição.
Conserta a CLSC4 sem salvar quem realmente encolhe.

| Ativo | g antes | g agora | TIR antes | TIR agora |
|---|---|---|---|---|
| **CLSC4** | 0,0% | **+2,8%** | 5,2% | **6,8%** |
| LEVE3 | 1,5% | 0,3% | 12,8% | 12,0% |
| CPFE3 | 4,3% | 3,1% | 8,9% | 8,4% |

As outras 25 não se moveram — na maioria o `gRoe` já era o menor dos dois.

### Coluna 23 · Crescimento, com o valor bruto ao lado

O `g` movia a TIR inteira e só aparecia dentro de uma tooltip. Agora é coluna — e mostra
**entre parênteses o valor bruto** quando o piso ou o teto está cortando, porque **é exatamente
aí que está a informação escondida**:

| Ativo | Exibido | Bruto | O que isso diz |
|---|---|---|---|
| BBSE3 | +15,0% | **+23,1%** | o teto está cortando |
| BMEB4 | +15,0% | +19,6% | idem |
| BPAC11 | +15,0% | +17,1% | idem |
| **PASS3** | +0,0% | **−16,4%** | **está encolhendo** |
| **SHUL4** | +0,0% | **−3,2%** | estagnada |

⚠️ **Sem o bruto, PASS3 e SHUL4 pareciam idênticas na tela.** Uma anda de lado; a outra perdeu
metade do lucro recorrente em quatro anos. O piso de zero continua no cálculo (por coerência do
modelo), mas deixou de apagar o fato.

E a **SHUL4 vira uma pergunta de investimento**: retém **94% do lucro** (payout de 6%) com
**ROE de 17%**, e o lucro recorrente **cai 3,2% ao ano**. Para onde vai esse dinheiro?

⚠️ **São 5 pontos de série.** Regressão sobre 5 observações é melhor que sobre 2 e continua
frágil. É estimativa, não medida.

## 27. Dois itens do punch-list de 06/09/2026: TIR ao vivo e ROXO34 (07/09/2026)

Depois do `g` virar coluna, o usuário pediu a lista do que faltava em preço-teto e TIR. Saiu
um punch-list de 11 itens; os três primeiros — TIR com cotação ao vivo, ROXO34, sensibilidade
do juro real — foram aprovados para começar de imediato. Esta seção cobre os dois primeiros.

### Item #8 · TIR real recalculando com a cotação ao vivo

`data/tir.data.js` era gerado por `scripts/gerar_tir.py` com o preço do **data-base do
HIST_SEED** (`preco`), não a cotação de hoje — e a tooltip da coluna dizia isso explicitamente:
"Snapshot ... não recalcula com a cotação ao vivo". Um dia depois de gerado (07/09/2026), a
defasagem já era:

| Ativo | Defasagem |
|---|---|
| IRBR3 | −9,9% |
| BBSE3 | −8,1% |
| PASS3 | −6,3% |
| CPFE3 | −5,5% |

É o mesmo padrão que motivou o próprio `gerar_tir.py` um dia antes: um número que segue o
motor, mas trava no preço do dia em que rodou, e piora sozinho sem que nada quebre.

**A correção não recalcula tudo em Python a cada carregamento** — seria reintroduzir o mesmo
problema do preço-teto de rodar o motor inteiro no navegador. Em vez disso, `cx`, `div` e `luc`
só dependem do preço através do valor de mercado (cotação × papéis); `g`, `payout` e o lucro
normalizado não dependem de preço nenhum. Então `gerar_tir.py` passou a exportar também `pap`
(papéis), `d0` (dividendo por papel) e `fcfe` (FCO−capex nominal, não dividido por valor de
mercado) — os insumos que sobrevivem à mudança de cotação — e `js/decisao.js` ganhou
`_tirAoVivo()`, que recompõe as três medidas a cada render da linha usando a cotação do DOM,
espelhando exatamente as fórmulas de `gerar_tir.py` (mesmo Fisher, mesmo DDM de dois estágios
por busca binária). Testado numericamente: rodando os dois lados (Python e a réplica em Node)
com o mesmo preço de geração, os três números batem ao centavo.

O padrão é o mesmo de `calcularPrecoTeto()`/`atualizarPLAtualLinha()`: nada trava no preço do
dia em que o motor rodou — tudo que depende de cotação recalcula quando ela muda.

### Item #3 · ROXO34 — recusa declarada em vez de número extremo

O ticker seguia com margem de **−122%** (teto R$ 5,58 contra cotação R$ 12,40) mesmo depois da
arquitetura de consenso de N métodos. A causa não era discordância entre métodos — a nota do
motor dizia "convicção pela dispersão", ou seja, Gordon, lucro residual e múltiplo próprio
(P/VP-alvo) **concordavam** entre si. O problema é que os três corriam sobre **exatamente um
ano de dado**: a Nu Holdings é BDR de empresa estrangeira (Nu Holdings Ltd, NYSE, sede nas
Cayman), fora da cobertura B3/CVM que o MCP Partnr oferece, e a única linha em
`data/historico.data.js` (2025, ROE 33%, P/VP 5,06x) foi lida à mão de um release — não há
série para saber se é o padrão da empresa ou um ano atípico.

Rodar um "consenso de 3 métodos" sobre `n=1` fabrica validação cruzada **aparente**, não real:
os três concordam porque vêm da **mesma fonte única**, não porque fontes independentes bateram
— exatamente o requisito de 2+ anos válidos (ou peer fallback) que o motor cobra de toda outra
empresa da base, e que aqui não existe como cumprir.

**Não é "achar um motor melhor"**: não há segunda fonte para checar a primeira. A correção foi
adicionar um dicionário `SEM_TETO` em `scripts/motor_teto.py`, com o motivo escrito por
extenso, e fazer `calcular()` devolver recusa declarada para quem está nele, antes de chamar
o consenso de métodos:

```python
SEM_TETO = {
    'ROXO34': ('BDR de empresa estrangeira ... A base tem exatamente 1 ano de dado ... '
               'Sem segunda fonte independente, não há preço-teto defensável ...'),
}
```

A célula de Preço Teto do ROXO34 agora mostra "—" com o motivo completo na tooltip, em vez de
R$ 5,58. Payout, TIR real, ROE, P/L e as demais colunas continuam calculados normalmente — só
o teto, que dependeria de extrapolar Gordon/lucro residual por 10 anos a partir de um único
ponto, foi suprimido. Diferente da recusa por `LIM_MARGEM` (que hoje não dispara mais — ver
seção 17), esta é uma recusa **por ticker, declarada por nome**, para um caso que nenhuma
correção de motor resolve: falta de dado, não bug de motor.

### Sensibilidade do juro real (5,5% vs NTN-B spot 7,70%) — informativo, sem mudança de premissa

O terceiro item aprovado foi medir, não mudar: rodei o motor inteiro duas vezes, uma com
`RF_REAL_NORM` na premissa atual (5,5%, perto da média histórica da NTN-B longa) e outra com
a NTN-B spot (7,70%), e comparei os 29 tetos.

Delta mediano no teto: **0,0%**. Mais da metade dos ativos usa só métodos que não passam por
Ke (EV/EBITDA, EV/Receita, P/VP puro) e não se move. O efeito concentra em financeiras e nos
poucos não-financeiros com peso forte de Gordon/lucro residual: BPAC11 −34%, ITUB3 −33%,
SAUD3 −24%, AXIA3 −23%, PASS3 −23%, CXSE3 −20%, BMEB4 −20%.

Dois ativos **mudam de lado** (teto passa de acima para abaixo da cotação) entre as duas
premissas: **BRSR6** e **PSSA3**. Nestes dois, a classificação "compra" vs "acima" depende de
qual premissa de juro real se usa — é fragilidade real do modelo, não ruído, e fica registrada
aqui para quem for revisar `RF_REAL_NORM` no futuro. A premissa em produção continua 5,5%;
nada em `motor_teto.py` mudou nesta seção.

## 28. FCFE de verdade (07/09/2026)

A medida CAIXA da TIR real (`cx`) usava (FCO − capex) ÷ valor de mercado do equity como proxy
de "quanto sobra para o acionista". Isso é **FCFF** — fluxo de caixa livre para a FIRMA inteira
(dívida + equity) — não **FCFE** (fluxo livre para o EQUITY), e dividir um numerador de firma
por um denominador de equity distorce nos dois sentidos: quem está pagando dívida tem uma
fatia do FCO indo para o credor, que nunca chega ao acionista, e a medida superestima; quem
está alavancando recebe caixa que não veio do negócio mas ainda chega ao acionista (via
investimento, recompra, dividendo futuro), e a medida subestima.

O caso que expôs isto: a PETR4 pagou **R$ 17,5 bi de dívida bruta líquida** no período TTM —
caixa que entrou pela operação (FCO) mas saiu para o credor. O FCO−capex bruto (R$ 109,4 bi)
superestimava o FCFE real (R$ 91,9 bi) em 16%.

**Correção**: `FCFE = FCO − capex + Δdívida bruta`, com Δ calculado entre os dois anos mais
recentes e CONSECUTIVOS da base (`delta_divida_bruta()`, `scripts/motor_teto.py`), restrito a
depois da última quebra (`anos_validos`) — dívida de antes de uma incorporação ou privatização
é consolidação contábil, não financiamento orgânico. Usei dívida BRUTA, não líquida: a líquida
já embute caixa, que está do lado errado da equação e dobraria a contagem.

Sem 2 anos consecutivos de dívida bruta na base, a função cai para o FCO−capex bruto (mais
informação que nenhuma) e marca isso no campo `fcfeAjustada: false` — a tooltip da TIR real
mostra o aviso "⚠️ sem dívida de 2 anos consecutivos — FCFF, não FCFE" nesses casos.

Efeito nos 28 ativos regenerados: mediana do `cx` pouco se move (a maioria das empresas tem
dívida estável ano a ano), mas alguns saltam — SBSP3 (TIR mediana 6,2%→11,6%, dívida bruta
+R$ 11,5 bi financiando o programa de investimento pós-privatização), FIQE3 (8,5%→19,2%,
+R$ 0,5 bi), KLBN11 (9,2%→11,9%, −R$ 1,9 bi de dívida), AXIA3 (2,8%→0,8%, −R$ 3,3 bi) e CLSC4
(6,8%→5,2%, +R$ 0,7 bi). Nenhum é bug: é exatamente a distinção que FCFF vs FCFE deveria fazer
— empresa alavancando aparece com caixa a mais para o acionista, empresa desalavancando com
caixa a menos, e antes da correção nenhuma das duas aparecia.

---

## 29. O critério que ORDENA a fila é testado — e trocado (13/09/2026)

Pergunta do usuário, e é a pergunta certa: *"preciso que este projeto me ajude a encontrar as
empresas mais baratas e com maior potencial de retorno, mas não estou confiante que este
modelo está me trazendo isso"*. Junto veio a delimitação que muda tudo: os segmentos que ele
compra são **bancos, seguradoras, elétricas, telecom e saneamento** — pagadoras de dividendo,
risco baixo. Não cíclica de commodity, não construtora.

### O buraco: o critério em produção nunca tinha sido testado

A seção 12 (`backtest_multiplos.py`) testou múltiplos e a MARGEM SOBRE O PREÇO-TETO. Mas o que
ordenava a lista "Por onde começar" não era nenhum dos dois: era a **TIR real**. Ela entrou na
seção 24 substituindo a Nota 0-100 — que saiu porque *"o backtest do projeto não validou"* — e
nunca passou pelo mesmo teste que derrubou a antecessora. Um critério herdou o lugar de outro
por ser melhor construído, não por ter medido melhor.

E o backtest que existia misturava os 30 tickers num universo só. Um sinal que funciona na
VALE3 e falha no ITUB3 aparece ali como "funciona" — o que não serve para quem só compra o
lado defensivo da tabela.

### `scripts/backtest_ranking.py`

Script novo, com dois cortes que o anterior não fazia: separa por **grupo de motor** (o mesmo
dicionário `MOTOR` de `motor_teto.py`, lido por `exec` do arquivo — não uma cópia que diverge)
e testa a **TIR real**, não o preço-teto.

A TIR aqui é PROXY, e a diferença importa: a TIR de produção é a mediana de três medidas
(caixa/FCFE, dividendos/DDM, lucro). FCO, capex e dívida bruta não estão no HIST_SEED, então
só a medida LUCRO é reconstruível ano a ano — `real(ey + g)`, com `g = ROE × retenção` capado
em 15% e o mesmo Fisher do gerador. Como `real()` é monotônico em `(ey + g)`, ordenar por essa
TIR é ordenar por `(ey + g)`, e o teste vira uma pergunta limpa: **somar `g` ao earnings yield
melhora ou piora a ordenação?**

### O resultado

**Defensivos (FIN + UTIL) — 17 tickers, 76 observações, 5 transições anuais:**

| Critério | n | BARATO | CARO | spread | ρ | t | anos certos |
|---|---|---|---|---|---|---|---|
| **L/P (earnings yield)** | 74 | 33,9% | 13,6% | **+20,3 p.p.** | +0,22 | +2,52 | **5 de 5** |
| TIR real (proxy `ey+g`) | 73 | 29,1% | 17,8% | +11,4 p.p. | +0,16 | +1,04 | 3 de 5 |
| Dividend yield | 76 | 22,9% | 18,8% | +4,1 p.p. | +0,09 | +0,69 | 4 de 5 |
| `g` isolado | 73 | 28,2% | 19,9% | +8,3 p.p. | +0,09 | +0,64 | 2 de 5 |

**Somar `g` ao earnings yield PIORA o spread em 8,9 p.p.** O componente que a TIR acrescenta ao
L/P não tem sinal próprio nesses setores — dilui o que o L/P já entrega.

**Controle (CICL, IND, SHOP, NAV) — 11 tickers, 49 observações:**

| Critério | n | spread | ρ | t | anos certos |
|---|---|---|---|---|---|
| **Dividend yield** | 49 | **+19,5 p.p.** | +0,27 | +3,89 | **5 de 5** |
| L/P | 46 | +8,0 p.p. | −0,01 | +1,05 | 3 de 5 |
| `g` isolado | 44 | **−10,3 p.p.** | −0,18 | −1,37 | 2 de 5 |

A régua que funciona **muda com o grupo**, e há razão econômica antes do número: banco,
seguradora, elétrica, telecom e saneamento têm lucro estável e regulado — o lucro de hoje já é
proxy razoável do lucro normal, e L/P mede valor direto. Na cíclica e na construtora o lucro do
ano engana (pico de ciclo vira P/L baixo enganoso) e o **dividendo** é o sinal mais honesto: a
empresa só distribui caixa que realmente tem, então é sinal revelado pela administração, não
apurado por competência. O `g` é ruim nos dois grupos — neutro-ruidoso no defensivo, **negativo**
no controle.

### A mudança

`js/decisao.js` passou a ordenar a fila pelo **yield validado do grupo da empresa**
(`RANK_CRIT_POR_GRUPO`): L/P em FIN e UTIL, DY nos demais. Os dois critérios são yields na
mesma unidade (% ao ano sobre o preço de hoje), então um eixo só ordena a fila inteira sem
normalizar percentil — que num grupo de 2 elementos (SHOP) não significaria nada. Sem o dado da
régua do grupo, cai na outra e o cartão declara qual usou ("L/P 9,0%" não se confunde com
"DY 5,1%").

A TIR real **continua na tabela**. Ela responde "quanto rende acima da NTN-B", que é pergunta
diferente de "qual está mais barata" — só deixou de ordenar a fila, e a tooltip da coluna passou
a dizer isso com os números acima.

### ⚠️ O que este teste NÃO diz

São 5 transições anuais, observações correlacionadas dentro do ano — o n efetivo para
significância é o número de ANOS, não o de observações. Isto **não prova que L/P prediz
retorno**. Prova que a TIR real, no período medido e nesses setores, ordenou pior que o insumo
mais simples que ela usa por dentro. Ordenar pelo que errou menos é o mínimo defensável, e é
diferente de ter critério validado. O item #1 do punch-list (300+ papéis, 10 anos) continua
sendo a única coisa que mudaria a resposta de fundo.

### Dois bugs achados no caminho

**`seg` envelhecendo em silêncio.** `gerar_tir.py` gravava
`seg=(velho or {}).get('seg') or MOTOR.get(t)` — preferia o campo do snapshot de 05/09, anterior
à criação do grupo UTIL. Resultado: 14 tickers carregavam `seg:'IND'` e só 1 dizia `'UTIL'`,
enquanto o `MOTOR` classificava 8 como UTIL. O campo preferia a fonte velha e envelhecia sem
sintoma — a falha da seção 24, dentro do script escrito para consertá-la. Agora o `MOTOR` é a
única fonte, e o ranking por grupo depende disso para funcionar.

**Gerador não idempotente.** O mesmo script montava o cabeçalho com `cab = antigo[:...]` e depois
`cab += <bloco de aviso>` — relia o cabeçalho já gerado e anexava o aviso de novo a cada rodada.
O arquivo em produção carregava o mesmo bloco **nove vezes**. Gerador que produz saída diferente
com a mesma entrada torna o diff do git inútil justamente onde ele é a única auditoria (ninguém
revisa arquivo gerado linha a linha). O cabeçalho passou a ser escrito do zero; rodar duas vezes
seguidas agora dá o mesmo md5.

### VIVA3 e ASAI3 entram com lacuna declarada

Entraram a pedido do usuário depois do screener do universo B3 inteiro (as duas passam em
P/L ≤ 12x + ROE ≥ 15% + dív.líq/EBITDA ≤ 3x). **Não têm a mesma qualidade de série das outras
30**, e os campos que faltam estão `null` em vez de estimados: a chave de API desta sessão não
tem escopo para cotação histórica (`@quotes/post/eod`) nem para valuation ratios anuais — de
onde sairiam `preco`, `pl`, `pvp` e `dy` de cada exercício.

Sem preço histórico não há múltiplo histórico, e todo método do motor ancora em múltiplo da
própria série. As duas entram em **`SEM_TETO`**, declaradas por nome, em vez de receber teto
calculado sobre o único ano com cotação — que seria o erro do ROXO34 outra vez, agora sabendo.
L/P, margem e alavancagem continuam calculados normalmente, e é o L/P que as ordena.

Da VIVA3 a DRE consolidada de 2021-2025 veio completa e auditável. Da ASAI3 não: a API só
devolveu 2019-2020, anteriores ao spin-off do GPA, com base de ações incomparável (LPA de
R$5,80 em 2020 contra R$0,71 no LTM). Restaram margem líquida e dív.líq/EBITDA por exercício —
e a margem caindo de **3,84% (2021) para 0,64% (2025)** é o dado mais importante dessa linha.

---

## 30. O preço-teto vira faixa, e o ranking vira score composto (13/09/2026)

Cobrança do usuário, e ela é sobre postura antes de ser sobre método: *"eu te peço desde o
começo para ajudar a definir uma metodologia eficiente, e tudo que eu dou de sugestão você
fala que é melhor assim. Fica difícil de confiar — parece que está com viés no que eu falo."*

Procede. Nas rodadas anteriores eu abri quase toda resposta validando a sugestão dele antes
de analisá-la, e num caso extrapolei feio: declarei que margem líquida é "sinal invertido,
tire do motor" com base em 5 anos e 30 empresas, contra décadas de evidência em sentido
contrário. Tratar um backtest minúsculo como árbitro da verdade é o mesmo erro de confiança
excessiva que o resto desta metodologia combate — só que virado para o outro lado.

O que segue é a posição do motor, independente de quem sugeriu o quê.

### 30.1 Duas perguntas que estavam misturadas

| Pergunta | Natureza | Instrumento |
|---|---|---|
| "Qual está mais barata?" | comparação, ordinal | score relativo, ordena a fila |
| "Quanto esta empresa vale?" | avaliação, cardinal | faixa em reais |

A primeira é tratável. A segunda é difícil, e nenhuma casa do mercado a resolve bem. Usar o
mesmo aparato para as duas — um número em reais com estrelas de confiança, servindo ao mesmo
tempo de valuation e de régua de ordenação — era a confusão de base.

### 30.2 O preço-teto vira FAIXA (p25–p75 do múltiplo próprio)

`scripts/backtest_margem.py` reconstruiu o teto **ponto no tempo** — base truncada a cada ano,
motor rodando sem saber que os anos seguintes existem — e mediu três coisas:

- **como porteira, funciona**: abaixo do teto rendeu +21,4 p.p. (defensivos) e +22,2 p.p.
  (Radar) a mais que acima dele;
- **como régua, não funciona**: ordenar pela margem deu spread **−10,7 p.p.**, acertando 1 de
  3 anos. Margem de 50% não rendeu mais que margem de 10%;
- **a convicção não mede confiança**: no Radar inteiro o teto ★★★ rendeu 18,3% e o ★ rendeu
  18,9%. A estrela prometia precisão que o método não tem.

Um número com estrela comunica exatidão falsa. A faixa comunica a incerteza real: nasce larga
quando o múltiplo oscilou muito, estreita quando o mercado precificou o negócio de forma
reconhecível ano após ano. **A largura É a convicção**, derivada do dado em vez de uma régua
de dispersão inventada. Percentis 25 e 75, não mínimo e máximo, porque um ano de pânico ou
euforia não deve definir o limite — mesma razão de o motor usar mediana desde a seção 19.

**Teto de compra = limite inferior da faixa.** Abaixo dele a ação está barata por todas as
réguas, não só pela mais generosa.

### 30.3 O que saiu da composição, e por quê

`scripts/backtest_metricas.py` mediu cada múltiplo contra retorno futuro com p-valor por
permutação:

| Múltiplo | Método no motor | Defensivos | Radar |
|---|---|---|---|
| Receita/Preço | EV/Receita | **p=0,007** | **p=0,000** |
| Lucro/Preço | E/P histórico | p=0,083 | p=0,098 |
| VP/P | P/VP-alvo | p=0,370 | p=0,307 |
| EBITDA/EV | EV/EBITDA | +1,6 p.p. | −0,3 p.p. |
| Dividendo | Gordon/Bazin | **p=0,620** | p=0,393 |

Na versão anterior os cinco votavam **com peso igual na mediana** — o múltiplo mais forte
pesava o mesmo que o que não prediz nada, e três fracos podiam dominar o resultado sozinhos.

- **`teto_bazin` saiu**: ancora em dividendo, e o DY foi a única métrica com spread NEGATIVO
  nos setores que o usuário compra. Não é régua de valor, é régua de renda.
- **`teto_fin` (DDM de 2 estágios) saiu**: depende de Ke, parâmetro não observável de altíssima
  alavancagem — o próprio docstring de `rim_fade` registrava que entre Ke de 13% e 16% o
  resultado variava 1,46x. Financeira passa a usar E/P + P/VP, ambos ancorados em dado
  observável. EV/Receita se auto-exclui em banco por falta de EBITDA, sem precisar de regra.
- **EV/EBITDA virou verificação**: continua calculado e aparece na nota — se discordar da
  faixa, isso é informação sobre a empresa — mas não puxa mais o limite.

### 30.4 Duas travas que eu quebrei e tive que refazer

Rodar a versão nova e **olhar os extremos** expôs dois estragos da remoção do `teto_fin`:

- **IRBR3**: faixa de R$24,25 a R$55,79 (57% de largura) e teto de R$24,25 contra cotação de
  R$56,78 — margem de −134%. Com os métodos discordando tanto, o limite inferior não é
  estimativa conservadora de valor: é a saída do método mais pessimista.
- **SAUD3**: método único (E/P de peer comp), R$3,20 contra cotação de R$14,60 — margem de
  −357%. Pior: a metodologia já registrava que o histórico pré-2026 é da ODONTOPREV, empresa
  diferente. A trava que protegia esse caso vivia **dentro** do `teto_fin`, e eu a removi
  junto com o Ke sem notar.

Correção (`LIM_LARGURA = 0.50` em `_sanidade`): faixa mais larga que 50%, ou método único sem
série para formar faixa, **suprime o teto de compra**. A faixa continua na tabela porque
descreve a empresa; o que desaparece é o número de compra, porque comprar exige confiança que
ali não existe. Mesmo princípio do `SEM_TETO` do ROXO34.

Resultado: 22 empresas com teto, 10 sem (3 declaradas + 7 suprimidas). O total de "compráveis"
foi de 4 para 3, e a margem mediana passou de −21% para −12% — o motor novo **não é mais
restritivo**, é diferente. Quatro empresas mudaram de lado (BRSR6 e PSSA3 saíram, KLBN11 e
RANI3 entraram).

### 30.5 O ranking vira score composto

O critério de ordenação anterior — L/P nas defensivas, DY nas demais — **durou um dia**. O que
o derrubou: `backtest_metricas.py` mediu DY com corte na MEDIANA e deu p=0,62 nos defensivos,
spread negativo. O resultado favorável ao DY vinha de corte em TERCIS. **Sinal que muda de
veredicto conforme você corta em tercis ou em metades não é sinal** — é ruído com sorte de
amostragem, e é exatamente o tipo de fragilidade que métrica isolada tem e composto não tem.

Novo score: percentil médio de **quatro réguas de preço** (L/P, Receita/Preço, EBIT/EV, VP/P)
com peso 70%, mais **duas de qualidade** (ROE, margem bruta) com peso 30%, comparado **dentro
do grupo de motor** — P/L de banco não se compara com P/L de telecom. Grupo com menos de 4
empresas cai para o universo inteiro, porque com 2 elementos o percentil é sempre 0 ou 1.

`scripts/backtest_conjunto.py` confirmou a lógica do composto: o conjunto de 3-4 bateu qualquer
métrica sozinha, e — contraintuitivo — **o conjunto de 10 indicadores foi o PIOR de todos**
(p=0,36 defensivos, p=0,26 Radar), porque indicador ruim contamina a média. O ponto ideal é
poucos e bons, não muitos.

⚠️ **Os pesos 70/30 são premissa, não calibração.** Com 5 transições anuais não há amostra para
calibrar peso nenhum, e fingir que há seria o superajuste que o teste de permutação existe para
denunciar. Ficam na mesma prateleira do juro real normalizado de 5,5% (seção 25.3): juízo
declarado, aberto a revisão.

### 30.6 O que continua sem resposta

O teste de permutação de `backtest_metricas.py` é claro: testadas 136 combinações em 5 anos, o
**melhor resultado real não se separa do acaso** (o embaralhamento bate o vencedor em 60,8% das
rodadas nos defensivos). Só métricas com hipótese prévia forte — receita/preço, L/P — sobrevivem
ao p-valor individual. Tudo aqui é o melhor palpite disponível, não verdade estabelecida.

O universo de 30 empresas **é escolha deliberada do usuário**, não defeito de amostragem: são as
empresas que ele compraria. A crítica de viés de sobrevivência vale para o BACKTEST, não para a
lista de compra — e essa distinção estava confusa nas rodadas anteriores.

---

## 31. Um múltiplo, não uma mediana de vários (13/09/2026)

### 31.1 O que o usuário disse

> "O preço justo ainda não está LPA × múltiplo que a empresa deve ser negociada. Está a mediana
> de um monte de critérios que não acho justo. Deve ser **LPA projetado × múltiplo que a empresa
> deve ser negociada com base no seu histórico e de seus pares**."

Ele estava certo, e o defeito era conceitual, não numérico.

### 31.2 Por que a mediana de métodos era indefensável

A arquitetura de 06/09/2026 (seção 19) rodava todos os métodos que o dado permitisse e tirava a
mediana. O argumento era bom no papel — "a mediana ignora o método que enlouqueceu" — e produzia
um número que **ninguém consegue explicar em uma frase**.

A ALOS3 é o caso que expôs isso. O motor devolvia R$21,42 e depois R$32,06 sem que fosse possível
dizer POR QUÊ: era o meio de P/FFO R$26,74, EV/Receita R$32,60 e mais dois. No mesmo dia, o
relatório embutido da ALOS3 dizia R$29,50 usando o que qualquer analista usa — FFO projetado ×
P/FFO que o setor pratica — e era o número que fazia sentido. A tabela e o relatório discordavam
porque **a tabela respondia a uma pergunta que ninguém tinha feito**: "qual o número do meio entre
quatro réguas diferentes?"

Três defeitos concretos da composição por mediana:

1. **Dupla contagem.** E/P, EV/Receita e EV/EBITDA não são opiniões independentes — são a mesma
   demonstração de resultado dividida em pontos diferentes. Somar três leituras da mesma linha e
   chamar de consenso é inventar corroboração.
2. **Múltiplo fraco com voto igual ao forte.** O backtest de 13/09 (seção 30) já tinha mostrado
   que P/VP não tem sinal (p=0,37) e receita/preço tem (p=0,007). Na mediana, os dois pesavam igual.
3. **A faixa media a coisa errada.** "Do método mais pessimista ao mais otimista" descreve o
   desacordo entre réguas, não a incerteza sobre a empresa.

### 31.3 O que passou a valer

Cada empresa tem **UM método que decide**, escolhido pelo que o negócio é:

| Grupo | Método | Por quê |
|---|---|---|
| Geral (IND, UTIL, VAREJO, FIN) | **P/L** | LPA projetado 2026 × múltiplo-alvo |
| Shopping | **P/FFO** | o imóvel entra a custo e é depreciado — lucro e patrimônio mentem |
| Cíclica de commodity | **EV/EBITDA** sobre a MÉDIA do ciclo | o lucro de um ano é fundo ou pico, nunca normal |
| Holding | **Paridade** com a investida | vale o que a investida vale, com o desconto que o mercado pratica |

O múltiplo-alvo continua sendo a **média entre a própria história e a dos pares** — a âncora que
`backtest_pares.py` mediu em +14,1 p.p. contra as duas pontas isoladas (seção 30). O que mudou é
que o resultado dessa conta **é** o preço justo, em vez de ser um voto entre vários.

Os demais métodos continuam calculados e aparecem na tooltip como **verificação**: se discordarem
muito, isso é informação sobre a empresa. Só não entram na conta.

### 31.4 Quatro bugs que só apareceram quando um método passou a decidir sozinho

Todos estavam escondidos pela mediana, que os diluía.

**(a) O justo caía FORA da própria faixa.** BPAC11 R$121,75 com faixa de R$181,65 a R$206,04;
SANB11, CXSE3, TIMS3, BBSE3 e BRSR6 igual. Causa: `justo` usava o múltiplo já misturado com os
pares, e p25/p75 vinham da série da própria empresa, sem a mistura. Duas réguas na mesma linha.
Corrigido por `recentrar()` — a faixa preserva a **amplitude relativa** da oscilação histórica e
passa a ser aplicada ao múltiplo efetivamente usado.

**(b) EV/EBITDA e paridade não tinham faixa nenhuma.** Nunca precisaram: como um voto entre
vários, a faixa saía do conjunto. Decidindo sozinhos, as cíclicas (KLBN11, PETR4, VALE3, RANI3) e
as holdings (ITSA4, BRAP4) ficavam com largura zero e o teto de compra era suprimido por uma
convenção, não pelo dado. Ambos ganharam faixa própria — percentis do múltiplo e do desconto de
holding.

**(c) Série de 3 anos virava ponto único.** `faixa_com_tendencia` devolvia p25=p50=p75 abaixo de
4 observações. Agora, com exatamente 3, devolve a **amplitude observada (mín-máx)**: mais larga
que percentis, que é o lado certo para errar — comunica amostra pequena em vez de fingir precisão.

**(d) A trava de supressão passou a misturar duas incertezas.** `largura` mudou de significado —
antes media desacordo ENTRE MÉTODOS, agora mede oscilação histórica de UM múltiplo. Virou duas
travas:

- **sem faixa nenhuma** (menos de 3 exercícios): recusa o preço justo inteiro. Um ponto não
  descreve quanto a empresa deveria valer; descreve um ano. Atinge AXIA3, PASS3 e SAUD3.
- **faixa larga** (acima de 50%): mantém o preço justo — a mediana do múltiplo continua sendo a
  melhor estimativa única — e suprime só o **teto de compra**. É o retrato honesto de uma cíclica.
  Atinge AURE3, IRBR3 e VALE3.

### 31.5 A cópia manual da coluna acabou

`scripts/gerar_preco_justo.py` (novo) propaga `analise/tetos.json` para
`data/radar-rows.data.js` — célula, tooltip e `data-preco-justo`, de uma vez. Era a última
coluna colada à mão, e a cópia manual já tinha cobrado o preço duas vezes: em 11/09 a célula
visível da ALOS3 mostrava R$19,61 enquanto o atributo da mesma linha dizia R$21,42 (só o atributo
tinha sido colado), e em 13/09 um deslocamento de índice apagou a escrita de uma coluna em
silêncio. É sempre a mesma falha: duas fontes de verdade, e a errada é a que o usuário lê.

A tooltip tem **três linhas e nada mais**: a conta, o resultado, e de onde saiu o múltiplo.

```
PREÇO JUSTO — R$ 48,47

LPA projetado 2026 R$ 5,16 × P/L 9,39x = R$ 48,47

O múltiplo é a média entre 10,00x da própria série e 8,79x dos 8 pares do grupo FIN.
```

A primeira versão trazia também FAIXA e TETO, e o usuário cortou as duas na hora: *"aqui no texto
você colocou como preço teto, mas não quero preço teto, quero o preço justo — LPA × o múltiplo que
ela deve ser negociada"*. Ele está certo: teto de compra é outra pergunta, e a coluna de Margem de
Segurança ao lado já a responde. A faixa continua no motor e em `analise/tetos.json`, onde serve
para auditoria e para as travas de supressão — só não polui a tooltip.

Para isso os métodos passaram a devolver dois campos NOVOS, `conta` e `origem_mult`, em vez de a
tooltip parsear a string `motor` com regex. Extrair número de prosa com expressão regular já
falhou neste projeto (o vazamento de `gCagr` entre tickers vizinhos, 12/09/2026) e não havia
motivo para repetir o padrão.

### 31.6 Onde isto é PIOR que a mediana

Honestidade sobre o custo da mudança:

- **Cíclica no fundo do ciclo.** O EV/EBITDA médio protege, mas se a série de EBITDA for curta o
  método se recusa e a linha fica sem preço justo — onde antes três métodos fracos produziam um
  número qualquer.
- **Prejuízo ou LPA perto de zero.** P/L não existe com lucro negativo. A empresa desce o
  encadeamento de métodos do grupo e, se nada responder, sai sem número.
- **Três linhas a menos com preço justo** (AXIA3, PASS3, SAUD3) do que na versão anterior.

É o preço de ter um método com significado: ele pode dizer "não se aplica". A mediana nunca dizia,
e era essa a aparência de robustez que a versão anterior vendia.

### 31.7 Os relatórios embutidos passam a usar o mesmo motor

O usuário abriu um relatório e leu, no bloco de valuation: *"Preço justo = média dos 2 métodos.
Preço teto = preço justo × 0,85."* Resposta dele: *"eu já disse que não quero dessa forma, você
precisa entender o que estou pedindo e implementar"*.

Ele estava certo e o erro era meu: troquei o motor do **Radar** para método único e deixei os
**14 relatórios** com o valuation antigo, escrito à mão em datas diferentes, cada um com sua
média de métodos e sua margem de 15%. É a queixa que abriu esta linha de trabalho inteira — *"não
faz sentido eu ter um valor no relatório e outro no radar"* — reaparecendo pelo outro lado.

`scripts/gerar_relatorio_valuation.py` (novo) reescreve, em cada relatório, o bloco `valuation`,
o preço do veredicto, o do cabeçalho e o número dentro do bloco colável, tudo a partir de
`analise/tetos.json`. O `secValuation` de `js/navegacao.js` foi reescrito junto: sai a tabela de
métodos com "dispersão" e "preço justo ponderado", entra o critério, a conta, a origem do
múltiplo e uma tabela separada rotulada **"Verificação — não entra na conta"**.

A prosa do relatório (tese, riscos, gatilhos, bloco de descobertas) **não** é tocada: aquilo é
análise escrita com data e fonte declaradas, e regenerar texto de análise a partir de um JSON
seria inventar.

### 31.8 O bug que escondeu tudo isso: o `cp` manual

Duas publicações seguidas saíram com a correção no repositório e a versão ANTIGA na tela do
usuário. A causa não estava no motor nem no gerador:

```
app/scripts/build.py  →  app/exports/Analista Investimento standalone.html
                              ↓  cp MANUAL, documentado só no README
                         Analista Investimento.html   ← o que o GitHub Pages serve
```

Eu rodava `build.py`, via "OK", commitava e publicava — e o arquivo da raiz continuava no build
de dois commits atrás. Nada quebrava, nenhum teste falhava, e a tooltip `"Justo = mediana dos 2
métodos"` sobreviveu a duas correções que a tinham removido do motor.

É a pior forma da falha de duas fontes de verdade que já apareceu quatro vezes neste projeto,
porque aqui as duas fontes são o MESMO arquivo em dois caminhos. `build.py` agora escreve os dois
de uma vez. **Passo manual em pipeline é passo que não existe.**

### 31.9 Shopping mede FFO em TODAS as colunas (13/09/2026)

> "Para shopping trocar lucro líquido por FFO em todas as colunas."

O motivo é contábil, não preferência. O shopping registra o imóvel a **custo** e o deprecia como
se ele se desgastasse — mas shopping bem administrado não perde valor, ganha. E o peso dessa
depreciação depende de como cada empresa contabiliza:

| ano | D&A ÷ EBITDA · ALOS3 | D&A ÷ EBITDA · MULT3 |
|---|---|---|
| 2024 | **30%** | 7% |
| 2025 | **29%** | 7% |
| 2026 | **29%** | **6%** |

A MULT3 usa valor justo e quase não deprecia; a ALOS3 usa custo e deprecia quatro vezes mais.
O lucro líquido de shopping mede política contábil junto com operação. FFO = lucro + D&A devolve
a despesa que não sai caixa — é o que o setor usa e o que o preço justo já multiplicava pelo
múltiplo. Agora é o que a tabela inteira mostra, com uma etiqueta **FFO** roxa em cada célula
afetada.

| coluna | ALOS3 antes | ALOS3 depois |
|---|---|---|
| Lucro 2025 | R$ 945 mi | **R$ 1,58 bi** (FFO) |
| Projetado 2026 | R$ 1,11 bi | **R$ 1,70 bi** |
| Crescimento 25→26 | +17,9% (CAGR do lucro recorrente) | **+7,7%** (regressão log do FFO) |
| Lucro por ação | R$ 2,20 | **R$ 3,37** (FFO/ação) |
| Payout | 63% (estático, errado) | **60%** sobre FFO |
| Div./Ação | R$ 1,39 | **R$ 2,02** |
| DY projetado | 5,36% | **7,75%** |
| P/L | 12,8x | **7,9x** (P/FFO) |
| ROE | 7,6% | **12,3%** (FFO ÷ PL) |

O DY projetado passou a bater com o DY realizado de 2025 (7,75% contra 7,54%), o que antes não
acontecia — a projeção sobre lucro contábil dava 5,36% para uma empresa que tinha acabado de
pagar 7,54%.

**A regra mora em `crescimento()`, dentro de `motor_teto.py`, não no gerador de colunas.** É a
mesma função que `teto_ffo()` usa para projetar o FFO por papel do preço justo: se a tabela
crescesse o FFO e o motor crescesse o lucro, a coluna "Projetado 2026" e o fundamento dentro do
preço justo divergiriam na mesma linha. Como efeito, o preço justo da ALOS3 caiu de R$ 31,53 para
**R$ 28,80** — a projeção de FFO cresce 7,7% ao ano, não os 17,9% do lucro recorrente.

**O ROE foi trocado com ressalva registrada.** Levantei que FFO ÷ patrimônio não é ROE e que o
denominador continua a custo histórico; o usuário confirmou a troca. A ressalva não some por
decisão, então ela está na tooltip da célula: o retorno sai alto por construção e **não é
comparável** com o ROE das outras linhas.

**Duas colunas manuais a menos.** A coluna 8 (Payout) nunca esteve na lista do gerador e estava
divergindo em silêncio: a célula exibia 63% para a ALOS3 enquanto o motor usava 100% para calcular
o dividendo da mesma linha. O atributo `data-payout` idem. Quinta aparição de "duas fontes de
verdade" nesta base — as duas entraram na geração.

### 31.10 Coluna Múltiplo (13/09/2026)

> "Acrescente uma coluna com o múltiplo que o LPA está sendo multiplicado e o tooltip com cálculo."

Entra na posição 16, imediatamente antes do Preço Justo, e mostra o múltiplo aplicado com o
rótulo do que ele é — `9,39x P/L`, `8,13x P/FFO`, `4,30x EV/EBITDA`, `0,322 paridade`. A tooltip
traz a conta inteira:

```
P/L APLICADO — 9,39x

LPA projetado 2026 R$ 5,16 × P/L 9,39x = R$ 48,47

O múltiplo é a média entre o P/L mediano da própria empresa ao longo de 6 anos (10,00x)
e o dos 8 pares do grupo FIN (8,79x).
```

Com ela, a linha fica conferível de ponta a ponta sem abrir tooltip nenhuma: **Lucro 2025 →
Projetado 2026 → LPA → × Múltiplo → Preço Justo**.

O valor é extraído da mesma string `conta` que alimenta a tooltip do preço justo, e é gerado na
mesma passada de `scripts/gerar_preco_justo.py`. Ter dois lugares escrevendo o mesmo número —
um a coluna, outro a tooltip — seria repetir o defeito que as seções 31.5 e 31.8 documentam.

⚠️ **A inserção deslocou as colunas 16-20 para 17-21.** Deslocamento de índice já apagou a
escrita de uma coluna em silêncio neste projeto (seção 31.4), então os consumidores foram
atualizados junto e conferidos no navegador: `js/calculos.js` (16,17,19 → 17,18,20),
`js/cotacoes.js` (17 → 18), `js/main.js` (19 → 20) e a guarda do sort em `js/radar.js`
(a coluna Relatório, não ordenável, foi de 20 para 21).

### 31.11 BBDC3 entra no Radar (13/09/2026)

Bradesco ON, grupo **FIN**. Série 2021-2026 de `companies_reports` (DRE e balanço
CONSOLIDATED/ANNUAL, mais TTM 2026-06-30), `companies_ratios` e `companies_valuationRatios`,
com preço de fechamento do último pregão de cada ano.

⚠️ **Classe de ação.** `pl`, `pvp` e `dy` vêm dos ids terminados em **`_CS`** (ordinária), não
`_PS`. A Partnr separa as duas classes e a PN negocia com prêmio — P/VP de 1,09x contra 0,97x em
2026. Pegar a série errada colocaria o múltiplo da BBDC4 sobre o preço da BBDC3. É a mesma
armadilha que já apareceu no DY do ITUB3.

| | |
|---|---|
| Preço justo | **R$ 18,73** = LPA projetado R$ 2,30 × P/L 8,15x |
| Múltiplo | média entre 7,19x da própria série (6 anos) e 9,11x dos 9 pares do grupo FIN |
| Cotação | R$ 16,32 · margem **+13%** |

Entrar no grupo FIN move o múltiplo dos pares para todo mundo: o P/L mediano do setor caiu de
8,9x para 8,6x, e ITUB3 foi de R$ 48,47 para R$ 47,63. É o comportamento esperado de uma âncora
que usa pares — não um efeito colateral.

### 31.12 O bug que o BBDC3 revelou: seis linhas publicadas desalinhadas

Ao incluir o ticker, a contagem de células acusou 23 em vez de 22 — e não só na linha nova.
**VIVA3, ASAI3, ROXO34, PASS3, SAUD3 e AXIA3 tinham sido publicadas com uma célula a mais**, com
a linha inteira deslocada em relação ao cabeçalho a partir da coluna do múltiplo.

A causa: a migração da coluna 16 (seção 31.10) detectava "esta linha já migrou?" procurando a
tooltip do múltiplo no texto da linha. Nas seis linhas **sem preço justo** não existe tooltip
nenhuma, então a resposta era sempre "ainda não migrou" e cada nova execução do gerador inseria
a célula de novo. Rodar duas vezes bastava.

Duas correções:

1. A detecção passou a ser por **contagem de células** (21 = migrar, 22 = substituir) — a única
   verificação que não depende de o conteúdo ter sido escrito antes.
2. O gerador **conserta** uma linha de 23 células removendo a duplicata, em vez de exigir que
   alguém edite HTML à mão.

Conferido com três execuções seguidas: 33 linhas, todas com 22 células.

### 31.13 Toda empresa passa a ter preço justo (13/09/2026)

> "Para as empresas que não têm preço justo, preencher — toda empresa deve ter um preço justo
> com base no LPA × múltiplo."

Sete linhas estavam sem número. Três travas caíram:

1. **`SEM_TETO` deixou de recusar.** VIVA3, ASAI3 e ROXO34 não têm série de preço própria, então
   não têm múltiplo PRÓPRIO — mas o múltiplo não precisa ser próprio: o dos pares serve, e o
   lucro delas é real e auditável. A série curta vira ressalva na nota, não ausência de número.
2. **Série curta deixou de recusar** (AXIA3, PASS3, SAUD3). Sem 3 exercícios não há faixa, mas há
   múltiplo dos pares e há lucro. O preço justo fica; o **teto de compra** continua suprimido,
   porque não se deriva preço de entrada de uma amostra sem dispersão.
3. **`PL_SETOR['_UNIVERSO']`** — o grupo VAREJO tem duas empresas e as duas entraram sem histórico
   de preço, então o grupo não produzia mediana nenhuma. Sem par, o múltiplo vem da mediana das
   22 empresas com série limpa (7,87x). Referência pior que a do setor certo, melhor que nenhuma,
   e a célula diz qual das duas está em uso.

Também: `teto_ep` passou a derivar o LPA de `lucro ÷ papéis` quando o campo `lpa` falta na base —
a ASAI3 saía sem preço justo por falta de **um campo**, tendo lucro e contagem de papéis.

**Resultado: 33 de 33 linhas com preço justo.**

### 31.14 AURE3: por que P/VP e não LPA × múltiplo

> "Por que o de energia você deixou VPA × P/VP? Não dá para deixar LPA × algum múltiplo?"

Não dá, e a razão está nos números da própria empresa. As três réguas foram testadas:

| régua | conta | resultado |
|---|---|---|
| **LPA × P/L** | LPA LTM = **−R$ 0,98** | não existe — múltiplo sobre lucro negativo não é múltiplo |
| **EBITDA × EV/EBITDA** | 3,96x × R$ 3,16 bi − R$ 20,02 bi de dívida | **−R$ 7,15** por ação |
| **VPA × P/VP** | 1,48x × R$ 13,04 | **R$ 19,31** |

A Auren deu prejuízo em 2023, 2025 e 2026, e carrega dívida líquida de **6,3x EBITDA** (herança da
compra da AES Brasil). Com alavancagem dessa ordem, o valor de firma pelo múltiplo dos pares não
cobre a dívida e o equity sai negativo — o que é informação real sobre a empresa, não falha de
conta, mas não é exibível como preço. Sobra o patrimônio.

Isso agora está escrito na tooltip da célula, com os três números.

### 31.15 O bloco "Por onde começar" saiu (13/09/2026)

> "Tire os cards e os textos acima da tabela dessa página."

Removidos o contêiner `#rankingDecisao` do `index.html` e, em `js/decisao.js`, a função
`renderRankingDecisao()` junto com o score composto que só ela consumia (`_calcularScores`,
`_rankPercentis`, `RANK_VALOR`, `RANK_QUALIDADE`) — 131 linhas.

⚠️ **O que isso custa, declarado:** o score ordenava os CARDS, não a tabela — o Radar sempre
esteve na ordem do HTML. Então a "fila para ler o relatório" que a seção 30 descreve não existe
mais na tela. A régua continua documentada e `scripts/backtest_conjunto.py`, que a validou, segue
no repositório; se ela voltar, o lugar certo é **ordenar a tabela** por ela, não recriar os cards.

O filtro "✅ Passa no filtro" não depende disso: ele lê `row.dataset.decScore`, escrito por
`atualizarDecisaoLinha()` a partir dos critérios — outro número com o mesmo apelido.

### 31.16 O ⓘ sai, o tooltip fica (13/09/2026)

> "Vamos retirar o símbolo de tooltip mas deixar a funcionalidade — quando eu passar o mouse
> por cima do número ele vai mostrar a explicação."

573 bolinhas ⓘ saíram da tela. Mudança só de CSS: os elementos `.col-tip` e `.teto-tip`
**continuam no HTML**, porque são eles que carregam o `data-tip` e ancoram o balão — viram
marcadores invisíveis e o gatilho do hover passa da bolinha de 13px para a **célula inteira**.
Na prática a área sensível cresceu para a largura da coluna.

Dois mecanismos diferentes, duas soluções:

- **`.col-tip`** (balão em CSS puro, `::after`): vira largura zero com `font-size:0` e
  `color:transparent`, mantendo `position:relative` para o balão continuar ancorado no fim do
  número. Gatilho: `tbody td:hover > .col-tip::after` e `thead th:hover .col-tip::after`.
- **`.teto-tip`** (popup `#cellTipPop` posicionado por JS): vira `position:absolute;inset:0` —
  cobre a célula inteira, então o `mouseover` do `js/calculos.js` a encontra sem nenhuma
  mudança no JavaScript.

As regras de `overflow:visible` e `z-index` que existiam para o balão não ser cortado pela
célula seguiam a bolinha (`.col-tip:hover`); passaram a seguir a célula (`td:has(> .col-tip):hover`).

Conferido no navegador: 573 marcadores, **zero visíveis**, e os três caminhos de tooltip
(célula do Radar, popup de Margem/Retorno e cabeçalho de coluna) abrindo no hover.

### 31.17 Colgroup, altura de linha e segmentos (13-14/09/2026)

**O bug que quebrou a tabela.** `#mainTable` é `table-layout:fixed`, então quem manda na largura
é o `<colgroup>` — e ele tinha **21 `<col>` para 23 colunas**. Criei as colunas Múltiplo (31.10) e
P/L médio sem acrescentar as entradas correspondentes, e as duas últimas colunas colapsaram para
**largura zero**: Retorno Total com 68px de conteúdo e Relatório com 64px vazando por cima da
vizinha. Foi o que o usuário viu como "o texto do retorno total está ultrapassando a célula" e
"você tirou a coluna de relatório detalhado" — ela não tinha sido removida, tinha sido espremida
a zero. Regra escrita no topo do colgroup: **nº de `<col>` == nº de `<th>` == nº de `<td>`**.

**Altura de linha padronizada em 44px.** Quem tem relatório recebe "📄 Ver" mais a data embaixo
(`.report-date` é `display:block`), duas linhas de conteúdo contra uma das demais — a linha da
ALOS3 ficava ~8px mais alta que a da VIVA3 e o olho não conseguia varrer na horizontal.

**Divisórias padronizadas.** Só as colunas marcadas `.sep` tinham linha vertical, e mais escura;
agora toda coluna tem a mesma divisória, na cor da linha horizontal.

**Cabeçalho fixo voltou a ficar por cima.** `#mainTable thead` empatava em `z-index:50` com a
linha promovida no hover e, no empate, quem vem depois no DOM pinta por cima — as linhas passavam
POR CIMA do cabeçalho ao rolar. Só aparecia com o mouse sobre a bolinha ⓘ; quando o gatilho do
tooltip virou a célula inteira (31.16), passou a acontecer a cada linha tocada. Agora thead=60,
linha em hover=40. Os seletores `:has()` avaliados a cada movimento do mouse (que travavam a
rolagem) viraram `:hover` puro: 20 passos de rolagem em **49ms**.

**20 segmentos → 10.** Doze tinham UMA empresa só, e havia "Papel e Celulose" e "Papel e celulose"
duplicados por causa de uma maiúscula. O segmento passa a coincidir com o **grupo de pares** que o
motor usa para escolher o múltiplo, então o rótulo que se lê e a régua que decide o preço justo
falam da mesma coisa: Bancos (7), Utilities (6), Commodities (4), Seguros (4), Varejo, Shoppings,
Telecom, Indústria, Holding e Saúde (2 cada).

**Coluna P/L médio.** Mediana do P/L da própria empresa na série, com os anos um a um na tooltip.
⚠️ **São 6 anos, não 10** — o HIST_SEED cobre 2021-2026 — e a tooltip diz isso em vez de fingir a
década. É a metade PRÓPRIA do múltiplo do Preço Justo; a outra é a mediana dos pares.

**Auditoria do Dív.Líq./EBITDA.** Conferido linha a linha contra `dívida líquida ÷ EBITDA` do
HIST_SEED: bate em **todas as 24 empresas** onde a métrica se aplica. As 9 financeiras mostram
"—" por decisão de método (em banco o passivo é matéria-prima, não alavancagem).

## 32. O relatório alimenta o motor — lucro de 2026 e múltiplo declarados (14/09/2026)

> "Para o nosso motor as variáveis mais importantes são o lucro estimado 2026 e o múltiplo a
> qual a empresa está sendo valorada, então precisamos ser assertivos nessas métricas — o
> relatório detalhado de cada empresa deve nos dar insumos para definirmos esses critérios de
> forma assertiva."

Preço justo = LPA projetado × múltiplo. A precisão do motor inteiro mora nessas duas variáveis, e
as duas saíam de regressão estatística sobre o histórico — **nenhuma olhava a empresa**. Guidance
da companhia, consenso de mercado e projeção de casa de análise são informação que a regressão não
tem como capturar.

### 32.1 Dois dicionários, e a regra da hierarquia

`LUCRO_2026_DECLARADO` e `MULTIPLO_DECLARADO` em `motor_teto.py`. O declarado **vence** o estimado
e a tooltip diz de onde veio — mesmo princípio que `POLITICA` já aplica ao payout desde 06/09.

| ticker | lucro 2026E | origem |
|---|---|---|
| BBSE3 | R$ 8,65 bi | **guidance oficial** (−7% a −3%; base é o meio) + consenso R$ 8,65-8,69 bi |
| ITUB3 | R$ 50,60 bi | g financeiro 8% sobre o lucro RECORRENTE de 2025 |
| CXSE3 | R$ 4,64 bi | g financeiro 8%, sem novo choque regulatório ⚠️ sem guidance oficial |
| BMEB4 | R$ 1,03 bi | ponto médio entre g padrão (8%) e ROE × retenção (19,3%) |
| FIQE3 | R$ 218 mi | cenário base do relatório (LPA R$ 0,55) |
| IRBR3 | R$ 330 mi | cenário **conservador** — o relatório se recusa a publicar um base |

E um múltiplo: **RANI3 · EV/EBITDA 5,5x** de meio de ciclo (faixa 5,0x-6,0x), contra a mediana da
própria série que mede onde o ciclo esteve, não onde ele normaliza. Preço justo R$ 8,06 → R$ 9,21.

⚠️ **Oito dos catorze relatórios não entraram, e é de propósito.** Eles projetam EBITDA (PASS3),
NOI (ALOS3, MULT3), LPA em 2031 (CPFE3, ROXO34) ou lucro num horizonte de 3 anos (TIMS3, LEVE3).
Converter qualquer um desses em lucro de 2026 exigiria premissa minha sobre depreciação, papéis ou
cronograma — e **premissa minha disfarçada de guidance é pior que estimativa assumida**.

Na tabela, um selo verde **REL** marca as linhas cujo lucro veio do relatório. Guidance e
extrapolação estatística têm confiabilidade muito diferente e, sem marca, se parecem.

### 32.2 Dois preços justos que estavam errados por quebra de série

Quando houve evento societário em 2025 ou depois, o exercício de 2025 **não é base limpa**: o lucro
é de antes do evento e a contagem de papéis é de depois. Dividir um pelo outro mistura duas
empresas e o LPA sai pela metade.

| | lucro 2025 | LTM | LPA antes → depois | preço justo |
|---|---|---|---|---|
| AXIA3 | R$ 6,56 bi | R$ 12,06 bi (+84%) | R$ 2,24 → **R$ 4,53** | R$ 21,89 → **R$ 40,25** |
| SAUD3 | R$ 0,58 bi | R$ 1,05 bi (+81%) | R$ 0,20 → **R$ 0,38** | R$ 1,88 → R$ 3,36 |

`base_projecao()` passa a usar o LTM nesses casos, e também quando a base não tem o exercício de
2025 fechado (ASAI3) ou não traz lucro em reais, só LPA (ROXO34).

### 32.3 Seguradora sai do grupo dos bancos

`FIN` virou **FIN** (7 bancos) e **SEG** (5 seguradoras). Banco e seguradora dividiam o mesmo grupo
de pares e o múltiplo de um virava régua do outro: a SAUD3 recebia o P/L mediano de 8,6x dos bancos
enquanto a própria série rodava entre 10,9x e 15,2x. São negócios diferentes — banco ganha no
spread de crédito, seguradora na subscrição e no float — e o ciclo de um não é o do outro. O P/L
dos pares separou em **7,5x (bancos)** contra **9,1x (seguradoras)**.

### 32.4 A tabela e o motor lendo a mesma fonte

O motor passou a aceitar lucro declarado e base corrigida; se a tabela continuasse projetando por
conta própria, a coluna "Lucro Projetado 2026" e o fundamento dentro do preço justo divergiriam **na
mesma linha**. Auditoria de reconciliação criada e rodada: **as 26 linhas com preço justo batem**,
LPA da tabela contra LPA dentro da conta do preço justo. Quatro divergências foram encontradas e
corrigidas no caminho:

- **ALOS3 e MULT3** — `teto_ffo` projetava do LTM e a coluna projetava de 2025 (R$ 3,54 contra
  R$ 3,37 na ALOS3). Agora as duas partem de 2025.
- **ASAI3 e ROXO34** — a coluna punha "—" quando não havia taxa de crescimento ou lucro em reais,
  enquanto o motor usava um número lá dentro.

### 32.5 P/L de até 16 anos para empresa madura (14/09/2026)

> "Eu gostaria do P/L de 10 anos para empresas maduras, mesmo que tenhamos que pegar de outra
> fonte."

**Não precisou de outra fonte.** A Partnr tem a série longa em `companies_valuationRatios` com
`frequency=TTM` — o que ela não tem é `ANNUAL` nem `QUARTERLY` (404 nas duas). O TTM devolve uma
revisão por DIA, o que dá respostas de 0,2 a 2,7 MB por empresa e estoura o limite da ferramenta.

`scripts/coletar_pl_historico.py` resolve: cada resposta é salva em disco pelo harness, o script
lê os arquivos, extrai o último registro de cada ano civil e grava `analise/pl_historico.json`.
O conteúdo gigante nunca entra no contexto. **23 empresas coletadas, até 16 anos (2011-2026).**

Três armadilhas que o coletor trata, e que só apareceram porque a primeira versão caiu em todas:

- **Identificação por conteúdo não funciona.** A primeira versão tentava descobrir de quem era
  cada arquivo casando o P/L com o HIST_SEED. A VIVA3 (um único ano de P/L na base) reivindicou a
  série da BBSE3, que começava em 2013 — seis anos antes do IPO da Vivara; a série `_PS` do
  arquivo do ITUB (que é a ITUB4, nem está no Radar) foi atribuída à MULT3. Séries de P/L se
  parecem demais. O ticker passou a ser **informado**, não inferido.
- **Classe de ação.** A resposta traz `_CS` (ordinária), `_PS` (preferencial), `_UNIT` e `_PSB`.
  Escolher errado põe o múltiplo da PN sobre o preço da ON. Isso **sim** é decidido por conteúdo:
  fica a série cujo P/L reproduz o que o HIST_SEED registra para aquele ticker.
- **Âncora no ano fechado.** Casar por 2026 reprovava a série certa do PETR4 (11% de diferença),
  porque o HIST_SEED usa o fechamento do ano e a série TTM de 2026 tem data-base 30/06. Em 2025 os
  dois batem na casa decimal (5,41x).

A coluna P/L médio passa a usar a série longa quando há 8+ anos, com selo azul **10a**, e a
tooltip lista todos os anos. Quebra de série continua respeitada: anos anteriores ao evento
descrevem outra empresa e saem fora.

### 32.6 Por que o preço justo NÃO passou a usar a série longa

Medi o efeito antes de mexer, e ele é sistemático e para cima:

| | 6 anos | série longa | preço justo | com a longa |
|---|---|---|---|---|
| LEVE3 | 6,7x | 11,8x | R$ 33,37 | R$ 59,21 (**+77%**) |
| CPFE3 | 7,9x | 12,8x | R$ 42,69 | R$ 55,35 (+30%) |
| BBSE3 | 8,6x | 12,2x | R$ 37,04 | R$ 44,57 (+20%) |
| CLSC4 | 4,5x | 6,3x | R$ 139,81 | R$ 159,00 (+14%) |
| ITUB3 | 7,8x | 9,8x | R$ 46,93 | R$ 52,73 (+12%) |

**Todas sobem, e a razão é uma só: juro.** A janela de 2011-2020 tem Selic média perto de 7% e
fundo de 2% em 2020; a de 2021-2026 tem Selic de 13% a 15%. Múltiplo é o inverso de uma taxa de
desconto — a década inteira embute dinheiro barato que não existe hoje, e o ITUB3 negociando a
16,1x em 2020 não é referência para 2026.

Por isso a série longa entra como **contexto na coluna**, e o preço justo continua na janela de 6
anos, que cobre o regime de juro atual. A tooltip diz isso explicitamente, para a comparação entre
as duas colunas ser a informação — se o múltiplo aplicado está dentro ou fora do que a empresa
negociou na década.

### 32.7 O overlay que cobria a linha inteira (14/09/2026)

> "Agora o tooltip do retorno total está aparecendo em todas as colunas — cada coluna deve ter
> seu tooltip."

Regressão da unificação do tooltip (31.16 + 32.x). Quando o símbolo ⓘ foi removido, o `.teto-tip`
virou `position:absolute; inset:0` para continuar cobrindo a célula e receber o `mouseover`. Só
que `inset:0` posiciona em relação ao **ancestral posicionado mais próximo**, e o `<td>` é
`position:static` — o ancestral virava o `<tr>`, que é `position:relative` desde o conserto do
z-index do cabeçalho.

Resultado medido: o span do Retorno Total esticava **2483px**, a largura da linha inteira, por
cima de todas as colunas. E como o listener resolve `closest('td')` a partir do elemento sob o
mouse, qualquer ponto da linha devolvia a célula 21.

A regra `td:has(> .teto-tip){position:relative}` existia justamente para prender o overlay na
célula e não bastou. Mas o overlay só era necessário enquanto o **gatilho era o próprio span** —
desde que o gatilho virou a célula (o listener procura o marcador dentro dela), não há nada a
cobrir. O `.teto-tip` virou um marcador de tamanho zero, igual ao `.col-tip`.

Varredura de verificação nas 33 linhas: **559 tooltips abertos, zero spans escapando da célula,
zero títulos repetidos dentro da mesma linha, zero células com marcador que não abrem.**

## 33. A receita do relatório — múltiplo, três cenários e leitura dos dados (14/09/2026)

> "Nos relatórios das empresas eu quero ver o cálculo de múltiplo e a regra que adotamos para cada
> empresa, e também um detalhamento do LPA projetado considerando 3 cenários. Deixe essa regra bem
> estabelecida para o momento de gerar cada relatório. Além disso quero uma análise qualitativa."

A regra está escrita no topo de `scripts/gerar_relatorio_valuation.py` e vale para todo relatório
gerado daqui em diante. O renderizador só exibe o que o gerador produziu — não há duas definições
da mesma coisa.

### 33.1 Seção 8b · A regra desta empresa

Declara, nesta ordem: **qual método decide e por quê** — e a razão é sempre do NEGÓCIO, nunca "o
backtest gostou mais" —, as **duas metades do múltiplo** (a própria série e a dos pares, cada uma
com seu número) e a **conta completa** até o preço justo.

| grupo | método | a razão, em uma linha |
|---|---|---|
| SHOP | P/FFO | o imóvel entra a custo e é depreciado; a ALOS3 deprecia 29% do EBITDA e a MULT3 6% |
| CICL | EV/EBITDA do ciclo | o lucro de um ano é fundo ou pico — a KLBN11 saiu com LPA de R$ 0,09 |
| NAV | paridade | o lucro da holding é equivalência patrimonial, herda o ciclo amplificado |
| FIN | P/L | banco ganha no spread; o passivo é matéria-prima, não alavancagem |
| SEG | P/L | seguradora ganha na subscrição e no float; grupo de pares próprio desde 14/09 |

### 33.2 Três cenários — e o fundamento não é sempre o LPA

Um número só de LPA esconde que ele é projeção. Os três cenários usam a **mesma base** e variam
só o crescimento: **conservador** = crescimento zero (a empresa repete o que acabou de fazer — é
o piso sem premissa nenhuma); **base** = a taxa do motor, ou o lucro declarado no relatório;
**otimista** = a taxa do base × 1,5, limitada ao teto de 25%. O fator 1,5 é **premissa declarada,
não calibração** — com 6 anos não há amostra para calibrar dispersão de crescimento.

⚠️ **Duas correções que só apareceram testando fora do P/L:**

- **O fundamento muda com o método.** A primeira versão assumia "LPA × múltiplo" para todos e
  produziu R$ 15,20 de preço justo para a ALOS3 contra R$ 27,39 no Radar — dividia o LUCRO por
  papéis num método que multiplica o FFO. Agora são três famílias: por ação × múltiplo (P/L,
  P/FFO), `(múltiplo × EBITDA − dívida) ÷ papéis` (EV/EBITDA) e `preço justo da investida × razão`
  (paridade).
- **Em cíclica a sensibilidade é no MÚLTIPLO, não no crescimento.** O método já usa o EBITDA médio
  de seis anos, um número que atravessa o ciclo de propósito; aplicar taxa de crescimento sobre ele
  é projetar a média. A primeira versão fez isso e pôs o cenário base da RANI3 **abaixo** do
  conservador (crescimento de −14,6%, que é a queda até o fundo do ciclo). Agora varia o múltiplo,
  usando a faixa que o próprio relatório sensibilizou quando existe — a RANI3 tem 5,0x a 6,0x
  declarados, e por isso `MULTIPLO_DECLARADO` ganhou um campo de faixa.

### 33.3 Seção 2b · Leitura dos dados — o que ela NÃO é

Rentabilidade, tendência do ROE, alavancagem, consistência do lucro, sustentabilidade do payout e
quebra de série, traduzidos para frase a partir do HIST_SEED. **Não é tese de analista, e o rótulo
na tela diz isso.**

⚠️ **O que não se faz: inventar tese para empresa sem relatório.** Dezenove das trinta e três não
têm análise escrita. Elas recebem a leitura derivada, não um texto plausível gerado do nada — que
é o mais fácil de produzir e o mais perigoso de ler.

Quando o fundamento não fecha com a contagem de papéis (ROXO34, BDR sem lucro em reais na base), os
três cenários **não são exibidos** e a seção diz por quê, em vez de mostrar três preços com
aparência de precisão.

---

## 34. O múltiplo sai dos pares e passa a ser a própria série ajustada pelo ROE (14/09/2026)

Pedido do usuário, textual:

> "Para a conta de múltiplo, vamos levar em consideração somente os últimos 6 anos da média de P/L
> que a empresa foi negociada. Mas temos que levar em consideração o ROE médio do período também.
> Não vamos mais levar em consideração o múltiplo do setor."

E, no mesmo dia:

> "Acrescente uma coluna de ROE médio — ou seja, teremos P/L atual, P/L médio, ROE atual e ROE médio."
> "Para o P/L médio e ROE médio vamos manter desde 2021 para cá."

### 34.1 O que mudou

Antes (13/09) o múltiplo-alvo era a **média entre a mediana da própria empresa e a mediana dos
pares do grupo**. Agora é:

```
múltiplo-alvo = mediana do próprio múltiplo (janela 2021→) × ajuste de ROE
ajuste de ROE = ROE atual ÷ ROE mediano do período,  limitado a [0,70 ; 1,30]
```

O múltiplo do setor **não entra mais no preço justo**. Ele sobrevive em um lugar só: o *fallback*
de quem não tem série própria utilizável (menos de 3 anos comparáveis, ou quebra de série que
invalidou o histórico). Um múltiplo DECLARADO em relatório (`MULTIPLO_DECLARADO`, seção 32)
continua prevalecendo sobre tudo.

### 34.2 A evidência que essa decisão contraria, registrada

`scripts/backtest_pares.py` mediu, em 54 observações, a média (própria + pares) em **+14,1 p.p.**
contra as duas pontas isoladas, com p=0,040. A âncora própria **sozinha** foi a que deu negativo:
**−1,8 p.p.**, p=0,549. A mudança vai contra esse número e isso fica escrito aqui porque o projeto
não apaga medição que incomoda.

O argumento que a decisão ganha: a mediana do segmento mistura empresas com rentabilidade e risco
diferentes. O **BPAC11** é o caso limpo — P/L próprio de 39,4x contra 7,5x dos bancos, e a média
cortava a diferença pela metade sem que nada no negócio justificasse o corte.

O que o ROE entra para fazer é **substituir a informação que os pares traziam**. Pela relação de
Gordon, `P/L = payout ÷ (Ke − g)` e `g = ROE × retenção`: mais ROE significa mais crescimento
sustentável e, com o resto constante, múltiplo justificadamente maior. É informação sobre o
negócio, não sobre a vizinhança.

### 34.3 O limite de ±30% é premissa declarada

Não é calibração. A relação entre ROE e P/L justo é não-linear e depende de payout e de Ke — e o
Ke variável saiu do motor em 13/09 justamente por não ser observável sem premissa (seção 30).
Proporção direta sem limite faria o múltiplo dobrar quando o ROE dobrasse, o que a teoria não
sustenta. O limite deixa o ajuste **mover** o múltiplo sem deixá-lo **dominar** a média histórica.

Hoje três linhas batem no teto superior — TIMS3 (bruto 1,43), LEVE3 (1,37) e BRSR6 (1,34) — e
nenhuma bate no piso de 0,70.

### 34.4 O efeito, medido

| | |
|---|---|
| Linhas que subiram | 16 |
| Linhas que caíram | 9 |
| Sem efeito (método declarado, paridade, EV/EBITDA de ciclo) | 8 |
| Δ mediano | 0,0% |
| Δ médio | +9,4% |

Os extremos, e é neles que está o risco:

| Ativo | Múltiplo antes | Múltiplo depois | Justo antes | Justo depois | Δ |
|---|---|---|---|---|---|
| BPAC11 | 23,81x | 45,69x | R$ 120,19 | R$ 230,69 | **+92%** |
| TIMS3 | 11,16x | 18,56x | R$ 22,95 | R$ 38,18 | +66% |
| CXSE3 | 9,98x | 13,23x | R$ 15,42 | R$ 20,43 | +33% |
| SANB11 | 11,93x | 15,70x | R$ 40,92 | R$ 53,84 | +32% |
| PASS3 | 8,89x | 7,10x | R$ 15,19 | R$ 12,14 | −20% |
| SHUL4 | 7,01x | 5,66x | R$ 5,50 | R$ 4,44 | −19% |
| BRSR6 | 6,85x | 5,80x | R$ 30,83 | R$ 26,11 | −15% |

⚠️ **O BPAC11 é o alerta que a própria decisão cria.** Sem par que o puxe para baixo, o preço justo
passa a ser a média histórica de um banco que negociou a 39x logo depois do IPO — margem de
segurança de 73% sobre uma cotação de R$ 57,80. Ele não tem relatório detalhado; até ter, o número
descreve o múltiplo que o mercado praticou, não o que o negócio justifica.

### 34.5 Em shopping o ROE é FFO ÷ patrimônio

`serie_roe(t, A)` (em `scripts/motor_teto.py`) é **uma função, dois consumidores**: o ajuste do
múltiplo e a coluna ROE médio do Radar leem o mesmo número. Em shopping o numerador é o FFO, não o
lucro líquido, porque o usuário pediu FFO em **todas** as colunas.

A ressalva permanece: o imóvel está no balanço a custo histórico, então FFO ÷ patrimônio lê **alto
por construção** e não se compara com o de empresa que não carrega imóvel. Para o ajuste isso não
contamina nada — ele só usa a razão da empresa contra ela mesma —, mas a tooltip da coluna diz,
porque lá o número é lido de frente.

### 34.6 As colunas P/L médio e ROE médio, janela 2021→

O Radar passou a 24 colunas. A sequência de leitura é **P/L atual (13) · P/L médio (14) · ROE atual
(15) · ROE médio (16)**, e ela é a **conta do múltiplo aberta na tela**:

```
Múltiplo (col. 18) = P/L médio (col. 14) × [ ROE atual (15) ÷ ROE médio (16) ]
```

O leitor divide duas células da mesma linha e confere. No ITUB3: 10,0x × (21,0 ÷ 18,2) = 11,56x —
que é exatamente o que a coluna Múltiplo mostra.

Três decisões dentro disso:

1. **A janela é 2021→**, fixada pelo usuário. É o HIST_SEED inteiro e é a mesma janela do motor —
   as três coisas coincidem por construção, não por coincidência.

2. **A série longa de 16 anos saiu da coluna**, e o selo azul "10a" com ela. O motivo é medido:
   usar 2011-2020 no preço justo subia **toda** empresa entre +12% e +77%, porque naquele intervalo
   a Selic rodou perto de 7% e chegou a 2%. O P/L praticado ali descreve outro custo de capital.
   `scripts/coletar_pl_historico.py` e `analise/pl_historico.json` continuam no repositório para
   quem quiser olhar o ciclo inteiro; para valorar hoje, eles desancoram.

3. **A coluna P/L médio usa `faixa_com_tendencia`, a mesma do motor.** A primeira versão usava
   `st.median()` cru e mostrava 7,8x no ITUB3 enquanto o motor ancorava em 10,0x — porque a regra de
   tendência detecta série que sobe e passa a usar só a metade recente. Com o número cru na tela, a
   conta que a tooltip promete não fechava: 7,8 × 1,16 = 9,1 contra os 11,6x da coluna Múltiplo.
   Duas definições do mesmo conceito, pela quinta vez neste projeto.

Quando o método que decide **não** é P/L (P/FFO em shopping, EV/EBITDA em cíclica, paridade em
holding), a tooltip da coluna 14 diz que ali ela é **contexto**, não o múltiplo aplicado — e aponta
para a coluna Múltiplo. Prometer uma conta que não fecha naquela linha seria o mesmo defeito com
outra roupa.

### 34.7 A detecção de tendência passa a comparar medianas (14/09/2026)

> "Troca média por mediana do P/L."

O **valor** já era mediana: `faixa_com_tendencia` devolve o percentil 50, e `pl_setorial` e
`multiplos_pares` usam `st.median`. A média sobrevivia em um lugar só — o **teste que decide se a
série tem tendência**:

```python
d   = st.mean(novo) - st.mean(velho)          # antes
lim = abs(st.mean(velho)) * limiar_rel
```

Isso era incoerente com o próprio método. Um único ano de pânico ou euforia move a média de uma
metade de 3 pontos e **liga ou desliga o truncamento da série inteira** — exatamente o que a
mediana existe para evitar, e a mesma razão que já tinha tirado a média do valor reportado
(seção 19). Agora as duas metades são comparadas pela mediana.

Efeito: **5 das 33 linhas** mudaram. O detector passou a disparar em três casos onde o outlier
inflava a média da metade antiga e escondia a tendência.

| Ativo | Múltiplo | Justo | Δ | O que mudou |
|---|---|---|---|---|
| BRSR6 | 5,80x → 4,51x | R$ 26,11 → R$ 20,31 | **−22%** | passou a detectar queda (−1,1), usa só 2024-2026 |
| SHUL4 | 5,66x → 5,03x | R$ 4,44 → R$ 3,95 | −11% | passou a detectar queda (−1,6) |
| PSSA3 | 10,81x → 11,53x | R$ 67,41 → R$ 71,93 | +7% | passou a detectar alta (+1,3) |
| TIMS3 | 18,56x → 18,85x | R$ 38,18 → R$ 38,77 | +1,5% | mesma direção, faixa mais estreita |
| SANB11 | 15,70x → 15,88x | R$ 53,84 → R$ 54,46 | +1,1% | mesma direção, faixa mais estreita |

As duas quedas grandes vão na direção conservadora — o motor passou a enxergar deterioração que a
média escondia.

**Uma média continua no motor, de propósito**, e é a de `mediana_com_tendencia` quando a metade
recente tem menos de 5 pontos (`est = st.median(novo) if len(novo) >= 5 else st.mean(novo)`). Ela
não toca o P/L — vale para P/VP, EV/Receita, ROE e paridade — e existe porque a **mediana de 3
pontos é só escolher um deles**: descarta 2 de 3 observações e devolve dado cru. Foi o defeito que
o usuário encontrou em 13/09 ("o lucro normalizado está quase igual ao de 2025 em todos"), e trocar
de volta o reintroduziria.

### 34.8 Os rótulos passam a dizer "mediano"

A tela dizia "P/L médio" e "ROE médio" para números que sempre foram medianas. Corrigido no
cabeçalho das colunas 14 e 16, nas tooltips e no texto do motor. As ocorrências de "média" que
**permanecem** são as que descrevem médias de verdade: a média do ciclo no EV/EBITDA de cíclica, a
média própria+pares que o `backtest_pares` mediu (história, não método vigente) e a citação
literal do pedido do usuário.

---

## 35. A amarração P/L ↔ ROE em proporção direta, sem teto (14/09/2026)

O usuário escreveu a regra que quer, com a ponte do P/VP e um exemplo numérico:

```
P/L Ajustado = P/L Mediano Histórico × (ROE Atual ÷ ROE Histórico)
```

Duas mudanças no motor para que ele execute exatamente isso.

### 35.1 O teto de ±30% saiu

A fórmula do usuário não tem teto. Saiu. O que o teto protegia continua verdadeiro e fica
registrado: proporção direta faz o múltiplo **dobrar** quando o ROE dobra, e a teoria não sustenta
isso — a relação entre ROE e P/L justo é não-linear e depende de payout e de Ke, nenhum dos dois
observável sem premissa. Hoje nenhuma linha do Radar passa de ±45%, então o efeito prático é
pequeno; o risco aparece em empresa vindo de ano de prejuízo ou de lucro extraordinário.

### 35.2 A truncagem de tendência sai de onde o ROE atua

"P/L **mediano histórico**" é a mediana da série inteira, não a dos 3 anos recentes. E não é só
literalidade: truncar a série **e** multiplicar pelo ajuste de ROE aplica a correção de recência
**duas vezes**. Os dois mecanismos fazem o mesmo trabalho — dizer que a empresa de hoje não é a
dos anos antigos — só que a truncagem faz isso **mudo**, jogando metade da série fora sem declarar
por quê, e o ROE faz **declarando** o motivo e o tamanho.

O ITUB3 é o caso limpo: truncada, a âncora era 10,0x (só 2024-2026, o período caro); plena, 7,8x.
Com o ajuste de 1,156 em cima, a versão truncada cobrava 11,56x — o múltiplo caro **e** o prêmio
de rentabilidade, pelo mesmo fato.

`truncar=False` passa a valer nos quatro pontos onde `alvo_com_pares` atua (E/P, P/VP, EV/Receita,
P/FFO). A regra de tendência continua onde o ROE **não** corrige: lucro normalizado, crescimento e
o EV/EBITDA de ciclo.

### 35.3 Efeito: 13 das 33 linhas

| Ativo | Múltiplo | Justo | Δ |
|---|---|---|---|
| CLSC4 | 6,28x → 4,86x | R$ 121,95 → R$ 94,50 | −23% |
| ITSA4 | paridade | R$ 19,26 → R$ 15,03 | −22% |
| **ITUB3** | 11,56x → **9,03x** | R$ 59,75 → **R$ 46,63** | −22% |
| BMEB4 | 8,89x → 7,47x | R$ 87,29 → R$ 73,36 | −16% |
| PSSA3 | 11,53x → 10,81x | R$ 71,93 → R$ 67,41 | −6% |
| LEVE3 | 9,63x → 9,15x | R$ 43,38 → R$ 41,23 | −5% |
| CPFE3 | 7,72x → 7,46x | R$ 39,67 → R$ 38,36 | −3% |
| SANB11 | 15,88x → 15,70x | R$ 54,46 → R$ 53,84 | −1% |
| BBSE3 | 8,42x → 8,62x | R$ 36,43 → R$ 37,27 | +2% |
| TIMS3 | 18,85x → 20,80x | R$ 38,77 → R$ 42,77 | +10% |
| SHUL4 | 5,03x → 5,66x | R$ 3,95 → R$ 4,44 | +13% |
| MULT3 | 10,53x → 12,22x | R$ 28,57 → R$ 33,17 | +16% |
| BRSR6 | 4,51x → 5,97x | R$ 20,31 → R$ 26,91 | +33% |

### 35.4 ⚠️ A identidade citada aponta para o outro lado

A ponte `P/L = P/VP ÷ ROE` está correta, mas ela **não** implica a regra de três. Lida ao pé da
letra, ela diz o contrário: se o ROE cai e o P/VP se mantém, o P/L justo **sobe** (o denominador
encolheu), não desce.

A regra de três é uma afirmação separada e mais forte. Abrindo:

```
Preço = LPA × P/L_ajustado
      = (VPA × ROE_atual) × P/L_hist × (ROE_atual ÷ ROE_hist)
      = VPA × P/VP_hist × (ROE_atual ÷ ROE_hist)²
```

Ou seja: ela escala o **P/VP justo pelo QUADRADO** da razão de ROE. O ROE menor já derruba o preço
uma vez, pelo **LPA projetado menor**; ajustar o múltiplo pela mesma razão aplica o golpe uma
segunda vez. A versão linear (P/VP justo ∝ ROE) deixaria o P/L **inalterado** — toda a proteção
viria do LPA.

Isso não invalida a escolha: ela é **deliberadamente conservadora**, e é o que a última frase do
pedido diz — *"você só deve pagar o P/L de 9,2x se acreditar que o ROE vai voltar para a casa dos
16%"*. Fica declarado que o efeito é quadrático, não que ele seja um erro.

### 35.5 Por que o SANB11 não reproduz o exemplo

O exemplo esperava fator 0,689 (ROE 16% → 11,03%). O motor dá **1,00**. A conta está certa; os
insumos é que são outros:

| | Exemplo | Motor (base Partnr) |
|---|---|---|
| P/L mediano | 9,2x (10 anos) | **15,70x** (2021→) |
| ROE histórico | 16,0% | **11,4%** |
| ROE atual | 11,03% | 11,4% |
| Fator | 0,689 | **1,000** |
| LPA projetado | R$ 4,25 | R$ 3,43 |
| Preço justo | R$ 26,94 | R$ 53,84 |

**A causa é a janela.** O ROE do Santander na base é `2021 18,5% · 2022 16,7% · 2023 9,8% ·
2025 10,4% · 2026 11,4%` (2024 ausente). A deterioração já ocupa **3 dos 5 anos** da janela 2021→,
então a mediana do período **é** 11,4% — o nível de hoje. A razão vira 1,00 e o ajuste desaparece
exatamente onde deveria morder.

Isto é estrutural, não um caso isolado: **quando a queda de rentabilidade é velha o bastante para
ocupar metade da janela, a amarração se auto-neutraliza.** Para ela morder, o `ROE histórico`
precisa vir de uma janela mais longa que a do P/L — o nível de tempos normais, não o recente.

E a série longa não resolve sozinha: o P/L do SANB11 na Partnr nunca passou perto de 9,2x
(`2016 36,2x · 2019 16,9x · 2022 11,0x · 2025 17,0x`; mediana de 10 anos = **18,68x**). Com a
janela longa e o fator 0,689 o preço justo sairia R$ 44,17 — ainda longe dos R$ 26,94, porque o
9,2x e o LPA de R$ 4,25 do exemplo vêm de outra fonte.

**Decisão pendente do usuário:** manter `ROE histórico` na janela 2021→ (como está, e como ele
fixou) ou coletar ROE de 10 anos só para esse denominador. A segunda opção faz a amarração morder
em bancos deteriorados e exige uma coleta nova na Partnr.

---

## 36. O múltiplo de unit vinha inflado, e o filtro do celular estava fora da tela (14/09/2026)

> "O P/L mediano do BTG está errado, não é esse."
> "O filtro não aparece no celular."

### 36.1 O bug do múltiplo de unit

O Radar mostrava **P/L mediano de 39,45x** para o BPAC11 e daí tirava preço justo de **R$ 230,69**
(margem de 73%). O BTG negocia perto de **11x**.

**A causa:** para alguns papéis a Partnr traz `pl` e `pvp` como *preço da UNIT ÷ valor por AÇÃO*.
A unit do BPAC11 é 1 ON + 2 PN, então o múltiplo sai **3× inflado**. O motor já tinha `FATOR_UNIT`
e o aplicava no LPA derivado e no P/VP — mas `teto_ep` lia o campo `pl` **cru**, e esse campo
ganhava da derivação sempre que existia. O `pl_setorial` lia cru também, contaminando a mediana do
grupo FIN.

**E o fator declarado não resolve.** Conferindo contra o balanço (valor de mercado ÷ lucro):

| ativo | campo `pl` | P/L do balanço | fator medido | é unit? |
|---|---|---|---|---|
| BPAC11 | 32,48 | **11,55** | 2,81 → **3** | sim |
| SANB11 | 15,52 | **7,73** | 2,01 → **2** | sim |
| KLBN11 | 43,67 | 43,96 | **0,99 → 1** | **sim, e mesmo assim não infla** |

A unit da Klabin vale 5 ações, mas os campos dela **já vêm por unit**. Dividir por 5 quebraria a
Klabin para consertar o BTG. **Não existe regra de unit que acerte os três — só medição acerta.**

A correção: `fator_multiplo(t, A)` mede o fator contra o balanço; `pl_ano(t, A, y)` é a **única**
definição de P/L do exercício e serve os três consumidores (`teto_ep`, `pl_setorial` e a coluna
P/L mediano). A medição decide o **valor**; a lista `FATOR_UNIT` decide quem é **elegível** —
papel que não é unit nunca entra, por mais ruidosa que a contagem de papéis esteja num ano (o
ITUB3 mede 1,19 e o BMEB4 1,13, e nem chegam a ser testados).

**Efeito — 4 linhas:**

| Ativo | Múltiplo | Justo | Δ | Margem |
|---|---|---|---|---|
| **BPAC11** | 45,69x → **15,23x** | R$ 230,69 → **R$ 76,90** | **−67%** | 73% → 18% |
| **SANB11** | 15,70x → **7,85x** | R$ 53,84 → **R$ 26,92** | **−50%** | +36% → −29% |
| VIVA3 | 7,87x → 7,80x | R$ 24,21 → R$ 24,00 | −1% | — |
| ASAI3 | 7,87x → 7,80x | R$ 5,61 → R$ 5,56 | −1% | — |

VIVA3 e ASAI3 usam o P/L do `_UNIVERSO` (não têm série própria), que caiu de 7,9x para 7,8x quando
a contaminação saiu.

⚠️ **Este bug também explica a seção 35.5.** O exemplo do usuário para o SANB11 dava preço justo de
**R$ 26,94** e o motor dava R$ 53,84 — exatamente o dobro, porque o P/L estava dobrado. Corrigido,
o motor dá **R$ 26,92**. A divergência não era de janela nem de método; era o fator de unit.

### 36.2 O filtro de segmento no celular

Duas causas em série, e a primeira escondeu a segunda.

**Primeira** (corrigida antes): `.filter-group{display:none}` dentro de `@media(max-width:768px)`,
regra que vinha da versão original — fazia sentido com 20 segmentos ocupando três linhas, deixou
de fazer com 10.

**Segunda, e era esta que importava:** com `display` devolvido, os chips continuavam invisíveis.
A tabela tem 2.563px, então o **documento** fica com ~1.560px de largura no telefone.
`width:100%` numa barra `position:fixed` resolve contra o **bloco contêiner inicial** — 1.560px —
e elemento fixo **não acompanha rolagem horizontal**. Tudo o que passava dos 390px da tela ficava
inalcançável **para sempre**. Os chips de segmento são os últimos da barra: existiam no DOM,
respondiam a clique via JS, e nenhum dedo conseguia chegar neles.

**Terceira, porque a segunda correção trocou um defeito por outro.** `width:100vw` resolveu os
chips e quebrou o cabeçalho — o usuário devolveu: *"o cabeçalho tá menor que a largura do espaço
no iPhone Pro, tava bom antes do último ajuste"*. Estava.

São **duas larguras diferentes**, e a barra precisa de uma para cada coisa:

| | largura certa | no iPhone 15 Pro | o que quebra com a outra |
|---|---|---|---|
| **CAIXA** (fundo, borda) | a do **conteúdo** | 1.572px | com 100vw vira tarja de 25% da área visível, o resto vazio |
| **CONTEÚDO** (busca, chips, botões) | a da **tela** | 393px | com 100% os chips caem fora e ficam inalcançáveis |

A solução usa as duas ao mesmo tempo:

```css
.nav, .radar-controls{
  width: 100%;                                        /* caixa = 1.572px */
  padding-right: max(1rem, calc(100% - 100vw + 1rem)); /* conteúdo = 393px */
}
```

`box-sizing:border-box` faz o resto: o fundo continua com 1.572px e a caixa de conteúdo encolhe
para 393px. O `max()` protege o caso sem transbordo, onde a conta seria negativa.

Verificado em iPhone 15 Pro (393px de tela, 1.572 visíveis), 15 Pro Max (430/1.720), 13 (390),
SE (320) e Pixel 5 (393), e por varredura de 320px a 1920px: **em toda largura a barra cobre a
tela inteira E os 10 chips ficam dentro dela**. Clique no último chip filtra a tabela; a barra
continua ancorada em `left:0` depois de rolar 800px para a direita. Zero erro de console,
desktop sem regressão (24 col == 24 th == 24 td, zero desalinho).
