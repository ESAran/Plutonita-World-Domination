import io
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from rich.console import Console
from plutonita.game import Game
from plutonita.actions import RuleError
from plutonita.events import EVENTS
from plutonita.ui.dashboard import dashboard
from plutonita.ui import reports
from tools.simulate import run_campaign, STRATEGIES

class GameplayTests(unittest.TestCase):
    def test_two_actions_and_free_config(self):
        g=Game();g.act('efficiency');g.act('research','baba')
        self.assertEqual(g.state.actions,0)
        with self.assertRaises(RuleError):g.act('upgrade')
        cash=g.state.player.cash;rng=g.rng.getstate()
        for _ in range(5):g.configure('br','economico',3);g.set_active(['lingua'])
        self.assertEqual(g.state.player.cash,cash);self.assertEqual(g.rng.getstate(),rng)
        g.close_month();self.assertEqual(g.state.actions,2)
    def test_full_campaign_all_strategies_reproducible(self):
        for strategy in STRATEGIES:
            a=run_campaign('4321',strategy);b=run_campaign('4321',strategy)
            self.assertEqual(a,b);self.assertLessEqual(a['months'],24)
            self.assertTrue(a['ending']);self.assertGreaterEqual(a['share'],0);self.assertLessEqual(a['share'],1)
    def test_eight_events_and_no_mutation_after_closing(self):
        g=Game('24meses')
        while g.state.phase!='finished':
            if g.state.phase=='event':
                with self.assertRaises(RuleError):g.configure('br','premium',1)
                g.decide(next(i for i,o in enumerate(EVENTS[g.state.pending_event]['options']) if o['cost']==0))
            else:g.close_month()
        self.assertEqual(g.state.month,24);self.assertEqual(g.state.stats['events'],8)
        with self.assertRaises(RuleError):g.close_month()
        with self.assertRaises(RuleError):g.act('upgrade')
    def test_bankruptcy_is_early_and_recovery_loan_works(self):
        g=Game();g.state.player.cash=-200;g.act('loan');self.assertEqual(g.state.player.cash,2800)
        g.state.player.cash=-20000;g.close_month()
        self.assertEqual(g.state.ending,'bankrupt');self.assertEqual(g.state.month,1)
    def test_experiment_requires_progress_and_is_reproducible(self):
        def create():
            g=Game('formula');g.act('technology');g.act('experiment',traits=(1,1,1,2));return g
        a=create();b=create();self.assertEqual(a.state.experimental,b.state.experimental)
        self.assertTrue(a.state.flags['recipe_terca']);self.assertEqual(a.state.actions,0)
        g=Game()
        with self.assertRaises(RuleError):g.act('experiment',traits=(3,3,3,3))
    def test_ui_narrow_and_no_color(self):
        for width in (48,80):
            output=io.StringIO();console=Console(file=output,width=width,no_color=True,force_terminal=False,markup=False)
            g=Game();dashboard(console,g.state);reports.markets(console,g.state);reports.competitors(console,g.state)
            self.assertNotIn('\x1b[',output.getvalue())
            self.assertTrue(all(len(line)<=width for line in output.getvalue().splitlines()))
    def test_terminal_handles_invalid_input_and_eof(self):
        with TemporaryDirectory() as d:
            result=subprocess.run([sys.executable,'main.py','--no-color','--seed','123','--save-dir',d],input='abc\n1\n0\n',text=True,capture_output=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertIn('Digite um número',result.stdout)
            self.assertIn('Campanha salva',result.stdout)
            self.assertEqual(Game.load(Path(d)/'campaign.json').state.month,1)
    def test_terminal_full_campaign_and_pending_resume(self):
        g=Game('terminal-completo');inputs=['1','0']
        # As mesmas decisões no motor geram um roteiro numérico para a interface.
        while g.state.phase!='finished':
            if g.state.phase=='event':
                i=next(i for i,o in enumerate(EVENTS[g.state.pending_event]['options']) if o['cost']==0)
                inputs.extend([str(i+1),'1']);g.decide(i)
            else:
                if g.state.month==1:
                    inputs.extend(['1']);g.act('efficiency')
                inputs.extend(['0','1']);g.close_month()
        inputs.extend(['', '0'])
        with TemporaryDirectory() as d:
            result=subprocess.run([sys.executable,'main.py','--no-color','--seed','terminal-completo','--save-dir',d],input='\n'.join(inputs)+'\n',text=True,capture_output=True,timeout=15)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertNotIn('Traceback',result.stdout+result.stderr)
            self.assertIn('EDIÇÃO FINAL',result.stdout)
            saved=Game.load(Path(d)/'campaign.json')
            self.assertEqual(saved.state.ending,g.state.ending)
            self.assertEqual(saved.state.player.cash,g.state.player.cash)
            self.assertEqual(saved.state.stats['events'],8)
    def test_legal_paths_to_financial_and_regulatory_failure(self):
        from tools.scenarios import industrial_overinvestment, antitrust_campaign
        self.assertEqual(industrial_overinvestment().state.ending,'bankrupt')
        self.assertEqual(antitrust_campaign().state.ending,'antitrust')
