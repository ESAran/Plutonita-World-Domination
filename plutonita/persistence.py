"""JSON versionado, gravação atômica e perfil idempotente."""
import json
import os
import tempfile
from pathlib import Path
from random import Random
from .state import GameState

VERSION = 1
class SaveError(ValueError):
    pass

def atomic_json(path: Path, value: dict) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name+".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2, allow_nan=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)

def save_game(path: Path, state: GameState, rng: Random) -> None:
    atomic_json(path, {"version":VERSION,"state":state.to_dict(),"rng":rng.getstate()})

def tuples(value):
    return tuple(tuples(v) for v in value) if isinstance(value,list) else value

def load_game(path: Path) -> tuple[GameState, Random]:
    try:
        with Path(path).open(encoding="utf-8") as stream:
            data = json.load(stream)
        if data.get("version") != VERSION:
            raise SaveError("Versão de salvamento incompatível.")
        state = GameState.from_dict(data["state"])
        from .validation import validate_state
        validate_state(state)
        if not 1 <= state.month <= 24 or not 0 <= state.actions <= 2:
            raise SaveError("Ano ou ações inválidos no salvamento.")
        if state.phase not in ("planning","event","finished"):
            raise SaveError("Fase inválida no salvamento.")
        rng = Random()
        rng.setstate(tuples(data["rng"]))
        return state, rng
    except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError) as exc:
        raise SaveError(f"Não foi possível carregar a campanha: {exc}") from exc

def empty_profile() -> dict:
    return {"version":VERSION,"campaigns":[],"achievements":[],"endings":[],"unlocks":[],"records":{},"totals":{"revenue":0,"months":0}}

def load_profile(path: Path) -> dict:
    if not Path(path).exists():
        return empty_profile()
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if data.get("version") != VERSION or not isinstance(data.get("campaigns"), list):
            raise ValueError("formato incompatível")
        from .endings import ENDINGS
        from .achievements import ACHIEVEMENTS
        for key in ('achievements','endings','unlocks'):
            if not isinstance(data.get(key),list):raise ValueError('lista de perfil inválida')
        if any(k not in ACHIEVEMENTS for k in data['achievements']) or any(k not in ENDINGS for k in data['endings']):raise ValueError('conquista ou final desconhecido')
        if not isinstance(data.get('records'),dict) or not isinstance(data.get('totals'),dict):raise ValueError('estatísticas inválidas')
        if any(not isinstance(data['totals'].get(k),(int,float)) or data['totals'][k]<0 for k in ('revenue','months')):raise ValueError('total acumulado inválido')
        for c in data['campaigns']:
            if not isinstance(c,dict) or not all(k in c for k in ('id','seed','ending','months','value','share','revenue','chaos')) or c['ending'] not in ENDINGS:raise ValueError('campanha histórica inválida')
        return {**empty_profile(), **data}
    except (OSError,ValueError,TypeError,AttributeError) as exc:
        raise SaveError(f"Perfil ilegível; o arquivo foi preservado: {exc}") from exc
