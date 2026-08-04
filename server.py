import os
import requests
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

API_KEY = os.getenv("IMEI_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/check-fmi", methods=["POST"])
def check_fmi():
    data = request.get_json(silent=True) or {}
    serial = data.get("serial", "").strip()

    if not serial:
        return jsonify({"error": "Enter serial number"}), 400

    if not API_KEY:
        return jsonify({"error": "API key is missing"}), 500

    try:
        response = requests.get(
            "https://api-client.imei.org/api/submit",
            params={
                "apikey": API_KEY,
                "service_id": "171",
                "input": serial
            },
            timeout=30
        )

        return jsonify({
            "status_code": response.status_code,
            "response": response.json()
        })

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"API connection failed: {str(e)}"}), 502

    except ValueError:
        return jsonify({
            "status_code": response.status_code,
            "response": response.text
        }), response.status_code


if __name__ == "__main__":
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
