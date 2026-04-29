import os
from flask import send_file, Flask, render_template, request, jsonify, make_response

app = Flask(__name__)
os.environ["FLAG_SECRET_ADMIN"] = "FLG{Env_V4r_Is_B3tt3r_Th4n_F1l3}"
ADMIN_COOKIE = "ADMIN_SECRET_KEY_2026"
# -------------------------
# DOWNLOAD PCAP ROUTE
# -------------------------
@app.route('/admin/download/pcap')
def download_pcap():
    session_id = request.cookies.get('session_id')
    # On protège le téléchargement : seul l'admin y a accès
    if session_id != ADMIN_COOKIE:
        return "Accès Refusé", 403
    
    # Vérifie si le fichier généré par ton script existe bien
    if os.path.exists('capture.pcap'):
        return send_file('capture.pcap', as_attachment=True)
    return "Fichier introuvable", 404
# -------------------------
# DATABASE
# -------------------------
db = {
    "messages": [],
    "dns_logs": [],
    "logs": []
}




# -------------------------
# ROUTES
# -------------------------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.json
    db["messages"].append(data)
    
    print(f"[CONTACT] Received message from {data.get('name')}")
    print("[CONTACT] Bot will pick this up on next refresh cycle")

    return jsonify({"message": "Admin va vérifier..."})

# -------------------------
# DNS EXFIL SIMULATION
# -------------------------
@app.route('/exfil/<data>')
def exfil(data):
    db["dns_logs"].append(data)
    print("[DNS EXFIL]:", data)
    return "OK"

@app.route('/dns')
def dns_logs():
    output = ""
    for log in db["dns_logs"]:
        output += f"[DNS] {log}\n"
    return f"<pre>{output}</pre>"

# -------------------------
# ADMIN PANEL
# -------------------------
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    session_id = request.cookies.get('session_id')

    if session_id != ADMIN_COOKIE:
        return render_template("admin.html", access_denied=True), 403

    active_tab = request.args.get('tab', 'dashboard')
    result = ""



    if request.method == 'POST':
        active_tab = 'maintenance'
        pin = request.form.get('pin')
        target = request.form.get('host')

        if pin != "8492":
            result = "[ERREUR] Code PIN de maintenance invalide."
        else:
            # --- MODIFICATION DU FILTRAGE POUR WINDOWS ---
            # On interdit l'espace (' '), le point-virgule (';') et le pipe ('|')
            # Mais on laisse '&' (esperluette) pour permettre l'enchaînement
            forbidden = [';', '|', ' ', '>', '<', '`', '$', '(', ')']
            
            if any(char in target for char in forbidden):
                result = "⚠️ Sécurité  : Caractère interdit détecté."
            else:
                try:
                    # Syntaxe Windows pour le ping
                    param = "-c" 
                    
                    # L'injection se fera via & (ex: 127.0.0.1&set)
                    command = f"ping {param} 1 {target}"
                    result = os.popen(command).read()

                except Exception as e:
                    result = str(e)

    return render_template("admin.html",
                           access_denied=False,
                           active_tab=active_tab,
                           result=result,
                           messages=db["messages"],
                           dns_logs=db["dns_logs"],
                           logs=db["logs"])
# -------------------------
# ADMIN MESSAGES (XSS)
# -------------------------

@app.route('/admin/messages')
def messages():
    print(f"DEBUG RECV: {request.cookies.get('session_id')}")
    if request.cookies.get('session_id') != ADMIN_COOKIE:
        return "Accès Refusé", 403
    else:   
        html = "<h2>Admin Console</h2>"
        for m in db["messages"]:
            html += f"<div>{m.get('name')} : {m.get('message')}</div>"

        resp = make_response(html)
        resp.set_cookie("session_id", ADMIN_COOKIE)

        return resp

# -------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)