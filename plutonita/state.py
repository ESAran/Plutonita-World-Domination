"""Estado serializável. Nenhuma dependência de terminal ou gerador global."""
from dataclasses import asdict, dataclass, field
from typing import Any
from .balance import load_balance

@dataclass
class Region:
    recognition: float = 30
    marketing: float = 0
    price: str = "normal"
    priority: int = 2

@dataclass
class Company:
    id: str
    name: str
    cash: float
    regions: dict[str, Region] = field(default_factory=dict)
    factories: int = 1
    level: int = 1
    efficiency: int = 0
    reputation: float = 50
    chaos: float = 5
    innovation: int = 0
    products: list[str] = field(default_factory=lambda: ["lingua"])
    active: list[str] = field(default_factory=lambda: ["lingua"])
    extra_capacity: int = 0
    extra_maintenance: float = 0
    damage: int = 0
    loan: float = 0
    royalty: float = 0
    eliminated: bool = False
    personality: str = "player"
    aggression: int = 0
    last_profit: float = 0
    last_revenue: float = 0
    last_share: float = 0

@dataclass
class GameState:
    seed: str
    balance: dict
    companies: list[Company]
    month: int = 1
    actions: int = 2
    phase: str = "planning"
    research: dict[str, int] = field(default_factory=dict)
    experimental: dict[str, dict] = field(default_factory=dict)
    flags: dict[str, Any] = field(default_factory=dict)
    effects: list[dict] = field(default_factory=list)
    scheduled: list[dict] = field(default_factory=list)
    seen: list[str] = field(default_factory=list)
    pending_event: str | None = None
    history: list[dict] = field(default_factory=list)
    news: list[str] = field(default_factory=list)
    news_used: list[str] = field(default_factory=list)
    reports: list[dict] = field(default_factory=list)
    rival_history: list[str] = field(default_factory=list)
    decisions: list[str] = field(default_factory=list)
    stats: dict = field(default_factory=lambda: {"revenue":0.0,"profit":0.0,"investments":0.0,"units":0,"events":0,"peaks":{},"defeated":0})
    ending: str | None = None
    campaign_id: str = ""
    theme: str = "green"

    @property
    def year(self) -> int:
        """Ano civil; month permanece como índice legado do turno nos saves."""
        return 1997 + self.month

    @property
    def player(self) -> Company:
        return self.companies[0]

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, value: dict) -> "GameState":
        value = dict(value)
        value["companies"] = [Company(**{**c,"regions":{k:Region(**v) for k,v in c["regions"].items()}}) for c in value["companies"]]
        return cls(**value)

def new_state(seed: str, balance: dict | None = None) -> GameState:
    b = dict(balance or load_balance())
    player = Company("player", "Plutonita Corp.", b["starting_cash"], {"br":Region()}, reputation=b["reputation"],chaos=b["chaos"])
    rivals = [
        Company("goma", "GomaMax", 8000, {k:Region(40,price="economico") for k in ("br","latam","east","africa")},extra_capacity=1500,personality="barata"),
        Company("sweet", "SweetCorp International", 14000, {k:Region(45,price="premium") for k in ("br","na","west")},extra_capacity=1000,reputation=65,personality="premium"),
        Company("bubble", "Dr. Bubble Industries", 7500, {k:Region(35) for k in ("br","asia","sea")},extra_capacity=600,chaos=35,personality="experimental")
    ]
    return GameState(seed, b, [player,*rivals])
