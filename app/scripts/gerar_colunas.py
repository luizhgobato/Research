#!/usr/bin/env python3
# ══════════════════════════════════════════════════════════════════════════════════════════
# GERADOR DAS COLUNAS DE LUCRO DO RADAR — auditoria de 06/09/2026
# ══════════════════════════════════════════════════════════════════════════════════════════
# Pedido do usuário: "valide todos os campos da tabela e garanta que todos estejam de um motor
# com racional declarado e que não tem nada na mão. E que esteja tudo preenchido."
#
# A auditoria achou três coisas, e as três eram piores que "faltou tooltip":
#
#  1. O RÓTULO DA COLUNA 4 MENTIA. Ela diz "Lucro 2025 REAL" e 20 das 30 linhas traziam o
#     lucro LTM de 2026. PETR4 (R$133,76 bi), VALE3 (R$8,69 bi), KLBN11 (R$0,54 bi), SAUD3,
#     AXIA3 e AURE3 batem exatamente com o TTM 2T26, não com o exercício de 2025. Quem lesse
#     a coluna como "o que a empresa ganhou em 2025" lia errado em dois terços da tabela.
#
#  2. A COLUNA 5 MISTURAVA DUAS DEFINIÇÕES. Em algumas linhas era projeção de 2026 (CPFE3
#     R$6,10 bi contra LTM de R$6,29 bi); em outras era lucro NORMALIZADO de meio de ciclo
#     (VALE3 R$43,26 bi contra LTM de R$8,69 bi — cinco vezes; KLBN11 R$2,51 bi contra
#     R$0,54 bi). Duas grandezas diferentes empilhadas na mesma coluna e ordenáveis juntas.
#
#  3. 29 DAS 30 LINHAS TINHAM `data-lucro-manual`. Eram números digitados, curados em datas
#     diferentes, sem motor comum — exatamente o que o usuário mandou eliminar.
#
# O QUE ESTE SCRIPT FAZ: regenera as colunas 4, 5, 6, 7, 9 e 10 a partir de duas fontes, e
# só duas — HIST_SEED (Partnr/B3/CVM) e o lucro normalizado de data/tir.data.js, que tem
# motor declarado por setor (METODOLOGIA_ANALISE.md seção 10). Nenhum número digitado.
#
#   col 4  Lucro LTM         = lucrolin do último exercício da base (TTM 2T26)
#   col 5  Lucro normalizado = motor por setor (receita × margem mediana · ROE × PL · FFO ·
#                              lucro recorrente), o mesmo que alimenta a TIR real
#   col 6  Δ normalizado/LTM = quanto o resultado atual está acima ou abaixo do normalizado
#   col 7  LPA normalizado   = lucro normalizado ÷ papéis negociados (units já resolvidas)
#   col 9  Div./Ação         = LPA × payout (seção 22)
#   col 10 DY                = Div./Ação ÷ cotação
#
# ⚠️ A COLUNA 6 MUDA DE SIGNIFICADO. Era "crescimento projetado"; passa a ser a DISTÂNCIA
# entre o resultado corrente e o normalizado. Não é previsão: é diagnóstico de ciclo. KLBN11
# com −83% não vai cair 83%; ela está 83% abaixo do que a própria série sugere como normal.
import json
import math, re, statistics as st
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
src = (RAIZ / 'scripts/motor_teto.py').read_text()
M = {}
exec(src[:src.index("if __name__")], M)
H = M['carregar']()
M['H_GLOBAL'] = H

# lucro normalizado + motor declarado, de data/tir.data.js (seção 10 da metodologia)
tir = (RAIZ / 'data/tir.data.js').read_text()

# Série anual de dividend yield, 2016-2026, coletada da Partnr em 13/09/2026. Substituiu duas
# fontes que brigavam pela mesma célula: um texto digitado à mão (várias linhas citando
# StatusInvest, a do ITUB3 usando o DY da ITUB4) e um bloco de runtime que sobrescrevia com a
# API. Agora as duas colunas de DY realizado — a de 2025 e a mediana de 10 anos — saem daqui.
DYH = json.loads((RAIZ / 'analise/dy_historico.json').read_text())['tickers']

def dy_ano(t, ano):
    v = DYH.get(t, {}).get(str(ano))
    return v if (v and v > 0) else None      # zero na base = dado ausente, não dividendo zero

def dy_mediana(t, n=10, ate=2025):
    anos = {int(y): v for y, v in DYH.get(t, {}).items()
            if ate - n + 1 <= int(y) <= ate and v and v > 0}
    if len(anos) < 3:
        return None, anos
    return st.median(anos.values()), anos
