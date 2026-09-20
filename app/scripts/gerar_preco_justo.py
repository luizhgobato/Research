#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ══════════════════════════════════════════════════════════════════════════════════════════
# PROPAGA O PREÇO JUSTO DO MOTOR PARA A TABELA — analise/tetos.json → data/radar-rows.data.js
# ══════════════════════════════════════════════════════════════════════════════════════════
# POR QUE EXISTE — o scripts/README.md registrava, como pendência, que a coluna de preço justo
# era "colada manualmente do output do motor". Isso já cobrou o preço duas vezes neste projeto:
#
#   · 11/09/2026 — a célula visível da ALOS3 mostrava R$19,61 (motor de 06/09) enquanto o
#     atributo data-preco-teto da MESMA LINHA dizia R$21,42. Só o atributo tinha sido colado.
#   · 13/09/2026 — três splices consecutivos deslocaram índices e a escrita de uma coluna
#     sumiu em silêncio; o conteúdo antigo ficou na tela sem nada quebrar.
#
# É sempre a mesma falha: duas fontes de verdade para o mesmo número, e a errada é a que o
# usuário lê. Este script elimina a cópia manual — o motor escreve, a tabela recebe.
#
# ⚠️ A TOOLTIP É SÓ O RACIONAL. Pedido explícito do usuário, duas vezes: "no preço justo o
# tooltip deve ter o racional pra chegar no valor, somente isso — e o racional é quanto a
# empresa deveria valer baseada em algum critério, e esse critério deve estar lá". Então ela
# tem quatro linhas e nada mais: o critério, a conta, de onde veio o múltiplo, e a faixa.
# A metodologia inteira mora em METODOLOGIA_ANALISE.md, não na tooltip.
import json, re, unicodedata
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
TETOS = RAIZ / 'analise' / 'tetos.json'
ROWS = RAIZ / 'data' / 'radar-rows.data.js'

def brl(v):
    return f'R$ {v:,.2f}'.replace(',', '§').replace('.', ',').replace('§', '.')


def esc(t):
    """Escapa para dentro de um atributo HTML. &#10; é a quebra de linha da tooltip."""
    return (t.replace('&', '&amp;').replace('"', '&quot;')
             .replace('<', '&lt;').replace('>', '&gt;').replace('\n', '&#10;'))


def ptbr(txt):
    """Vírgula decimal dentro da conta. As f-strings do motor saem em formato americano
    (8.13x, R$ 3.88) e a tabela inteira ao redor usa vírgula — misturar as duas na mesma
    tooltip faz o leitor conferir a conta duas vezes."""
    return re.sub(r'(\d)\.(\d)', r'\1,\2', txt)


def conta_limpa(motor):
    """A linha `motor` do método, sem o prefixo redundante do nome do método.

    O motor devolve coisas como "E/P: P/L 8,13x × LPA projetado R$ 2,20" — o "E/P:" já está
    no cabeçalho da tooltip, repetir polui a única linha que interessa.
    """
    m = re.sub(r'^(E/P|P/FFO|P/VP|EV/EBITDA|EV/Receita|Paridade|Pares)\s*[:·]?\s*', '', motor)
    return m.strip()


MULT_ROTULO = {'E/P': 'P/L', 'P/L': 'P/L', 'P/FFO': 'P/FFO', 'EV/EBITDA': 'EV/EBITDA',
                'EV/Receita': 'EV/Receita', 'P/VP': 'P/VP', 'Paridade': 'paridade',
                'Pares': 'múltiplo dos pares'}


def extrair_multiplo(met):
    """(rótulo, valor formatado) do múltiplo aplicado, lido da string `conta` do método.

    A conta sai do motor já formatada — "LPA projetado 2026 R$ 5,16 × P/L 9,39x" — e o
    múltiplo é o número seguido de 'x' (ou de três casas, no caso da paridade de holding).
    Extrair daqui em vez de criar mais um campo evita que a coluna e a tooltip do preço justo
    discordem: as duas leem a MESMA string.
    """
    conta = met.get('conta') or ''
    chave = met.get('chave') or ''
    m = re.search(r'×\s*(?:[A-Za-z/]+\s+)?([\d.,]+)x', conta)
    if m:
        return MULT_ROTULO.get(chave, chave), ptbr(m.group(1)) + 'x'
    m = re.search(r'×\s*paridade\s*([\d.,]+)', conta)
    if m:
        return 'paridade', ptbr(m.group(1))
    return MULT_ROTULO.get(chave, chave), None


