import requests
from lib.config import SUPABASE_REST, SUPABASE_HEADERS


# ---------- settings (header / footer) ----------

def get_setting(key: str, default: str = "") -> str:
    r = requests.get(
        f"{SUPABASE_REST}/settings",
        headers=SUPABASE_HEADERS,
        params={"key": f"eq.{key}", "select": "value"},
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0]["value"] if rows else default


def set_setting(key: str, value: str) -> None:
    requests.post(
        f"{SUPABASE_REST}/settings",
        headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
        json={"key": key, "value": value},
    )


# ---------- channels ----------

def list_channels() -> list:
    r = requests.get(
        f"{SUPABASE_REST}/channels",
        headers=SUPABASE_HEADERS,
        params={"select": "chat_id,title"},
    )
    r.raise_for_status()
    return r.json()


def add_channel(chat_id: str, title: str = "") -> None:
    requests.post(
        f"{SUPABASE_REST}/channels",
        headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
        json={"chat_id": str(chat_id), "title": title},
    )


def remove_channel(chat_id: str) -> None:
    requests.delete(
        f"{SUPABASE_REST}/channels",
        headers=SUPABASE_HEADERS,
        params={"chat_id": f"eq.{chat_id}"},
    )


# ---------- pending link (waiting for the image) ----------

def set_pending_link(admin_chat_id: int, link: str) -> None:
    requests.post(
        f"{SUPABASE_REST}/pending",
        headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
        json={"chat_id": str(admin_chat_id), "link": link},
    )


def get_pending_link(admin_chat_id: int) -> str | None:
    r = requests.get(
        f"{SUPABASE_REST}/pending",
        headers=SUPABASE_HEADERS,
        params={"chat_id": f"eq.{admin_chat_id}", "select": "link"},
    )
    r.raise_for_status()
    rows = r.json()
    return rows[0]["link"] if rows else None


def clear_pending_link(admin_chat_id: int) -> None:
    requests.delete(
        f"{SUPABASE_REST}/pending",
        headers=SUPABASE_HEADERS,
        params={"chat_id": f"eq.{admin_chat_id}"},
    )
      
