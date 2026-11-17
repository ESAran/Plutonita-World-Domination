import unittest
from plutonita.game import Game
from plutonita.events import EVENTS, NEWS, eligible, choose_event, resolve_event, process_due, apply_effects
from plutonita.actions import RuleError

class EventTests(unittest.TestCase):
    def test_catalog_integrity(self):
        self.assertGreaterEqual(len(EVENTS),40);self.assertGreaterEqual(len(NEWS),50)
        self.assertEqual(len({n['id'] for n in NEWS}),len(NEWS))
        for event in EVENTS.values():
            self.assertEqual(len(event['options']),3)
            self.assertTrue(any(o['cost']==0 for o in event['options']),event['id'])
            self.assertIn('weight',event)
            for option in event['options']:
                self.assertGreaterEqual(option['cost'],0)
                self.assertIn('risk',option)
                for item in option['effects'].get('schedule',[]):
                    self.assertGreater(item['delay'],0)
                    if 'event' in item:self.assertIn(item['event'],EVENTS)
    def test_flavor_chaos_and_annual_conditions(self):
        g=Game();s=g.state
        self.assertFalse(eligible(EVENTS['chamas'],s))
        s.player.products.append('dentada');self.assertTrue(eligible(EVENTS['chamas'],s))
        self.assertFalse(eligible(EVENTS['buraco'],s))
        s.player.chaos=50;self.assertTrue(eligible(EVENTS['buraco'],s))
        s.player.products.append('abobora');s.month=9
        self.assertTrue(eligible(EVENTS['abobora_presidente'],s))
        s.month=12;self.assertTrue(eligible(EVENTS['abobora_presidente'],s))
    def test_story_cannot_resurrect_retired_intern(self):
        g=Game();s=g.state;s.month=9
        s.scheduled=[{'due':9,'event':'sapatos'}]
        s.flags['intern_departed']=True
        self.assertNotEqual(choose_event(s,g.rng),'sapatos')
        self.assertFalse(any(x.get('event')=='sapatos' for x in s.scheduled))
    def test_delayed_effect_exactly_once(self):
        g=Game();s=g.state
        apply_effects(s,{'schedule':[{'delay':2,'effects':{'cash':500,'flags':{'paid':True}}}]},g.rng)
        cash=s.player.cash;s.month=2;process_due(s,g.rng);self.assertEqual(s.player.cash,cash)
        s.month=3;process_due(s,g.rng);self.assertEqual(s.player.cash,cash+500)
        process_due(s,g.rng);self.assertEqual(s.player.cash,cash+500)
        self.assertTrue(s.flags['paid'])
    def test_intern_four_chapters(self):
        g=Game();s=g.state;s.player.cash=10000
        for month,event in ((3,'estagiario'),(9,'sapatos'),(15,'sindicato'),(21,'golpe')):
            s.month=month;s.phase='event'
            if month>3:self.assertEqual(choose_event(s,g.rng),event)
            s.pending_event=event;resolve_event(s,g.rng,0)
        self.assertTrue(s.flags['republic']);self.assertEqual(s.stats['events'],4)
    def test_invalid_choice_does_not_consume_rng_or_cash(self):
        g=Game();s=g.state;s.phase='event';s.pending_event='estagiario';before=s.to_dict();rng=g.rng.getstate()
        with self.assertRaises(RuleError):resolve_event(s,g.rng,99)
        self.assertEqual(s.to_dict(),before);self.assertEqual(g.rng.getstate(),rng)
    def test_events_remain_resolvable_with_negative_cash(self):
        for event in EVENTS.values():
            g=Game();g.state.player.cash=-100;g.state.phase='event';g.state.pending_event=event['id']
            i=next(i for i,o in enumerate(event['options']) if o['cost']==0)
            resolve_event(g.state,g.rng,i)
            self.assertIsNone(g.state.pending_event)
    def test_effects_start_after_event_and_expire(self):
        g=Game();s=g.state;s.month=3;s.phase='event'
        apply_effects(s,{'effects':[{'kind':'demand','value':1.3,'duration':3}]},g.rng)
        self.assertEqual(s.effects[-1]['until'],6)
