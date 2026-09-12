# Research

Dashboard de análise de investimentos (ações B3), publicado via GitHub Pages
em `luizhgobato.github.io/Research`.

## Sobre este repositório

`Analista Investimento.html` (raiz) é a página publicada — gerada por
`app/scripts/build.py` a partir do projeto-fonte em `app/`. **Não edite esse
arquivo diretamente**: qualquer mudança (layout, CSS, JS, metodologia de
cálculo) deve ser feita em `app/` e reexportada, senão se perde/diverge na
próxima geração (é exatamente o tipo de "duas fontes de verdade" que
`METODOLOGIA_ANALISE.md` trata como bug recorrente do projeto).

- `Analista Investimento.html` — dashboard completo publicado (gerado, não editar)
- `index.html` — redireciona para o arquivo acima
- `robots.txt` + `<meta name="robots">` — bloqueiam indexação por buscadores
  (o link continua acessível a quem o tiver)
- `docs/changelog/` — resumos de sessões de desenvolvimento
- `app/` — projeto-fonte completo:
  - `app/index.html`, `app/css/styles.css`, `app/js/*.js` — dashboard modular (dev)
  - `app/scripts/build.py` — gera `app/exports/Analista Investimento standalone.html`
    (CSS+JS inline) a partir do dev acima
  - `app/scripts/motor_teto.py`, `gerar_tir.py`, `gerar_colunas.py`,
    `backtest_multiplos.py` — motor de cálculo (preço-teto, TIR real, colunas
    derivadas, backtest de múltiplos). Ver `app/scripts/README.md`
  - `app/data/` — `HIST_SEED`, `TIR_SEED`, fluxo de caixa, dados setoriais e
    `radar-rows.data.js` (snapshots coletados via MCP Partnr — não atualizam
    automaticamente)
  - `app/analise/` — saídas dos scripts acima (`tetos.json`, `tir.json`, etc.)
  - `app/METODOLOGIA_ANALISE.md` — racional de cada decisão do motor (28 seções)

### Como publicar uma atualização

```bash
cd app
python3 scripts/build.py                 # gera app/exports/Analista Investimento standalone.html
cp "exports/Analista Investimento standalone.html" "../Analista Investimento.html"
```

Depois commitar e dar push (Pages publica a partir de `master`).

## Dados e privacidade

O HTML publicado **não contém** posições, quantidades ou valores reais de
carteira — esses dados ficam só no `localStorage` do navegador de quem usa o
dashboard (não sincronizam entre dispositivos nem chegam a este repositório).

A cotação ao vivo usa um token free-tier do [brapi.dev](https://brapi.dev)
exposto no client-side (inevitável em um app 100% estático sem backend) —
risco aceito dado o baixo impacto de um token free-tier.
