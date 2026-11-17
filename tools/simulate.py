#!/usr/bin/env python3
"""Campanhas headless com seis estratégias. Nenhuma IA externa ou rede."""
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
from random import Random
import statistics
import sys

if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plutonita.game import Game
from plutonita.actions import offers, RuleError
from plutonita.events import EVENTS, eligible
from plutonita.markets import MARKETS
from plutonita.production import capacity, valuation
from plutonita.products import CLASSICS

STRATEGIES=('expansao','conservador','pesquisa','precos','caos','aleatorio')

class Agent:
    def __init__(self,strategy: str,seed: str):
        self.strategy=strategy
        self.rng=Random('agente:'+seed+':'+strategy)

    def configure(self,game):
        s=game.state;p=s.player
        for key,r in p.regions.items():
            if self.strategy=='precos':policy='economico'
            elif self.strategy=='aleatorio':policy=self.rng.choice(('economico','normal','premium'))
            else:policy='premium' if MARKETS[key]['sensitivity']<1 else 'normal'
            priority=3 if MARKETS[key]['income']>1.1 else 2
            game.configure(key,policy,priority)
        # A troca de linhas não cobra nem gera recursos; só determina a próxima venda.
        if self.strategy in ('pesquisa','caos'):
            selected=sorted(p.products,key=lambda k:(k.startswith('exp'),k in ('atomic','abraco','dentada')),reverse=True)[:3]
        elif self.strategy=='precos':
            selected=sorted(p.products,key=lambda k:k in ('lingua','abraco','baba'),reverse=True)[:3]
        else:selected=sorted(p.products,key=lambda k:k in ('dentada','abraco','baba'),reverse=True)[:3]
        game.set_active(selected)

    def choose_action(self,game):
        s=game.state;p=s.player; strategy=self.strategy
        all_offers=[o for cat in ('production','marketing','research','expansion','negotiation') for o in offers(s,cat)]
        reserve=250 if strategy in ('expansao','caos','aleatorio') else 750
        choices=[o for o in all_offers if o.available and (o.cost==0 or o.cost<=p.cash-reserve)]
        if not choices:return None
        last=s.reports[-1]['companies']['player'] if s.reports else {}
        utilization=last.get('sold',400)/max(1,capacity(p,s.balance))
        def score(o):
            kind=o.kind
            points={
                'expand':7 if utilization<.8 else 3,
                'upgrade':8 if utilization>.85 else 1,
                'factory':7 if utilization>.88 else .3,
                'efficiency':4.5-p.efficiency*.35,
                'repair':11 if p.damage>300 else 3,
                'sell_factory':-10,'marketing':3 if utilization<.8 else -1,
                'research':5 if len(p.products)<3 else .5,
                'technology':4 if p.innovation<2 else 1,
                'anomaly':-2,'stabilize':1 if p.reputation<85 else -5,
                'deal':2 if utilization<.8 else -2,'spy':2 if p.innovation<4 else -5,
                'sabotage':-.5,'smear':-2,'acquire':6,'merge':1,
                'loan':12 if p.cash<900 else -5,'repay':7 if p.cash>7000 else -3,
                'retire':-20
            }.get(kind,0)
            if strategy=='expansao':
                points+= {'expand':4,'acquire':4,'merge':2,'upgrade':1,'factory':1}.get(kind,0)
            elif strategy=='conservador':
                points+= {'efficiency':2,'stabilize':4,'research':1,'merge':-6,'acquire':-3,'spy':-4,'sabotage':-4}.get(kind,0)
                if kind=='expand' and len(p.regions)>=5:points-=5
            elif strategy=='pesquisa':
                points+= {'research':6 if len(p.products)<7 else 0,'technology':4,'expand':-1,'acquire':-3}.get(kind,0)
            elif strategy=='precos':
                points+= {'upgrade':2,'factory':2,'efficiency':3,'marketing':1,'acquire':2}.get(kind,0)
            elif strategy=='caos':
                points+= {'anomaly':12 if p.chaos<85 or not s.flags.get('founder_notes') else -5,'technology':6 if p.innovation<3 else 0,'research':3,'stabilize':-8,'expand':-1}.get(kind,0)
            if kind=='research' and o.target=='abraco':points+=1
            if kind=='research' and o.target=='abobora' and s.month in (7,8,9,10,19,20,21,22):points+=1.5
            if kind=='marketing':
                market,style=o.target.split(':')
                points+=1 if p.regions[market].marketing<20 else -3
                if style=='agressiva' and strategy=='conservador':points-=8
                if style=='absurda' and strategy=='caos':points+=3
            if kind=='expand':points+=MARKETS[o.target]['demand']/5000
            return points+self.rng.uniform(-1.1,1.1)
        if strategy=='aleatorio':
            if self.rng.random()<.12:return None
            chosen=self.rng.choice(choices)
        else:chosen=max(choices,key=score)
        if strategy in ('pesquisa','caos') and p.innovation>=1 and p.cash>2500 and len(s.experimental)<(3 if strategy=='pesquisa' else 2):
            if strategy=='caos' and p.innovation>=3 and not s.flags.get('recipe_definitivo'):
                return ('experiment','',(3,3,3,3))
            if strategy=='pesquisa' and s.month%4==0:
                return ('experiment','',[(1,1,1,2),(0,2,1,3),(0,0,0,0)][len(s.experimental)%3])
        return chosen.kind,chosen.target,None

    def event_choice(self,game):
        s=game.state;event=EVENTS[s.pending_event];p=s.player
        affordable=[(i,o) for i,o in enumerate(event['options']) if o['cost']==0 or o['cost']<=p.cash]
        if self.strategy=='aleatorio':return self.rng.choice(affordable)[0]
        def score(item):
            i,o=item;e=o['effects']
            points=-o['cost']/500+e.get('cash',0)/500+e.get('capacity',0)/400+e.get('efficiency',0)*3+e.get('innovation',0)*2
            points+=e.get('reputation',0)*(0.7 if self.strategy=='conservador' else .2)
            points+=e.get('chaos',0)*(.8 if self.strategy=='caos' else -.08)
            points+=len(e.get('schedule',[]))*2
            if e.get('unlock_market') not in (None,*p.regions):points+=4
            if 'definitive' in e.get('flags',{}):points+=50
            if e.get('ending')=='republic':points+=25 if self.strategy=='caos' else 1
            if 'biosphere' in e.get('flags',{}):points+=30 if self.strategy=='caos' else -10
            if self.strategy=='caos' and event['id'] in ('estagiario','sapatos','sindicato','pernas','gravida','lua','lua_alfandega','lua_contrato') and i==0:points+=12
            if self.strategy=='conservador' and e.get('aggression',0)>0:points-=10
            return points+self.rng.uniform(-.5,.5)
        return max(affordable,key=score)[0]


