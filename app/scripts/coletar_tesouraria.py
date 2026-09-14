#!/usr/bin/env python3
"""Extrai a linha 'Ações em Tesouraria' do BPP e alimenta analise/tesouraria.json.

POR QUE EXISTE — 14/09/2026, pergunta do usuário: "para o LPA você está considerando retirar
as ações que estão na tesouraria?". Não estava. Ação em tesouraria não recebe dividendo, não
vota e não tem direito ao lucro — dividir o lucro por ela subestima o LPA de todo mundo.

⚠️ O BPP TRAZ O VALOR EM REAIS, NÃO A QUANTIDADE. A quantidade só aparece no Formulário de
Referência e nas notas do ITR, fora da estrutura normalizada da Partnr. Por isso o motor
aceita duas origens (ver `tesouraria()` em motor_teto.py):

  · `quantidade` declarada — quando há fonte confiável. Em empresa SEM acionista controlador,
    `1 − free_float` é essencialmente a tesouraria;
  · ESTIMATIVA pelo preço — valor ÷ cotação. Premissa: a recompra correu perto do preço de
    hoje, verdade para quem compra continuamente a mercado. Validada na VALE3, onde os dois
    caminhos dão 3,95% e 3,96%.

USO — as respostas do Partnr às vezes passam do limite de contexto e o harness as salva em
arquivo; quando cabem, salve você mesmo. Depois:

    companies_rawReports(symbol=TICKER, report_type=BPP, aggregation=CONSOLIDATED,
                         year=2026, quarter=2, flat=True)
    python3 scripts/coletar_tesouraria.py VALE3=arq.json PETR4=arq2.json ...

O ticker é informado por fora, nunca deduzido do conteúdo — lição do coletor de P/L (seção 33).
"""
import json, sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
DEST = RAIZ / 'analise/tesouraria.json'
# A linha aparece em DOIS lugares do plano de contas da CVM, conforme a empresa classifique:
# sob Reservas de Capital ou sob Reservas de Lucros. A BPAC11 usa a segunda, a VALE3 a
# primeira. Somar as duas é o certo — nunca ficam preenchidas ao mesmo tempo com sinais
# diferentes, e ler só uma foi o que quase deixou a BPAC11 passar como zero.
SUFIXOS = ('| Reservas de Capital | Ações em Tesouraria',
           '| Reservas de Lucros | Ações em Tesouraria')


def extrai(arq):
    d = json.load(open(arq, encoding='utf-8'))
    if isinstance(d, dict) and d and all(isinstance(v, dict) for v in d.values()):
        d = list(d.values())[0]          # {"2026Q2": {...}} → {...}
    total = 0.0
    achou = False
    for k, v in d.items():
        if any(k.endswith(sfx) for sfx in SUFIXOS) and v is not None:
            total += abs(float(v)); achou = True
    return (total if achou else None)


def main(args):
    try:
        base = json.loads(DEST.read_text(encoding='utf-8'))
    except Exception:
        base = {'fonte': 'MCP Partnr — companies_rawReports BPP CONSOLIDATED',
                'nota': "valor_brl = linha 'Ações em Tesouraria' do BPP, ao CUSTO.",
                'tickers': {}}
    for a in args:
        if '=' not in a:
            raise SystemExit(f'esperado TICKER=arquivo, veio {a!r}')
        t, arq = a.split('=', 1)
        v = extrai(arq)
        if v is None:
            print(f'{t}: linha de tesouraria ausente no arquivo — pulado')
            continue
        ent = base['tickers'].setdefault(t, {})
        ent['valor_brl'] = v
        ent.setdefault('quantidade', None)
        ent.setdefault('metodo', 'zero' if v == 0 else 'estimado_por_preco')
        ent['data'] = ent.get('data') or '2026-06-30'
        print(f'{t}: R$ {v/1e6:,.1f} mi'.replace(',', '.'))
    base['coletado_em'] = date.today().isoformat()
    DEST.write_text(json.dumps(base, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'\n{len(base["tickers"])} tickers → {DEST.relative_to(RAIZ)}')


if __name__ == '__main__':
    main(sys.argv[1:])
