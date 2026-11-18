"""Catálogo inicial. Valores de protótipo, concentrados para ajuste após jogar."""
from dataclasses import dataclass

YEARS = 24
GLOBAL_YEAR = 10
CRITICAL_CHAOS = 75
COLLAPSE_YEARS = 4


@dataclass(frozen=True)
class Unit:
    name: str
    cost: int
    income: int
    year: int = 1
    flavor: str = "lingua"


UNITS = {
    "seller": Unit("Vendedores", 120, 90),
    "machine": Unit("Máquinas de venda", 500, 320, flavor="baba"),
    "factory": Unit("Fábricas", 2800, 1400, year=3),
    "network": Unit("Redes de distribuição", 18000, 7600, year=8, flavor="zumbi"),
    "orbital": Unit("Centrais orbitais", 120000, 46000, year=10, flavor="atomic"),
}


@dataclass(frozen=True)
class Flavor:
    name: str
    cost: int
    year: int
    detail: str
    chaos: int = 0
    drift: int = 0


FLAVORS = {
    "lingua": Flavor("Língua Ácida", 0, 1, "Sabor inicial. Vendedores disponíveis."),
    "baba": Flavor("Baba de Bruxa", 800, 1,
                   "Libera máquinas de venda; vendedores rendem +25%.", 5),
    "abraco": Flavor("Abraço Congelante", 1800, 4,
                     "Toda a renda +12%; caos -2 por ano."),
    "dentada": Flavor("Dentada Ardente", 4200, 5,
                      "Fábricas rendem +50%.", 8),
    "abobora": Flavor("Cabeça de Abóbora", 6500, 6,
                      "Toda a renda +15%; presença nos mercados cresce +15%.", 5),
    "zumbi": Flavor("Mordida de Zumbi", 14000, 8,
                    "Libera redes de distribuição; caos +2 por ano.", 12, 2),
    "atomic": Flavor("Atomic Mistério", 36000, 10,
                     "Libera centrais orbitais; toda a renda +35%; caos +5 por ano.", 18, 5),
}


@dataclass(frozen=True)
class Market:
    name: str
    cost: int
    year: int
    resistance: int
    weight: float
    rival: str = ""


MARKETS = {
    "br": Market("Brasil", 0, 1, 220, .14),
    "latam": Market("América Latina", 2500, 4, 650, .14),
    "na": Market("América do Norte", 10000, 10, 3600, .20, "GomaMax"),
    "eu": Market("Europa", 14000, 10, 4400, .18, "SweetCorp"),
    "asia": Market("Ásia e Oceania", 18000, 10, 5200, .24, "Dr. Bubble"),
    "africa": Market("África e Oriente Médio", 9000, 10, 2800, .10, "GomaMax"),
}

ENDINGS = {
    "perfect": ("WORLD DOMINATION — FINAL PERFEITO",
                "Todos os mercados conquistados antes do prazo. A Plutonita domina o mundo. "
                "Pela primeira vez, o departamento jurídico não encontrou uma ressalva."),
    "collapse": ("A EMPRESA CONTINUA. VOCÊ, NÃO.",
                 "Após quatro anos em estado crítico, a Plutonita deixou de reconhecer seus administradores. "
                 "O balanço segue positivo. Seu crachá foi digerido."),
    "federation": ("FEDERAÇÃO DAS FÁBRICAS",
                   "As instalações continuam produzindo, mas assinam os próprios contratos. "
                   "Você fundou um império que decidiu trabalhar por conta própria."),
    "late": ("O MUNDO, COM UM ANO DE ATRASO",
             "Você conquistou todos os mercados no último fechamento. "
             "A dominação veio; o final perfeito exigia chegar antes."),
    "unstable": ("UM IMPÉRIO EM ESTADO CRÍTICO",
                 "O mundo consome Plutonita, mas ninguém pode garantir quem estará no comando amanhã. "
                 "A expansão venceu a geografia e perdeu o controle."),
    "magnate": ("O GRANDE MAGNATA",
                "O mundo ainda tem outras marcas. Sua conta bancária considera isso um detalhe."),
    "regional": ("POTÊNCIA LATINO-AMERICANA",
                 "Do Brasil ao continente, a Plutonita virou parte da paisagem. "
                 "O resto do mundo permanece uma oportunidade para outra campanha."),
    "survivor": ("AINDA ESTAMOS VENDENDO",
                 "A empresa atravessou 24 anos. Não conquistou o planeta, mas conquistou clientes "
                 "que agora só aceitam pagar em dinheiro, por precaução."),
}
