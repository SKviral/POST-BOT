import os

# --- Telegram ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Only this Telegram user ID is allowed to control the bot
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# --- Supabase ---
SUPABASE_URL = os.environ.get("SUPABASE_URL", "")          # e.g. https://xxxx.supabase.co
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY", "")  # service_role key (server-side only!)

SUPABASE_REST = f"{SUPABASE_URL}/rest/v1"
SUPABASE_HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}
