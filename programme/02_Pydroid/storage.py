import json
import os
from dataclasses import asdict

SAVE_PATH_DEFAULT = os.path.join(os.path.dirname(__file__), "..", "save.json")
SAVE_PATH_DEFAULT = os.path.abspath(SAVE_PATH_DEFAULT)

def save_state(state: dict, path: str = SAVE_PATH_DEFAULT, make_backup: bool = True) -> str:
    # optional: exactly one backup (overwrite)
    if make_backup and os.path.exists(path):
        bak = path.replace(".json", ".bak.json")
        try:
            with open(path, "r", encoding="utf-8") as fsrc:
                old = fsrc.read()
            with open(bak, "w", encoding="utf-8") as fdst:
                fdst.write(old)
        except Exception:
            pass

    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    return path

def load_state(path: str = SAVE_PATH_DEFAULT) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_qubit(qb, path: str = SAVE_PATH_DEFAULT) -> str:
    # qb is Qubit dataclass
    state = {"qubit": {"theta": qb.theta, "phi": qb.phi}}
    return save_state(state, path=path)

def load_qubit(qb, path: str = SAVE_PATH_DEFAULT) -> bool:
    data = load_state(path)
    q = data.get("qubit")
    if not q:
        return False
    qb.set_angles(float(q.get("theta", 0.0)), float(q.get("phi", 0.0)))
    return True
