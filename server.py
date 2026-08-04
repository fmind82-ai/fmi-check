import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

API_KEY = os.getenv("IMEI_API_KEY")
API_BASE = os.getenv("IMEI_API_BASE", "https://api-client.imei.org/api")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check-fmi", methods=["POST"])
def check_fmi():
    data = request.get_json(silent=True) or {}
    serial = data.get("serial", "").strip()

    if not serial:
        return jsonify({"error": "Serial number is required"}), 400

    if not API_KEY:
        return jsonify({"error": "API key is not configured"}), 500

    try:
        response = requests.post(
            API_BASE,
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "service_id": 171,
                "serial": serial
            },
            timeout=30
        )

        return jsonify(response.json()), response.status_code

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
