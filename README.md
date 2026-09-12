# Research

Dashboard de análise de investimentos (ações B3), publicado via GitHub Pages
em `luizhgobato.github.io/Research`.

## Sobre este repositório

`Analista Investimento.html` é a página publicada (exportada por
`scripts/build.py` — build.py em si ainda não está neste repo, só o motor de
cálculo). Editar o HTML diretamente funciona para correções pontuais de
front-end (layout, CSS, JS de exibição), mas qualquer mudança na
metodologia de cálculo (preço-teto, TIR) deve ser feita no motor abaixo e
reexportada, senão se perde/diverge na próxima geração.

- `Analista Investimento.html` — dashboard completo (arquivo servido pelo Pages)
- `index.html` — redireciona para o arquivo acima
- `robots.txt` + `<meta name="robots">` — bloqueiam indexação por buscadores
  (o link continua acessível a quem o tiver)
- `docs/changelog/` — resumos de sessões de desenvolvimento
- `scripts/motor_teto.py`, `scripts/gerar_tir.py`, `scripts/gerar_colunas.py`,
  `scripts/backtest_multiplos.py` — motor de cálculo (Python): preço-teto,
  TIR real, colunas derivadas e backtest de múltiplos. Ver `scripts/README.md`
  para como rodar
- `data/` — `HIST_SEED`, `TIR_SEED`, fluxo de caixa e dados setoriais que
  alimentam o motor (snapshots coletados via MCP Partnr — não são
  atualizados automaticamente)
- `analise/tetos.json` — saída do `motor_teto.py`
- `METODOLOGIA_ANALISE.md` — racional de cada decisão do motor (28 seções)

## Dados e privacidade

O HTML publicado **não contém** posições, quantidades ou valores reais de
carteira — esses dados ficam só no `localStorage` do navegador de quem usa o
dashboard (não sincronizam entre dispositivos nem chegam a este repositório).

A cotação ao vivo usa um token free-tier do [brapi.dev](https://brapi.dev)
exposto no client-side (inevitável em um app 100% estático sem backend) —
risco aceito dado o baixo impacto de um token free-tier.
