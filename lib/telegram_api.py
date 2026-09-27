import requests
from lib.config import TELEGRAM_API, BOT_TOKEN


def send_message(chat_id, text: str, reply_markup: dict = None) -> None:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "disable_web_page_preview": False,
    }
    if reply_markup:
        payload["reply_markup"] = reply_markup
    r = requests.post(f"{TELEGRAM_API}/sendMessage", json=payload)
    result = r.json()
    if not result.get("ok"):
        print("TELEGRAM sendMessage FAILED:", result, "| token_len:", len(BOT_TOKEN))


def send_photo(chat_id, file_id: str, caption: str) -> dict:
    r = requests.post(f"{TELEGRAM_API}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": file_id,
        "caption": caption,
    })
    return r.json()


def send_animation(chat_id, file_id: str, caption: str) -> dict:
    r = requests.post(f"{TELEGRAM_API}/sendAnimation", json={
        "chat_id": chat_id,
        "animation": file_id,
        "caption": caption,
    })
    return r.json()


def send_video(chat_id, file_id: str, caption: str) -> dict:
    r = requests.post(f"{TELEGRAM_API}/sendVideo", json={
        "chat_id": chat_id,
        "video": file_id,
        "caption": caption,
    })
    return r.json()


def answer_callback_query(callback_query_id: str, text: str = None) -> None:
    payload = {"callback_query_id": callback_query_id}
    if text:
        payload["text"] = text
    requests.post(f"{TELEGRAM_API}/answerCallbackQuery", json=payload)


def inline_keyboard(rows: list) -> dict:
    """rows: list of lists of {'text': ..., 'callback_data': ...}"""
    return {"inline_keyboard": rows}