def run_campaign(seed: str,strategy: str,balance=None) -> dict:
    game=Game(seed,balance);agent=Agent(strategy,str(seed))
    seen_eligible=set();steps=0
    while game.state.phase!='finished':
        steps+=1
        if steps>100:raise RuntimeError('Campanha não terminou em 100 ciclos.')
        if game.state.phase=='event':
            game.decide(agent.event_choice(game));continue
        agent.configure(game)
        for _ in range(2):
            choice=agent.choose_action(game)
            if choice:
                try:game.act(choice[0],choice[1],choice[2])
                except RuleError as exc:raise RuntimeError(f'Agente escolheu ação inválida: {choice}: {exc}') from exc
            if game.state.phase=='finished':break
        if game.state.month%3==0:
            seen_eligible.update(e['id'] for e in EVENTS.values() if eligible(e,game.state))
        if game.state.phase=='planning':game.close_month()
    s=game.state
    validate_campaign(s)
    return {'strategy':strategy,'seed':str(seed),'ending':s.ending,'months':len(s.reports),'profit':round(s.stats['profit']/max(1,len(s.reports)),2),'share':s.player.last_share,'value':valuation(s.player,s),'cash':s.player.cash,'revenue':round(s.stats['revenue'],2),'events':s.seen,'eligible_events':sorted(seen_eligible),'products':s.player.products,'active':s.player.active,'chaos':s.player.chaos,'reputation':s.player.reputation}


