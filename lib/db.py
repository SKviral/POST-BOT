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
    r = requests.post(
        f"{SUPABASE_REST}/settings",
        headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
        json={"key": key, "value": value},
    )
    if not r.ok:
        print("DB set_setting FAILED:", r.status_code, r.text)


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
    r = requests.post(
        f"{SUPABASE_REST}/channels",
        headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
        json={"chat_id": str(chat_id), "title": title},
    )
    if not r.ok:
        print("DB add_channel FAILED:", r.status_code, r.text)


def remove_channel(chat_id: str) -> None:
    r = requests.delete(
        f"{SUPABASE_REST}/channels",
        headers=SUPABASE_HEADERS,
        params={"chat_id": f"eq.{chat_id}"},
    )
    if not r.ok:
        print("DB remove_channel FAILED:", r.status_code, r.text)


# ---------- pending record (link, media, and menu "waiting for text" state) ----------

def get_pending(admin_chat_id: int) -> dict | None:
    r = requests.get(
        f"{SUPABASE_REST}/pending",
        headers=SUPABASE_HEADERS,
        params={"chat_id": f"eq.{admin_chat_id}", "select": "*"},
    )
    if not r.ok:
        print("DB get_pending FAILED:", r.status_code, r.text)
        return None
    rows = r.json()
    return rows[0] if rows else None


def set_pending(admin_chat_id: int, **fields) -> None:
    """Upsert only the given fields; existing columns not passed are left untouched."""
    body = {"chat_id": str(admin_chat_id), **fields}
    r = requests.post(
        f"{SUPABASE_REST}/pending",
        headers={**SUPABASE_HEADERS, "Prefer": "resolution=merge-duplicates"},
        json=body,
    )
    if not r.ok:
        print("DB set_pending FAILED:", r.status_code, r.text, "| body:", body)


def clear_pending(admin_chat_id: int) -> None:
    r = requests.delete(
        f"{SUPABASE_REST}/pending",
        headers=SUPABASE_HEADERS,
        params={"chat_id": f"eq.{admin_chat_id}"},
    )
    if not r.ok:
        print("DB clear_pending FAILED:", r.status_code, r.text)
