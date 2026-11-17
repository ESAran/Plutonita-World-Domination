"""Rivais com caixa, produção e decisões próprias; sem receitas gratuitas."""
from random import Random
from .state import GameState, Region
from .markets import MARKETS
from .production import capacity
from .products import CLASSICS


def take_turns(state: GameState, rng: Random) -> list[str]:
    messages=[]
    b=state.balance
    for rival in state.companies[1:]:
        if rival.eliminated: continue
        if rival.cash < -b["bankruptcy_credit"]:
            rival.eliminated=True
            messages.append(f"{rival.name} encerrou operações por insolvência.")
            state.stats["defeated"]+=1
            continue
        choices=[]
        previous=state.reports[-1]["companies"].get(rival.id,{}) if state.reports else {}
        utilization=previous.get("sold",0)/max(1,capacity(rival,b))
        pressure=state.player.last_share>.12
        attacked=state.flags.get(f"attacked_{rival.id}",0)>=state.month-1 and state.month>1
        # Valores de prioridade não alteram custos nem a contabilidade.
        if rival.level<b["max_level"]:
            cost=b["upgrade_cost"]*rival.level**1.25*rival.factories
            choices.append((4+utilization*6,cost,"upgrade",None))
        if rival.factories<min(4,b['max_factories']):
            cost=b["factory_cost"]*(1+.35*(rival.factories-1))
            choices.append((1+utilization*6,cost,"factory",None))
        for key,m in MARKETS.items():
            if key not in rival.regions and rival.reputation>=m["reputation"] and capacity(rival,b)>=m["capacity"]:
                affinity=3 if (rival.personality=="barata" and m["sensitivity"]>1.3) or (rival.personality=="premium" and m["income"]>1.1) or (rival.personality=="experimental" and key=="asia") else 0
                choices.append((3+affinity+state.month/8,m["entry"],"expand",key))
        if rival.innovation<4:
            choices.append((3+(3 if rival.personality=="experimental" else 0),1000*(rival.innovation+1),"research",None))
        product={"barata":"abraco","premium":"dentada","experimental":"atomic"}[rival.personality]
        project=f'{rival.id}:{product}'
        if product not in rival.products and (product!='atomic' or rival.innovation>=1):
            choices.append((6+state.research.get(project,0)*2,b['research_cost'],"flavor",product))
        if rival.efficiency<5:
            choices.append((2+(4 if rival.last_profit<300 else 0),700*(rival.efficiency+1),"efficiency",None))
        key=max(rival.regions,key=lambda k:(k in state.player.regions)*int(pressure or attacked)+MARKETS[k]["demand"]/4000+rng.random()*.4)
        choices.append((2+state.month/6+(5 if attacked else 0),b["marketing_cost"],"marketing",key))
        feasible=[item for item in choices if rival.cash-item[1]>=500]
        if feasible:
            # Uma decisão paga no início; duas na fase final somente se houver reserva.
            score,cost,kind,key=max(feasible,key=lambda x:x[0]+rng.uniform(-2,2))
            rival.cash=round(rival.cash-cost,2)
            if kind=="upgrade": rival.level+=1; text="modernizou suas fábricas"
            elif kind=="factory": rival.factories+=1; text="construiu uma unidade"
            elif kind=="efficiency": rival.efficiency+=1; text="reduziu desperdícios industriais"
            elif kind=="expand":
                rival.regions[key]=Region(recognition=25)
                text=f"entrou em {MARKETS[key]['name']}"
            elif kind=="research":
                rival.innovation+=1
                text="aprimorou seu laboratório"
            elif kind=="flavor":
                project=f'{rival.id}:{key}'
                state.research[project]=state.research.get(project,0)+1
                if state.research[project]>=CLASSICS[key]['steps']:
                    rival.products.append(key)
                    if len(rival.active)<b['line_limit']:rival.active.append(key)
                    else:rival.active[-1]=key
                    text="lançou uma nova linha de produtos"
                    if rival.personality=="experimental":rival.chaos=min(100,rival.chaos+9)
                else:text="financiou uma etapa de pesquisa de produto"
            else:
                rival.regions[key].marketing=min(180,rival.regions[key].marketing+40)
                rival.regions[key].recognition=min(100,rival.regions[key].recognition+7)
                text=f"anunciou em {MARKETS[key]['name']}"+(" em resposta à Plutonita" if attacked else "")
            messages.append(f"{rival.name} {text} (R$ {cost:.0f}).")
        else:
            messages.append(f"{rival.name} preservou caixa e suspendeu investimentos.")
        for key,region in rival.regions.items():
            policy={"barata":"economico","premium":"premium","experimental":"normal"}[rival.personality]
            if rival.last_profit<0: policy="normal"
            if attacked and key in state.player.regions and rival.cash>1000: policy="economico"
            if region.price!=policy:
                region.price=policy
                messages.append(f"{rival.name} mudou preços em {MARKETS[key]['name']}: {policy.replace('economico','econômico')}.")
            region.priority=3 if key in state.player.regions and pressure else 2
        if state.month>=13 and rival.cash>4000 and (pressure or attacked):
            rival.cash-=b["marketing_cost"]
            defensive=max(rival.regions,key=lambda k:(k in state.player.regions,MARKETS[k]['demand']))
            rival.regions[defensive].marketing=min(180,rival.regions[defensive].marketing+40)
            messages.append(f"{rival.name} financiou uma segunda campanha defensiva (R$ {b['marketing_cost']:.0f}).")
    state.rival_history.extend(f"{state.year}: {m}" for m in messages)
    state.rival_history=state.rival_history[-100:]
    return messages
