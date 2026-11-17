"""Motor narrativo orientado a dados, sem entrada/saída de terminal."""
from random import Random
from .balance import read_data
from .state import GameState, Region
from .actions import RuleError, ledger
EVENTS = {e["id"]:e for e in read_data("events")}
NEWS = read_data("news")


def eligible(event: dict, state: GameState, scheduled: bool = False) -> bool:
    c=event["conditions"]; p=state.player
    if event["id"] in state.seen and not event.get("repeat",False): return False
    if c.get("scheduled_only") and not scheduled: return False
    if not c.get("min_month",1)<=state.month<=c.get("max_month",24): return False
    if p.chaos<c.get("min_chaos",0) or p.aggression<c.get("min_aggression",0): return False
    if any(not state.flags.get(f) for f in c.get("flags_all",[])): return False
    if any(state.flags.get(f) for f in c.get("flags_none",[])): return False
    if c.get("flavor") and c["flavor"] not in p.products: return False
    if c.get("market") and c["market"] not in p.regions: return False
    if c.get("experimental") and not state.experimental: return False
    if c.get("rival") and not any(r.id==c["rival"] and not r.eliminated for r in state.companies): return False
    return True


def apply_effects(state: GameState, effects: dict, rng: Random) -> None:
    p=state.player
    for key in ("reputation","chaos","innovation","efficiency","aggression"):
        if key in effects: setattr(p,key,getattr(p,key)+effects[key])
    if "cash" in effects: ledger(state,effects["cash"],effects.get("narrative","Consequência narrativa"))
    if "capacity" in effects:
        value=effects["capacity"]
        if value<0: p.damage-=value
        else: p.extra_capacity+=value
    p.extra_maintenance=max(0,p.extra_maintenance+effects.get("maintenance",0))
    p.damage=max(0,p.damage+effects.get("damage",0))
    p.royalty=max(0,min(.6,p.royalty+effects.get("royalty",0)))
    if effects.get("unlock_market") and effects["unlock_market"] not in p.regions:
        p.regions[effects["unlock_market"]]=Region(recognition=25)
    for flag in effects.get("remove_flags",[]): state.flags.pop(flag,None)
    state.flags.update(effects.get("flags",{}))
    for e in effects.get("effects",[]):
        item=dict(e)
        start=state.month+1 if state.phase=="event" else state.month
        item["until"]=start+item.pop("duration",1)-1
        state.effects.append(item)
    for item in effects.get("schedule",[]):
        scheduled=dict(item)
        scheduled["due"]=state.month+scheduled.pop("delay")
        state.scheduled.append(scheduled)
    if "chance" in effects:
        chance=effects["chance"]
        success=rng.random()<chance["probability"]
        outcome=chance["success"] if success else chance["failure"]
        details=[]
        for key,label in (("cash","caixa"),("reputation","reputação"),("chaos","Caos")):
            if key in outcome:details.append(f"{label} {outcome[key]:+g}")
        if outcome.get('schedule'):details.append('consequência agendada para '+', '.join(str(x['delay']) for x in outcome['schedule'])+' ano(s)')
        state.history.append({"month":state.month,"kind":"risco","text":"Desfecho do risco anunciado: "+('; '.join(details) or 'nenhum efeito adicional')+'.'})
        apply_effects(state,outcome,rng)
    if effects.get("ending"): state.flags["requested_ending"]=effects["ending"]
    if effects.get("narrative"):
        state.news.append(effects["narrative"])
        state.history.append({"month":state.month,"kind":"consequência","text":effects["narrative"]})
    p.reputation=max(0,min(100,p.reputation)); p.chaos=max(0,min(100,p.chaos))
    p.innovation=max(0,min(4,p.innovation)); p.efficiency=max(0,min(5,p.efficiency)); p.aggression=max(0,p.aggression)


def process_due(state: GameState, rng: Random) -> None:
    remaining=[]
    due=[]
    for item in state.scheduled:
        if item["due"]<=state.month and "effects" in item: due.append(item)
        else: remaining.append(item)
    state.scheduled=remaining
    for item in due:
        if all(state.flags.get(f) for f in item.get("requires",[])):
            apply_effects(state,item["effects"],rng)


def choose_event(state: GameState, rng: Random) -> str | None:
    due=[item for item in state.scheduled if "event" in item and item["due"]<=state.month]
    due.sort(key=lambda item:item["due"])
    for item in due:
        event=EVENTS[item["event"]]
        if eligible(event,state,scheduled=True):
            state.scheduled.remove(item)
            return event["id"]
        # Um capítulo incompatível não ressuscita personagens aposentados.
        state.scheduled.remove(item)
    pool=[e for e in EVENTS.values() if eligible(e,state)]
    if not pool: return None
    return rng.choices(pool,weights=[e["weight"] for e in pool],k=1)[0]["id"]


def resolve_event(state: GameState, rng: Random, choice: int) -> str:
    if state.phase!="event" or state.pending_event is None:
        raise RuleError("Não há decisão narrativa pendente.")
    event=EVENTS[state.pending_event]
    if type(choice) is not int or choice<0 or choice>=len(event["options"]):
        raise RuleError("Escolha uma das opções numeradas do evento.")
    option=event["options"][choice]
    if option["cost"]>0 and state.player.cash<option["cost"]:
        raise RuleError("Caixa insuficiente. As opções sem custo continuam disponíveis.")
    ledger(state,-option["cost"],event["title"]+": "+option["label"])
    apply_effects(state,option["effects"],rng)
    state.seen.append(event["id"])
    state.stats["events"]+=1
    summary=f"{state.year}: {event['title']} — {option['label']}"
    state.decisions.append(summary)
    state.history.append({"month":state.month,"kind":"evento","text":summary})
    state.pending_event=None
    return summary


def monthly_news(state: GameState, rng: Random) -> None:
    available=[n for n in NEWS if n["id"] not in state.news_used]
    if not available:
        state.news_used=[]; available=NEWS
    item=rng.choice(available)
    state.news_used.append(item["id"])
    text=item["text"]
    if "effect" in item:
        apply_effects(state,{"effects":[item["effect"]]},rng)
        text+=f" [Demanda comercial {(item['effect']['value']-1)*100:+.0f}% neste ano, incluindo rivais.]"
    state.news.append(text)
    state.history.append({"month":state.month,"kind":"notícia","text":text})
