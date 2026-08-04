import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)

API_KEY = os.getenv("IMEI_API_KEY", "")
API_BASE = os.getenv("IMEI_API_BASE", "https://api-client.imei.org/api").rstrip("/")
SERVICE_ID = os.getenv("FMI_SERVICE_ID", "171")

def api_get(path, params):
    params = dict(params)
    params["apikey"] = API_KEY
    r = requests.get(f"{API_BASE}/{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/check")
def check():
    data = request.get_json(silent=True) or {}
    value = (data.get("input") or "").strip()
    if not value:
        return jsonify({"ok": False, "error": "Enter an IMEI or Serial Number."}), 400
    if not API_KEY:
        return jsonify({"ok": False, "error": "API key is not configured. Put it in .env."}), 500
    try:
        result = api_get("submit", {"service_id": SERVICE_ID, "input": value})
        if result.get("status") != 1:
            return jsonify({"ok": False, "error": result}), 400
        response = result.get("response", {})
        services = response.get("services") if isinstance(response, dict) else None
        item = services[0] if isinstance(services, list) and services else response
        return jsonify({"ok": True, "result": item, "raw": result})
    except requests.RequestException as e:
        return jsonify({"ok": False, "error": f"API connection failed: {e}"}), 502
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500

@app.get("/api/balance")
def balance():
    if not API_KEY:
        return jsonify({"ok": False, "error": "API key is not configured."}), 500
    try:
        return jsonify({"ok": True, "result": api_get("balance", {})})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=True)
