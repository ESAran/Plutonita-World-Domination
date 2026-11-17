"""Regressões do fluxo compacto, limpeza e escala anual."""
import io
import unittest
from tempfile import TemporaryDirectory
from pathlib import Path
from unittest.mock import patch
from rich.console import Console
from plutonita.game import Game
from plutonita.markets import MARKETS, demand
from plutonita.products import commercial_profile
from plutonita.ui.menus import Terminal
from plutonita.ui.flow import proposals
from plutonita.ui.dashboard import dashboard
from plutonita.ui import reports


class InterfaceTests(unittest.TestCase):
    @patch.dict("os.environ", {"TERM": "xterm-256color"})
    def test_clear_on_terminal_only_and_can_disable(self):
        with TemporaryDirectory() as d:
            out=io.StringIO()
            console=Console(file=out, force_terminal=True, no_color=True)
            term=Terminal(console,Path(d),Game().state.balance)
            term.screen()
            self.assertIn('\x1b[2J',out.getvalue())
            out.seek(0);out.truncate()
            term.clear_enabled=False;term.screen()
            self.assertEqual(out.getvalue(),'')
            term=Terminal(Console(file=out,force_terminal=False),Path(d),Game().state.balance)
            term.screen();self.assertEqual(out.getvalue(),'')

    def test_proposals_and_company_are_read_only(self):
        g=Game('propostas'); before=g.state.to_dict();rng=g.rng.getstate()
        choices=proposals(g.state)
        self.assertEqual(len(choices),3)
        self.assertEqual(len({(p.offer.kind,p.offer.target) for p in choices}),3)
        self.assertTrue(all(p.offer.available and p.offer.cost<=g.state.player.cash for p in choices))
        reports.company_summary(Console(file=io.StringIO()),g.state)
        self.assertEqual(before,g.state.to_dict());self.assertEqual(rng,g.rng.getstate())

    def test_spent_actions_hide_choices_and_block_input(self):
        g=Game();g.act('efficiency');g.act('research','baba')
        self.assertEqual(proposals(g.state),[])
        out=io.StringIO();console=Console(file=out,markup=False,width=80)
        dashboard(console,g.state)
        self.assertNotIn('[4]',out.getvalue());self.assertNotIn('[1]',out.getvalue())
        self.assertIn('ESCOLHAS CONCLUÍDAS',out.getvalue())
        with TemporaryDirectory() as d:
            term=Terminal(console,Path(d),g.state.balance);term.game=g
            with patch.object(console,'input',side_effect=['1','6']):term.play()
            self.assertIn('Digite um número disponível',out.getvalue())
            self.assertEqual(g.state.actions,0)

    def test_zero_actions_advance_without_extra_confirmation(self):
        with TemporaryDirectory() as d:
            g=Game();g.act('efficiency');g.act('research','baba')
            console=Console(file=io.StringIO());term=Terminal(console,Path(d),g.state.balance);term.game=g
            with patch.object(console,'input',side_effect=['','6']):term.play()
            self.assertEqual(g.state.year,1999)
            self.assertEqual(g.state.actions,2)

    def test_dashboard_fits_common_terminal(self):
        output=io.StringIO();dashboard(Console(file=output,width=80,markup=False),Game().state)
        text=output.getvalue()
        self.assertLessEqual(len(text.splitlines()),24)
        self.assertIn('1998',text);self.assertIn('Caos:',text)
        self.assertNotIn('mês',text.lower())

    def test_annual_demand_and_halloween_are_consistent(self):
        g=Game();g.state.player.active=['abobora']
        g.state.month=1;a=commercial_profile(g.state.player,g.state,MARKETS['br'])
        g.state.month=10;b=commercial_profile(g.state.player,g.state,MARKETS['br'])
        self.assertEqual(a,b)
        for turn in range(1,24):
            self.assertGreaterEqual(demand(MARKETS['br'],turn+1),demand(MARKETS['br'],turn))
        g.state.month=24;self.assertEqual(g.state.year,2021)

    def test_clear_between_advanced_screens_and_feedback_survives(self):
        with TemporaryDirectory() as d:
            g=Game(); console=Console(file=io.StringIO());term=Terminal(console,Path(d),g.state.balance);term.game=g
            with patch.object(console,'input',side_effect=['4','1','3','1','6']), patch.object(term,'screen') as screen:
                term.play()
            self.assertGreaterEqual(screen.call_count,5)
            self.assertEqual(g.state.player.efficiency,1)
            self.assertEqual(g.state.actions,1)