LN = {k: (float(v), mo) for k, v, mo in
      re.findall(r"(\w+):\s*\{[^}]*lucroNorm:(-?[\d.]+)[^}]*motor:'([^']*)'", tir)}
FIN = {k for k, v in M['MOTOR'].items() if v in ('FIN', 'NAV')}

# Taxa de crescimento por ticker, de data/tir.data.js. Registro a registro, não por regex solto
# sobre o arquivo inteiro: `gCagr:` é null em metade dos tickers, e um `.*?` preguiçoso pula o
# null e pega o gCagr do PRÓXIMO ticker — 10 empresas saíram com a taxa da vizinha antes de eu
# perceber.
_REG = {m.group(1): m.group(2) for m in re.finditer(r'(\w+):\s*\{([^}]*)\}', tir)}

def _tircampo(t, c):
    b = _REG.get(t)
    if not b: return None
    m = re.search(r'\b%s:\s*(-?[\d.]+|null)' % c, b)
    return None if (not m or m.group(1) == 'null') else float(m.group(1))

# Crescimento, taxa declarada e cap vivem em scripts/motor_teto.py — UMA definição, carregada
# aqui pelo mesmo exec() que traz o resto do motor. Durante algumas horas em 13/09/2026 houve
# uma cópia de cada coisa nos dois arquivos, e elas já divergiam: a TIMS3 saía com 15,6% na
# tabela e 3,1% no preço justo, porque só um dos lados conhecia o CAGR do lucro recorrente.
CRESCIMENTO_DECLARADO = M['CRESCIMENTO_DECLARADO']
CRESC_CAP = M['CRESC_CAP']


def crescimento(t):
    """(taxa %, (origem, valor bruto)) — casca sobre M['crescimento'] no formato desta tabela."""
    A = H.get(t)
    if not A:
        return None, (None, None)
    g, fonte = M['crescimento'](t, A, H)
    if g is None:
        return None, (None, None)
    bruto = None
    if t not in CRESCIMENTO_DECLARADO:
        val, _q = M['anos_validos'](A)
        cands = [x for x in (M['_reg_log']([(y, A[y].get('lucrolin')) for y in val]),) if x is not None]
        if cands and abs(cands[0]) > CRESC_CAP:
            bruto = cands[0]
    return g, (fonte, bruto if bruto is not None else g)


def normalizado(t, A, usar_cache=True):
    """Lucro normalizado + nome do motor.

    ⚠️ `usar_cache` existe por causa de um CICLO, achado em 13/09/2026 quando o usuário
    perguntou por que o lucro normalizado da TIM (R$ 3,38 bi) estava abaixo do lucro de 2025:
    `gerar_tir.py` chamava esta função para CALCULAR o lucroNorm que ele grava em
    data/tir.data.js — e esta função começa lendo o lucroNorm de data/tir.data.js. O gerador
    lia a própria saída anterior. Uma vez escrito, o número nunca mais mudava, por mais que a
    base andasse. A TIM estava três regerações atrasada (3,38 contra 3,85 recalculado).
    Quem ESCREVE o cache passa usar_cache=False; quem só LÊ a planilha continua no padrão.

    ⚠️ MEDIANA COM TENDÊNCIA, não mediana simples. Também da pergunta da TIM: a margem líquida
    dela foi 7,8% → 11,9% → 12,4% → 16,2% → 15,8%. Isso não oscila, isso SOBE — e a mediana de
    6 anos (14,1%) ancorava no pior período e punia a empresa por ter melhorado. É exatamente o
    defeito que `mediana_com_tendencia` foi escrita para corrigir no ROE dos bancos (seção do
    motor), e que aqui nunca tinha sido aplicado. Com ela, a margem usada vira 15,8%.
    """
    if usar_cache and t in LN:
        return LN[t][0], LN[t][1], 'data/tir.data.js'
    val, q = M['anos_validos'](A)
    c = A[max(A)]
    if t in FIN:
        # ⚠️ O PATRIMÔNIO VEM DA CONTABILIDADE, NÃO DO PREÇO. Até 13/09/2026 esta linha fazia
        # `vpa() × papeis()`, e vpa() é preço ÷ P/VP — ou seja, o lucro NORMALIZADO, que é um
        # número de fundamento, se mexia quando a ação subia ou caía. Pior: o P/VP da base não
        # reconcilia com o par lucro/ROE da mesma base. O usuário achou pelo Itaú, cujo lucro
        # normalizado saía em R$ 40,1 bi contra R$ 45,9 bi de lucro real em 2025 — o P/VP
        # dizia patrimônio de R$ 190,9 bi e o ROE dizia R$ 228,0 bi, 16% de diferença. A
        # varredura achou o mesmo em quase todo o grupo: BMEB4 −12%, BRSR6 +11%, e a SAUD3
        # com +244%, que é a incorporação de 2026 batendo em cheio no P/VP.
        # Patrimônio = lucro ÷ ROE resolve: os dois campos são contábeis, da mesma fonte e do
        # mesmo exercício, e o preço sai da conta. Na prática a fórmula vira
        # `lucro_atual × (ROE típico ÷ ROE de hoje)` — escala o lucro pela distância entre a
        # rentabilidade normal do banco e a de agora, que é exatamente o que normalizar quer
        # dizer.
        roes = [A[y]['roe'] for y in val if A[y].get('roe') is not None]
        roe_hoje, lucro_hoje = c.get('roe'), c.get('lucrolin')
        if roes and roe_hoje and roe_hoje > 0 and lucro_hoje and lucro_hoje > 0:
            pl_contabil = lucro_hoje / (roe_hoje / 100)
            roe, _nota = M['mediana_com_tendencia'](roes, limiar_abs=2.0)
            return roe/100*pl_contabil, 'ROE mediano × patrimônio líquido', 'calculado agora'
    mg = [A[y]['lucrolin']/A[y]['receita'] for y in val
          if A[y].get('receita') and A[y].get('lucrolin')]
    if mg and c.get('receita'):
        m, _nota = M['mediana_com_tendencia'](mg)
        return m*c['receita'], 'receita × margem líquida mediana', 'calculado agora'
    return None, None, None


