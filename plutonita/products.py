"""Descrições reais separadas de atributos comerciais inteiramente fictícios."""
from .balance import read_data
from .state import Company, GameState
CLASSICS = {p["id"]: p for p in read_data("flavors")}

def catalog(state: GameState) -> dict:
    return {**CLASSICS, **state.experimental}

def active_products(company: Company, state: GameState) -> list[dict]:
    products = catalog(state)
    return [products[p] for p in company.active]

def commercial_profile(company: Company, state: GameState, market: dict) -> tuple[float,float,float]:
    products = active_products(company,state)
    attraction = sum(p["attraction"] * p["affinity"].get(market["id"],1) * (1.13 if p["category"]==market["favorite"] else 1) for p in products)/len(products)
    if "abobora" in company.active:
        attraction *= 1 + .55 * 2 / 12  # Halloween agregado em cada ano
    if "dentada" in company.active and "abraco" in company.active:
        attraction *= 1.17
    if "zumbi" in company.active:
        attraction *= 1 + state.month*.009
    if "baba" in company.active:
        attraction *= 1 + .12*((state.month*7 % 5)-2)/2
    if "atomic" in company.active:
        attraction *= 1 + .18*((state.month*11 % 7)-3)/3
    attraction *= 1 + .07*(len(products)-1)
    cost = state.balance["base_unit_cost"] * sum(p["cost"] for p in products)/len(products) * (1-.065*company.efficiency)
    bonus = sum(p["price_bonus"] for p in products)/len(products)
    return attraction, cost, bonus
