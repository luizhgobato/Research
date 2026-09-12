# Motor de preço-teto e TIR real — export para outro chat

Este pacote é só o **motor de cálculo** (Python), sem o dashboard HTML/JS. Serve para
levar para outra sessão do Claude Code e continuar evoluindo o motor separado da parte
visual, ou rodar as análises isoladas.

## O que tem aqui

- `scripts/motor_teto.py` — motor de preço-teto: consenso de métodos (E/P, EV/EBITDA,
  Gordon/Bazin, P/VP×ROE, P/VP, EV/Receita, paridade NAV), payout, detecção de quebra
  societária/operacional, `SEM_TETO` (recusa declarada por ticker).
- `scripts/gerar_tir.py` — motor de TIR real: três medidas (caixa/FCFE, dividendos/DDM,
  lucro), crescimento por regressão log, exporta os campos para recálculo ao vivo no
  navegador (`pap`, `d0`, `fcfe`).
- `scripts/gerar_colunas.py` — gera as colunas derivadas do Radar (lucro normalizado,
  LPA, etc.) a partir do `HIST_SEED`.
- `scripts/backtest_multiplos.py` — corrida de múltiplos (L/P vs EV/EBITDA vs DY vs
  P/VP) sobre os 30 tickers do Radar, 2021-2026.
- `data/historico.data.js` — `HIST_SEED`: histórico anual por ticker (receita, lucro,
  EBITDA, dívida, múltiplos), fonte MCP Partnr (B3/CVM). É um arquivo `.js` com uma
  constante — os scripts Python leem convertendo para JSON com regex.
- `data/fluxo.json` — FCO, capex, lucro recorrente histórico por ticker (coletado do
  Partnr, `CASH_FLOW_STATEMENT`/`INCOME_STATEMENT`, TTM).
- `data/tir.data.js` — saída de `gerar_tir.py` (`TIR_SEED`).
- `data/setorial.data.js` — dados setoriais usados no fallback de pares.
- `analise/tetos.json` — saída de `motor_teto.py`.
- `METODOLOGIA_ANALISE.md` — toda a documentação do racional de cada decisão do motor
  (28 seções, cada uma nasceu de uma pergunta ou bug real encontrado).

## Como rodar

```bash
cd motor_export
python3 scripts/motor_teto.py      # gera analise/tetos.json
python3 scripts/gerar_tir.py       # gera data/tir.data.js (lê motor_teto.py por import)
python3 scripts/gerar_colunas.py   # imprime as colunas derivadas
```

`gerar_tir.py` e `gerar_colunas.py` importam `motor_teto.py` via `exec()` do próprio
texto-fonte (não é um pacote Python normal) — mantenha os três na mesma pasta `scripts/`.

## O que NÃO está aqui

- O dashboard (HTML/CSS/JS) — isso é outro projeto/pasta, focado em apresentação, não
  em cálculo.
- `data/radar-rows.data.js` — as 30 linhas da tabela (tem preço-teto e outras colunas
  **coladas manualmente** do output do motor; não é gerado automaticamente ainda — ver
  seção da metodologia sobre isso).
- Acesso ao MCP Partnr (dados B3/CVM) — os arquivos `.json`/`.js` de dados são
  **snapshots já coletados**; para atualizar com dados novos, a outra sessão precisa
  de um conector Partnr próprio (ou equivalente) e recriar `data/fluxo.json` e
  `data/historico.data.js` no mesmo formato.

## Se for continuar o punch-list pendente

Ver a seção final do `METODOLOGIA_ANALISE.md` (ou pedir para o Claude ler o arquivo)
para a lista do que falta: o backtest grande (300+ papéis/10 anos), motor de shopping
por cap rate, auditoria de thresholds arbitrários e de double-counting entre métodos.
