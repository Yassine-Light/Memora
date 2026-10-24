"""Shared helpers for the supervisor and patient interfaces.

The two JSON "databases" (supervisor.json, patient.json) live in the repo-level
data/ folder: MemoryAnchor/data/  (override with MEMORYANCHOR_DATA_DIR).
"""
import hashlib
import hmac
import json
import os
import re
import secrets
import tempfile
import threading
import time
from pathlib import Path

DATA_DIR = Path(os.environ.get("MEMORYANCHOR_DATA_DIR", Path(__file__).resolve().parents[2] / "data"))
SUPERVISOR_FILE = DATA_DIR / "supervisor.json"
PATIENT_FILE = DATA_DIR / "patient.json"

EMPTY_PATIENT = {
    "patient": {
        "name": "",
        "age": None,
        "marital_status": "single",
        "spouse_name": "",
        "situation": "",
        "profession": "",
        "family": [],
        "hobby": "",
    },
    "events": [],
}

lock = threading.RLock()


def safe_page_config(**kwargs) -> None:
    """st.set_page_config that tolerates being called twice (app.py first, then the page script)."""
    import streamlit as st

    try:
        st.set_page_config(**kwargs)
    except Exception:  # StreamlitAPIException: already set by app.py
        pass


def _read(path: Path, default):
    """Read a JSON file. Missing, empty or corrupt files fall back to `default`.

    A corrupt (non-empty, unparseable) file is copied to <name>.corrupt first so nothing is lost.
    """
    fallback = json.loads(json.dumps(default))
    with lock:
        if not path.exists():
            return fallback
        raw = path.read_text(encoding="utf-8")
        if not raw.strip():
            return fallback
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            path.with_suffix(path.suffix + ".corrupt").write_text(raw, encoding="utf-8")
            return fallback


def _write(path: Path, data) -> None:
    """Atomic write: a crash never leaves a half-written JSON file."""
    with lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)


# ---------- patient.json (single patient) ----------
def load_patient() -> dict:
    """Always returns {"patient": {...all keys...}, "events": [valid events]}, whatever the file holds."""
    raw = _read(PATIENT_FILE, EMPTY_PATIENT)
    if not isinstance(raw, dict):
        raw = {}
    patient = raw.get("patient") if isinstance(raw.get("patient"), dict) else {}
    patient = {**EMPTY_PATIENT["patient"], **patient}
    if not isinstance(patient.get("family"), list):
        patient["family"] = []
    events = []
    for e in raw.get("events") or []:
        if isinstance(e, dict) and re.fullmatch(r"([01]?\d|2[0-3]):[0-5]\d", str(e.get("time", ""))):
            h, m = str(e["time"]).split(":")
            events.append({
                "time": f"{int(h):02d}:{m}",
                "event_type": e.get("event_type") if e.get("event_type") in ("medicine", "food", "date") else "date",
                "description": str(e.get("description", "")),
            })
    return {**raw, "patient": patient, "events": events}


def save_patient(data: dict) -> None:
    _write(PATIENT_FILE, data)


# ---------- supervisor.json ----------
def load_supervisors() -> list:
    raw = _read(SUPERVISOR_FILE, {"supervisors": []})
    users = raw.get("supervisors") if isinstance(raw, dict) else None
    return [u for u in users or [] if isinstance(u, dict) and {"username", "password_hash", "salt"} <= u.keys()]


def save_supervisors(users: list) -> None:
    _write(SUPERVISOR_FILE, {"supervisors": users})


def _hash(password: str, salt: str) -> str:
    return hashlib.scrypt(password.encode(), salt=bytes.fromhex(salt), n=2**14, r=8, p=1).hex()


def make_user(username: str, password: str, is_owner: bool) -> dict:
    salt = secrets.token_hex(16)
    return {
        "username": username,
        "password_hash": _hash(password, salt),
        "salt": salt,
        "is_owner": is_owner,
        "created_at": int(time.time()),
    }


def find_user(username: str):
    username = username.strip().lower()
    return next((u for u in load_supervisors() if u["username"].lower() == username), None)


def check_password(user: dict, password: str) -> bool:
    return hmac.compare_digest(_hash(password, user["salt"]), user["password_hash"])