 from flask import Flask, request, jsonify, Response
from twilio.twiml.voice_response import VoiceResponse
import os

app = Flask(__name__)

# Twilio routes added 

# --- Routes simples de test --------------------------------------------------

@app.route("/")
def index():
    """
    Petit résumé des endpoints disponibles.
    """
    return jsonify({
        "service": "telephonieexcel-backend",
        "endpoints": [
            "/hello",
            "/twilio/check",
            "/twilio/call?to=+1XXXXXXXXXX"
        ]
    })


@app.route("/hello")
def hello():
    """
    Test basique : confirme que le backend répond.
    """
    return jsonify({"message": "Hello from Excel Backend!"})


# --- Utilitaires Twilio ------------------------------------------------------

def get_twilio_client():
    """
    Lit les variables d'environnement et construit le client Twilio.
    Lève une exception explicite si quelque chose manque.
    """
    account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
    auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
    from_number = os.environ.get("TWILIO_FROM_NUMBER")

    if not account_sid or not auth_token or not from_number:
        raise RuntimeError(
            "Missing one of TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN / TWILIO_FROM_NUMBER"
        )

    client = Client(account_sid, auth_token)
    return client, from_number, account_sid


# --- Endpoints Twilio --------------------------------------------------------

@app.route("/twilio/check", methods=["GET"])
def twilio_check():
    """
    Vérifie simplement qu'on peut construire un client Twilio
    avec les variables d'environnement.
    """
    try:
        _, _, account_sid = get_twilio_client()
        return jsonify({
            "status": "ok",
            "account_sid": account_sid
        })
    except Exception as e:
        # On renvoie l'erreur dans la réponse pour le debug
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500


@app.route("/twilio/call", methods=["GET", "POST"])
def twilio_call():
    """
    Lance un appel sortant via Twilio.

    Paramètre :
      - to : numéro de destination (format E.164, ex: +15145551234)

    Exemple:
      https://telephonieexcel-backend.onrender.com/twilio/call?to=+15145551234
    """
    # Récupère le numéro cible soit en query string, soit dans le body (POST)
    to_number = request.args.get("to") or request.form.get("to")
    if not to_number:
        return jsonify({"error": "Missing 'to' parameter"}), 400

    try:
        client, from_number, _ = get_twilio_client()

        # Twilio utilisera cette URL pour la voix (TwiML)
        # On utilise une URL de démo fournie par Twilio
        twiml_url = "https://telephonieexcel-backend.onrender.com/twilio/voice"
        call = client.calls.create(
            to=to_number,
            from_=from_number,
            url=twiml_url
        )

        return jsonify({
            "status": "queued",
            "call_sid": call.sid,
            "to": to_number,
            "from": from_number
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e)
        }), 500

@app.route("/twilio/voice", methods=["POST"])
def twilio_voice():
    """TwiML renvoyé à Twilio pour l'appel vocal."""
    resp = VoiceResponse()
    resp.say(
        "Bonjour Michel. Ceci est un appel de test depuis l'application Excel et Twilio.",
        voice="alice",
        language="fr-CA"
    )
    resp.pause(length=1)
    resp.say(
        "Tout fonctionne correctement. Au revoir et à bientôt.",
        voice="alice",
        language="fr-CA"
    )
    return Response(str(resp), mimetype="text/xml")
    
# Point d'entrée pour gunicorn : "gunicorn app:app"
if __name__ == "__main__":
    # Utile uniquement si tu lances l'app en local
    app.run(host="0.0.0.0", port=5000, debug=True)
