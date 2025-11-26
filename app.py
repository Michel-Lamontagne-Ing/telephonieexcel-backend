from flask import Flask, request, jsonify
from twilio.rest import Client
import os

app = Flask(__name__)

# Page de test
@app.route("/hello")
def hello():
    return jsonify({"message": "Hello from Excel Backend!"})

# Endpoint pour déclencher un appel avec Twilio
@app.route("/call", methods=["POST"])
def make_call():
    data = request.get_json()

    to_number = data.get("to")
    message = data.get("message", "Hello! This is an automated call.")

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_number = os.getenv("TWILIO_PHONE_NUMBER")

    if not all([account_sid, auth_token, twilio_number]):
        return jsonify({"error": "Missing Twilio credentials"}), 500

    try:
        client = Client(account_sid, auth_token)

        call = client.calls.create(
            twiml=f'<Response><Say>{message}</Say></Response>',
            to=to_number,
            from_=twilio_number
        )

        return jsonify({"status": "Call initiated", "sid": call.sid})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/")
def index():
    return "Backend is alive!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
