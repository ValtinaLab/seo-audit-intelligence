from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


DATA_DIR = Path("data")
HISTORY_DIR = DATA_DIR / "history"
SNAPSHOT_DIR = DATA_DIR / "snapshots"


def domain_key(url: str) -> str:
    parsed = urlparse(url)
    key = parsed.netloc.replace("www.", "") or "site"
    return "".join(char if char.isalnum() or char in ".-" else "-" for char in key)


def save_history(start_url: str, summary: dict) -> None:
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    path = HISTORY_DIR / f"{domain_key(start_url)}.jsonl"
    record = {"created_at": datetime.utcnow().isoformat(), **summary}
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=True) + "\n")


def load_history(key: str) -> list[dict]:
    path = HISTORY_DIR / f"{key}.jsonl"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def save_snapshot(start_url: str, pages: list[dict], issues: list[dict]) -> None:
    SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOT_DIR / f"{domain_key(start_url)}.json"
    snapshot = {
        "created_at": datetime.utcnow().isoformat(),
        "pages": pages,
        "issues": issues,
    }
    path.write_text(json.dumps(snapshot, ensure_ascii=True, indent=2), encoding="utf-8")


def load_snapshot(start_url: str) -> dict | None:
    path = SNAPSHOT_DIR / f"{domain_key(start_url)}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
