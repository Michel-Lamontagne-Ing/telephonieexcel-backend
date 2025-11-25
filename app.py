from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return "Service Téléphonie Excel — Backend en ligne 🚀"

@app.route("/healthz")
def health():
    return jsonify({"status": "ok"}), 200

@app.route("/hello")
def hello():
    return "Bonjour mon ami, ton backend fonctionne !"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
