"""Painel curto: situação, decisões pagas e consultas em blocos separados."""
from rich.panel import Panel
from rich import box
from .flow import proposals


def money(value: float) -> str:
    text = f'{value:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
    return 'R$ ' + text


def bar(value: float) -> str:
    count = round(max(0, min(100, value)) / 10)
    return '[' + '#' * count + '.' * (10-count) + ']'


def dashboard(console, state, choices=None, notice=''):
    p = state.player
    choices = proposals(state) if choices is None else choices
    result = f'Último ano: {money(p.last_profit)}' if state.reports else 'Primeiro ano: faça até duas escolhas.'
    console.print(Panel(
        f'Caixa: {money(p.cash)}  |  {result}\n'
        f'Mercado: {p.last_share:.1%}  |  Reputação: {p.reputation:.0f}  |  Caos: {p.chaos:.0f}/100',
        title=f'PLUTONITA — ANO {state.month:02}/24 — {state.year}', box=box.ASCII,
        border_style=state.theme))
    if notice:
        console.print(notice, style='bright_green')
    elif p.cash < 0:
        console.print('Caixa negativo: crédito e venda de unidade ficam em Outras ações.', style='yellow')
    elif state.news:
        console.print('TIMES: ' + state.news[0], style='yellow')
    if state.actions:
        console.print(f'\nESCOLHAS — {state.actions} ação(ões) restante(s); cada proposta usa 1.', style=state.theme)
        for index, proposal in enumerate(choices, 1):
            console.print(f'[{index}] {proposal.title} — {money(proposal.offer.cost)}')
            console.print('    ' + proposal.summary, style='dim')
        console.print('[4] Outras ações')
    else:
        console.print('\nESCOLHAS CONCLUÍDAS — suas duas ações já foram usadas.', style=state.theme)
        console.print('O ano está pronto para fechar. Nenhum investimento restante.')
    console.print('\nCONSULTA — não gasta ação')
    console.print('[5] Ver empresa')
    console.print('\n[0 / Enter] Avançar ano     [6] Salvar e sair')
