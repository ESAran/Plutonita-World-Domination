"""Ações transacionais: validar primeiro, cobrar uma vez e consumir uma ação."""
from dataclasses import dataclass
from .markets import MARKETS
from .production import capacity, valuation
from .products import CLASSICS
from .research import experiment
from .state import GameState, Region

class RuleError(ValueError):
    """Escolha indisponível; nenhum recurso foi consumido."""

@dataclass
class Offer:
    kind: str
    target: str
    title: str
    cost: float
    detail: str
    available: bool = True
    reason: str = ""


def offers(state: GameState, category: str) -> list[Offer]:
    p,b=state.player,state.balance
    result=[]
    def add(kind,target,title,cost,detail,condition=True,reason="Requisito ainda não atendido."):
        result.append(Offer(kind,target,title,round(cost,2),detail,condition,reason))
    if category=="production":
        add("upgrade","","Melhorar fábricas",b["upgrade_cost"]*p.level**1.25*p.factories, f"+{b['capacity_per_level']*p.factories} capacidade; manutenção +R$ {b['level_maintenance']*p.factories}/ano.",p.level<b["max_level"],"Nível máximo atingido.")
        add("factory","","Construir unidade",b["factory_cost"]*(1+.35*(p.factories-1)),f"Nova unidade no nível {p.level}; manutenção própria.",p.factories<b["max_factories"],"Limite de seis fábricas.")
        add("efficiency","","Eficiência industrial",700*(p.efficiency+1),"Custo variável-base -6,5%; máximo de 5 melhorias.",p.efficiency<5)
        add("repair","","Reparar instalações",max(250,p.damage*.7),f"Recupera {p.damage} de capacidade danificada.",p.damage>0,"Nenhum dano a reparar.")
        add("sell_factory","","Vender uma unidade",0,"Recebe R$ 1.800; reduz capacidade e manutenção.",p.factories>1)
    elif category=="marketing":
        for key in p.regions:
            for style,cost,boost in (("tradicional",b["marketing_cost"],40),("agressiva",b["marketing_cost"]*1.6,70),("promocao",b["marketing_cost"]*.65,28)):
                add("marketing",f"{key}:{style}",f"{MARKETS[key]['name']}: {style}",cost,f"Força +{boost}; decai 35%/ano. "+("Reputação -2; provoca reação rival." if style=="agressiva" else "Reconhecimento +7."))
            if p.chaos>=25 or state.flags.get("absurd_ads"):
                add("marketing",f"{key}:absurda",f"{MARKETS[key]['name']}: propaganda extradimensional",850,"Força +85; Caos +6. Risco de 20%: reputação -5.")
    elif category=="research":
        for key,product in CLASSICS.items():
            if key in p.products: continue
            done=state.research.get(key,0)
            add("research",key,f"{product['name']} ({done}/{product['steps']})",b["research_cost"],product["special"],key!="atomic" or p.innovation>=1,"Exige nível de pesquisa 1.")
        add("technology","","Aprimorar laboratório",1000*(p.innovation+1),"Inovação +1, atratividade +7,5%; libera receitas avançadas.",p.innovation<4)
        add("anomaly","","Investigar o fundador",750,"Caos +12; avanço no dossiê. Após 2 estudos: anotações do fundador.")
        add("stabilize","","Comitê de normalidade",450,"Caos -18; reputação +4. A ata é escrita com lápis comuns.")
    elif category=="expansion":
        for key,m in MARKETS.items():
            if key in p.regions: continue
            add("expand",key,m["name"],m["entry"],f"Demanda-base {m['demand']}; reputação {m['reputation']}; capacidade {m['capacity']}; comercial R$ {b['commercial_cost']}/ano.",p.reputation>=m["reputation"] and capacity(p,b)>=m["capacity"],"Capacidade ou reputação insuficiente.")
    elif category=="negotiation":
        for rival in state.companies[1:]:
            if rival.eliminated: continue
            add("deal",rival.id,f"Distribuição com {rival.name}",850,"Demanda +25% por 4 fechamentos; rival recebe o pagamento.")
            add("spy",rival.id,f"Espionar {rival.name}",600,"70%: inovação +1 (máx. 4). Falha: reputação -5. Rival reage.")
            add("sabotage",rival.id,f"Enviar cupins contábeis a {rival.name}",800,"65%: demanda rival -35% por 3 anos. Falha: multa R$ 400. Agressividade +1; reação rival.")
            add("smear",rival.id,f"Campanha contra {rival.name}",950,"Demanda rival -20% por 3 anos; reputação -4. Agressividade +1; rival reage.")
            for kind,factor in (("acquire",.85),("merge",.48)):
                add(kind,rival.id,f"{'Adquirir' if kind=='acquire' else 'Fundir com'} {rival.name}",max(3000,valuation(rival,state)*factor),"Transfere capacidade, mercados e manutenção; caixa do rival quita passivos da operação. "+("Royalties +12% da receita para antigos sócios." if kind=="merge" else "Sem royalties.")+" Agressividade +3.")
        add("loan","","Crédito de recuperação",0,"Recebe R$ 3.000; juros de 2,5%/ano. Uma linha por campanha.",not state.flags.get("loan_taken") and p.cash<5000,"Crédito só disponível com caixa abaixo de R$ 5.000 e sem empréstimo anterior.")
        add("repay","","Quitar empréstimo",p.loan,"Encerra juros anuais.",p.loan>0)
        add("retire","","Vender a companhia e aposentar",0,"Encerra antecipadamente com O Grande Magnata.",state.month>=18 and valuation(p,state)>=b["magnate_value"],f"Exige ano 18 e patrimônio de R$ {b['magnate_value']:,.0f}.")
    return result


