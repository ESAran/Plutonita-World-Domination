"""Interface de terminal: investir no painel, consultar mapa, decidir no jornal."""
import secrets
from pathlib import Path

from rich import box
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from ..actions import RuleError
from ..persistence import SaveError
from .catalog import (COLLAPSE_YEARS, CRITICAL_CHAOS, ENDINGS, FLAVORS,
                      MARKETS, UNITS, YEARS)
from .game import Game
from .stories import EVENTS


def money(value):
    return "R$ " + f"{value:,.0f}".replace(",", ".")


def bar(value, width=12):
    filled = min(width, int(value / 100 * width))
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def visible_units(game):
    """Mostra o catálogo atual e só a próxima categoria bloqueada."""
    result = []
    future_shown = False
    for key in UNITS:
        blocked = bool(game.unit_reason(key)) and not game.state.units[key]
        if blocked and future_shown:
            continue
        if blocked:
            future_shown = True
        result.append(key)
    return result


def dashboard(console, game, notice=""):
    s = game.state
    console.print("PLUTONITA: WORLD DOMINATION", style="bold bright_green")
    console.print(f"{s.year} · ANO {s.turn:02}/{YEARS} · {s.stage}", style="magenta")
    console.print(f"Caixa: {money(s.cash)}  |  Renda: +{money(game.income())}/ano", style="bold")
    console.print(f"Caos: {s.chaos}/100 ({game.chaos_drift():+}/ano)  |  Mundo: {game.world_share():.1f}%")
    if s.chaos >= CRITICAL_CHAOS:
        console.print(f"CRÍTICO: {s.critical_years}/{COLLAPSE_YEARS} anos seguidos. "
                      "O quarto fechamento crítico encerra seu controle.", style="bold yellow")
    if s.flags.get("federation"):
        console.print("Rumo escolhido: Federação das Fábricas. Final perfeito indisponível.", style="yellow")
    if s.flags.get("sealed"):
        console.print("Projetos instáveis encerrados; bônus Atomic suspenso e renda orbital reduzida.", style="dim")
    table = Table(box=box.SIMPLE, padding=(0, 1), expand=True)
    table.add_column("COMPRAR UNIDADES", ratio=3)
    table.add_column("Tem", justify="right")
    table.add_column("Custo", justify="right")
    table.add_column("+Renda/ano", justify="right")
    for key in visible_units(game):
        index = list(UNITS).index(key) + 1
        reason = game.unit_reason(key)
        label = f"[{index}] {UNITS[key].name}"
        if s.upgrades[key]:
            label += f" N{s.upgrades[key] + 1}"
        if reason:
            label += "\n" + reason
        table.add_row(label, str(s.units[key]), money(game.unit_cost(key)),
                      money(game.unit_income(key)), style="dim" if reason else None)
    console.print(table)
    next_flavor = next((key for key in FLAVORS if not game.research_reason(key)), None)
    if next_flavor:
        flavor = FLAVORS[next_flavor]
        console.print(f"Pesquisa disponível: {flavor.name} · {money(flavor.cost)}", style="magenta")
    if s.turn == 1:
        console.print("Compre com o caixa disponível. Enter recebe a renda e encerra o ano.", style="dim")
    elif s.turn == 10:
        console.print("Mercados globais abertos! Escolha seu próximo destino em [M].", style="bright_green")
    if notice:
        console.print(notice, style="yellow")
    console.print("\n[P] Sabores  [U] Melhorias  [M] Mapa  [J] Jornal")
    console.print("[Enter] Encerrar o ano     [Q] Salvar e sair", style="bright_green")


WORLD = (
    "       NNNNNNNN              EEEE  AAAAAAAAA",
    "   NNNNNNNNNNN              EEEEEAAAAAAAAAAAA",
    "    NNNNNNNNN                EEE AAAAAAAAAAAA",
    "      NNNNN                  FFFFF AAAAAAAA",
    "        LL                  FFFFFFF  AAAA",
    "         LLLL                FFFFF    AA",
    "          LBBBB              FFFF",
    "          LBBBBB              FF        AAA",
    "           LBBB                        AAAA",
    "            LL",
    "             L",
)
MAP_KEYS = {"N": "na", "E": "eu", "A": "asia", "F": "africa", "L": "latam", "B": "br"}


