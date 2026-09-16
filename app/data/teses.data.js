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
  // Exemplo de formato (comentado — apagar quando a primeira tese de verdade for adicionada):
  // "BBAS3": {
  //   data: "2026-09-16",
  //   gatilho: "Normalização da inadimplência da carteira de agronegócio",
  //   premissa: "ROE volta a ~12% em até 2 anos, se a inadimplência do agro arrefecer como o próprio BB projeta para 2026",
  //   precoCenario: 19.53,
  //   precoOficial: 10.44,
  //   confianca: "média",
  //   condicaoDeRevisao: "Inadimplência agro (90d) cair 2 trimestres seguidos, OU ROE trimestral > 10%",
  //   fonte: "https://investalk.bb.com.br/radar/banco-do-brasil-espera-arrefecimento-da-inadimplencia-do-agronegocio-ainda-neste-ano"
  // },
};