def validate_campaign(state):
    """Invariantes econômicos auditados em cada campanha da bateria."""
    from plutonita.validation import validate_state
    validate_state(state)
    for report in state.reports:
        total=sum(report['market_sizes'].values())
        for result in report['companies'].values():
            assert 0<=result['sold']<=result['capacity'], 'Vendas excedem capacidade'
            assert abs(result['cash_after']-(result['cash_before']+result['profit']))<.011, 'Caixa não fecha'
            assert abs(result['profit']-(result['revenue']-result['expenses']))<.011, 'Lucro não fecha'
            assert abs(result['share']-result['sold']/total)<1e-10, 'Participação global incorreta'
            assert result['sold']==sum(r['units'] for r in result['regions'].values()), 'Alocação inconsistente'
            for key,row in result['regions'].items():
                assert abs(row['revenue']-row['units']*row['price'])<.011, 'Receita regional não fecha'
        for key,size in report['market_sizes'].items():
            sold=sum(r['regions'].get(key,{}).get('units',0) for r in report['companies'].values())
            assert 0<=sold<=size, 'Demanda regional excedida'


def summarize(results):
    strategies={}
    for strategy in sorted(set(r['strategy'] for r in results)):
        rows=[r for r in results if r['strategy']==strategy]
        strategies[strategy]={'campaigns':len(rows),'bankruptcy_rate':sum(r['ending']=='bankrupt' for r in rows)/len(rows),'mean_monthly_profit':round(statistics.mean(r['profit'] for r in rows),2),'mean_global_share':round(statistics.mean(r['share'] for r in rows),4),'mean_final_value':round(statistics.mean(r['value'] for r in rows),2),'endings':dict(Counter(r['ending'] for r in rows))}
    events=Counter(e for r in results for e in r['events'])
    accessible=set(e for r in results for e in r['eligible_events'])|set(events)
    flavors={key:{'researched':sum(key in r['products'] for r in results),'active_final':sum(key in r['active'] for r in results),'mean_profit_when_active':round(statistics.mean([r['profit'] for r in results if key in r['active']]) if any(key in r['active'] for r in results) else 0,2)} for key in CLASSICS}
    return {'campaigns':len(results),'strategies':strategies,'endings':dict(Counter(r['ending'] for r in results)),'events_seen':dict(events),'events_not_seen':sorted(set(EVENTS)-set(events)),'events_never_eligible':sorted(set(EVENTS)-accessible),'flavors':flavors,'note':'Correlação de agentes fixos não mede causalidade nem diversão. Tempo de partida exige teste humano.'}


def main():
    parser=argparse.ArgumentParser(description='Simulação de balanceamento sem interface.')
    parser.add_argument('--campaigns',type=int,default=600)
    parser.add_argument('--seed-start',type=int,default=1000)
    parser.add_argument('--strategy',choices=STRATEGIES)
    parser.add_argument('--output',type=Path,default=Path('simulation_report.json'))
    parser.add_argument('--balance',help='JSON de balanceamento alternativo')
    args=parser.parse_args()
    if args.campaigns<1:parser.error('--campaigns precisa ser positivo')
    from plutonita.balance import load_balance
    balance=load_balance(args.balance)
    results=[]
    for i in range(args.campaigns):
        strategy=args.strategy or STRATEGIES[i%len(STRATEGIES)]
        results.append(run_campaign(str(args.seed_start+i),strategy,balance))
        if (i+1)%100==0:print(f'{i+1}/{args.campaigns} campanhas concluídas',flush=True)
    summary=summarize(results)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps({'summary':summary,'campaigns':results},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