def map_screen(console, game):
    s = game.state
    console.print("SEU IMPÉRIO — MAPA DO MUNDO", style="bold bright_green")
    console.print(f"Domínio mundial: {game.world_share():.1f}%  |  Caixa: {money(s.cash)}")
    for row in WORLD:
        line = Text()
        for char in row:
            if char not in MAP_KEYS:
                line.append(char)
                continue
            key = MAP_KEYS[char]
            progress = s.markets.get(key, 0)
            color = "bright_green" if progress >= 100 else "magenta" if progress else "bright_black"
            line.append("#" if progress >= 100 else "+" if progress else ".", style=color)
        console.print(line)
    console.print("# consolidado   + presença   . ainda não entrou", style="dim")
    if s.flags.get("walking"):
        note = "filial da fábrica ambulante; bônus em pesos ativo" if s.flags.get("peso_income") else "rota aberta pela fábrica ambulante"
        console.print("Uruguai: " + note + ".", style="magenta")
    for index, (key, market) in enumerate(MARKETS.items(), 1):
        if key in s.markets:
            progress = s.markets[key]
            console.print(f"   {market.name}: {bar(progress)} {progress:.1f}% "
                          f"(+{game.market_growth(key):.1f} pontos/ano)")
        else:
            reason = game.market_reason(key)
            console.print(f"[{index}] {market.name} · {money(market.cost)}" + (f" · {reason}" if reason else ""),
                          style="dim" if reason else None)
    console.print("\nToda região aberta cresce automaticamente; domínio consolidado não regride.", style="dim")
    console.print("Entrada: +8 pontos no bônus de renda. Consolidação: +12 pontos.", style="dim")
    if s.turn >= 10:
        resistance = round((1 - 1 / game.competition("na")) * 100)
        console.print(f"Concorrência global reduz o avanço em {resistance}% neste ano.", style="yellow")
        console.print("GomaMax: América do Norte / África · SweetCorp: Europa · Dr. Bubble: Ásia", style="dim")
    else:
        console.print("Disputa mundial abre no ano 10, mesmo sem concluir a América Latina.", style="dim")
    console.print("[Número] Entrar no mercado   [Enter] Voltar")


def newspaper(console, game, paper=None, archive=False):
    s = game.state
    paper = paper or s.papers[-1]
    console.print(Panel(
        f"PLUTONITA TIMES\nEDIÇÃO {paper['year']} · FECHAMENTO DO ANO {paper['turn']:02}",
        box=box.DOUBLE, border_style="bright_green",
    ))
    console.print(f"RENDA DO ANO: +{money(paper['income'])}  |  MUNDO: {paper['share']:.1f}%", style="bold")
    console.print(f"Caixa no fechamento: {money(paper['cash'])}  ·  Caos: {paper['chaos']}/100", style="dim")
    if paper.get("event_expenses"):
        console.print(f"Despesa do acontecimento, já descontada: -{money(paper['event_expenses'])}", style="yellow")
    for line in paper["news"]:
        console.print("\n" + line)
    growth = [f"{MARKETS[key].name} +{change:.1f}" for key, change in paper["growth"].items() if change]
    if growth:
        console.print("\nEXPANSÃO (pontos): " + " · ".join(growth), style="magenta")
    event = EVENTS.get(paper["event"])
    if event:
        console.print("\n" + event["title"], style="bold yellow")
        console.print(event["body"])
        if paper["decision"] is not None:
            console.print("\nDecisão registrada: " + paper["decision"], style="bright_green")
            for outcome in paper.get("outcomes", []):
                console.print(outcome, style="yellow")
        elif not archive:
            console.print(f"\nDECISÃO PARA O PRÓXIMO ANO · Caixa atual: {money(s.cash)}", style="magenta")
            for i, option in enumerate(event["options"], 1):
                cost = money(option["cost"]) if option["cost"] else "sem custo"
                console.print(f"\n[{i}] {option['label']} · {cost}", style="bold")
                console.print(option["detail"])
        else:
            console.print("\nDecisão ainda pendente.", style="yellow")
    if archive:
        console.print("\n[Enter] Voltar")
    elif game.pending_event():
        console.print("\n[Q] Salvar e sair · Escolha uma decisão para continuar")
    else:
        console.print("\n[Enter] Continuar   [Q] Salvar e sair", style="bright_green")


