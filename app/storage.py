import json
import os
from datetime import datetime, timezone
from typing import Dict

LOG_PATH = os.getenv("LOG_PATH", "data/logs.jsonl")
MODE_PATH = os.getenv("MODE_PATH", "data/chat_modes.json")


def append_log(record: dict) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _load_modes() -> Dict[str, str]:
    if not os.path.exists(MODE_PATH):
        return {}
    with open(MODE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def get_mode(chat_id: int) -> str:
    data = _load_modes()
    return data.get(str(chat_id), "default")


def set_mode(chat_id: int, mode: str) -> None:
    os.makedirs(os.path.dirname(MODE_PATH), exist_ok=True)
    data = _load_modes()
    data[str(chat_id)] = mode
    with open(MODE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
