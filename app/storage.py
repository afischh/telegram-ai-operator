import json
import os
from datetime import datetime, timezone

LOG_PATH = os.getenv("LOG_PATH", "data/logs.jsonl")


def append_log(record: dict) -> None:
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    payload = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **record,
    }
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
