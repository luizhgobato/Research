// ══════════════════════════════════════════════════════════════════════════════════════════
// CENÁRIO DE TESE — registro manual, ticker por ticker (a pedido do usuário, 16/09/2026)
// ══════════════════════════════════════════════════════════════════════════════════════════
// NÃO é gerado por script e NÃO roda em lote para os 35 ativos do Radar. Cada entrada é
// escrita à mão, uma de cada vez, quando o usuário pede explicitamente para registrar uma
// tese (ex.: "faça a tese do BBAS3"). Ausência de entrada aqui = "sem tese" no Radar, e isso
// é o estado normal, não uma pendência.
//
// POR QUE ISTO É SEPARADO DO PREÇO JUSTO (analise/tetos.json / motor_teto.py):
// o Preço Justo nunca aposta no futuro — usa só ROE e múltiplo observados. O Cenário de Tese
// é o oposto: uma aposta explícita e datada de que o cenário vai mudar (ex.: ROE do BBAS3
// volta a subir). As duas coisas nunca se misturam — a Tese NUNCA entra no cálculo de
// margem, veredicto ou estrelas de convicção do motor. Ver conversa de 16/09/2026 sobre
// "como capturar oportunidade de virada sem contaminar o motor automático com previsão".
//
// CAMPOS obrigatórios por entrada:
//   data              - quando a tese foi escrita (revisar a cada resultado trimestral)
//   gatilho           - o que precisa acontecer para a tese se confirmar
//   premissa          - o pressuposto explícito (ex.: ROE-alvo, prazo) e o racional por trás
//   precoCenario      - preço-alvo SE a premissa se confirmar (mesma fórmula do motor, só
//                       trocando o ROE atual pelo ROE-alvo da premissa — nunca uma conta nova)
//   precoOficial      - o Preço Justo oficial do motor no momento em que a tese foi escrita,
//                       para contraste lado a lado (evita esquecer o número "sem aposta")
//   confianca         - qualitativa (baixa / média / alta) — nunca um % inventado
//   condicaoDeRevisao - o que invalida esta tese; dado observável, não sentimento
//   fonte             - de onde veio a premissa (ex.: guidance da empresa, notícia)
//
// Chave = ticker sem ".SA" (mesmo padrão de REPORTS em reportsData).
window.TESES = {
  "BBAS3": {
    data: "2026-09-16",
    gatilho: "Normalização da inadimplência da carteira de agronegócio, hoje a causa documentada da queda do ROE (lucro caiu 54% no 1T26 por avanço da crise no agro — Agência Brasil, 14/05/2026). O próprio BB projeta arrefecimento da inadimplência agro ainda em 2026.",
    premissa: "ROE volta à MEDIANA dos últimos 6 anos da própria empresa (13,8% — não um número novo, é a mesma mediana que já ancora o motor). Não usa a melhor marca histórica (17,64% em 2023), só o retorno ao padrão típico do banco. Sem prazo definido — a condição de revisão abaixo é o que decide, não o calendário.",
    precoCenario: 21.77,
    precoOficial: 10.44,
    confianca: "média",
    condicaoDeRevisao: "ROE trimestral do BB voltar a ficar acima de 10% por 2 trimestres seguidos, OU o próprio BB reportar queda na inadimplência agro (90d) por 2 trimestres seguidos. Se isso NÃO acontecer até o balanço do 4T26 (fev/2027), a tese fica sem sustentação e deve ser descartada, não renovada.",
    fonte: "https://agenciabrasil.ebc.com.br/economia/noticia/2026-05/lucro-do-banco-do-brasil-cai-54-com-avanco-da-crise-no-agro"
  },
};
