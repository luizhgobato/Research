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
CEL_MULT_VAZIA = '<td class="sep"><span class="muted">—</span></td>'


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
    saida, mudou, sem = [], [], []
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
            cel_mult = (f'<td class="sep"><span style="font-weight:600;">{_val}</span>'
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
        # ⚠️ A MIGRAÇÃO É DETECTADA PELA CONTAGEM DE CÉLULAS, não por procurar a tooltip no
        # texto. A primeira versão procurava 'APLICADO' no bloco e, numa linha que já tinha a
        # célula do múltiplo vazia (um ticker recém-incluído), inseria em vez de substituir — o BBDC3
        # ficou com 23 células e a linha inteira deslocada em relação ao cabeçalho. Contar é
        # a única verificação que não depende do conteúdo ter sido escrito antes.
        # ⚠️ OS ÍNDICES MUDARAM EM 14/09/2026 com a entrada da coluna ROE médio (16):
        # Múltiplo 17→18, Preço Justo 18→19, e a linha completa passou de 23 para 24 células.
        # A conferência continua sendo a contagem — é a que pegou o deslocamento duas vezes.
        tds = [x for x in re.finditer(r'<td\b[^>]*>.*?</td>', bloco, re.S)]
        if len(tds) == 25:
            # REPARO. A primeira versão desta migração detectava "já migrado" procurando a
            # tooltip do múltiplo no texto da linha. Nas 6 linhas SEM preço justo não há
            # tooltip nenhuma, então a detecção dizia "ainda não migrou" toda vez e a segunda
            # execução inseriu a célula de novo: VIVA3, ASAI3, ROXO34, PASS3, SAUD3 e AXIA3
            # foram publicadas com 23 células e a linha inteira deslocada em relação ao
            # cabeçalho — cotação aparecendo na coluna da margem, e assim por diante.
            # Remove a duplicata e segue. O gerador conserta o arquivo em vez de exigir que
            # alguém edite HTML à mão.
            bloco = bloco[:tds[18].start()] + bloco[tds[18].end():]
            tds = [x for x in re.finditer(r'<td\b[^>]*>.*?</td>', bloco, re.S)]
        if len(tds) == 24:
            bloco = bloco[:tds[18].start()] + cel_mult + bloco[tds[18].end():]
        else:
            raise SystemExit(f'{t}: {len(tds)} células — esperado 24')

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
            tds2 = [x for x in re.finditer(r'<td\b[^>]*>.*?</td>', novo, re.S)]
            if len(tds2) > 19:
                novo = novo[:tds2[19].start()] + cel + novo[tds2[19].end():]
            else:
                raise SystemExit(f'{t}: linha com {len(tds2)} células, esperado 24')

        # O ATRIBUTO — a fonte que o JS lê. Tem que sair junto ou volta a divergir da célula.
        # Escrito DEPOIS do data-ticker, para o corte acima continuar funcionando na próxima
        # execução independentemente de quantas vezes este script já rodou.
        novo = re.sub(r'\s*data-preco-justo="[^"]*"', '', novo, count=1)
        if attr:
            novo = re.sub(r'(<tr [^>]*data-ticker="[A-Z0-9]+\.SA")',
                          lambda m: m.group(1) + ' ' + attr, novo, count=1)
        saida.append(novo)
        mudou.append(t)

    ROWS.write_text(''.join(saida), encoding='utf-8', newline='')
    print(f'{len(mudou)} linhas atualizadas em data/radar-rows.data.js')
    if sem:
        print('sem preço justo: ' + ', '.join(sem))


if __name__ == '__main__':
    main()
