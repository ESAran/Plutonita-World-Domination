import unittest
from plutonita.game import Game
from plutonita.economy import simulate_month
from plutonita.actions import execute, RuleError
from plutonita.state import Region
from plutonita.production import capacity

class EconomyTests(unittest.TestCase):
    def test_capacity_money_and_market_totals(self):
        g=Game('economia'); s=g.state
        report=simulate_month(s)
        for c in s.companies:
            r=report['companies'][c.id]
            self.assertLessEqual(r['sold'],capacity(c,s.balance))
            self.assertAlmostEqual(r['cash_after'],r['cash_before']+r['revenue']-r['expenses'],2)
            self.assertAlmostEqual(r['share'],r['sold']/sum(report['market_sizes'].values()))
        for key,size in report['market_sizes'].items():
            self.assertLessEqual(sum(r['regions'].get(key,{}).get('units',0) for r in report['companies'].values()),size)
    def test_investment_is_not_charged_twice(self):
        g=Game(); initial=g.state.player.cash
        execute(g.state,g.rng,'upgrade')
        cost=g.state.balance['upgrade_cost']
        self.assertEqual(g.state.player.cash,initial-cost)
        r=simulate_month(g.state)['companies']['player']
        self.assertAlmostEqual(g.state.player.cash,initial-cost+r['profit'],2)
    def test_invalid_actions_do_not_spend(self):
        g=Game(); before=g.state.to_dict()
        with self.assertRaises(RuleError): execute(g.state,g.rng,'expand','asia')
        self.assertEqual(before,g.state.to_dict())
    def test_distribution_respects_priority(self):
        g=Game(); p=g.state.player
        p.regions['latam']=Region(recognition=100,priority=3)
        p.regions['br'].priority=1
        p.damage=900
        r=simulate_month(g.state)['companies']['player']
        self.assertEqual(r['regions']['latam']['units'],200)
        self.assertEqual(r['regions']['br']['units'],0)
