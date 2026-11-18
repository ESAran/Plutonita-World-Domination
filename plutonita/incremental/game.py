"""Motor anual incremental. Consultas não alteram o estado ou o sorteio."""
import json
import math
from pathlib import Path
from random import Random

from ..actions import RuleError
from ..persistence import SaveError, atomic_json, tuples
from .catalog import (COLLAPSE_YEARS, CRITICAL_CHAOS, ENDINGS, FLAVORS,
                      GLOBAL_YEAR, MARKETS, UNITS, YEARS)
from .state import State
from .stories import EVENTS, NEWS


class Game:
    def __init__(self, seed="1998"):
        self.state = State(str(seed))
        self.rng = Random(str(seed))

    def _planning(self):
        if self.state.phase != "planning":
            raise RuleError("Leia o jornal e resolva a decisão antes de investir novamente.")

    def _pay(self, cost, title):
        self._planning()
        if self.state.cash < cost:
            raise RuleError(f"Caixa insuficiente: esta compra custa R$ {cost:,}.")
        self.state.cash -= cost
        self.state.invested += cost
        self.state.history.append({"turn": self.state.turn, "text": title, "cost": cost})

    def unit_cost(self, key):
        return round(UNITS[key].cost * 1.18 ** self.state.units[key])

    def unit_reason(self, key):
        unit = UNITS[key]
        if self.state.turn < unit.year:
            return f"Disponível no ano {unit.year}."
        if unit.flavor not in self.state.flavors:
            return f"Pesquise {FLAVORS[unit.flavor].name}."
        if key == "orbital" and self.state.flags.get("sealed"):
            return "Projetos instáveis encerrados nesta campanha."
        if self.state.units[key] >= 100:
            return "Limite de 100 unidades desta categoria."
        return ""

    def global_multiplier(self):
        s = self.state
        multiplier = 1 + .08 * (len(s.markets) - 1) + .12 * sum(v >= 100 for v in s.markets.values())
        if "abraco" in s.flavors:
            multiplier *= 1.12
        if "abobora" in s.flavors:
            multiplier *= 1.15
        if "atomic" in s.flavors and not s.flags.get("sealed"):
            multiplier *= 1.35
        if s.flags.get("autonomous") or s.flags.get("federation"):
            multiplier *= 1.20
        if s.flags.get("travel_year"):
            multiplier *= .90
        for flag, bonus in (("peso_income", 1.10), ("elimar_promoted", 1.30),
                            ("elimar_discreet", 1.20), ("elimar_gone", .85),
                            ("stock_eaten", .80), ("court_ally", 1.15),
                            ("court_predator", .75), ("court_supply", 1.10),
                            ("court_tithe", .90)):
            if s.flags.get(flag):
                multiplier *= bonus
        return multiplier

    def unit_income(self, key):
        s = self.state
        multiplier = self.global_multiplier() * 1.5 ** s.upgrades[key]
        if key == "seller" and "baba" in s.flavors:
            multiplier *= 1.25
        if key == "factory":
            if "dentada" in s.flavors:
                multiplier *= 1.5
            if s.flags.get("extra_floor"):
                multiplier *= 1.2
            if s.flags.get("shared_custody"):
                multiplier *= .85
        if key == "orbital" and s.flags.get("sealed"):
            multiplier *= .5
        return round(UNITS[key].income * multiplier)

    def income(self):
        return sum(self.unit_income(key) * count for key, count in self.state.units.items())

    def buy(self, key):
        self._planning()
        if key not in UNITS:
            raise RuleError("Unidade desconhecida.")
        reason = self.unit_reason(key)
        if reason:
            raise RuleError(reason)
        self._pay(self.unit_cost(key), f"Comprou: {UNITS[key].name}")
        self.state.units[key] += 1
        return f"Unidade adquirida. Renda prevista: R$ {self.income():,}/ano."

    def upgrade_cost(self, key):
        return UNITS[key].cost * 8 * 2 ** self.state.upgrades[key]

    def upgrade(self, key):
        self._planning()
        if key not in UNITS or self.state.units[key] == 0:
            raise RuleError("Compre uma unidade dessa categoria primeiro.")
        if self.state.upgrades[key] >= 3:
            raise RuleError("Categoria já está no nível máximo.")
        if key == "orbital" and self.state.flags.get("sealed"):
            raise RuleError("Projetos orbitais encerrados.")
        self._pay(self.upgrade_cost(key), f"Melhorou: {UNITS[key].name}")
        self.state.upgrades[key] += 1
        return "Categoria melhorada: renda +50% nas unidades atuais e futuras."

    def research_reason(self, key):
        if key in self.state.flavors:
            return "Já pesquisado; benefício aplicado automaticamente."
        if self.state.turn < FLAVORS[key].year:
            return f"Disponível no ano {FLAVORS[key].year}."
        if FLAVORS[key].drift and self.state.flags.get("sealed"):
            return "Projetos instáveis encerrados nesta campanha."
        return ""

    def research(self, key):
        self._planning()
        if key not in FLAVORS:
            raise RuleError("Sabor desconhecido.")
        reason = self.research_reason(key)
        if reason:
            raise RuleError(reason)
        flavor = FLAVORS[key]
        self._pay(flavor.cost, f"Pesquisou: {flavor.name}")
        self.state.flavors.append(key)
        self.state.chaos = min(100, self.state.chaos + flavor.chaos)
        return f"{flavor.name} lançado! {flavor.detail}"

    def market_reason(self, key):
        s = self.state
        if key in s.markets:
            return "Mercado já aberto; crescimento automático."
        if s.turn < MARKETS[key].year:
            return f"Disponível no ano {MARKETS[key].year}."
        if key == "latam" and s.markets["br"] < 25:
            return "Alcance 25% do Brasil ou descubra uma rota alternativa."
        return ""

    def expand(self, key):
        self._planning()
        if key not in MARKETS:
            raise RuleError("Mercado desconhecido.")
        reason = self.market_reason(key)
        if reason:
            raise RuleError(reason)
        self._pay(MARKETS[key].cost, f"Entrou em: {MARKETS[key].name}")
        self.state.markets[key] = 5.0
        return f"Operação aberta: {MARKETS[key].name}. Toda a renda recebe +8 pontos de bônus de expansão."

    def world_share(self):
        return round(sum(self.state.markets.get(key, 0) * market.weight
                         for key, market in MARKETS.items()), 1)

    def competition(self, key):
        if not MARKETS[key].rival or self.state.turn < GLOBAL_YEAR:
            return 1.0
        return 1.20 + .025 * (self.state.turn - GLOBAL_YEAR)

    def market_growth(self, key, income=None):
        if key not in self.state.markets or self.state.markets[key] >= 100:
            return 0.0
        s = self.state
        income = self.income() if income is None else income
        growth = 2 + income / MARKETS[key].resistance
        if "abobora" in s.flavors:
            growth *= 1.15
        if s.flags.get("future_sales"):
            growth *= 1.20
        if s.flags.get("predators"):
            growth *= 1.30 if s.flags.get("big_predators") else 1.15
        cap = 25 if key in ("br", "latam") else 16
        growth = round(min(cap, growth / self.competition(key)), 1)
        return round(min(100 - s.markets[key], growth), 1)

    def chaos_drift(self):
        s = self.state
        drift = 0
        if not s.flags.get("sealed"):
            drift = sum(FLAVORS[key].drift for key in s.flavors)
            if s.flags.get("autonomous"):
                drift += 3
        return drift - (2 if "abraco" in s.flavors else 0)

    def _event(self):
        s = self.state
        # O aviso de crise tem prioridade. Capítulos adiados ficam na agenda.
        if s.critical_years >= 2 and "critical" not in s.seen:
            return "critical"
        for item in sorted(s.scheduled, key=lambda item: item["due"]):
            if item["due"] <= s.turn:
                s.scheduled.remove(item)
                return item["event"]
        if s.turn >= 4 and s.units["factory"] and not {"walking", "walking_v2"}.intersection(s.seen):
            return "walking_v2"
        if s.turn in (3, 5, 6, 8, 10, 12, 14, 16, 18, 20, 22):
            pool = [key for key, available in (
                ("elimar", s.turn >= 3),
                ("counterfeit", s.turn >= 6 and len(s.flavors) >= 2),
                ("court", s.turn >= GLOBAL_YEAR),
            ) if available and key not in s.seen]
            if pool:
                return self.rng.choice(pool)
        return None

    def close_year(self):
        self._planning()
        s = self.state
        income = self.income()
        growth = {key: self.market_growth(key, income) for key in s.markets}
        s.cash += income
        s.total_income += income
        s.flags.pop("travel_year", None)
        for key, change in growth.items():
            s.markets[key] = round(min(100, s.markets[key] + change), 1)
        s.chaos = max(0, min(100, s.chaos + self.chaos_drift()))
        s.critical_years = s.critical_years + 1 if s.chaos >= CRITICAL_CHAOS else 0
        available_news = [item["text"] for item in NEWS
                          if all(s.flags.get(flag) for flag in item.get("flags", ()))]
        news = [self.rng.choice(available_news)]
        if s.turn == GLOBAL_YEAR - 1:
            news.insert(0, "ABERTURA GLOBAL: no ano 10, América do Norte, Europa, Ásia e África "
                        "entram no mapa. GomaMax, SweetCorp e Dr. Bubble já estão nesses mercados.")
        conquered = [MARKETS[key].name for key, delta in growth.items()
                     if delta and s.markets[key] >= 100]
        if conquered:
            news.insert(0, "Mercado consolidado: " + ", ".join(conquered) + ". Bônus de renda no próximo ano.")
        if s.critical_years:
            news.insert(0, f"CAOS CRÍTICO: {s.critical_years}/{COLLAPSE_YEARS} fechamentos consecutivos. "
                        "O quarto causa perda irreversível do controle da companhia.")
        if s.critical_years >= COLLAPSE_YEARS:
            s.ending = "collapse"
        event = None if s.ending else self._event()
        expenses = 0
        if event and EVENTS[event].get("arrival"):
            before = s.cash
            outcomes = self._effects(EVENTS[event]["arrival"])
            expenses = before - s.cash
            news.extend([EVENTS[event]["arrival_detail"], *outcomes])
        s.papers.append({"turn": s.turn, "year": s.year, "income": income,
                         "cash": s.cash, "growth": growth, "chaos": s.chaos,
                         "share": self.world_share(), "news": news,
                         "event": event, "decision": None,
                         "event_expenses": expenses, "outcomes": []})
        s.phase = "newspaper"

    def pending_event(self):
        if self.state.phase != "newspaper" or not self.state.papers:
            return None
        paper = self.state.papers[-1]
        return paper["event"] if paper["decision"] is None else None

    def decide(self, choice):
        key = self.pending_event()
        if key is None:
            raise RuleError("Nenhuma decisão pendente nesta edição.")
        options = EVENTS[key]["options"]
        if type(choice) is not int or not 0 <= choice < len(options):
            raise RuleError("Escolha uma das opções disponíveis.")
        option = options[choice]
        s = self.state
        if s.cash < option["cost"]:
            raise RuleError("Caixa insuficiente. As alternativas gratuitas continuam disponíveis.")
        s.cash -= option["cost"]
        s.invested += option["cost"]
        outcomes = self._effects(option["effects"])
        s.seen.append(key)
        s.papers[-1]["decision"] = option["label"]
        s.papers[-1].setdefault("outcomes", []).extend(outcomes)
        s.history.append({"turn": s.turn, "text": option["label"], "cost": option["cost"]})
        return "Decisão registrada: " + option["label"] + "."

    def _effects(self, effects):
        """Aplica custos/consequências uma vez; sorteios só ocorrem após uma decisão válida."""
        s = self.state
        outcomes = []
        loss = effects.get("cash_loss", 0)
        if s.flags.get("big_predators"):
            loss = effects.get("big_predator_loss", loss)
        if loss:
            amount = round(s.cash * loss)
            s.cash -= amount
            text = f"Despesa narrativa: -R$ {amount:,} ({loss:.0%} do caixa)."
            outcomes.append(text)
            s.history.append({"turn": s.turn, "text": text, "cost": amount})
        if effects.get("cash_gain"):
            amount = effects["cash_gain"]
            s.cash += amount
            text = f"Acordo recebido: +R$ {amount:,}."
            outcomes.append(text)
            s.history.append({"turn": s.turn, "text": text, "cost": -amount})
        s.chaos = max(0, min(100, s.chaos + effects.get("chaos", 0)))
        s.flags.update(effects.get("flags", {}))
        if s.chaos < CRITICAL_CHAOS:
            s.critical_years = 0
        if "unit" in effects:
            s.units[effects["unit"]] = min(100, s.units[effects["unit"]] + 1)
        if "market" in effects:
            market = effects["market"]
            s.markets[market] = min(100, s.markets.get(market, 0) + effects.get("presence", 0))
        if "schedule" in effects:
            delay, event = effects["schedule"]
            s.scheduled.append({"due": s.turn + delay, "event": event})
        if "chance" in effects:
            chance = effects["chance"]
            outcome = chance["success"] if self.rng.random() < chance["probability"] else chance["failure"]
            outcomes.extend(self._effects(outcome))
        if effects.get("result"):
            outcomes.append(effects["result"])
            s.history.append({"turn": s.turn, "text": effects["result"], "cost": 0})
        return outcomes

    def _ending(self):
        s = self.state
        if s.ending:
            return s.ending
        complete = len(s.markets) == len(MARKETS) and all(v >= 100 for v in s.markets.values())
        stable = s.chaos < CRITICAL_CHAOS and not s.flags.get("autonomous")
        if complete and stable and not s.flags.get("federation") and s.turn < YEARS:
            return "perfect"
        if s.turn < YEARS:
            return None
        if s.flags.get("federation") or s.flags.get("autonomous"):
            return "federation"
        if complete:
            return "late" if stable else "unstable"
        if s.total_income >= 1500000:
            return "magnate"
        if s.markets.get("br", 0) >= 100 and s.markets.get("latam", 0) >= 100:
            return "regional"
        return "survivor"

    def continue_year(self):
        if self.state.phase != "newspaper":
            raise RuleError("O ano ainda não foi encerrado.")
        if self.pending_event():
            raise RuleError("Resolva a manchete antes de continuar.")
        s = self.state
        s.ending = self._ending()
        if s.ending:
            s.phase = "finished"
        else:
            s.turn += 1
            s.phase = "planning"

    def save(self, path):
        atomic_json(Path(path), {"mode": "incremental", "version": 1,
                                "state": self.state.to_dict(), "rng": self.rng.getstate()})

    @classmethod
    def load(cls, path):
        try:
            data = json.loads(Path(path).read_text(encoding="utf-8"))
            if data.get("mode") != "incremental" or data.get("version") != 1:
                raise ValueError("Este arquivo não é uma campanha incremental compatível.")
            state = State(**data["state"])
            cls._validate(state)
            game = cls(state.seed)
            game.state = state
            game.rng.setstate(tuples(data["rng"]))
            return game
        except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
            raise SaveError(f"Não foi possível carregar a campanha incremental: {exc}") from exc

    @staticmethod
    def _validate(s):
        def integer(value, low, high):
            return type(value) is int and low <= value <= high

        if not isinstance(s.seed, str) or not integer(s.turn, 1, YEARS):
            raise ValueError("Ano ou seed inválido.")
        if s.phase not in ("planning", "newspaper", "finished"):
            raise ValueError("Fase inválida.")
        if any(not integer(v, 0, 10**18) for v in (s.cash, s.total_income, s.invested)):
            raise ValueError("Valores financeiros inválidos.")
        if not integer(s.chaos, 0, 100) or not integer(s.critical_years, 0, COLLAPSE_YEARS):
            raise ValueError("Caos inválido.")
        if set(s.units) != set(UNITS) or any(not integer(v, 0, 100) for v in s.units.values()):
            raise ValueError("Unidades inválidas.")
        if set(s.upgrades) != set(UNITS) or any(not integer(v, 0, 3) for v in s.upgrades.values()):
            raise ValueError("Melhorias inválidas.")
        if (not isinstance(s.flavors, list) or "lingua" not in s.flavors
                or len(set(s.flavors)) != len(s.flavors) or set(s.flavors) - set(FLAVORS)):
            raise ValueError("Sabores inválidos.")
        if ("br" not in s.markets or set(s.markets) - set(MARKETS)
                or any(type(v) not in (int, float) or not math.isfinite(v) or not 0 <= v <= 100
                       for v in s.markets.values())):
            raise ValueError("Mapa inválido.")
        if not isinstance(s.flags, dict) or any(type(v) is not bool for v in s.flags.values()):
            raise ValueError("Consequências inválidas.")
        if not isinstance(s.seen, list) or set(s.seen) - set(EVENTS):
            raise ValueError("Histórias desconhecidas.")
        if not isinstance(s.scheduled, list) or any(
            item["event"] not in EVENTS or not integer(item["due"], 1, YEARS + 3)
            for item in s.scheduled
        ):
            raise ValueError("Agenda inválida.")
        expected = s.turn - 1 if s.phase == "planning" else s.turn
        if not isinstance(s.papers, list) or len(s.papers) != expected:
            raise ValueError("Jornal inconsistente com o ano da campanha.")
        for turn, paper in enumerate(s.papers, 1):
            if paper["turn"] != turn or paper["year"] != 1997 + turn:
                raise ValueError("Edição inválida.")
            if paper["event"] is not None and paper["event"] not in EVENTS:
                raise ValueError("Manchete inválida.")
            if paper["decision"] is not None and not isinstance(paper["decision"], str):
                raise ValueError("Decisão inválida.")
            if not isinstance(paper["news"], list) or any(not isinstance(n, str) for n in paper["news"]):
                raise ValueError("Notícias inválidas.")
            if not integer(paper.get("event_expenses", 0), 0, 10**18):
                raise ValueError("Despesa narrativa inválida.")
            if (not isinstance(paper.get("outcomes", []), list)
                    or any(not isinstance(text, str) for text in paper.get("outcomes", []))):
                raise ValueError("Desfecho narrativo inválido.")
            if any(not integer(paper[k], 0, 10**18) for k in ("income", "cash")):
                raise ValueError("Balanço inválido.")
            if not isinstance(paper["growth"], dict) or set(paper["growth"]) - set(MARKETS):
                raise ValueError("Expansão inválida.")
            if not integer(paper["chaos"], 0, 100):
                raise ValueError("Caos da edição inválido.")
            if not isinstance(paper["share"], (int, float)) or not 0 <= paper["share"] <= 100:
                raise ValueError("Participação inválida.")
        if not isinstance(s.history, list):
            raise ValueError("Histórico inválido.")
        if s.ending is not None and s.ending not in ENDINGS:
            raise ValueError("Final desconhecido.")
        if s.phase == "finished" and s.ending is None:
            raise ValueError("Campanha encerrada sem final.")
