import uuid
import threading
from flask import session
import os


HISTORY: dict[str, list[dict]] = {}
HISTORY_LOCK = threading.Lock()
MAX_MESSAGES: int = int(os.environ.get("MCP_MAX_RESULTS", "20"))  # limite pour ne pas exploser le contexte du modèle


def get_conv_id() -> str:
    if "conv_id" not in session:
        session["conv_id"] = uuid.uuid4().hex
    return session["conv_id"]


def load_history(conv_id: str) -> list[dict]:
    with HISTORY_LOCK:
        return list(HISTORY.get(conv_id, []))


def save_history(conv_id: str, history: list[dict]):
    history = history[-MAX_MESSAGES:]
    # l'historique doit commencer par un message "user"
    while history and history[0]["role"] != "user":
        history.pop(0)
    with HISTORY_LOCK:
        HISTORY[conv_id] = history

def clear_history(conv_id: str):
    with HISTORY_LOCK:
        HISTORY.pop(conv_id, None)