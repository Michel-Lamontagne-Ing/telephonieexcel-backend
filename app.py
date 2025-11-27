from flask import Flask, request, jsonify, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# -----------------------
# Page d'accueil
# -----------------------
@app.route("/")
def index():
    return jsonify({
        "service": "telephonieexcel-backend",
        "endpoints": [
            "/hello",
            "/twilio/check",
            "/twilio/call?to=+1XXXXXXXXXX"
        ]
    })

# -----------------------
# Test simple
# -----------------------
@app.route("/hello")
def hello():
    return jsonify({"message": "Hello from Excel Backend!"})


# ---------------------------------------------------
# TWILIO : Utilities
# ---------------------------------------------------
def get_twilio_client():
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise Exception("Twilio credentials missing")

    client = Client(account_sid, auth_token)
    return client, account_sid


# ---------------------------------------------------
# TWILIO : Vérification des identifiants
# ---------------------------------------------------
@app.route("/twilio/check")
def twilio_check():
    try:
        client, sid = get_twilio_client()
        return jsonify({
            "status": "ok",
            "account_sid": sid
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------------------------------------------------
# TWILIO : Réponse vocale (Twilio va appeler cette URL)
# ---------------------------------------------------
@app.route("/twilio/voice", methods=["POST"])
def twilio_voice():
    response = VoiceResponse()
    response.say("Bonjour, ceci est un appel de test depuis votre système Excel.", voice="alice")
    return Response(str(response), mimetype="text/xml")


# ---------------------------------------------------
# TWILIO : Effectuer un appel
# ---------------------------------------------------
@app.route("/twilio/call", methods=["GET"])
def twilio_call():
    to_number = request.args.get("to")

    if not to_number:
        return jsonify({"error": "Missing 'to' parameter"}), 400

    try:
        client, account_sid = get_twilio_client()
        from_number = os.getenv("TWILIO_FROM_NUMBER")

        if not from_number:
            return jsonify({"error": "Missing TWILIO_FROM_NUMBER"}), 500

        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url="https://telephonieexcel-backend.onrender.com/twilio/voice"
        )

        return jsonify({
            "status": "queued",
            "call_sid": call.sid,
            "to": to_number,
            "from": from_number
        })

    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500


# ---------------------------------------------------
# Démarrage local (Render utilise gunicorn)
# ---------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
