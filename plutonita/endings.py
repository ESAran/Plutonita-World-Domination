"""Prioridade determinística: insolvência, segredos, regulação, vitórias econômicas."""
from .balance import read_data
from .production import valuation
from .state import GameState
ENDINGS = {e["id"]:e for e in read_data("endings")}

def eligible_endings(state: GameState) -> list[str]:
    p=state.player; f=state.flags; result=[]
    if p.cash < -state.balance["bankruptcy_credit"]: result.append("bankrupt")
    if f.get("definitive") and f.get("founder_notes") and f.get("recipe_definitivo") and p.innovation>=3: result.append("definitive")
    if f.get("republic") and f.get("goma_citizens") and f.get("intern_director"): result.append("republic")
    if f.get("biosphere") and p.chaos>=85: result.append("mutation")
    if p.aggression>=6 and p.last_share>=.30 and not f.get("antitrust_settlement"): result.append("antitrust")
    if p.last_share>=state.balance["imperial_share"] and len(p.regions)>=6: result.append("emperor")
    if valuation(p,state)>=state.balance["magnate_value"]: result.append("magnate")
    if p.reputation>=85 and len(p.regions)>=5 and p.last_share>=.16: result.append("people")
    if f.get("factory_federation") and f.get("factory_family"): result.append("federation")
    if f.get("gum_church") and p.chaos>=60 and len(p.regions)>=4: result.append("church")
    result.append("survivor")
    return result

def select_ending(state: GameState) -> str:
    return eligible_endings(state)[0]