class Terminal:
    def __init__(self, console, save_dir, clear=True):
        self.console = console
        self.save_path = Path(save_dir) / "incremental.json"
        self.game = None
        self.clear_enabled = clear
        self.notice = ""

    def screen(self):
        if self.clear_enabled and self.console.is_terminal and not self.console.is_dumb_terminal:
            self.console.clear(home=True)

    def checkpoint(self):
        if self.game:
            self.game.save(self.save_path)

    def ask(self, prompt="> "):
        return self.console.input(prompt).strip().lower()

    def pause(self):
        self.console.input("\nEnter para voltar > ")

    def research_menu(self):
        while True:
            self.screen()
            game, s = self.game, self.game.state
            self.console.print("PESQUISA DE SABORES", style="bold magenta")
            self.console.print(f"Caixa: {money(s.cash)} · Benefícios automáticos e permanentes.\n")
            choices = []
            future_shown = False
            for key, flavor in FLAVORS.items():
                if key in s.flavors:
                    self.console.print(f"DESCOBERTO · {flavor.name}", style="dim")
                    continue
                reason = game.research_reason(key)
                if reason and future_shown:
                    continue
                if reason:
                    future_shown = True
                choices.append(key)
                self.console.print(f"\n[{len(choices)}] {flavor.name} · {money(flavor.cost)}", style="bold")
                self.console.print(flavor.detail)
                if flavor.chaos:
                    self.console.print(f"Ao lançar: caos +{flavor.chaos}.", style="yellow")
                if reason:
                    self.console.print(reason, style="dim")
            if s.flags.get("sealed"):
                self.console.print("\nContenção permanente: bônus Atomic suspenso; renda orbital pela metade.", style="yellow")
            self.console.print("\n[Enter] Voltar")
            if self.notice:
                self.console.print(self.notice, style="yellow")
                self.notice = ""
            answer = self.ask("Pesquisar > ")
            if answer in ("", "0"):
                return
            try:
                if not answer.isdigit() or not 1 <= int(answer) <= len(choices):
                    raise RuleError("Escolha um sabor exibido na tela.")
                self.notice = game.research(choices[int(answer) - 1])
                self.checkpoint()
            except RuleError as exc:
                self.notice = str(exc)

    def upgrades_menu(self):
        while True:
            self.screen()
            game, s = self.game, self.game.state
            self.console.print("EVOLUIR UNIDADES", style="bold bright_green")
            self.console.print(f"Caixa: {money(s.cash)}\nUma melhoria aumenta a renda de toda a categoria em 50%.\n")
            choices = [key for key in UNITS if s.units[key]]
            for i, key in enumerate(choices, 1):
                level = s.upgrades[key]
                price = money(game.upgrade_cost(key)) if level < 3 else "nível máximo"
                self.console.print(f"[{i}] {UNITS[key].name} · Nível {level + 1}/4 · {price}")
                self.console.print(f"    {s.units[key]} unidades · renda atual {money(game.unit_income(key) * s.units[key])}/ano", style="dim")
            self.console.print("\n[Enter] Voltar")
            if self.notice:
                self.console.print(self.notice, style="yellow")
                self.notice = ""
            answer = self.ask("Melhorar > ")
            if answer in ("", "0"):
                return
            try:
                if not answer.isdigit() or not 1 <= int(answer) <= len(choices):
                    raise RuleError("Escolha uma categoria disponível.")
                self.notice = game.upgrade(choices[int(answer) - 1])
                self.checkpoint()
            except RuleError as exc:
                self.notice = str(exc)

    def map_menu(self):
        while True:
            self.screen()
            map_screen(self.console, self.game)
            if self.notice:
                self.console.print(self.notice, style="yellow")
                self.notice = ""
            answer = self.ask("Destino > ")
            if answer in ("", "0"):
                return
            try:
                if not answer.isdigit() or not 1 <= int(answer) <= len(MARKETS):
                    raise RuleError("Escolha um destino numerado.")
                self.notice = self.game.expand(list(MARKETS)[int(answer) - 1])
                self.checkpoint()
            except RuleError as exc:
                self.notice = str(exc)

    def archive(self):
        while True:
            self.screen()
            papers = self.game.state.papers
            self.console.print("ARQUIVO DO PLUTONITA TIMES", style="bold bright_green")
            if not papers:
                self.console.print("Sua primeira edição chega ao encerrar o ano.")
            for i, paper in enumerate(papers, 1):
                event = EVENTS.get(paper["event"])
                headline = event["title"] if event else "Expansão e resultados"
                self.console.print(f"[{i}] {paper['year']} · {headline}")
            self.console.print("[Enter] Voltar")
            answer = self.ask("Edição > ")
            if answer in ("", "0"):
                return
            if answer.isdigit() and 1 <= int(answer) <= len(papers):
                self.screen()
                newspaper(self.console, self.game, papers[int(answer) - 1], archive=True)
                self.pause()

    def finale(self):
        self.screen()
        s = self.game.state
        title, body = ENDINGS[s.ending]
        self.console.print(Panel(body, title=title, border_style="bright_green", box=box.DOUBLE))
        self.console.print(f"Ano {s.turn}/{YEARS} · Mundo: {self.game.world_share():.1f}% · Caos: {s.chaos}")
        self.console.print(f"Renda acumulada: {money(s.total_income)} · Caixa: {money(s.cash)}")
        self.console.print(f"Sabores: {len(s.flavors)} · Unidades: {sum(s.units.values())} · Seed: {s.seed}")
        self.console.print("\nFinal perfeito: todos os mercados a 100% antes do ano 24, caos abaixo de 75 "
                           "e companhia sob seu controle.", style="dim")
        self.pause()

    def play(self):
        while self.game.state.phase != "finished":
            self.screen()
            try:
                if self.game.state.phase == "newspaper":
                    newspaper(self.console, self.game)
                    if self.notice:
                        self.console.print(self.notice, style="yellow")
                        self.notice = ""
                    answer = self.ask("Jornal > ")
                    if answer in ("q", "s"):
                        self.checkpoint()
                        return
                    if self.game.pending_event():
                        if not answer.isdigit():
                            raise RuleError("Escolha uma das decisões numeradas.")
                        self.notice = self.game.decide(int(answer) - 1)
                    elif answer == "":
                        self.game.continue_year()
                    else:
                        raise RuleError("Enter continua para o próximo ano; Q salva e sai.")
                    self.checkpoint()
                    continue
                dashboard(self.console, self.game, self.notice)
                self.notice = ""
                answer = self.ask("Império > ")
                if answer in ("q", "s"):
                    self.checkpoint()
                    return
                if answer == "":
                    self.game.close_year()
                    self.checkpoint()
                elif answer == "p":
                    self.research_menu()
                elif answer == "u":
                    self.upgrades_menu()
                elif answer == "m":
                    self.map_menu()
                elif answer == "j":
                    self.archive()
                elif answer.isdigit() and 1 <= int(answer) <= len(UNITS):
                    key = list(UNITS)[int(answer) - 1]
                    if key not in visible_units(self.game):
                        raise RuleError("Essa categoria ainda não está disponível no painel.")
                    self.notice = self.game.buy(key)
                    self.checkpoint()
                else:
                    raise RuleError("Use uma das opções exibidas no painel.")
            except RuleError as exc:
                self.notice = str(exc)
        self.checkpoint()
        self.finale()

    def home(self, seed=None, resume=False):
        if resume:
            if not self.save_path.exists() and (self.save_path.parent / "campaign.json").exists():
                raise SaveError("Só existe uma campanha clássica. Use --classic --resume para retomá-la.")
            self.game = Game.load(self.save_path)
            self.play()
            return
        while True:
            self.screen()
            self.console.print("PLUTONITA\nWORLD DOMINATION", style="bold bright_green")
            self.console.print("Compre unidades. Pesquise sabores. Conquiste o mundo.", style="magenta")
            self.console.print("\nCampanha incremental · 24 anos · Brasil → América Latina → Mundo")
            self.console.print("O dinheiro limita as compras. Enter fecha o ano e traz o jornal.")
            self.console.print("\n[1] Nova campanha\n[2] Continuar\n[0] Sair")
            self.console.print("\nProtótipo jogável — conteúdo e equilíbrio em desenvolvimento.", style="dim")
            answer = self.ask("Início > ")
            if answer in ("", "0", "q"):
                return
            if answer == "1":
                if self.save_path.exists():
                    self.console.print("Já existe uma campanha incremental. Substituir? [1] Sim [Enter] Voltar")
                    if self.ask() != "1":
                        continue
                chosen_seed = seed
                if chosen_seed is None:
                    chosen_seed = self.ask("Seed (Enter para sortear) > ") or secrets.token_hex(4)
                self.game = Game(chosen_seed)
                self.notice = "Brasil, 1998. Três vendedores, um sabor e uma ambição desproporcional."
                self.checkpoint()
                self.play()
            elif answer == "2":
                try:
                    self.game = Game.load(self.save_path)
                    self.play()
                except SaveError as exc:
                    self.console.print(str(exc), style="red")
                    self.pause()
