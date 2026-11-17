import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from plutonita.game import Game
from plutonita.events import EVENTS
from plutonita.persistence import SaveError, empty_profile, load_profile, atomic_json
from plutonita.achievements import update_profile

class PersistenceTests(unittest.TestCase):
    def test_pending_event_roundtrip_and_rng(self):
        g=Game('salvo')
        for _ in range(3):g.close_month()
        self.assertEqual(g.state.phase,'event')
        with TemporaryDirectory() as d:
            path=Path(d)/'save.json';g.save(path);h=Game.load(path)
            self.assertEqual(g.state.to_dict(),h.state.to_dict())
            choice=next(i for i,o in enumerate(EVENTS[g.state.pending_event]['options']) if o['cost']==0)
            g.decide(choice);h.decide(choice)
            self.assertEqual(g.state.to_dict(),h.state.to_dict());self.assertEqual(g.rng.getstate(),h.rng.getstate())
            h.save(path);self.assertEqual(list(Path(d).glob('*.tmp')),[])
    def test_truncated_and_unknown_save_versions(self):
        with TemporaryDirectory() as d:
            path=Path(d)/'save.json';path.write_text('{')
            with self.assertRaises(SaveError):Game.load(path)
            path.write_text('{"version":999}')
            with self.assertRaises(SaveError):Game.load(path)
    def test_profile_completion_is_idempotent(self):
        g=Game();s=g.state;s.phase='finished';s.ending='survivor';s.stats['revenue']=5000
        profile=empty_profile()
        update_profile(profile,s);update_profile(profile,s)
        self.assertEqual(len(profile['campaigns']),1);self.assertEqual(profile['totals']['revenue'],5000)
        with TemporaryDirectory() as d:
            path=Path(d)/'profile.json';atomic_json(path,profile)
            self.assertEqual(load_profile(path),profile)
    def test_balance_is_saved_with_campaign(self):
        g=Game();g.state.balance['base_price']=7.1
        with TemporaryDirectory() as d:
            path=Path(d)/'save.json';g.save(path)
            self.assertEqual(Game.load(path).state.balance['base_price'],7.1)
    def test_rejects_impossible_state_without_overwriting_file(self):
        g=Game()
        with TemporaryDirectory() as d:
            path=Path(d)/'save.json';g.save(path)
            data=json.loads(path.read_text());data['state']['companies'][0]['active']=['produto_inexistente']
            path.write_text(json.dumps(data));original=path.read_text()
            with self.assertRaises(SaveError):Game.load(path)
            self.assertEqual(path.read_text(),original)
    def test_every_transition_survives_reload(self):
        from tools.simulate import Agent
        g=Game('retomar-cada-decisao');agent=Agent('caos','retomar-cada-decisao')
        with TemporaryDirectory() as d:
            path=Path(d)/'save.json'
            for _ in range(80):
                g.save(path);clone=Game.load(path)
                self.assertEqual(g.state.to_dict(),clone.state.to_dict());self.assertEqual(g.rng.getstate(),clone.rng.getstate())
                g=clone
                if g.state.phase=='finished':break
                if g.state.phase=='event':g.decide(agent.event_choice(g))
                else:
                    agent.configure(g)
                    for _ in range(2):
                        choice=agent.choose_action(g)
                        if choice:g.act(*choice)
                        g.save(path);g=Game.load(path)
                    g.close_month()
            self.assertEqual(g.state.phase,'finished')