def tooltip_multiplo(t, r):
    met = (r.get('metodos') or [{}])[0]
    rot, val = extrair_multiplo(met)
    if not val:
        return 'SEM MÚLTIPLO — esta linha não tem preço justo calculado.'
    return '\n'.join([
        f'{rot.upper()} APLICADO — {val}',
        '',
        f'{ptbr(met.get("conta") or "")} = {brl(r["justo"])}',
        '',
        f'O múltiplo é {ptbr(met.get("origemMult") or "o mediano da própria série")}.',
    ])


def tooltip(t, r):
    met = (r.get('metodos') or [{}])[0]
    chave = met.get('chave') or '—'
    justo = r['justo']
    # ⚠️ TRÊS LINHAS, e a terceira só existe porque o múltiplo é a metade da conta que o
    # leitor não consegue conferir sozinho. Não entra faixa, não entra teto de compra, não
    # entra ressalva de método: o usuário foi explícito — "não quero preço teto, quero o preço
    # justo: LPA × o múltiplo que ela deve ser negociada". Teto de compra é outra pergunta e
    # tem a coluna de Margem de Segurança ao lado para respondê-la.
    return '\n'.join([
        f'PREÇO JUSTO — {brl(justo)}',
        '',
        f'{ptbr(met.get("conta") or conta_limpa(met.get("motor") or ""))} = {brl(justo)}',
        '',
        f'O múltiplo é {ptbr(met.get("origemMult") or "o mediano da própria série")}.',
    ])


# A célula da coluna 16 quando não há múltiplo. `sep` mantém a divisória visual do grupo.
CEL_MULT_VAZIA = '<td class="sep mult-cell"><span class="muted">—</span></td>'


