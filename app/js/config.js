const IPCA=0.055, DIV_GROWTH=0.08, PREMIO_IPCA=0.07;

// ── TAXA LIVRE DE RISCO ──────────────────────────────────────────────────────────────────
// Selic meta definida pelo Copom. É o "custo de oportunidade zero-risco": qualquer ação
// precisa entregar earnings yield (L/P) acima disso para justificar o risco de renda variável.
// Usada pelo motor de decisão (js/decisao.js — coluna "Prêmio Selic" e score de critérios).
// ATUALIZAR a cada reunião do Copom. Última: 05/08/2026 (manteve em 14,00%).
// Próxima reunião: 16/09/2026.
const SELIC = 0.14;
const SELIC_DATA = '05/08/2026';
// Piso de ROE aceitável: acima do custo de capital próprio (Ke = 16% em financeiras,
// ver METODOLOGIA_ANALISE.md seção 8). 15% é o corte prático usado no score.
const ROE_MINIMO = 15;
// Alavancagem máxima tolerada para não-financeiras (dív. líq./EBITDA).
const ALAVANCAGEM_MAX = 3;

// Cap de crescimento de lucro por segmento (floor universal = IPCA)
const CRESCIMENTO_SEGMENTO = {
  'Shoppings':            0.12, // reajuste IGP-M + expansão ABL
  'Bancos':               0.15, // carteira de crédito + spread (NIM)
  'Seguradoras':          0.18, // volume de prêmios + resultado financeiro
  'Energia Elétrica':     0.10, // reajuste tarifário regulado (ANEEL)
  'Saneamento':           0.10, // reajuste tarifário regulado (ARSESP/ARSAE)
  'Telecom':              0.10, // ARPU + expansão de clientes (mercado maduro)
  'Varejo':               0.20, // ciclo econômico + same-store sales
  'Agronegócio':          0.25, // preço de commodity + volume safra
  'Tecnologia':           0.30, // receita recorrente (SaaS) + expansão
  'Saúde':                0.18, // sinistralidade + volume de procedimentos
  'Construção Civil':     0.20, // VSO + lançamentos + ciclo imobiliário
  'Mineração':            0.20, // preço commodity + volume de produção
  'Petróleo e Gás':       0.25, // preço do petróleo + produção (boe/dia)
  'Transportes':          0.15, // volume + reajuste tarifário de concessões
  'Alimentos e Bebidas':  0.15, // volume + preço/mix de produtos
  'Papel e Celulose':     0.20, // preço da celulose (USD) + volume
  'Locação de Veículos':  0.20, // expansão de frota + diária média
  'Educação':             0.15, // matrículas + ticket médio
  'Químico':              0.15, // spread petroquímico + volume
  'Real Estate':          0.12, // aluguel + vacância (similar a shoppings)
};
// ── UNITS: quantas AÇÕES cada unit empacota ──────────────────────────────────────────────
// Sexta aparição do mesmo erro neste projeto, e a primeira vez que ele é corrigido no lugar
// certo em vez de caso a caso. O Partnr reporta LPA e valor patrimonial POR AÇÃO; o PREÇO e o
// DIVIDENDO negociados são POR UNIT. Misturar as duas bases erra por um fator inteiro:
//   · KLBN11 = 1 ON + 4 PN  → 5 ações por unit
//   · SANB11 = 1 ON + 1 PN  → 2
//   · BPAC11 = 1 ON + 2 PN  → 3
// Sintoma que denunciou: a coluna de LPA mostrava R$2,02 no SANB11 contra dividendo de R$1,91,
// um payout aparente de 95% para um banco que distribui ~49%. Com o LPA por unit (R$4,04) a
// conta fecha. O BPAC11 idem: 23% aparente vira 26%, batendo com os 24% que o motor de
// preço-teto calcula pela DFP.
// Mesma tabela de scripts/motor_teto.py (FATOR_UNIT) — se um dia mudar, muda nos dois.
const FATOR_UNIT = { KLBN11: 5, SANB11: 2, BPAC11: 3 };

const COLORS=['#4f46e5','#0891b2','#16a34a','#d97706','#dc2626','#7c3aed','#0d9488','#ea580c','#2563eb','#65a30d'];


// ── API TOKENS ──
// ATENÇÃO: token exposto no client-side. Se o repositório for público,
// use um token free-tier dedicado ou regenere em https://brapi.dev/dashboard
const BRAPI_TOKEN = '9BpaYC3MrtWYicZWEoWQeP';
