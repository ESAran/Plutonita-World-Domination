"""Telas curtas; consultas separadas das decisões que consomem ações."""
import argparse
import secrets
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import box
from ..game import Game
from ..actions import offers, RuleError
from ..balance import load_balance
from ..persistence import SaveError, load_profile
from ..achievements import update_profile, ACHIEVEMENTS
from ..markets import MARKETS
from ..products import catalog
from .ascii_art import LOGO, MONSTER, RAT
from .dashboard import dashboard, money
from .flow import proposals, describe
from . import reports

TUTORIAL = '''24 anos, de 1998 a 2021. Duas escolhas por ano.

• Escolha uma das três propostas: custo e efeito aparecem juntos.
• Outras ações guarda as opções avançadas. Use quando quiser.
• Ver empresa é uma consulta gratuita, com preços e sabores opcionais.
• Acabaram as ações? Enter fecha o ano e calcula as vendas.
• Caos abre histórias estranhas; reputação ajuda a conquistar clientes.

Tudo é salvo após cada decisão. Não há cronômetro.'''


class Terminal:
    def __init__(self, console, save_dir, balance, clear=True):
        self.console = console
        self.save_path = save_dir / 'campaign.json'
        self.profile_path = save_dir / 'profile.json'
        self.profile = load_profile(self.profile_path)
        self.balance = balance
        self.game = None
        self.session_achievements = []
        self.clear_enabled = clear
        self.notice = ''

    def screen(self):
        # Rich usa a sequência apropriada; pipes e TERM=dumb mantêm a saída legível.
        if self.clear_enabled and self.console.is_terminal and not self.console.is_dumb_terminal:
            self.console.clear(home=True)

    def pause(self):
        self.console.input('\nEnter para voltar > ')

    def number(self, prompt, minimum, maximum, allowed=None):
        while True:
            text = self.console.input(prompt).strip()
            try:
                value = int(text) if text else 0
                if minimum <= value <= maximum and (allowed is None or value in allowed):
                    return value
            except ValueError:
                pass
            self.console.print('Digite um número disponível na tela.', style='yellow')

    def confirm(self, prompt):
        return self.number(prompt + '\n[1] Confirmar  [0 / Enter] Voltar > ', 0, 1) == 1

    def checkpoint(self):
        if self.game:
            self.game.save(self.save_path)
            newly = update_profile(self.profile, self.game.state, self.profile_path)
            self.session_achievements.extend(newly)
            if newly:
                self.notice += '\nConquista: ' + ', '.join(ACHIEVEMENTS[k][0] for k in newly)

    def purchase(self, offer, detailed=False):
        if not offer.available:
            raise RuleError(offer.reason)
        p = self.game.state.player
        if offer.cost > 0 and p.cash < offer.cost:
            raise RuleError('Caixa insuficiente para esta ação.')
        significant = (offer.cost >= 3000 or offer.cost >= max(1, p.cash) * .4
                       or offer.kind in ('loan', 'acquire', 'merge', 'retire', 'sell_factory', 'spy', 'sabotage', 'smear'))
        if detailed or significant:
            self.screen()
            self.console.print(offer.title, style='bright_green')
            self.console.print(offer.detail)
            if not self.confirm(f'Custo: {money(offer.cost)} e 1 ação. Caixa: {money(p.cash)}.'):
                return
        self.notice = self.game.act(offer.kind, offer.target)
        self.checkpoint()

    def action_menu(self, category):
        s = self.game.state
        if s.actions <= 0:
            raise RuleError('As duas ações deste ano já foram usadas.')
        options = offers(s, category)
        page = 0
        while True:
            self.screen()
            self.console.print('OUTRAS AÇÕES — escolher custa 1 ação', style='bright_green')
            visible = options[page * 6:page * 6 + 6]
            if not options:
                self.console.print('Nenhuma opção restante nesta categoria.'); self.pause(); return
            for i, o in enumerate(visible, 1):
                available = o.available and (o.cost == 0 or s.player.cash >= o.cost)
                self.console.print(f'[{i}] {o.title} — {money(o.cost)}' + ('' if available else ' (indisponível)'), style=None if available else 'dim')
            self.console.print(f'\nPágina {page + 1}/{(len(options) + 5) // 6}. Selecione para ver efeitos e confirmar.')
            navigation = [0, *range(1, len(visible) + 1)]
            if page:
                self.console.print('[7] Página anterior'); navigation.append(7)
            if (page + 1) * 6 < len(options):
                self.console.print('[8] Próxima página'); navigation.append(8)
            self.console.print('[0] Voltar')
            selected = self.number('Ação > ', 0, 8, navigation)
            if not selected:
                return
            if selected == 7: page -= 1
            elif selected == 8: page += 1
            else:
                self.purchase(visible[selected - 1], detailed=True)
                return

    def other_actions(self):
        self.screen()
        self.console.print('ESCOLHAS AVANÇADAS — 1 ação por operação\n\n[1] Produção\n[2] Marketing\n[3] Pesquisa\n[4] Expansão\n[5] Negociação\n[6] Experimento\n[0] Voltar')
        choice = self.number('Categoria > ', 0, 6)
        if choice == 6: self.experiment_menu()
        elif choice: self.action_menu(['production', 'marketing', 'research', 'expansion', 'negotiation'][choice - 1])

    def market_menu(self):
        self.screen()
        keys = list(self.game.state.player.regions)
        self.console.print('AJUSTES GRÁTIS — valem no próximo fechamento anual.\n')
        for i, key in enumerate(keys, 1):
            r = self.game.state.player.regions[key]
            self.console.print(f'[{i}] {MARKETS[key]["name"]}: {r.price}, prioridade {r.priority}')
        self.console.print('[0] Voltar')
        selected = self.number('Mercado > ', 0, len(keys))
        if not selected: return
        key = keys[selected - 1]
        self.screen()
        self.console.print(MARKETS[key]['name'] + '\n[1] Econômico: mais volume\n[2] Normal: equilíbrio\n[3] Premium: mais margem\n[0] Voltar')
        policy = self.number('Preço > ', 0, 3)
        if not policy: return
        self.screen()
        self.console.print('Quem recebe produção primeiro quando faltar capacidade?')
        priority = self.number('[1] Baixa  [2] Normal  [3] Alta  [0] Voltar > ', 0, 3)
        if not priority: return
        self.game.configure(key, ['economico', 'normal', 'premium'][policy - 1], priority)
        self.notice = 'Preços e prioridade definidos para o próximo fechamento.'
        self.checkpoint()

    def portfolio(self):
        s = self.game.state; p = s.player
        products = catalog(s); selected = list(p.active)
        feedback = ''
        while True:
            self.screen()
            self.console.print(f'SABORES ATIVOS — ajuste gratuito; até {s.balance["line_limit"]} linhas.\n')
            for i, key in enumerate(p.products, 1):
                self.console.print(f'[{i}] {"ATIVO" if key in selected else "-----"} {products[key]["name"]}')
            if feedback: self.console.print(feedback, style='yellow')
            self.console.print('[0] Aplicar e voltar')
            index = self.number('Alternar linha > ', 0, len(p.products))
            feedback = ''
            if not index:
                self.game.set_active(selected); self.notice = 'Linhas ativas atualizadas.'; self.checkpoint(); return
            key = p.products[index - 1]
            if key in selected:
                if len(selected) == 1: feedback = 'Mantenha pelo menos uma linha ativa.'
                else: selected.remove(key)
            elif len(selected) >= s.balance['line_limit']: feedback = 'Desative uma linha antes de incluir outra.'
            else: selected.append(key)

    def experiment_menu(self):
        self.screen()
        self.console.print('EXPERIMENTOS — usam 1 ação; exigem laboratório 1.\n\n[1] Sabor de Nada — R$ 1.100; Caos +0\n[2] Sabor Terça-Feira — R$ 1.600; Caos +8\n[3] Criar minha fórmula\n[0] Voltar')
        choice = self.number('Receita > ', 0, 3)
        if not choice: return
        self.screen()
        if choice == 3:
            self.console.print('Cada ponto custa R$ 100 além da base de R$ 1.100.\nEstranheza: +4 Caos por ponto. Soma acima de 9 exige laboratório 3.')
            traits = tuple(self.number(label + ' [0–3] > ', 0, 3) for label in ('Acidez', 'Temperatura', 'Efervescência', 'Estranheza'))
        else: traits = (0, 0, 0, 0) if choice == 1 else (1, 1, 1, 2)
        if self.confirm(f'Criar por {money(1100 + 100 * sum(traits))} e 1 ação; Caos +{traits[3]*4}?'):
            self.notice = self.game.act('experiment', traits=traits); self.checkpoint()

    def company_menu(self):
        self.screen()
        reports.company_summary(self.console, self.game.state)
        self.console.print('\nAJUSTES GRÁTIS\n[1] Preços e distribuição   [2] Sabores ativos\n\nCONSULTA OPCIONAL\n[3] Arquivo completo       [0 / Enter] Voltar')
        choice = self.number('Empresa > ', 0, 3)
        if choice == 1: self.market_menu()
        elif choice == 2: self.portfolio()
        elif choice == 3: self.journal_menu()

    def journal_menu(self):
        self.screen()
        self.console.print('ARQUIVO — consultas opcionais\n[1] Finanças\n[2] Mercados\n[3] Concorrentes\n[4] Sabores e receitas\n[5] História e notícias\n[6] Conquistas\n[7] Ajuda\n[0] Voltar')
        choice = self.number('Arquivo > ', 0, 7)
        if not choice: return
        self.screen(); s = self.game.state
        if choice == 1: reports.finances(self.console, s)
        elif choice == 2: reports.markets(self.console, s)
        elif choice == 3: reports.competitors(self.console, s)
        elif choice == 4:
            reports.products(self.console, s)
            self.console.print('\nReceitas: acidez / temperatura / efervescência / estranheza.\n3/3/2/2: Nuclear Supreme; 0/2/1/3: Croissant Radioativo;\n1/0/0/3: Sabor de Imposto; 0/0/3/3: Buraco Negro.\nAcidez = temperatura e efervescência >=2 liberam campanhas absurdas.')
            if s.flags.get('founder_notes'):
                self.console.print('Fundador: laboratório 3 + receita 3/3/3/3. A oportunidade final surge a partir de 2015.')
        elif choice == 5:
            for x in s.history[-16:]: self.console.print(f"{1997+x['month']}: {x['text']}")
            for e in s.scheduled: self.console.print(f"Consequência prevista a partir de {1997+e['due']}; depende das decisões e da agenda de eventos.")
        elif choice == 6: reports.achievements(self.console, self.profile)
        elif choice == 7: self.console.print(TUTORIAL)
        self.pause()

    def play(self):
        self.session_achievements = []
        while self.game.state.phase != 'finished':
            s = self.game.state
            self.screen()
            try:
                if s.phase == 'event':
                    reports.event_screen(self.console, s)
                    if self.notice: self.console.print(self.notice, style='yellow'); self.notice = ''
                    choice = self.number('Decisão > ', 0, 3)
                    if not choice: self.checkpoint(); return
                    if self.confirm('Registrar esta decisão narrativa?'):
                        self.notice = self.game.decide(choice - 1); self.checkpoint()
                    continue
                choices = proposals(s)
                dashboard(self.console, s, choices, self.notice)
                self.notice = ''
                allowed = [0, 5, 6] + ([4, *range(1, len(choices) + 1)] if s.actions else [])
                choice = self.number('Diretoria > ', 0, 6, allowed)
                if choice in (1, 2, 3): self.purchase(choices[choice - 1].offer)
                elif choice == 4: self.other_actions()
                elif choice == 5: self.company_menu()
                elif choice == 6: self.checkpoint(); return
                elif choice == 0:
                    if s.actions:
                        self.screen()
                        if not self.confirm(f'Avançar o ano e dispensar {s.actions} ação(ões)?'): continue
                    self.game.close_year(); self.checkpoint()
            except RuleError as exc:
                self.notice = str(exc)
        self.checkpoint()
        self.screen()
        reports.finale(self.console, self.game.state, self.session_achievements)
        self.pause()

    def home(self, seed=None, resume=False):
        if resume:
            self.game = Game.load(self.save_path); self.play(); return
        theme = 'green'
        while True:
            self.screen()
            self.console.print(LOGO if self.console.width >= 65 else 'PLUTONITA\nWORLD DOMINATION', style='bright_green')
            self.console.print('Capitalismo, chicletes e decisões empresariais questionáveis.\nProjeto de fã independente, não oficial. Sem vínculo com a Arcor.')
            self.console.print('\n[1] Nova campanha  [2] Continuar  [3] Conquistas\n[4] Histórico      [5] Cosméticos [0] Sair')
            choice = self.number('Início > ', 0, 5)
            if choice == 0: return
            self.screen()
            if choice == 1:
                if self.save_path.exists() and not self.confirm('Substituir o salvamento? O histórico será preservado.'): continue
                chosen_seed = seed
                if chosen_seed is None:
                    chosen_seed = self.console.input('Seed (vazio para sortear) > ').strip() or secrets.token_hex(4)
                self.game = Game(chosen_seed, self.balance); self.game.state.theme = theme
                self.checkpoint()
                self.screen()
                self.console.print(Panel('PARABÉNS! Você herdou uma fábrica que a prefeitura considera um arbusto. O fundador desapareceu ao mascar o Sabor Definitivo.\n\nVocê tem '+money(self.game.state.player.cash)+' e 24 anos para dominar o mercado mundial.', title='1998 — A HERANÇA', box=box.ASCII, border_style=theme))
                self.console.print(RAT if 'mascote_rato' in self.profile['unlocks'] else MONSTER, style=theme)
                self.console.print('Seed: ' + str(chosen_seed))
                if self.number('Tutorial? [1] Sim [0 / Enter] Começar > ', 0, 1):
                    self.screen(); self.console.print(TUTORIAL); self.pause()
                self.play()
            elif choice == 2:
                try: self.game = Game.load(self.save_path); self.play()
                except SaveError as exc: self.console.print(str(exc), style='red'); self.pause()
            elif choice == 3: reports.achievements(self.console, self.profile); self.pause()
            elif choice == 4: reports.campaign_history(self.console, self.profile); self.pause()
            elif choice == 5:
                themes = [('Verde ácido', 'green')]
                if 'tema_roxo' in self.profile['unlocks']: themes.append(('Roxo efervescente', 'magenta'))
                if 'tema_azul' in self.profile['unlocks']: themes.append(('Azul congelante', 'cyan'))
                for i, (name, _) in enumerate(themes, 1): self.console.print(f'[{i}] {name}')
                self.console.print('[0] Voltar — temas extras são liberados por conquistas.')
                picked = self.number('Tema da próxima campanha > ', 0, len(themes))
                if picked: theme = themes[picked - 1][1]


