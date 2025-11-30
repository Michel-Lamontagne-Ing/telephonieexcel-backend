from flask import Flask, request, jsonify, Response
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
##################################################################################
from twilio.twiml.messaging_response import MessagingResponse
##################################################################################
import os

app = Flask(__name__)

# ---------------------------------------------------------------------
# Utilitaires Twilio
# ---------------------------------------------------------------------

def get_twilio_client():
    """
    Crée un client Twilio à partir des variables d'environnement.
    Nécessite :
      - TWILIO_ACCOUNT_SID
      - TWILIO_AUTH_TOKEN
    """
    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")

    if not account_sid or not auth_token:
        raise RuntimeError("Variables TWILIO_ACCOUNT_SID ou TWILIO_AUTH_TOKEN manquantes.")

    return Client(account_sid, auth_token)


def get_twilio_from_number():
    """
    Récupère le numéro Twilio (celui de ton compte) à utiliser comme 'from'.
    Nécessite TWILIO_FROM_NUMBER dans l'environnement.
    """
    from_number = os.getenv("TWILIO_FROM_NUMBER")
    if not from_number:
        raise RuntimeError("Variable TWILIO_FROM_NUMBER manquante.")
    return from_number


# ---------------------------------------------------------------------
# Routes simples de test
# ---------------------------------------------------------------------

@app.route("/")
def index():
    """
    Petit résumé des endpoints disponibles.
    Utile pour vérifier que l'app tourne.
    """
    return jsonify({
        "service": "telephonieexcel-backend",
        "endpoints": [
            "/hello",
            "/twilio/check",
            "/twilio/call?to=+1XXXXXXXXXX",
            "/twilio/voice (appelé par Twilio)"
        ]
    })


@app.route("/hello")
def hello():
    """
    Test basique : confirme que le backend répond.
    """
    return jsonify({"message": "Hello from Excel Backend!"})


# ---------------------------------------------------------------------
# Vérification Twilio : /twilio/check
# ---------------------------------------------------------------------

@app.route("/twilio/check", methods=["GET"])
def twilio_check():
    """
    Vérifie que le client Twilio peut être créé correctement.
    Ne fait pas d'appel, mais retourne l'account_sid si tout va bien.
    """
    try:
        client = get_twilio_client()
        # Juste pour vérifier que la connexion est valide :
        account_sid = client.username  # ou client.account_sid
        return jsonify({"account_sid": account_sid, "status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


# ---------------------------------------------------------------------
# Lancer un appel Twilio : /twilio/call
# ---------------------------------------------------------------------
# Exemple d'appel :
#   https://telephonieexcel-backend.onrender.com/twilio/call?to=+14185207138
#
# Twilio appellera ensuite /twilio/voice pour savoir quoi dire.
# ---------------------------------------------------------------------

@app.route("/twilio/call", methods=["POST", "GET"])
def twilio_call():
    """
    Lance un appel via Twilio vers le numéro 'to'.
    - 'to' peut venir de la query string (?to=...) ou du body JSON.
    """
    # Récupère le paramètre 'to'
    to_number = request.args.get("to") or (
        request.json.get("to") if request.is_json else None
    )

    if not to_number:
        return jsonify({"error": "Missing 'to' parameter"}), 400

    try:
        client = get_twilio_client()
        from_number = get_twilio_from_number()

        # URL de TwiML que Twilio utilisera pour savoir quoi dire
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
        return jsonify({"status": "error", "error": str(e)}), 500

################################################################################
@app.route("/twilio/sms", methods=["POST"])
def twilio_sms():
    from_number = request.form.get("From")
    body = request.form.get("Body", "")

    # Ici tu pourras plus tard enregistrer le SMS en base ou dans Excel
    print(f"SMS reçu de {from_number}: {body}")

    resp = MessagingResponse()
    resp.message("Merci pour votre message ! Nous vous contacterons bientôt.")
    return Response(str(resp), mimetype="text/xml")

################################################################################

# ---------------------------------------------------------------------
# Réponse vocale Twilio : /twilio/voice
# ---------------------------------------------------------------------
# C'est cette route que Twilio appelle pendant l'appel pour savoir
# quoi dire à la personne.
# ---------------------------------------------------------------------

@app.route("/twilio/voice", methods=["GET", "POST"])
def twilio_voice():
    """Réponse vocale envoyée à Twilio pendant l'appel."""
    response = VoiceResponse()

    # Ton message en français
    response.say(
        "Bonjour, ceci est un appel de test effectué depuis votre application Excel. "
        "Passez une excellente journée !",
        voice="alice",
        language="fr-FR"
    )

    return Response(str(response), mimetype="text/xml")


# ---------------------------------------------------------------------
# Point d'entrée local (utile si tu veux tester en local avec 'python app.py')
# Sur Render, c'est gunicorn qui utilisera 'app' directement.
# ---------------------------------------------------------------------

if __name__ == "__main__":
    # Pour exécuter en local : python app.py
    app.run(host="0.0.0.0", port=5000, debug=True)
