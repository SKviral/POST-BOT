from lib.config import ADMIN_ID
from lib import db
from lib.telegram_api import send_message, send_photo


def build_caption(link: str) -> str:
    header = db.get_setting("header", "")
    footer = db.get_setting("footer", "")
    parts = [p for p in [header, link, footer] if p]
    return "\n\n".join(parts)


def handle_update(update: dict) -> None:
    message = update.get("message")
    if not message:
        return  # ignore edited_message, callback_query, etc. for now

    chat_id = message["chat"]["id"]

    # Only the admin may control the bot
    if chat_id != ADMIN_ID:
        send_message(chat_id, "এই বটটি ব্যক্তিগত ব্যবহারের জন্য।")
        return

    text = message.get("text", "")

    # ---------- commands ----------
    if text.startswith("/start"):
        send_message(chat_id,
            "স্বাগতম! ব্যবহার:\n"
            "১. আগে লিংক পাঠাও\n"
            "২. তারপর ছবি পাঠাও — বট ছবিটি সব চ্যানেলে লিংকসহ পোস্ট করবে\n\n"
            "কমান্ডসমূহ:\n"
            "/addchannel <chat_id> - চ্যানেল যোগ করো\n"
            "/removechannel <chat_id> - চ্যানেল বাদ দাও\n"
            "/channels - চ্যানেল লিস্ট দেখাও\n"
            "/setheader <text> - হেডার সেট করো\n"
            "/setfooter <text> - ফুটার সেট করো\n"
            "/header /footer - বর্তমান হেডার/ফুটার দেখাও")
        return

    if text.startswith("/addchannel"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "ব্যবহার: /addchannel -1001234567890")
            return
        db.add_channel(parts[1].strip())
        send_message(chat_id, f"চ্যানেল যোগ হয়েছে: {parts[1].strip()}")
        return

    if text.startswith("/removechannel"):
        parts = text.split(maxsplit=1)
        if len(parts) < 2:
            send_message(chat_id, "ব্যবহার: /removechannel -1001234567890")
            return
        db.remove_channel(parts[1].strip())
        send_message(chat_id, f"চ্যানেল বাদ দেওয়া হয়েছে: {parts[1].strip()}")
        return

    if text.startswith("/channels"):
        channels = db.list_channels()
        if not channels:
            send_message(chat_id, "কোনো চ্যানেল যোগ করা হয়নি।")
        else:
            lines = [f"- {c['chat_id']} {c.get('title') or ''}" for c in channels]
            send_message(chat_id, "যুক্ত চ্যানেলসমূহ:\n" + "\n".join(lines))
        return

    if text.startswith("/setheader"):
        header = text[len("/setheader"):].strip()
        db.set_setting("header", header)
        send_message(chat_id, "হেডার সেট হয়েছে ✅")
        return

    if text.startswith("/setfooter"):
        footer = text[len("/setfooter"):].strip()
        db.set_setting("footer", footer)
        send_message(chat_id, "ফুটার সেট হয়েছে ✅")
        return

    if text.startswith("/header"):
        send_message(chat_id, db.get_setting("header", "(খালি)"))
        return

    if text.startswith("/footer"):
        send_message(chat_id, db.get_setting("footer", "(খালি)"))
        return

    # ---------- step 1: plain text = link ----------
    if text:
        db.set_pending_link(chat_id, text.strip())
        send_message(chat_id, "লিংক সেভ হয়েছে। এখন ছবিটি পাঠাও।")
        return

    # ---------- step 2: photo ----------
    photo = message.get("photo")
    if photo:
        link = db.get_pending_link(chat_id)
        if not link:
            send_message(chat_id, "আগে একটি লিংক পাঠাও, তারপর ছবি দাও।")
            return

        file_id = photo[-1]["file_id"]  # largest resolution
        caption = build_caption(link)

        channels = db.list_channels()
        if not channels:
            send_message(chat_id, "কোনো চ্যানেল যোগ করা নেই। /addchannel দিয়ে যোগ করো।")
            return

        sent, failed = 0, []
        for ch in channels:
            result = send_photo(ch["chat_id"], file_id, caption)
            if result.get("ok"):
                sent += 1
            else:
                failed.append(str(ch["chat_id"]))

        db.clear_pending_link(chat_id)

        summary = f"পোস্ট করা হয়েছে {sent} চ্যানেলে ✅"
        if failed:
            summary += f"\nব্যর্থ: {', '.join(failed)}"
        send_message(chat_id, summary)
        return
