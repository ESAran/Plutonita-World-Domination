"""Disputa de demanda, distribuição limitada e contabilidade anual."""
from .markets import MARKETS, PRICES, demand
from .production import capacity, maintenance
from .products import commercial_profile
from .state import GameState

def modifier(state: GameState, company_id: str, market_id: str, kind: str) -> float:
    result = 1.0
    for effect in state.effects:
        if effect.get("company","player") in (company_id,"all") and effect.get("market","all") in (market_id,"all") and effect["kind"]==kind and effect["until"]>=state.month:
            result *= effect["value"]
    return max(.25,min(3.0,result))

def simulate_month(state: GameState) -> dict:
    b = state.balance
    companies = [c for c in state.companies if not c.eliminated]
    sizes = {k:demand(m,state.month) for k,m in MARKETS.items()}
    prices, costs, weights, allocation = {}, {}, {}, {}
    remaining = {c.id:capacity(c,b) for c in companies}
    for c in companies:
        for key, region in c.regions.items():
            m=MARKETS[key]
            quality,cost,bonus=commercial_profile(c,state,m)
            price = b["base_price"] * m["income"] * PRICES[region.price] * (1+bonus)
            price = round(price,2)
            prices[c.id,key],costs[c.id,key]=price,cost
            marketing = region.marketing * (1.18 if "baba" in c.active else 1)
            weights[c.id,key] = max(.01,(.28+region.recognition/70) * (.5+c.reputation/100) * quality * (1+marketing/65) * (1+c.innovation*.075) * (price/(b["base_price"]*m["income"]))**(-m["sensitivity"]*1.7) * modifier(state,c.id,key,"demand"))
            allocation[c.id,key]=0
    wanted={}
    residual={}
    outside={}
    for key,size in sizes.items():
        total=b["outside_attraction"]+sum(weights.get((c.id,key),0) for c in companies)
        outside[key]=int(size*b["outside_attraction"]/total)
        residual[key]=size-outside[key]
        for c in companies:
            wanted[c.id,key]=int(size*weights.get((c.id,key),0)/total)
    # Primeiro atendimento pela prioridade definida ANTES do fechamento.
    for c in companies:
        for key in sorted(c.regions, key=lambda k:(-c.regions[k].priority,k)):
            sold=min(remaining[c.id],wanted[c.id,key])
            allocation[c.id,key]+=sold
            remaining[c.id]-=sold
            residual[key]-=sold
    # Clientes sem produto consideram outras marcas; não há vendas sem estoque.
    for _ in range(8):
        additions=0
        proposals={}
        for key,left in residual.items():
            total=sum(weights.get((c.id,key),0) for c in companies if remaining[c.id]>0)
            if total<=0 or left<=0:
                continue
            for c in companies:
                if remaining[c.id]>0 and (c.id,key) in weights:
                    proposals[c.id,key]=int(left*weights[c.id,key]/total)
        for c in companies:
            for key in sorted(c.regions,key=lambda k:(-c.regions[k].priority,k)):
                extra=min(remaining[c.id],proposals.get((c.id,key),0),residual[key])
                allocation[c.id,key]+=extra
                remaining[c.id]-=extra
                residual[key]-=extra
                additions+=extra
        if additions==0:
            break
    report={"month":state.month,"market_sizes":sizes,"outside":outside,"companies":{}}
    for c in companies:
        cash_before=c.cash
        rows={}
        variable=0.0
        revenue=0.0
        sold=0
        for key,region in c.regions.items():
            units=allocation[c.id,key]
            income=round(units*prices[c.id,key],2)
            expense=round(units*costs[c.id,key],2)
            revenue+=income; variable+=expense; sold+=units
            rows[key]={"units":units,"price":prices[c.id,key],"revenue":income,"variable":expense,"contribution":round(income-expense-b["commercial_cost"],2),"share":units/sizes[key],"demand":wanted[c.id,key]}
            # Conhecimento cresce com vendas; campanhas perdem 35% da força.
            region.recognition=max(8,min(100,region.recognition + 1.8*units/max(1,wanted[c.id,key]) - (0.25 if "abraco" in c.active else .8)))
            region.marketing*=.65
        fixed=round(maintenance(c,b),2)
        commercial=len(c.regions)*b["commercial_cost"]
        interest=round(c.loan*.025,2)
        royalty=round(revenue*c.royalty,2)
        profit=round(revenue-variable-fixed-commercial-interest-royalty,2)
        share=sold/sum(sizes.values())
        previous_share=c.last_share
        c.cash=round(c.cash+profit,2)
        c.last_profit,c.last_revenue,c.last_share=profit,round(revenue,2),share
        report["companies"][c.id]={"cash_before":cash_before,"cash_after":c.cash,"revenue":round(revenue,2),"variable":round(variable,2),"maintenance":fixed,"commercial":commercial,"interest":interest,"royalty":royalty,"expenses":round(variable+fixed+commercial+interest+royalty,2),"profit":profit,"capacity":capacity(c,b),"sold":sold,"share":share,"share_change":share-previous_share,"regions":rows,"unmet":max(0,sum(wanted[c.id,k] for k in c.regions)-sold)}
    player=report["companies"]["player"]
    for stat,key in (("revenue","revenue"),("profit","profit"),("units","sold")):
        state.stats[stat]+=player[key]
    state.stats["peaks"]["share"]=max(state.stats["peaks"].get("share",0),player["share"])
    state.reports.append(report)
    return report
