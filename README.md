# Research

Dashboard de análise de investimentos (ações B3), publicado via GitHub Pages
em `luizhgobato.github.io/Research`.

## Sobre este repositório

Este repo guarda **apenas o export estático** do dashboard — o arquivo
`Analista Investimento.html` é gerado por `scripts/build.py` a partir do
projeto de origem (`js/`, `css/`, `scripts/motor_teto.py`, `scripts/gerar_tir.py`),
que **não vive aqui**. Edições devem ser feitas no projeto de origem e
reexportadas; editar o HTML diretamente funciona para correções pontuais,
mas se perde na próxima geração.

- `Analista Investimento.html` — dashboard completo (arquivo servido pelo Pages)
- `index.html` — redireciona para o arquivo acima
- `robots.txt` + `<meta name="robots">` — bloqueiam indexação por buscadores
  (o link continua acessível a quem o tiver)
- `docs/changelog/` — resumos de sessões de desenvolvimento

## Dados e privacidade

O HTML publicado **não contém** posições, quantidades ou valores reais de
carteira — esses dados ficam só no `localStorage` do navegador de quem usa o
dashboard (não sincronizam entre dispositivos nem chegam a este repositório).

A cotação ao vivo usa um token free-tier do [brapi.dev](https://brapi.dev)
exposto no client-side (inevitável em um app 100% estático sem backend) —
risco aceito dado o baixo impacto de um token free-tier.
