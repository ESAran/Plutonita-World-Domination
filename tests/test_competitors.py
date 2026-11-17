import unittest
from plutonita.game import Game
from plutonita.competitors import take_turns
from plutonita.production import capacity

class CompetitorTests(unittest.TestCase):
    def test_cannot_spend_money_they_do_not_have(self):
        g=Game();s=g.state
        for r in s.companies[1:]:r.cash=0
        before=[(r.cash,capacity(r,s.balance),r.innovation,len(r.regions)) for r in s.companies[1:]]
        take_turns(s,g.rng)
        self.assertEqual(before,[(r.cash,capacity(r,s.balance),r.innovation,len(r.regions)) for r in s.companies[1:]])
    def test_paid_actions_reduce_cash(self):
        g=Game();s=g.state
        for r in s.companies[1:]:r.cash=15000
        take_turns(s,g.rng)
        self.assertTrue(all(0<=r.cash<15000 for r in s.companies[1:]))
    def test_insolvency_removes_rival(self):
        g=Game();g.state.companies[1].cash=-4000
        take_turns(g.state,g.rng)
        self.assertTrue(g.state.companies[1].eliminated)
    def test_rival_reacts_to_attack(self):
        g=Game();s=g.state;s.month=14;s.flags['attacked_goma']=14
        s.companies[1].cash=10000
        messages=take_turns(s,g.rng)
        self.assertTrue(any('defensiva' in m and 'GomaMax' in m for m in messages))
    def test_rival_laboratory_does_not_grant_free_products(self):
        class FixedRandom:
            def random(self):return .5
            def uniform(self,a,b):return 0
        g=Game();s=g.state
        for c in s.companies[1:]:c.eliminated=True
        rival=s.companies[3];rival.eliminated=False;rival.innovation=0
        rival.cash=1600;rival.products=['lingua'];rival.active=['lingua']
        take_turns(s,FixedRandom())
        self.assertEqual(rival.innovation,1)
        self.assertEqual(rival.products,['lingua'])
        self.assertEqual(rival.cash,600)
        for step in (1,2):
            rival.cash=1600
            take_turns(s,FixedRandom())
            self.assertEqual(rival.cash,1600-s.balance['research_cost'])
            self.assertEqual('atomic' in rival.products,step==2)
