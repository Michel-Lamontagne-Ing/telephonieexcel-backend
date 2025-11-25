from flask import Flask, request, jsonify

app = Flask(__name__)

# ---------------------------------------------------------
#  Endpoint de test : permet de vérifier que le backend vit
# ---------------------------------------------------------
@app.route("/health", methods=["GET"])
def health():
    """
    Simple vérification de santé.
    Utilisation :
        GET /health
    Réponse :
        {"status": "ok", "message": "Telephonie Excel backend is alive"}
    """
    return jsonify(status="ok", message="Telephonie Excel backend is alive")


# ---------------------------------------------------------
#  Endpoint pour démarrer un appel (stub pour l'instant)
#  Plus tard : intégration réelle avec l'API Twilio
# ---------------------------------------------------------
@app.route("/api/call/start", methods=["POST"])
def start_call():
    """
    Endpoint appelé par Excel (ou autre client) pour lancer un appel.

    Exemple de JSON envoyé par Excel :
    {
        "mode": "manual" ou "auto",
        "to": "+1XXXXXXXXXX",
        "message_tts": "Texte à lire"  (pour le mode auto)
    }
    """
    data = request.get_json(silent=True) or {}

    # Pour l'instant, on ne fait que renvoyer ce qu'on a reçu.
    # Plus tard, ici on :
    #   - validera les données
    #   - appellera Twilio pour lancer l'appel
    #   - enregistrera un log en base de données
    return jsonify(
        status="accepted",
        info="Stub start_call - Twilio integration to be added",
        received=data,
    ), 200


# ---------------------------------------------------------
#  Endpoint TwiML : contrôle ce que Twilio doit faire
#  quand l'appel est connecté (message automatique, etc.)
# ---------------------------------------------------------
@app.route("/twiml/outbound", methods=["POST", "GET"])
def twiml_outbound():
    """
    Twilio viendra ici pour savoir quoi faire lors d'un appel sortant.

    Pour l'instant :
      - On lit un simple message de test.
    Plus tard :
      - On lira dynamiquement un texte reçu d'Excel
      - Ou on jouera un fichier audio pré-enregistré.
    """
    # Plus tard on pourra lire des paramètres (par ex. ?msg=...)
    # pour personnaliser le message.
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Joanna" language="fr-CA">
        Bonjour, ceci est un test du système Téléphonie Excel.
    </Say>
</Response>
"""
    return xml, 200, {"Content-Type": "application/xml"}


# ---------------------------------------------------------
#  Webhook de statut d'appel : Twilio nous dira ici
#  si l'appel a réussi, échoué, a été répondu, etc.
# ---------------------------------------------------------
@app.route("/webhook/call-status", methods=["POST"])
def call_status():
    """
    Twilio enverra ici des informations de statut sur l'appel.
    Exemples de champs :
      - CallSid
      - CallStatus (queued, ringing, in-progress, completed, busy, no-answer, failed)
      - To, From
      - Timestamp, etc.
    """
    payload = request.form.to_dict()
    # Pour le prototype : on affiche simplement dans les logs du serveur.
    print("Call status webhook:", payload)
    # Twilio n'attend qu'un 200 OK
    return ("", 200)


# ---------------------------------------------------------
#  Point d'entrée local (utile si tu lances ce script
#  sur ta machine un jour). Sur Render, on utilisera gunicorn.
# ---------------------------------------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
