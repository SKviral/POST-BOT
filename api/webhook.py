import sys
import os

# make the project root importable ("lib" package) on Vercel
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, request, jsonify
from lib.handlers import handle_update

app = Flask(__name__)


@app.route("/api/webhook", methods=["POST"])
def webhook():
    update = request.get_json(force=True, silent=True) or {}
    try:
        handle_update(update)
    except Exception as e:
        # never let Telegram retry forever on a crash — log and return 200
        print("handler error:", e)
    return jsonify({"ok": True})


@app.route("/api/webhook", methods=["GET"])
def health():
    return jsonify({"status": "bot is alive"})
  