def ledger(state: GameState, amount: float, reason: str) -> None:
    state.player.cash=round(state.player.cash+amount,2)
    state.history.append({"month":state.month,"kind":"caixa","text":reason,"amount":round(amount,2)})
    if amount<0:
        state.stats["investments"]-=amount


def execute(state: GameState, rng, kind: str, target: str = "", traits=None) -> str:
    p=state.player
    if state.phase!="planning" or state.actions<=0:
        raise RuleError("Você precisa de uma ação estratégica disponível na fase de planejamento.")
    if kind=="experiment":
        if not isinstance(traits,(tuple,list)) or len(traits)!=4 or any(type(v) is not int or v<0 or v>3 for v in traits):
            raise RuleError("Escolha quatro características inteiras de 0 a 3.")
        if len(state.experimental)>=8:
            raise RuleError("O laboratório comporta oito fórmulas por campanha.")
        if p.innovation<1 or (sum(traits)>9 and p.innovation<3):
            raise RuleError("Requer laboratório 1; receitas com soma acima de 9 requerem nível 3.")
        offer=Offer(kind,"","Experimento",1100+100*sum(traits),"Resultado reproduzível pela seed.")
    else:
        options=[o for category in ("production","marketing","research","expansion","negotiation") for o in offers(state,category)]
        offer=next((o for o in options if o.kind==kind and o.target==target),None)
        if offer is None: raise RuleError("Ação desconhecida ou produto já desenvolvido.")
        if not offer.available: raise RuleError(offer.reason)
    if offer.cost>0 and p.cash<offer.cost:
        raise RuleError(f"Caixa insuficiente: esta decisão custa R$ {offer.cost:.2f}.")
    ledger(state,-offer.cost,offer.title)
    state.actions-=1
    message=offer.title+" concluído."
    if kind=="upgrade": p.level+=1
    elif kind=="factory": p.factories+=1
    elif kind=="efficiency": p.efficiency+=1
    elif kind=="repair": p.damage=0
    elif kind=="sell_factory":
        p.factories-=1; ledger(state,1800,"Venda de unidade")
    elif kind=="marketing":
        key,style=target.split(":")
        region=p.regions[key]
        region.marketing=min(180,region.marketing+{"tradicional":40,"agressiva":70,"promocao":28,"absurda":85}[style])
        region.recognition=min(100,region.recognition+7)
        if style=="agressiva":
            p.reputation-=2; state.flags["provoked"]=True
        elif style=="absurda":
            p.chaos+=6
            if rng.random()<.2:
                p.reputation-=5; message+=" O anúncio processou os espectadores: reputação -5."
    elif kind=="research":
        state.research[target]=state.research.get(target,0)+1
        if state.research[target]>=CLASSICS[target]["steps"]:
            p.products.append(target)
            if len(p.active)<state.balance["line_limit"]: p.active.append(target)
            message=f"{CLASSICS[target]['name']} lançado! Ajuste as linhas ativas no laboratório."
            if target in ("baba","atomic","zumbi"): p.chaos+=6
    elif kind=="technology": p.innovation+=1
    elif kind=="anomaly":
        p.chaos+=12
        state.research["founder"]=state.research.get("founder",0)+1
        if state.research["founder"]>=2:
            state.flags["founder_notes"]=True
            message+=" Dossiê: laboratório 3 + receita 3/3/3/3 pode reconstruir o Sabor Definitivo."
    elif kind=="stabilize": p.chaos-=18; p.reputation+=4
    elif kind=="expand": p.regions[target]=Region(recognition=25)
    elif kind=="experiment":
        product=experiment(state,rng,tuple(traits))
        state.experimental[product["id"]]=product
        p.products.append(product["id"])
        if len(p.active)<state.balance["line_limit"]: p.active.append(product["id"])
        p.chaos+=traits[3]*4
        if traits[0]==traits[1] and traits[2]>=2: state.flags["absurd_ads"]=True
        message=f"Criado: {product['name']}. Atratividade {product['attraction']:.2f}; custo relativo {product['cost']:.2f}."
    elif kind=="loan":
        ledger(state,3000,"Crédito de recuperação"); p.loan+=3000; state.flags["loan_taken"]=True
    elif kind=="repay": p.loan=0
    elif kind=="retire": state.ending="magnate"; state.phase="finished"
    else:
        rival=next(c for c in state.companies if c.id==target)
        if kind=="deal":
            rival.cash+=offer.cost
            state.effects.append({"kind":"demand","value":1.25,"until":state.month+3,"company":"player"})
        elif kind in ("acquire","merge"):
            p.extra_capacity+=capacity(rival,state.balance)
            from .production import maintenance
            p.extra_maintenance+=maintenance(rival,state.balance)
            for key,region in rival.regions.items():
                if key not in p.regions: p.regions[key]=Region(recognition=region.recognition*.7)
            if kind=="merge": p.royalty+=.12
            rival.eliminated=True; p.aggression+=3; state.stats["defeated"]+=1
        elif kind=="spy":
            if rng.random()<.7:
                p.innovation=min(4,p.innovation+1); message+=" Documentos obtidos: inovação +1, limitada a 4."
            else: p.reputation-=5; message+=" O espião assinou o livro de visitas. Reputação -5."
            state.flags[f"attacked_{target}"]=state.month
        elif kind in ("sabotage","smear"):
            p.aggression+=1
            if kind=="smear" or rng.random()<.65:
                state.effects.append({"company":target,"kind":"demand","value":.8 if kind=="smear" else .65,"until":state.month+2})
            else: ledger(state,-400,"Multa: cupins sem crachá"); message+=" Os cupins denunciaram você: multa de R$ 400."
            if kind=="smear": p.reputation-=4
            state.flags[f"attacked_{target}"]=state.month
    p.reputation=max(0,min(100,p.reputation)); p.chaos=max(0,min(100,p.chaos))
    state.history.append({"month":state.month,"kind":"ação","text":message})
    return message
