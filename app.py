import os
from flask import Flask, request, jsonify
from twilio.rest import Client

app = Flask(__name__)

# --- Configuration Twilio depuis les variables d'environnement ---
TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.environ.get("TWILIO_NUMBER")  # ton numéro Twilio (ex: +15145551234)
BASE_URL = os.environ.get("BASE_URL", "https://telephonieexcel-backend.onrender.com")

twilio_client = None
if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN:
    twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


# --- Routes de base ---

@app.route("/")
def index():
    return "Backend TelephonieExcel – en ligne", 200


@app.route("/healthz")
def healthz():
    return jsonify({"status": "ok"}), 200


# --- Lancer un appel Twilio depuis Excel ou autre ---

@app.route("/api/call", methods=["POST"])
def api_call():
    """
    JSON attendu:
    {
      "to": "+1XXXXXXXXXX",
      "message": "Texte du message à lire"
    }
    """
    if not twilio_client:
        return jsonify({"error": "Twilio n'est pas configuré (variables d'environnement manquantes)."}), 500

    data = request.get_json(silent=True) or {}
    to = data.get("to")
    message = data.get("message", "")

    if not to:
        return jsonify({"error": "Champ 'to' (numéro à appeler) manquant."}), 400
    if not message:
        return jsonify({"error": "Champ 'message' vide."}), 400

    # TwiML pour lire le message (voix anglaise par défaut, on pourra choisir autre chose ensuite)
    # Tu peux changer la langue/voix plus tard.
    from xml.sax.saxutils import escape
    safe_message = escape(message)

    twiml = f"""
    <Response>
        <Say language="fr-CA" voice="Polly.Joanna">
            {safe_message}
        </Say>
    </Response>
    """

    try:
        call = twilio_client.calls.create(
            to=to,
            from_=TWILIO_NUMBER,
            twiml=twiml,
            status_callback=f"{BASE_URL}/twilio/status",
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            status_callback_method="POST",
        )
        return jsonify({
            "status": "queued",
            "call_sid": call.sid
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# --- Réception des statuts d'appel Twilio ---

@app.route("/twilio/status", methods=["POST"])
def twilio_status():
    """
    Twilio enverra ici les statuts de l'appel.
    Pour l'instant, on logge simplement les infos.
    """
    data = request.form.to_dict()
    print("== Statut d'appel Twilio ==")
    for k, v in data.items():
        print(f"{k}: {v}")
    print("== Fin statut ==")

    # Twilio s'attend juste à un 200 OK
    return ("", 200)


if __name__ == "__main__":
    # Pour un lancement local éventuel
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

