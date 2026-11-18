"""Estado simples, serializável, sem dependência da interface."""
from dataclasses import asdict, dataclass, field
from .catalog import UNITS


@dataclass
class State:
    seed: str
    turn: int = 1
    phase: str = "planning"
    cash: int = 1000
    units: dict[str, int] = field(default_factory=lambda: {
        key: 3 if key == "seller" else 0 for key in UNITS
    })
    upgrades: dict[str, int] = field(default_factory=lambda: {key: 0 for key in UNITS})
    flavors: list[str] = field(default_factory=lambda: ["lingua"])
    markets: dict[str, float] = field(default_factory=lambda: {"br": 5.0})
    chaos: int = 5
    critical_years: int = 0
    flags: dict = field(default_factory=dict)
    scheduled: list[dict] = field(default_factory=list)
    seen: list[str] = field(default_factory=list)
    papers: list[dict] = field(default_factory=list)
    history: list[dict] = field(default_factory=list)
    total_income: int = 0
    invested: int = 0
    ending: str | None = None

    @property
    def year(self):
        return 1997 + self.turn

    @property
    def stage(self):
        if self.turn >= 10:
            return "DISPUTA GLOBAL"
        if "latam" in self.markets or self.turn >= 4:
            return "EXPANSÃO LATINO-AMERICANA"
        return "PRIMEIROS PASSOS NO BRASIL"

    def to_dict(self):
        return asdict(self)
