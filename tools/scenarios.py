#!/usr/bin/env python3
"""Cenários dirigidos, usando somente decisões legais, para finais raros."""
import json
from pathlib import Path
import sys
if __package__ in (None,''):
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from plutonita.game import Game
from plutonita.actions import offers
from plutonita.events import EVENTS
from tools.simulate import Agent, validate_campaign


def industrial_overinvestment(seed='1') -> Game:
    game=Game(seed);game.act('factory')
    while game.state.phase!='finished':
        s=game.state
        if s.phase=='event':
            choice=next(i for i,o in enumerate(EVENTS[s.pending_event]['options']) if o['cost']==0)
            game.decide(choice);continue
        game.configure('br','premium',2)
        while s.actions:
            choices=[o for o in offers(s,'production') if o.kind in ('factory','upgrade') and o.available and o.cost<=s.player.cash]
            if not choices:break
            choice=min(choices,key=lambda o:o.cost)
            game.act(choice.kind)
        game.close_month()
    validate_campaign(s)
    return game


def antitrust_campaign(seed='1000') -> Game:
    game=Game(seed);agent=Agent('expansao',seed)
    while game.state.phase!='finished':
        s=game.state
        if s.phase=='event':
            choice=1 if s.pending_event=='antitruste' and s.player.cash>=500 else agent.event_choice(game)
            if s.pending_event=='golpe':choice=1 if s.player.cash>=1600 else 0
            game.decide(choice);continue
        agent.configure(game)
        for _ in range(2):
            if s.month>=19 and s.player.aggression<7:
                options=[o for o in offers(s,'negotiation') if o.kind=='smear' and o.cost<=s.player.cash]
                choice=(options[0].kind,options[0].target,None) if options else agent.choose_action(game)
            else:choice=agent.choose_action(game)
            if choice:game.act(*choice)
        game.close_month()
    validate_campaign(s)
    return game


def main():
    results=[]
    for name,run in [('Excesso industrial sem expansão',industrial_overinvestment),('Concentração e guerra comercial',antitrust_campaign)]:
        g=run();s=g.state
        results.append({'cenario':name,'seed':s.seed,'final':s.ending,'mes':s.month,'caixa':s.player.cash,'participacao':s.player.last_share,'agressividade':s.player.aggression,'decisoes':s.decisions})
    assert results[0]['final']=='bankrupt'
    assert results[1]['final']=='antitrust'
    path=Path('reports/targeted_scenarios.json');path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(results,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
