from lib.config import ADMIN_ID
from lib import db
from lib.telegram_api import (
    send_message, send_photo, send_animation, send_video,
    answer_callback_query, inline_keyboard,
)


def get_order_mode() -> str:
    return db.get_setting("order_mode", "link_first")


def order_label(mode: str) -> str:
    return "মিডিয়া ➜ লিংক" if mode == "media_first" else "লিংক ➜ মিডিয়া"


def build_main_menu() -> dict:
    mode = get_order_mode()
    return inline_keyboard([
        [{"text": "➕ চ্যানেল যোগ", "callback_data": "add_channel"},
         {"text": "➖ চ্যানেল বাদ", "callback_data": "remove_channel"}],
        [{"text": "📋 চ্যানেল লিস্ট", "callback_data": "list_channels"}],
        [{"text": "✏️ হেডার সেট", "callback_data": "set_header"},
         {"text": "✏️ ফুটার সেট", "callback_data": "set_footer"}],
        [{"text": "👁 হেডার/ফুটার দেখাও", "callback_data": "view_hf"}],
        [{"text": f"🔄 অর্ডার: {order_label(mode)}", "callback_data": "toggle_order"}],
        [{"text": "❓ সাহায্য", "callback_data": "help"}],
    ])


VIDEO_CONFIRM = inline_keyboard([
    [{"text": "✅ পোস্ট করো", "callback_data": "confirm_video"},
     {"text": "❌ বাতিল", "callback_data": "cancel_video"}],
])


def help_text() -> str:
    mode = get_order_mode()
    if mode == "link_first":
        steps = "১. আগে লিংক পাঠাও\n২. তারপর ছবি, GIF অথবা ভিডিও পাঠাও"
    else:
        steps = "১. আগে ছবি, GIF অথবা ভিডিও পাঠাও\n২. তারপর লিংক পাঠাও"
    return (
        f"বর্তমান মোড: {order_label(mode)}\n\n"
        "ব্যবহার:\n" + steps + "\n"
        "   - ছবি/GIF এর ক্ষেত্রে সাথে সাথে সব চ্যানেলে পোস্ট হয়ে যাবে\n"
        "   - ভিডিওর ক্ষেত্রে আগে কনফার্ম করতে বলবে\n\n"
        "মেনু থেকে অর্ডার বদলানো, চ্যানেল, হেডার, ফুটার ম্যানেজ করতে পারো।"
    )


def build_caption(link: str) -> str:
    header = db.get_setting("header", "")
    footer = db.get_setting("footer", "")
    parts = [p for p in [header, link, footer] if p]
    return "\n\n".join(parts)


def post_to_channels(admin_chat_id, file_id: str, link: str, media_type: str) -> None:
    caption = build_caption(link)
    channels = db.list_channels()
    if not channels:
        send_message(admin_chat_id, "কোনো চ্যানেল যোগ করা নেই। মেনু থেকে চ্যানেল যোগ করো।")
        return

    sender = {"photo": send_photo, "animation": send_animation, "video": send_video}[media_type]

    sent, failed = 0, []
    for ch in channels:
        result = sender(ch["chat_id"], file_id, caption)
        if result.get("ok"):
            sent += 1
        else:
            failed.append(str(ch["chat_id"]))

    summary = f"পোস্ট করা হয়েছে {sent} চ্যানেলে ✅"
    if failed:
        summary += f"\nব্যর্থ: {', '.join(failed)}"
    send_message(admin_chat_id, summary)


def finalize_post(chat_id, link: str, file_id: str, media_type: str) -> None:
    """Both link and media are known — either post immediately or ask for video confirmation."""
    if media_type == "video":
        send_message(chat_id, "ভিডিও থাম্বেইল হিসেবে পোস্ট করবো?", reply_markup=VIDEO_CONFIRM)
        # keep the pending row as-is; confirm_video callback will use it
    else:
        post_to_channels(chat_id, file_id, link, media_type)
        db.clear_pending(chat_id)


def show_channels(chat_id) -> None:
    channels = db.list_channels()
    if not channels:
        send_message(chat_id, "কোনো চ্যানেল যোগ করা হয়নি।")
    else:
        lines = [f"- {c['chat_id']} {c.get('title') or ''}" for c in channels]
        send_message(chat_id, "যুক্ত চ্যানেলসমূহ:\n" + "\n".join(lines))


def show_header_footer(chat_id) -> None:
    header = db.get_setting("header", "(খালি)")
    footer = db.get_setting("footer", "(খালি)")
    send_message(chat_id, f"হেডার:\n{header}\n\nফুটার:\n{footer}")


