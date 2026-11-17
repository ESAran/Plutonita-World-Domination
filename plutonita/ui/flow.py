"""Propostas curtas para o jogador. Consultar não altera estado nem sorteios."""
from dataclasses import dataclass
from ..actions import Offer, offers
from ..products import CLASSICS


@dataclass(frozen=True)
class Proposal:
    offer: Offer
    title: str
    summary: str


def describe(offer: Offer, state) -> Proposal:
    p = state.player
    title = offer.title
    summary = offer.detail
    if offer.kind == 'research':
        flavor = CLASSICS[offer.target]
        step = state.research.get(offer.target, 0) + 1
        title = (f"Lançar {flavor['name']}" if step == flavor['steps']
                 else f"Pesquisar {flavor['name']} ({step}/{flavor['steps']})")
        summary = flavor['special']
    elif offer.kind == 'expand':
        title = 'Entrar em ' + offer.title
        summary = f"Novo mercado; despesas +R$ {state.balance['commercial_cost']:.0f}/ano."
    elif offer.kind == 'efficiency':
        title = 'Reduzir o custo de produção'
        summary = 'Custo variável-base -6,5%. Sem nova manutenção.'
    elif offer.kind == 'upgrade':
        title = 'Aumentar a produção'
        summary = offer.detail
    elif offer.kind == 'marketing':
        summary = 'Mais procura agora; a campanha perde força a cada ano.'
    elif offer.kind == 'anomaly':
        summary = 'Investigar o desaparecimento. Caos +12; abre histórias.'
    elif offer.kind == 'technology':
        summary = 'Laboratório +1. Melhora produtos e libera experimentos.'
    elif offer.kind == 'stabilize':
        summary = 'Caos -18; reputação +4. Operação mais previsível.'
    return Proposal(offer, title, summary)


def proposals(state) -> list[Proposal]:
    if state.phase != 'planning' or state.actions == 0:
        return []
    p = state.player
    groups = {key: [o for o in offers(state, key)
                    if o.available and (o.cost == 0 or o.cost <= p.cash)]
              for key in ('production', 'research', 'expansion', 'marketing', 'negotiation')}
    result = []

    def choose(group, preferred):
        choices = groups[group]
        for kind, target in preferred:
            offer = next((o for o in choices if o.kind == kind and
                          (target is None or o.target == target)), None)
            if offer:
                result.append(describe(offer, state))
                return True
        return False

    report = state.reports[-1]['companies']['player'] if state.reports else None
    busy = report is not None and report['sold'] >= report['capacity'] * .85
    if p.cash < 900:
        choose('negotiation', [('loan', None)])
    if not result:
        industrial = [('repair', None)] if p.damage else []
        industrial += ([('upgrade', None), ('factory', None), ('efficiency', None)]
                       if busy else [('efficiency', None), ('upgrade', None)])
        choose('production', industrial)
    research = []
    if p.chaos >= 75 and state.month % 2 == 0:
        research.append(('stabilize', None))
    if state.month >= 7 and len(p.products) >= 3:
        research.append(('anomaly' if state.month % 3 == 0 else 'technology', None))
    # Projetos iniciados aparecem antes de uma nova pesquisa.
    research += [('research', key) for key, value in state.research.items()
                 if key in CLASSICS and value and key not in p.products]
    research += [('research', None), ('technology', None), ('anomaly', None)]
    choose('research', research)
    expansion = sorted(groups['expansion'], key=lambda o: o.cost)
    if expansion:
        result.append(describe(expansion[0], state))
    else:
        marketing = [o for o in groups['marketing'] if o.target.endswith(':tradicional')]
        if marketing:
            marketing.sort(key=lambda o: p.regions[o.target.split(':')[0]].marketing)
            result.append(describe(marketing[0], state))
    if len(result) < 3:
        selected = {(x.offer.kind, x.offer.target) for x in result}
        for group in ('production', 'research', 'negotiation'):
            for offer in groups[group]:
                if (offer.kind, offer.target) not in selected and offer.kind not in ('retire', 'acquire', 'merge', 'sabotage', 'smear'):
                    result.append(describe(offer, state))
                    selected.add((offer.kind, offer.target))
                    if len(result) == 3:
                        return result
    return result[:3]
