import requests
from lib.config import TELEGRAM_API


def send_message(chat_id, text: str) -> None:
    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    })


def send_photo(chat_id, file_id: str, caption: str) -> dict:
    r = requests.post(f"{TELEGRAM_API}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": file_id,
        "caption": caption,
        "parse_mode": "HTML",
    })
    return r.json()
