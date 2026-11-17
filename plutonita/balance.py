"""Configuração central, copiada para o save para preservar a campanha."""
import json
import math
from pathlib import Path

DATA = Path(__file__).parent / "data"

def read_data(name: str) -> list | dict:
    with (DATA / f"{name}.json").open(encoding="utf-8") as stream:
        return json.load(stream)

def load_balance(path: str | None = None) -> dict:
    result = read_data("balance")
    if path:
        with open(path, encoding="utf-8") as stream:
            custom = json.load(stream)
        if not isinstance(custom,dict):
            raise ValueError('A configuração precisa ser um objeto JSON com parâmetros e valores.')
        unknown = set(custom) - set(result)
        if unknown:
            raise ValueError(f"Parâmetros desconhecidos: {', '.join(sorted(unknown))}")
        result.update(custom)
    for key, value in result.items():
        minimum=0 if key in ('reputation','chaos') else 1e-9
        if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or value < minimum:
            raise ValueError(f"O parâmetro {key} precisa ser um número válido, maior ou igual a {minimum:g}.")
    for key in ("months", "actions", "starting_capacity", "max_factories", "max_level", "line_limit"):
        if not isinstance(result[key], int):
            raise ValueError(f"O parâmetro {key} precisa ser inteiro.")
    if result["months"] != 24 or result["actions"] != 2:
        raise ValueError("A campanha usa 24 anos e 2 ações por ano.")
    if result["reputation"] > 100 or result["chaos"] > 100:
        raise ValueError("Reputação e Caos devem estar entre 0 e 100.")
    if result['imperial_share']>1:
        raise ValueError('Participação imperial deve estar entre 0 e 1.')
    return result