def main():
    parser = argparse.ArgumentParser(description='PLUTONITA: WORLD DOMINATION — 24 anos para conquistar o mundo.', add_help=False, usage='%(prog)s [opções]')
    parser._optionals.title = 'opções'
    parser.add_argument('-h', '--help', action='help', help='mostrar esta ajuda e sair')
    parser.add_argument('--seed', help='seed para uma nova campanha')
    parser.add_argument('--no-color', action='store_true', help='desativar cores')
    parser.add_argument('--no-clear', action='store_true', help='preservar telas anteriores no terminal')
    parser.add_argument('--resume', action='store_true', help='continuar diretamente o salvamento')
    parser.add_argument('--classic', action='store_true', help='jogar a campanha clássica anterior ao redesenho')
    parser.add_argument('--save-dir', type=Path, default=Path('saves'), help='diretório de campanha e perfil (padrão: saves)')
    parser.add_argument('--balance', help='JSON com parâmetros de balanceamento substitutos')
    args = parser.parse_args()
    if args.balance and not args.classic:
        parser.error('--balance pertence ao modo anterior; use --classic --balance ARQUIVO')
    console = Console(no_color=args.no_color, highlight=False, markup=False, width=None)
    console.width = min(80, console.width)
    terminal = None
    try:
        if args.classic:
            terminal = Terminal(console, args.save_dir, load_balance(args.balance), clear=not args.no_clear)
        else:
            from ..incremental.ui import Terminal as IncrementalTerminal
            terminal = IncrementalTerminal(console, args.save_dir, clear=not args.no_clear)
        terminal.home(args.seed, args.resume)
    except (EOFError, KeyboardInterrupt):
        console.print('\nSessão interrompida.')
        if terminal and terminal.game:
            try:
                terminal.checkpoint()
                console.print('Campanha salva. Continue com python main.py ' + ('--classic ' if args.classic else '') + '--resume.')
            except OSError as exc: console.print(f'Não foi possível salvar: {exc}', style='red')
    except (SaveError, OSError, ValueError) as exc:
        console.print(f'Não foi possível concluir a operação: {exc}', style='red')
        return 1
    return 0
