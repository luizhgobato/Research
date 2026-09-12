# Receita: puxar dados do MCP Partnr para a aba "Base de Dados"

Alvo: preencher `HIST_SEED[TICKER][ANO]` em `data/historico.data.js`.
Anos: **2021 a 2026**.
- 2021-2025 → `frequency:"ANNUAL"` com `reference_date` = "AAAA-12-31" de cada ano.
- **2026 → `frequency:"TTM"` com `reference_date:"2026-06-30"`.** 2026 NÃO fechou: pedir ANNUAL
  devolve nada e a empresa aparece sem o ano corrente. Este erro já aconteceu — não repita.
- **Sempre passe `reference_date`.** Sem ele a resposta vira um arquivo de centenas de milhares
  de caracteres (a série é diária).
- `ROE` e `ROIC` muitas vezes NÃO existem em ANNUAL, só em TTM. Se vier vazio no ano fechado,
  refaça aquele ano com `frequency:"TTM"` e `reference_date:"AAAA-12-31"` — é equivalente.

## Campos do objeto de cada ano (nomes EXATOS)

| Campo | Origem | ID Partnr | Observação |
|---|---|---|---|
| `preco` | `stocks_quotes` | — | Fechamento do último pregão do ano (2026 = último disponível) |
| `receita` | `companies_reports` INCOME_STATEMENT | `NET_REVENUE` | BRL absoluto |
| `custos` | derivado | — | `receita - lucrobruto`, gravado **negativo**. null se faltar qualquer um |
| `lucrobruto` | `companies_reports` INCOME_STATEMENT | `GROSS_INCOME` | |
| `ebitda` | `companies_reports` INCOME_STATEMENT | `EBITDA` | |
| `ebit` | `companies_reports` INCOME_STATEMENT | `EBIT` | |
| `imposto` | `companies_reports` INCOME_STATEMENT | `INCOME_TAXES` | |
| `lucrolin` | `companies_reports` INCOME_STATEMENT | `NET_INCOME` | |
| `divbruta` | `companies_reports` BALANCE_SHEET | `GROSS_DEBT` | |
| `divliq` | `companies_reports` BALANCE_SHEET | `NET_DEBT` | |
| `mgBruta` | `companies_ratios` | `GROSS_MARGIN` | **× 100** e arredonde em 2 casas |
| `mgEbitda` | `companies_ratios` | `EBITDA_MARGIN` | **× 100**, 2 casas |
| `mgLiq` | `companies_ratios` | `NET_MARGIN` | **× 100**, 2 casas |
| `roe` | `companies_ratios` | `ROE_AVG` | **× 100**, 2 casas |
| `roic` | `companies_ratios` | `ROIC` | **× 100**, 2 casas. **NÃO usar `ROIC_AVG`** — é outra definição (capital médio), dá número diferente e não existe para seguradora |
| `pl` | `companies_valuationRatios` | `PRICE_TO_EARNINGS` | múltiplo, 2 casas |
| `pvp` | `companies_valuationRatios` | `PRICE_TO_BOOK` | múltiplo, 2 casas |
| `dy` | `companies_valuationRatios` | `DIVIDEND_YIELD` | **× 100**, 2 casas |
| `evEbitda` | `companies_valuationRatios` | `EV_TO_EBITDA` | múltiplo, 2 casas |
| `divPl` | `companies_ratios` | `NET_DEBT_TO_SHAREHOLDERS_EQUITY` | múltiplo, 2 casas |
| `lpa` | `companies_reports` INCOME_STATEMENT | `EPS` | BRL por ação, 2 casas |
| `divEbitda` | `companies_ratios` | `NET_DEBT_TO_EBITDA` | múltiplo, 2 casas. Só inclua se existir |

## Chamadas por empresa (4 no total)

1. `companies_reports` — `symbol`, `section:"INCOME_STATEMENT"`, `frequency:"ANNUAL"`,
   `aggregation:"CONSOLIDATED"`, `latest_by_reference_date:true`