def handle_callback(cq: dict) -> None:
    chat_id = cq["message"]["chat"]["id"]
    from_id = cq["from"]["id"]
    data = cq.get("data", "")
    cq_id = cq["id"]

    if from_id != ADMIN_ID:
        answer_callback_query(cq_id, "এই বটটি ব্যক্তিগত ব্যবহারের জন্য।")
        return

    answer_callback_query(cq_id)  # stop the button's loading spinner

    if data == "add_channel":
        db.set_pending(chat_id, state="awaiting_channel_add")
        send_message(chat_id, "চ্যানেলের numeric ID পাঠাও (যেমন -1001234567890)।\nবটকে ওই চ্যানেলে অবশ্যই admin বানাতে হবে।")

    elif data == "remove_channel":
        db.set_pending(chat_id, state="awaiting_channel_remove")
        send_message(chat_id, "যে চ্যানেল বাদ দিতে চাও তার ID পাঠাও।")

    elif data == "list_channels":
        show_channels(chat_id)

    elif data == "set_header":
        db.set_pending(chat_id, state="awaiting_header")
        send_message(chat_id, "নতুন হেডার টেক্সট পাঠাও।")

    elif data == "set_footer":
        db.set_pending(chat_id, state="awaiting_footer")
        send_message(chat_id, "নতুন ফুটার টেক্সট পাঠাও।")

    elif data == "view_hf":
        show_header_footer(chat_id)

    elif data == "toggle_order":
        current = get_order_mode()
        new_mode = "media_first" if current == "link_first" else "link_first"
        db.set_setting("order_mode", new_mode)
        db.clear_pending(chat_id)  # avoid confusion with a half-finished post in the old mode
        send_message(chat_id, f"অর্ডার পরিবর্তন হয়েছে ✅\nএখন থেকে: {order_label(new_mode)}",
                     reply_markup=build_main_menu())

    elif data == "help":
        send_message(chat_id, help_text(), reply_markup=build_main_menu())

    elif data == "confirm_video":
        pending = db.get_pending(chat_id)
        if pending and pending.get("file_id") and pending.get("link"):
            post_to_channels(chat_id, pending["file_id"], pending["link"], "video")
            db.clear_pending(chat_id)
        else:
            send_message(chat_id, "কিছু পাওয়া যায়নি, আবার প্রথম থেকে পাঠাও।")

    elif data == "cancel_video":
        db.clear_pending(chat_id)
        send_message(chat_id, "বাতিল করা হয়েছে।")


def handle_link_first_text(chat_id, text: str) -> None:
    db.set_pending(chat_id, link=text.strip(), file_id=None, media_type=None, state=None)
    send_message(chat_id, "লিংক সেভ হয়েছে। এখন ছবি, GIF অথবা ভিডিও পাঠাও।")


def handle_media_first_text(chat_id, text: str, pending: dict) -> None:
    file_id = pending.get("file_id") if pending else None
    media_type = pending.get("media_type") if pending else None
    if not file_id:
        send_message(chat_id, "আগে ছবি, GIF অথবা ভিডিও পাঠাও, তারপর লিংক দাও।", reply_markup=build_main_menu())
        return
    link = text.strip()
    db.set_pending(chat_id, link=link)
    finalize_post(chat_id, link, file_id, media_type)


def handle_media(chat_id, file_id: str, media_type: str, pending: dict, mode: str) -> None:
    if mode == "link_first":
        link = pending.get("link") if pending else None
        if not link:
            send_message(chat_id, "আগে একটি লিংক পাঠাও, তারপর ছবি/GIF/ভিডিও দাও।", reply_markup=build_main_menu())
            return
        db.set_pending(chat_id, file_id=file_id, media_type=media_type)
        finalize_post(chat_id, link, file_id, media_type)
    else:  # media_first
        db.set_pending(chat_id, file_id=file_id, media_type=media_type, link=None, state=None)
        send_message(chat_id, "মিডিয়া সেভ হয়েছে। এখন লিংক পাঠাও।")


def handle_update(update: dict) -> None:
    if "callback_query" in update:
        handle_callback(update["callback_query"])
        return

    message = update.get("message")
    if not message:
        return

    chat_id = message["chat"]["id"]

    if chat_id != ADMIN_ID:
        send_message(chat_id, "এই বটটি ব্যক্তিগত ব্যবহারের জন্য।")
        return

    text = message.get("text", "")

    if text.startswith("/start"):
        send_message(chat_id, help_text(), reply_markup=build_main_menu())
        return

    pending = db.get_pending(chat_id)
    state = pending.get("state") if pending else None

    # ---------- menu-driven text replies ----------
    if state == "awaiting_channel_add" and text:
        db.add_channel(text.strip())
        db.set_pending(chat_id, state=None)
        send_message(chat_id, f"চ্যানেল যোগ হয়েছে: {text.strip()}", reply_markup=build_main_menu())
        return

    if state == "awaiting_channel_remove" and text:
        db.remove_channel(text.strip())
        db.set_pending(chat_id, state=None)
        send_message(chat_id, f"চ্যানেল বাদ দেওয়া হয়েছে: {text.strip()}", reply_markup=build_main_menu())
        return

    if state == "awaiting_header" and text:
        db.set_setting("header", text.strip())
        db.set_pending(chat_id, state=None)
        send_message(chat_id, "হেডার সেট হয়েছে ✅", reply_markup=build_main_menu())
        return

    if state == "awaiting_footer" and text:
        db.set_setting("footer", text.strip())
        db.set_pending(chat_id, state=None)
        send_message(chat_id, "ফুটার সেট হয়েছে ✅", reply_markup=build_main_menu())
        return

    mode = get_order_mode()

    # ---------- link / media, in whichever order the current mode expects ----------
    if text:
        if mode == "link_first":
            handle_link_first_text(chat_id, text)
        else:
            handle_media_first_text(chat_id, text, pending or {})
        return

    photo = message.get("photo")
    animation = message.get("animation")
    video = message.get("video")

    if photo:
        handle_media(chat_id, photo[-1]["file_id"], "photo", pending or {}, mode)
        return

    if animation:
        handle_media(chat_id, animation["file_id"], "animation", pending or {}, mode)
        return

    if video:
        handle_media(chat_id, video["file_id"], "video", pending or {}, mode)
        return
