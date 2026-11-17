"""Catálogo regional e políticas comerciais."""
from .balance import read_data
MARKETS = {m["id"]: m for m in read_data("markets")}
PRICES = {"economico":0.78, "normal":1.0, "premium":1.38}
PRICE_NAMES = {"economico":"Econômico", "normal":"Normal", "premium":"Premium"}

def demand(market: dict, month: int) -> int:
    # Crescimento orgânico previsível; o desafio vem das decisões dos rivais.
    # Cada turno agrega o ano inteiro: sem alternar outubro entre anos.
    seasonal = 1.03  # média anual do antigo pico de 12% em três meses
    return round(market["demand"] * (1 + 0.008*(month-1)) * seasonal)
