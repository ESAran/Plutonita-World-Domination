"""Limites industriais e custos de ativos."""
from .state import Company, GameState

def capacity(company: Company, balance: dict) -> int:
    return max(0, int(company.factories * (balance["starting_capacity"] + (company.level-1)*balance["capacity_per_level"]) + company.extra_capacity - company.damage))

def maintenance(company: Company, balance: dict) -> float:
    return company.factories * (balance["factory_maintenance"] + (company.level-1)*balance["level_maintenance"]) + company.extra_maintenance

def valuation(company: Company, state: GameState) -> float:
    return round(max(0, company.cash - company.loan + company.factories * state.balance["factory_cost"] * company.level + company.extra_capacity*2 + max(0,company.last_profit)*24 + len(company.regions)*1800),2)