2. `companies_reports` — igual, `section:"BALANCE_SHEET"`
3. `companies_ratios` — `frequency:"ANNUAL"`, `latest_by_reference_date:true`,
   `ids:"GROSS_MARGIN,EBITDA_MARGIN,NET_MARGIN,ROE_AVG,ROIC,NET_DEBT_TO_EBITDA,NET_DEBT_TO_SHAREHOLDERS_EQUITY"`
4. `companies_valuationRatios` — `frequency:"ANNUAL"`,
   `ids:"PRICE_TO_EARNINGS,PRICE_TO_BOOK,DIVIDEND_YIELD,EV_TO_EBITDA"`

E `stocks_quotes` (`type:"historical"`, `start_date`/`end_date`) para o `preco` de cada
fim de ano — pode ser uma chamada cobrindo 2021-01-01 até hoje.

## Armadilhas conhecidas (leia antes de começar)

- **Resultado gigante vira arquivo.** Quando a resposta exceder o limite, ela é salva num
  `.txt` cujo caminho aparece no erro. O formato é `[{type,text}]` e o payload real está em
  `.[0].text` — **use `jq -r '.[0].text' ARQ | jq ...`** para extrair. NUNCA leia o arquivo
  inteiro; extraia só o que precisa e apague o arquivo ao terminar.
- **Estrutura da resposta:** `{ID: {FREQUENCIA: [ {value, format, reference_date, publish_date}, ... ]}}`.
  Pegue o item de cada ano por `reference_date` (ex.: `2025-12-31`). Se houver mais de um
  para o mesmo ano, use o de `publish_date` mais recente.
- **Percentuais vêm como fração** (0,7604 = 76,04%) mesmo com `format:"PERCENTAGE"`. Multiplique por 100.
- **`companies_ratios` recusa report items** e vice-versa. O erro diz qual ferramenta usar — obedeça.
- **`COST_OF_GOODS_SOLD` não existe** no motor. Por isso `custos` é derivado.
- **Bancos e seguradoras** (ITUB3, BMEB4, BBSE3, CXSE3, IRBR3): receita/EBITDA/margens
  frequentemente não se aplicam ou vêm vazios. **Grave `null`, não invente e não force.**
- **ROXO34 é BDR** (Nubank). Pode não existir como empresa brasileira no Partnr. Se não
  achar, devolva `"SEM_DADOS"` para ele — não tente outro ticker.
- Campo sem dado = `null`. **Nunca chute um número.**
- ⚠️ **UNITS (tickers terminados em 11: SANB11, KLBN11, BPAC11).** Uma unit é um pacote de
  várias ações (KLBN11 = 1 ON + 4 PN; SANB11 = 1 ON + 1 PN; BPAC11 = 1 ON + 2 PN). O `EPS`
  do Partnr é **por ação, não por unit** — dividir o preço da unit por esse LPA dá um P/L errado
  por um fator inteiro. Nesses casos: pegue `pl`, `pvp` e `dy` **do `companies_valuationRatios`**
  (que já vêm na base correta) e **NÃO os recalcule** a partir de preço ÷ LPA. Reporte o `lpa`
  como veio e avise no retorno que é por ação.
- Para o `preco` use o **ticker** (SANB11), mas para os fundamentos use o **símbolo** (SANB).

## Formato do retorno

Devolva SÓ um bloco JSON, sem texto em volta:

```json
{
  "ALOS3": {
    "2025": {"preco":28.40,"receita":2858517000,"custos":-746351000, ...},
    "2024": {...}
  },
  "ROXO34": "SEM_DADOS"
}
```

Inclua todos os 21 campos em cada ano (com `null` onde não houver), exceto `divEbitda`
que é opcional. Não escreva em nenhum arquivo do projeto — só devolva o JSON.