def main():
    tetos = json.load(open(TETOS, encoding='utf-8'))
    s = ROWS.read_text(encoding='utf-8')

    # Uma linha da tabela = de `<tr data-ticker=` até `</tr>`. Recorta e trata uma por vez,
    # porque regex global sobre o arquivo inteiro já vazou valor de um ticker para o
    # seguinte neste projeto (o bug do `gCagr` com quantificador preguiçoso, 12/09/2026).
    # ⚠️ O corte é por `<tr `, NÃO por `<tr data-ticker=`. A primeira versão cortava pelo
    # segundo e escrevia o atributo ANTES do data-ticker — então na segunda execução o corte
    # não encontrava mais as linhas que ela própria havia escrito, deixava 29 delas dentro de
    # um bloco único e dizia "3 linhas atualizadas" sem erro nenhum. Gerador que não é
    # idempotente é gerador que mente na segunda vez.
    partes = re.split(r'(?=<tr )', s)
    saida, mudou, sem, reparadas = [], [], [], []
    for bloco in partes:
        tk = re.search(r'<tr [^>]*data-ticker="([A-Z0-9]+)\.SA"', bloco)
        if not tk:
            saida.append(bloco); continue
        t = tk.group(1)
        r = tetos.get(t) or {}
        justo = r.get('justo')

        if justo and justo > 0:
            cel = (f'<td>{brl(justo)}<span class="col-tip" data-tip="{esc(tooltip(t, r))}">'
                   f'ⓘ</span></td>')
            attr = f'data-preco-justo="{justo:.2f}"'
            _rot, _val = extrair_multiplo((r.get('metodos') or [{}])[0])
            cel_mult = (f'<td class="sep mult-cell"><span style="font-weight:600;">{_val}</span>'
                        f'<span style="font-size:9px;color:#6b7280;margin-left:4px;">{_rot}</span>'
                        f'<span class="col-tip" data-tip="{esc(tooltip_multiplo(t, r))}">ⓘ</span></td>'
                        if _val else CEL_MULT_VAZIA)
        else:
            motivo = (r.get('nota') or 'sem motor aplicável').split('||')[0].strip()
            cel = (f'<td><span class="muted">—</span><span class="col-tip" '
                   f'data-tip="{esc("SEM PREÇO JUSTO" + chr(10) + chr(10) + motivo)}">ⓘ</span></td>')
            attr = None
            cel_mult = CEL_MULT_VAZIA
            sem.append(t)

        # ── COLUNA 18 · MÚLTIPLO ────────────────────────────────────────────────────
        # Pedido do usuário: "acrescente uma coluna com o múltiplo que o LPA está sendo
        # multiplicado e o tooltip com cálculo". Ela entra ANTES do preço justo, e é gerada
        # aqui de propósito: o múltiplo e o preço saem do mesmo método, na mesma passada.
        # Gerar em lugares diferentes seria repetir o defeito que esta sessão passou o dia
        # corrigindo — dois números do mesmo conceito, escritos por donos diferentes.
        # ⚠️ A CÉLULA É ENCONTRADA POR MARCADOR, NÃO POR ÍNDICE — 20/09/2026.
        #
        # As duas versões anteriores contavam células e mexiam em `tds[18]`, com o número 18
        # escrito à mão. A conferência era a CONTAGEM TOTAL (24, depois 25), e os comentários
        # que este bloco substitui narram as duas vezes em que isso deslocou a linha inteira.
        # Deslocou uma TERCEIRA, e desta vez apagando dado: quando a coluna "Cenário de Tese"
        # entrou (commit 0b9de66) a linha legítima passou a ter 25 células, o ramo de REPARO
        # — escrito para remover uma duplicata do múltiplo — leu 25 como "duplicou de novo" e
        # DELETOU UMA CÉLULA REAL. O commit 97a3655 regenerou o arquivo e as 35 linhas
        # perderam a célula `cotacao-cell`: cabeçalho com 25 colunas, linhas com 24, tudo da
        # Cotação para a direita deslocado — e `aplicarPrecoRadar` estourando em
        # `row.querySelector('.cotacao-cell').classList` para TODA linha. É esta a causa de
        # "o atualizar cotação não está funcionando".
        #
        # A lição que a contagem não aprendeu: índice fixo e total fixo são a MESMA aposta —
        # a de que o layout nunca muda. Ele mudou três vezes em uma semana. Marcador de
        # classe não tem opinião sobre quantas colunas existem.
        achou_mult = re.search(r'<td\b[^>]*class="[^"]*\bmult-cell\b[^"]*"[^>]*>.*?</td>',
                               bloco, re.S)
        if achou_mult:
            bloco = bloco[:achou_mult.start()] + cel_mult + bloco[achou_mult.end():]
        else:
            # PRIMEIRA MIGRAÇÃO desta linha (ou linha recém-incluída): ancora na célula do
            # Preço Justo, que é única e identificável pela tooltip, e insere logo ANTES.
            # Âncora real, não posição decorada.
            anc = re.search(r'<td>[^<]*<span class="col-tip" data-tip="PREÇO JUSTO[^"]*">ⓘ</span></td>'
                            r'|<td><span class="muted">—</span><span class="col-tip" '
                            r'data-tip="SEM PREÇO JUSTO[^"]*">ⓘ</span></td>', bloco, re.S)
            if not anc:
                raise SystemExit(f'{t}: sem célula de múltiplo e sem âncora de preço justo — '
                                 f'linha fora do layout, corrija à mão')
            # ⚠️ SUBSTITUIR ou INSERIR, e a diferença importa: as linhas escritas antes deste
            # commit JÁ TÊM a célula do múltiplo, só que sem o marcador. Inserir uma segunda
            # deixaria a linha com uma célula a mais — foi o que o validador pegou na
            # primeira execução (26 células contra 25 colunas). A vizinha imediata à esquerda
            # da âncora é o múltiplo se, e só se, ela não for nenhuma das outras células
            # marcadas. Vizinhança é âncora; índice não.
            antes = [x for x in re.finditer(r'<td\b[^>]*>.*?</td>', bloco[:anc.start()], re.S)]
            legado = antes[-1] if antes else None
            outras = ('cotacao-cell', 'margem-cell', 'report-cell', 'tese-cell')
            if legado and 'class="sep"' in legado.group(0) and not any(m in legado.group(0) for m in outras):
                bloco = bloco[:legado.start()] + cel_mult + bloco[legado.end():]
            else:
                bloco = bloco[:anc.start()] + cel_mult + bloco[anc.start():]

        # A CÉLULA DO PREÇO JUSTO — identificada pela tooltip, que é única na linha.
        novo, n = re.subn(
            r'<td>[^<]*<span class="col-tip" data-tip="PREÇO JUSTO[^"]*">ⓘ</span></td>'
            r'|<td><span class="muted">—</span><span class="col-tip" '
            r'data-tip="SEM PREÇO JUSTO[^"]*">ⓘ</span></td>',
            lambda m: cel, bloco, count=1)
        if n != 1:
            # LINHA NOVA, ainda sem tooltip de preço justo (é assim que um ticker recém-
            # incluído chega aqui — o BBDC3 em 13/09/2026). Cai para a posição: a célula 19 é
            # o Preço Justo no layout de 24 colunas. Levantar erro obrigaria quem inclui um
            # ativo a colar a tooltip à mão antes de rodar o gerador, que é exatamente o
            # trabalho manual que estes scripts existem para eliminar.
            # Mesma regra: ancora na célula do múltiplo, que acabou de ser escrita acima e
            # é o vizinho imediato à esquerda do Preço Justo. Sem número decorado.
            m_mult = re.search(r'<td\b[^>]*class="[^"]*\bmult-cell\b[^"]*"[^>]*>.*?</td>',
                               novo, re.S)
            if not m_mult:
                raise SystemExit(f'{t}: sem âncora para inserir o preço justo')
            novo = novo[:m_mult.end()] + cel + novo[m_mult.end():]

        # ── AUTO-REPARO: A CÉLULA DA COTAÇÃO ────────────────────────────────────────
        # Nove módulos de JS leem `.cotacao-cell` e `aplicarPrecoRadar` estoura sem ela. Se a
        # linha perdeu a célula (como perdeu em 97a3655), o gerador devolve — ancorada logo
        # DEPOIS do Preço Justo, que é a posição dela no cabeçalho. Consertar o arquivo é o
        # que estes scripts existem para fazer; exigir edição de HTML à mão é o contrário.
        if not re.search(r'class="[^"]*\bcotacao-cell\b', novo):
            m_pj = re.search(r'<td>[^<]*<span class="col-tip" data-tip="PREÇO JUSTO[^"]*">ⓘ</span></td>'
                             r'|<td><span class="muted">—</span><span class="col-tip" '
                             r'data-tip="SEM PREÇO JUSTO[^"]*">ⓘ</span></td>', novo, re.S)
            if not m_pj:
                raise SystemExit(f'{t}: sem cotacao-cell e sem âncora de preço justo')
            _cot = r.get('cot')
            _txt = brl(_cot) if _cot and _cot > 0 else '<span class="muted">—</span>'
            novo = novo[:m_pj.end()] + f'<td class="cotacao-cell">{_txt}</td>' + novo[m_pj.end():]
            reparadas.append(t)

        # O ATRIBUTO — a fonte que o JS lê. Tem que sair junto ou volta a divergir da célula.
        # Escrito DEPOIS do data-ticker, para o corte acima continuar funcionando na próxima
        # execução independentemente de quantas vezes este script já rodou.
        novo = re.sub(r'\s*data-preco-justo="[^"]*"', '', novo, count=1)
        if attr:
            novo = re.sub(r'(<tr [^>]*data-ticker="[A-Z0-9]+\.SA")',
                          lambda m: m.group(1) + ' ' + attr, novo, count=1)
        saida.append(novo)
        mudou.append(t)

    saida_txt = ''.join(saida)

    # ⚠️ CONFERÊNCIA CONTRA O CABEÇALHO DE VERDADE, não contra um número escrito aqui.
    # O erro que este script cometeu três vezes foi comparar com uma constante (23, depois
    # 24, depois 25) que envelhecia toda vez que uma coluna entrava. O `<colgroup>` do
    # index.html É o layout; conferir contra ele nunca fica desatualizado.
    idx = (ROWS.parent.parent / 'index.html').read_text(encoding='utf-8')
    tabela = re.search(r'<colgroup>.*?</colgroup>', idx, re.S)
    n_col = len(re.findall(r'<col\b', tabela.group(0))) if tabela else None
    problemas = []
    for bloco in re.split(r'(?=<tr )', saida_txt):
        tk = re.search(r'data-ticker="([A-Z0-9]+)\.SA"', bloco)
        if not tk: continue
        n_td = len(re.findall(r'<td\b', bloco))
        if n_col and n_td != n_col:
            problemas.append(f'{tk.group(1)}: {n_td} células contra {n_col} colunas')
        for marca in ('cotacao-cell', 'margem-cell', 'mult-cell'):
            if marca not in bloco:
                problemas.append(f'{tk.group(1)}: sem {marca}')
    if problemas:
        raise SystemExit('LAYOUT QUEBRADO — nada foi gravado:\n  ' + '\n  '.join(problemas[:12]))

    ROWS.write_text(saida_txt, encoding='utf-8', newline='')
    print(f'{len(mudou)} linhas atualizadas em data/radar-rows.data.js'
          + (f' · {len(reparadas)} com cotacao-cell restaurada' if reparadas else '')
          + (f' · layout conferido: {n_col} colunas' if n_col else ''))
    if sem:
        print('sem preço justo: ' + ', '.join(sem))


if __name__ == '__main__':
    main()
