import sys
import os

# make the project root importable ("lib" package) on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import traceback
from flask import Flask, request, jsonify
from lib.handlers import handle_update
from lib.config import BOT_TOKEN, ADMIN_ID, SUPABASE_URL

app = Flask(__name__)


@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    print("CONFIG CHECK -> BOT_TOKEN len:", len(BOT_TOKEN),
          "| ADMIN_ID:", ADMIN_ID,
          "| SUPABASE_URL set:", bool(SUPABASE_URL))
    print("INCOMING UPDATE:", update)
    try:
        handle_update(update)
    except Exception:
        # never let Telegram retry forever on a crash — log and return 200
        print("handler error:\n", traceback.format_exc())
    return jsonify({"ok": True})


@app.route("/api/webhook", methods=["GET"])
def health():
    return jsonify({"status": "bot is alive"})
