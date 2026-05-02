from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import psycopg2
import psycopg2.extras
import os

app = Flask(__name__)
app.secret_key = "securetask_cle_secrete_2024"
CORS(app)

DATABASE_URL = os.environ.get(
    'DATABASE_URL',
    'postgresql://postgres:Z9qa5U5_i?LPZ8cCfymp@db.rsobwoxyijaivbvzefaw.supabase.co:5432/postgres'
)

def get_db():
    return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)

# ── Pages HTML ──
@app.route('/')
def index():
    return send_from_directory('.', 'connexion.html')

@app.route('/<path:filename>')
def static_files(filename):
    return send_from_directory('.', filename)

# ── LOGIN ──
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        db.close()

        if user and user['mot_de_passe'] == data['password']:
            return jsonify({
                "success": True,
                "user": {
                    "id": user['id'],
                    "nom": user['nom'],
                    "email": user['email'],
                    "role": user['role']
                }
            })
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

# ── TÂCHES ──
@app.route('/api/taches', methods=['GET'])
def get_taches():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM taches ORDER BY created_at DESC")
        taches = cursor.fetchall()
        db.close()
        result = []
        for t in taches:
            t = dict(t)
            if t.get('echeance'):
                t['echeance'] = str(t['echeance'])
            result.append(t)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/taches', methods=['POST'])
def create_tache():
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO taches (titre, description, priorite, echeance, assigne_a, statut, labels)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            data['titre'],
            data.get('description', ''),
            data.get('priorite', 'Moyenne'),
            data.get('echeance'),
            data.get('assigne