import unittest
from plutonita.game import Game
from plutonita.endings import select_ending, eligible_endings, ENDINGS
from plutonita.state import Region
from plutonita.markets import MARKETS

class EndingTests(unittest.TestCase):
    def test_no_unearned_special_ending(self):
        g=Game();s=g.state;s.player.chaos=100
        self.assertEqual(select_ending(s),'survivor')
        s.flags['definitive']=True
        self.assertNotIn('definitive',eligible_endings(s))
    def test_all_endings_have_valid_conditions(self):
        reached=set()
        for ending in ENDINGS:
            s=Game().state;p=s.player
            if ending=='bankrupt':p.cash=-4000
            elif ending=='definitive':s.flags.update(definitive=True,founder_notes=True,recipe_definitivo=True);p.innovation=3
            elif ending=='republic':s.flags.update(republic=True,goma_citizens=True,intern_director=True)
            elif ending=='mutation':s.flags['biosphere']=True;p.chaos=90
            elif ending=='antitrust':p.aggression=6;p.last_share=.31
            elif ending=='emperor':p.last_share=.5;p.regions={k:Region() for k in MARKETS}
            elif ending=='magnate':p.cash=1300000
            elif ending=='people':p.reputation=95;p.last_share=.18;p.regions={k:Region() for k in list(MARKETS)[:5]}
            elif ending=='federation':s.flags.update(factory_federation=True,factory_family=True)
            elif ending=='church':s.flags['gum_church']=True;p.chaos=65;p.regions={k:Region() for k in list(MARKETS)[:4]}
            self.assertEqual(select_ending(s),ending)
            reached.add(select_ending(s))
        self.assertEqual(reached,set(ENDINGS))
    def test_priority_and_antitrust_agreement(self):
        s=Game().state;s.player.aggression=8;s.player.last_share=.5;s.player.regions={k:Region() for k in MARKETS}
        self.assertEqual(select_ending(s),'antitrust')
        s.flags['antitrust_settlement']=True;self.assertEqual(select_ending(s),'emperor')
        s.player.cash=-4000;self.assertEqual(select_ending(s),'bankrupt')