def br(v, casas=2):
    return f"{v:,.{casas}f}".replace(',', '§').replace('.', ',').replace('§', '.')


def dinheiro(v):
    if v is None: return None
    a = abs(v)
    if a >= 1e9:  return ('-' if v < 0 else '') + f'R$ {br(a/1e9)} bi'
    if a >= 1e6:  return ('-' if v < 0 else '') + f'R$ {br(a/1e6, 0)} mi'
    return ('-' if v < 0 else '') + f'R$ {br(a)}'


VAZIO = '<span class="muted">—</span>'

# Etiqueta que marca, NA PRÓPRIA CÉLULA, que aquele número é FFO e não lucro líquido. O
# cabeçalho da coluna é global e continua dizendo "Lucro"; sem a marca, duas linhas da tabela
# mostrariam outra grandeza sem avisar — que é o tipo de coisa que só se descobre conferindo.
TAG_FFO = ('<span style="font-size:9px;font-weight:700;color:#7c3aed;background:#f3e8ff;'
           'border-radius:3px;padding:1px 4px;margin-left:4px;vertical-align:middle;">FFO</span>')


def cel(txt, tip):
    return f'{txt}<span class="col-tip" data-tip="{tip}">ⓘ</span>'


def gerar():
    p = RAIZ / 'data/radar-rows.data.js'
    h = p.read_text()
    log = []
    for t in sorted(H):
        if f'{t}.SA"' not in h:
            continue
        A = H[t]; c = A[max(A)]
        ano = max(A)

        # ══ SHOPPING MEDE FFO, NÃO LUCRO LÍQUIDO ═══════════════════════════════════════
        # Pedido do usuário, 13/09/2026: "para shopping trocar lucro líquido por FFO em todas
        # as colunas". O motivo é contábil e não é preferência: o shopping registra o imóvel a
        # CUSTO e o deprecia como se ele se desgastasse — só que shopping bem administrado não
        # perde valor, ganha. A depreciação come de 6% a 30% do EBITDA dependendo de como cada
        # empresa contabiliza (ALOS3 deprecia 29%, MULT3 6%, porque a MULT3 usa valor justo),
        # então o lucro líquido de shopping mede política contábil junto com operação.
        # FFO = lucro + D&A devolve a despesa que não sai caixa. É o que o setor inteiro usa,
        # é o que o motor de preço justo já usava, e agora é o que a tabela mostra.
        #
        # O QUE NÃO MUDA, e é o teste de consistência da troca: o DIVIDENDO POR AÇÃO. Ele é
        # FFO/ação × payout-sobre-FFO, e payout-sobre-FFO = payout-sobre-lucro × lucro/FFO.
        # O FFO se cancela e sobra LPA × payout — o mesmo dividendo de antes. Se a conta
        # tivesse mudado o dividendo, seria sinal de erro em algum dos dois lados.
        ffo_shop = M['MOTOR'].get(t) == 'SHOP'
        metrica = 'FFO' if ffo_shop else 'Lucro líquido'

        def _val(y):
            """O fundamento do exercício `y`: FFO em shopping, lucro líquido no resto."""
            return (M['ffo_ano'](t, A, y) if ffo_shop
                    else (A.get(y) or {}).get('lucrolin'))

        ltm = _val(ano)
        ln, motor, fonte = normalizado(t, A)   # segue alimentando a TIR; não é mais coluna
        pap = M['papeis'](t, A)
        po, npo, pf = M['payout_final'](t, A, H)
        l25 = _val(2025)
        # Payout sobre FFO = payout sobre lucro × (lucro ÷ FFO). O FFO é maior que o lucro,
        # então o payout sobre FFO é MENOR — e é a leitura certa: mede quanto do caixa da
        # operação vira dividendo, não quanto do lucro contábil.
        po_lucro, lucro25 = po, (A.get(2025) or {}).get('lucrolin')
        if ffo_shop and po and lucro25 and l25:
            po = min(po * (lucro25 / l25), 1.5)
        g, (origem_g, g_bruto) = crescimento(t)
        proj = l25 * (1 + g/100) if (l25 and l25 > 0 and g is not None) else None

        # ⚠️ 13/09/2026 — O LPA PASSOU A SAIR DO LUCRO PROJETADO, não do normalizado.
        # O usuário: "o LPA você está utilizando o lucro normalizado mas não tem mais essa
        # coluna". Estava — e o problema não era só a tooltip citar uma coluna que sumiu: a
        # cadeia inteira (LPA → dividendo → DY) pendurava num número que não aparecia em lugar
        # nenhum da tela. No Itaú o LPA de R$ 4,76 vinha de R$ 46,65 bi, que não é nem o lucro
        # de 2025 (R$ 45,85 bi) nem o projetado (R$ 50,54 bi). Não havia como conferir.
        # Agora a linha fecha e cada passo é visível: 2025 → projetado 2026 → ÷ papéis = LPA
        # → × payout = dividendo → ÷ cotação = DY.
        # ⚠️ O CUSTO, declarado: o normalizado existia para tirar o CICLO da conta. A VALE3 cai
        # de LPA 3,89 para 2,67 porque a projeção extrapola a queda do minério em vez de
        # suavizá-la. Para dividendo de UM ano isso é defensável — empresa no fundo do ciclo
        # paga menos mesmo —, mas quem ler o DY da VALE3 está lendo fundo de ciclo, não média.
        lpa = (proj/pap) if (proj and pap and proj > 0) else None
        dps = (lpa*po) if (lpa and po) else None
        preco = c.get('preco')
        dy = (dps/preco*100) if (dps and preco) else None

        base = (f'Fonte: MCP Partnr (B3/CVM), exercício {ano} — série TTM com data-base '
                f'30/06/2026. Nenhum valor digitado à mão: gerado por scripts/gerar_colunas.py.')
        cells = {}

        # ── Coluna 4 · LUCRO DO EXERCÍCIO FECHADO DE 2025 ────────────────────────────────
        # Pedido do usuário em 13/09/2026, e ela responde uma pergunta que o LTM sozinho não
        # responde: o LTM atravessa dois exercícios (2S25 + 1S26), então quando ele sobe não
        # dá para saber se foi o semestre novo que veio forte ou o velho que era fraco. Com o
        # ano fechado ao lado, a comparação fica direta.
        cells[4] = cel((dinheiro(l25) + (TAG_FFO if ffo_shop else '')) if l25 else VAZIO,
            (f'FFO — EXERCÍCIO FECHADO DE 2025 — {dinheiro(l25)}&#10;&#10;'
             f'FFO = lucro líquido {dinheiro(lucro25)} + depreciação e amortização&#10;&#10;'
             'Shopping registra o imóvel a CUSTO e o deprecia como se ele se desgastasse — '
             'mas shopping bem administrado não perde valor. O FFO devolve essa despesa, que '
             'não sai caixa. É a medida que o setor usa e a que o preço justo multiplica pelo '
             'múltiplo.&#10;Fonte: MCP Partnr (B3/CVM), exercício de 2025.'
             if ffo_shop else
             'LUCRO LÍQUIDO — EXERCÍCIO FECHADO DE 2025&#10;&#10;'
             'Fonte: MCP Partnr (B3/CVM), 1º de janeiro a 31 de dezembro de 2025.&#10;&#10;'
             'A coluna ao lado é o LTM, que vai de 01/07/2025 a 30/06/2026 e portanto mistura '
             'dois exercícios. Esta aqui é o ano civil fechado, sem mistura.'))

        # ── Coluna 5 · LUCRO PROJETADO 2026 ─────────────────────────────────────────────
        origem, bruto = origem_g, g_bruto
        cortado = (g is not None and bruto is not None and abs(bruto - g) > 0.05)
        cells[5] = cel((dinheiro(proj) + (TAG_FFO if ffo_shop else '')) if proj else VAZIO,
            (f'{"FFO" if ffo_shop else "LUCRO"} PROJETADO 2026 — {dinheiro(proj)}&#10;&#10;'
             f'{"FFO" if ffo_shop else "Lucro"} 2025 {dinheiro(l25)} × '
             f'(1 {"+" if g >= 0 else "−"} {br(abs(g),1)}%)&#10;&#10;'
             f'A taxa e a origem dela estão na coluna ao lado.'
             if proj else
             'LUCRO PROJETADO 2026 — não calculável&#10;&#10;'
             + ('Sem taxa de crescimento utilizável na base.' if (l25 and l25 > 0) else
                'Lucro de 2025 ausente ou negativo — sem base positiva não há percentual com '
                'significado.')))

        # ── Coluna 6 · TAXA DE CRESCIMENTO 2025 → 2026 ──────────────────────────────────
        # Pedido do usuário. Ela já existia embutida na projeção, mas só aparecia na tooltip —
        # e é o único número que separa a coluna de 2025 da de 2026. Exposta, a linha inteira
        # fica conferível de cabeça: lucro × (1 + taxa) = projetado.
        cells[6] = cel(
            (f'<span style="color:{"#0a5c35" if g >= 0 else "#9c1c1c"};font-weight:600;">'
             f'{"+" if g >= 0 else ""}{br(g,1)}%</span>'
             + (f' <span style="color:#b45309;font-size:11px;">({"+" if bruto >= 0 else ""}'
                f'{br(bruto,1)}%)</span>' if cortado else '')) if g is not None else VAZIO,
            (f'CRESCIMENTO 25→26 — {br(g,1)}%&#10;&#10;{origem.rstrip(".")}.'
             + (f'&#10;&#10;Valor bruto {br(bruto,1)}%, limitado a ±{br(CRESC_CAP,0)}%.'
                if cortado else '')
             if g is not None else
             'SEM TAXA DE CRESCIMENTO&#10;&#10;Nem lucro recorrente nem ROE utilizável na base.'))

        cells[7] = cel((f'R$ {br(lpa)}' + (TAG_FFO if ffo_shop else '')) if lpa else VAZIO,
            (f'{"FFO" if ffo_shop else "LUCRO"} POR AÇÃO — R$ {br(lpa)}&#10;&#10;'
             f'{"FFO" if ffo_shop else "Lucro"} projetado 2026 {dinheiro(proj)} ÷ '
             f'{pap/1e6:.0f} mi papéis&#10;&#10;'
             f'Papéis negociados, units já resolvidas — mesma base do preço e do dividendo.'
             + ('&#10;&#10;É este número que o preço justo multiplica pelo P/FFO.' if ffo_shop else '')
             if lpa else f'{"FFO" if ffo_shop else "LUCRO"} POR AÇÃO — sem projeção para 2026'))

        # ── Coluna 8 · PAYOUT ───────────────────────────────────────────────────────────
        # ⚠️ ÚLTIMA COLUNA MANUAL DA TABELA, e ela estava divergindo em silêncio: o motor
        # calculava 100% para a ALOS3 e a célula mostrava 63%, colado de uma geração antiga.
        # A célula 8 nunca entrou na lista do gerador (4,5,6,7,9,10,11,12) — então o payout
        # que a tabela EXIBIA e o payout que ela USAVA para o dividendo eram números
        # diferentes na mesma linha. Quinta vez que "duas fontes de verdade" aparece nesta
        # base. Entra na lista agora.
        rot8 = {'piso': 'piso da política declarada', 'teto': 'teto da política declarada',
                'estatutario': 'realizado — a política é só o mínimo legal',
                'outra_base': 'realizado — a política não é % do lucro',
                'nao_paga': 'a empresa não paga dividendos',
                'pares': 'payout mediano dos PARES, não da empresa',
                'realizado': 'realizado da própria série'}.get(pf[0], pf[0])
        base8 = 'FFO' if ffo_shop else 'lucro'
        cells[8] = cel((f'{po*100:.0f}%' + (TAG_FFO if ffo_shop else '')) if po is not None else VAZIO,
            (f'PAYOUT {po*100:.0f}% SOBRE O {base8.upper()} — {rot8}&#10;&#10;'
             f'Σ dividendos ÷ Σ {base8} de {npo} exercício(s), pela identidade '
             f'payout = DY × P/L (o preço se cancela).'
             + (f'&#10;&#10;Sobre o lucro contábil daria {po_lucro*100:.0f}%. O FFO é maior '
                f'que o lucro, então o payout sobre ele é menor — e é a leitura certa em '
                f'shopping: mede quanto do CAIXA da operação vira dividendo, não quanto do '
                f'lucro depois da depreciação do imóvel.' if ffo_shop else '')
             + f'&#10;&#10;É este payout que gera o Div./Ação desta linha: '
               f'{"FFO/ação" if ffo_shop else "LPA"} × {po*100:.0f}%.&#10;'
               'Anos de prejuízo e anos sem DY na base saem dos dois lados. Teto de 100% '
               'sobre o lucro. Metodologia: seção 22.'
             if po is not None else 'PAYOUT — sem dado de dividendo utilizável na base.'))

        rot = {'piso': 'piso da política', 'teto': 'teto da política',
               'estatutario': 'realizado (a política é só o mínimo legal)',
               'outra_base': 'realizado (a política não é % do lucro)',
               'nao_paga': 'a empresa não paga dividendos',
               'pares': 'payout mediano dos pares — não é da empresa',
               'realizado': 'realizado da própria série'}.get(pf[0], pf[0])
        cells[9] = cel(f'R$ {br(dps)}' if dps else VAZIO,
            (f'DIVIDENDO POR AÇÃO = {"FFO/ação" if ffo_shop else "LPA"} R$ {br(lpa)} × '
             f'payout {po*100:.0f}%'
             + (f'&#10;&#10;O payout aqui é sobre o FFO ({po*100:.0f}%), não sobre o lucro '
                f'contábil ({po_lucro*100:.0f}%). O dividendo em reais é o MESMO das duas '
                f'formas — o FFO se cancela entre numerador e denominador.' if ffo_shop else '')
             if dps else 'DIVIDENDO POR AÇÃO — sem LPA ou sem payout')
            + f'&#10;&#10;Payout: {rot} (detalhe na coluna Payout).&#10;'
              'É FUNDAMENTO, não deriva do preço: até 06/09/2026 o DPS era calculado como '
              '"DY × cotação", o que fazia o dividendo por ação subir quando a AÇÃO subia. '
              'A relação foi invertida — o DPS sai do lucro, e o DY é que deriva dele.&#10;' + base)

        cells[10] = cel(f'{br(dy,2)}%' if dy else VAZIO,
            (f'DIVIDEND YIELD = Div./Ação R$ {br(dps)} ÷ cotação R$ {br(preco)}'
             if dy else 'DIVIDEND YIELD — sem dividendo por ação calculável')
            + '&#10;&#10;Recalculado a cada atualização de cotação: o dividendo é fixo (vem do '
              'lucro) e o yield é que se move com o preço, como deve ser.&#10;' + base)

        # ── Coluna 11 · DIVIDEND YIELD REALIZADO DE 2025 ────────────────────────────────
        # Pedido do usuário: "troque a DY LTM por DY 2025". A coluna antiga era digitada à mão
        # — várias linhas citavam StatusInvest como fonte e a do ITUB3 usava o DY da ITUB4,
        # "mais líquida" — e ainda era reescrita em runtime pela API do Partnr. Dois números de
        # fora da base, brigando pela mesma célula. Este sai de data/historico.data.js, igual
        # ao resto da tabela, e é fato consumado: serve para conferir o DY projetado ao lado.
        dy25 = (A.get(2025) or {}).get('dy')
        # ── Coluna 11 · DY REALIZADO DE 2025 · Coluna 12 · MEDIANA DE 10 ANOS ───────────
        d25 = dy_ano(t, 2025)
        cells[11] = cel(
            (f'<span style="{"color:#059669;font-weight:600" if d25 >= 8 else ("" if d25 >= 4 else "color:#dc2626")}">'
             f'{br(d25,2)}%</span>') if d25 else VAZIO,
            (f'DIVIDEND YIELD REALIZADO DE 2025 = {br(d25,2)}%&#10;&#10;'
             'Proventos do exercício de 2025 ÷ preço da data-base.&#10;'
             if d25 else
             'DY DE 2025 — sem dado&#10;&#10;A base devolve yield ausente ou zero para este '
             'ticker em 2025, e zero aqui significa dado faltando, não dividendo zero.&#10;')
            + '&#10;É FATO, não projeção. A coluna à esquerda é o DY projetado (lucro de 2026 × '
              'payout ÷ cotação) e a da direita é a mediana de 10 anos — as três juntas mostram '
              'se a projeção está dentro do que a empresa costuma pagar.&#10;'
              'Fonte: MCP Partnr (B3/CVM), analise/dy_historico.json.')

        med10, usados = dy_mediana(t)
        # A tooltip mostra a SÉRIE que gera a mediana — é esse o racional. A versão anterior
        # explicava por que mediana e não média, avisava sobre zeros e sobre troca de empresa:
        # 600 caracteres de metodologia numa célula. Vendo os dez anos enfileirados, o leitor
        # confere a conta sozinho e enxerga o ano fora da curva sem ninguém apontar.
        if med10:
            anos = sorted(usados)
            linhas = []
            for k in range(0, len(anos), 5):
                linhas.append(' · '.join(f'{y} {br(usados[y],1)}%' for y in anos[k:k+5]))
            faltando = [y for y in range(max(anos) - 9, max(anos) + 1) if y not in usados]
            tip = (f'DY MEDIANO DE 10 ANOS — {br(med10,2)}%&#10;&#10;'
                   + '&#10;'.join(linhas)
                   + f'&#10;&#10;Mediana de {len(anos)} exercícios'
                   + (f' · {len(faltando)} sem dado ({", ".join(str(y) for y in faltando)})'
                      if faltando else '')
                   + f' · média {br(sum(usados.values())/len(usados),2)}%')
        else:
            tip = ('DY MEDIANO DE 10 ANOS — não calculável&#10;&#10;'
                   'Menos de 3 exercícios com dado na janela de 10 anos.')
        cells[12] = cel(
            (f'<span style="{"color:#059669;font-weight:600" if med10 >= 8 else ("" if med10 >= 4 else "color:#dc2626")}">'
             f'{br(med10,2)}%</span>') if med10 else VAZIO, tip)

        i = h.index(f'{t}.SA"'); m = h.find('<tr', i); end = m if m > 0 else len(h)
        blk = h[i:end]
        for idx in sorted(cells, reverse=True):
            tds = [x for x in re.finditer(r'<td\b[^>]*>.*?</td>', blk, re.S)]
            if idx >= len(tds): continue
            td = tds[idx]
            ini = re.match(r'<td\b[^>]*>', td.group(0)).group(0)
            blk = blk[:td.start()] + ini + cells[idx] + '</td>' + blk[td.end():]
        # LPA LTM por papel — alimenta a coluna P/L (js/fundamentos.js). Antes vinha curado à
        # mão e ficava defasado; agora sai da mesma base. Negativo é mantido de propósito: a
        # coluna de P/L precisa saber que houve prejuízo para declarar isso em vez de calar.
        # Em shopping isto é o FFO POR PAPEL, e a coluna 13 vira P/FFO. `data-metrica-lucro`
        # avisa o js/fundamentos.js para rotular a célula e a tooltip corretamente — sem ele a
        # coluna diria "P/L" sobre um denominador que não é lucro.
        lpa_ltm = (ltm/pap) if (ltm and pap) else None
        tag_end = blk.find('>')
        tag = blk[:tag_end]
        if lpa_ltm is not None:
            fonte_lpa = ((f'FFO por papel (LTM) = FFO dos últimos 12 meses R$ {br(ltm/1e9)} bi '
                          f'÷ {pap/1e6:.0f} mi papéis. FFO = lucro + depreciação, porque o imóvel '
                          f'do shopping entra a custo e é depreciado como se se desgastasse.'
                          if ffo_shop else
                          f'LPA LTM = lucro dos últimos 12 meses R$ {br(ltm/1e9)} bi ÷ '
                          f'{pap/1e6:.0f} mi papéis negociados (units resolvidas).')
                         + ' Fonte: MCP Partnr (B3/CVM), TTM 2T26. Gerado por scripts/gerar_colunas.py.')
            tag = (re.sub(r'data-lpa-ltm="[^"]*"', f'data-lpa-ltm="{lpa_ltm:.4f}"', tag)
                   if 'data-lpa-ltm=' in tag
                   else tag.replace(' data-veredicto=', f' data-lpa-ltm="{lpa_ltm:.4f}" data-veredicto=', 1))
            tag = (re.sub(r'data-lpa-fonte="[^"]*"', f'data-lpa-fonte="{fonte_lpa}"', tag)
                   if 'data-lpa-fonte=' in tag
                   else tag.replace(' data-veredicto=', f' data-lpa-fonte="{fonte_lpa}" data-veredicto=', 1))
        # ── MÉTRICA DA LINHA + ROE ──────────────────────────────────────────────────────
        # ROE do shopping passa a ser FFO ÷ patrimônio líquido, a pedido do usuário ("trocar
        # lucro líquido por FFO em TODAS as colunas"), repetido depois de eu levantar a
        # ressalva. A ressalva fica registrada aqui porque ela não some por decisão: o
        # denominador (patrimônio) continua medido a custo histórico, então FFO ÷ PL é um
        # retorno sobre um capital subavaliado — lê-se ALTO por construção, e não é comparável
        # com o ROE de uma empresa que não carrega imóvel no balanço. A tooltip diz isso.
        roe_ffo = None
        if ffo_shop and ltm:
            roe_base = c.get('roe')
            lucro_ltm = c.get('lucrolin')
            if roe_base and lucro_ltm and lucro_ltm > 0:
                pl_patr = lucro_ltm / (roe_base/100)          # patrimônio implícito do ROE da base
                roe_ffo = ltm / pl_patr * 100
        # data-payout também estava congelado: 0,6334 no atributo contra 60% na célula que
        # este script acabou de gerar. Mesmo defeito da coluna 8, no atributo em vez da célula.
        for at, val in (('data-metrica-lucro', 'FFO' if ffo_shop else None),
                        ('data-roe-ffo', f'{roe_ffo:.2f}' if roe_ffo else None),
                        ('data-payout', f'{po:.4f}' if po is not None else None)):
            tag = re.sub(r'\s*%s="[^"]*"' % at, '', tag)
            if val:
                tag = tag.replace(' data-veredicto=', f' {at}="{val}" data-veredicto=', 1)
        if 'data-lpa-manual=' not in tag:
            tag = tag.replace(' data-veredicto=', ' data-lpa-manual="true" data-veredicto=', 1)

        # ⚠️ 13/09/2026 — data-dy-proj PASSA A SER GERADO AQUI. Ele estava congelado de uma
        # geração antiga e divergia da própria coluna de DY em 28 das 30 linhas, às vezes pela
        # metade: SBSP3 mostrava 5,07% com o atributo em 10,67%, BRAP4 3,78% contra 9,53%,
        # PETR4 13,91% contra 6,24%. E não é enfeite — é ele que alimenta o Retorno Total e a
        # perna de dividendos da TIR real, então a tabela decidia com um número e exibia outro.
        # js/calculos.js já refazia a conta em runtime (atualizarDivDY), mas só DEPOIS de
        # "Atualizar Cotações"; em quem abre a página e não clica, o valor velho valia.
        # Escrever na geração deixa o arquivo coerente antes de qualquer JS rodar.
        if dy is not None:
            tag = (re.sub(r'data-dy-proj="[^"]*"', f'data-dy-proj="{dy/100:.4f}"', tag)
                   if 'data-dy-proj=' in tag
                   else tag.replace(' data-veredicto=', f' data-dy-proj="{dy/100:.4f}" data-veredicto=', 1))
        blk = tag + blk[tag_end:]
        h = h[:i] + blk + h[end:]
        log.append((t, ltm, ln, lpa, po, dps, dy))
    p.write_text(h)
    return log


if __name__ == '__main__':
    log = gerar()
    print(f"{'ativo':8}{'LTM':>10}{'normaliz':>10}{'LPA':>8}{'pay':>6}{'DPS':>8}{'DY':>8}")
    for t, ltm, ln, lpa, po, dps, dy in log:
        print(f"{t:8}{(f'{ltm/1e9:.2f}' if ltm else '—'):>10}{(f'{ln/1e9:.2f}' if ln else '—'):>10}"
              f"{(f'{lpa:.2f}' if lpa else '—'):>8}{(f'{po*100:.0f}%' if po is not None else '—'):>6}"
              f"{(f'{dps:.2f}' if dps else '—'):>8}{(f'{dy:.1f}%' if dy else '—'):>8}")
    print(f"\n{len(log)} linhas regeneradas — colunas 4,5,6,7,9,10,11,12")
