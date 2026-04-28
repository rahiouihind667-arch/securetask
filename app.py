from flask import Flask, request, jsonify
from flask_cors import CORS
import pymysql
import pymysql.cursors
import bcrypt
import os

app = Flask(__name__)
app.secret_key = "securetask_cle_secrete_2024"
CORS(app)

@app.route('/')
def home():
    return jsonify({
        "message": "✅ SecureTask API fonctionne !",
        "version": "1.0",
        "endpoints": ["/api/login", "/api/taches", "/api/users"]
    })

def get_db():
    return pymysql.connect(
        host=os.environ.get('MYSQLHOST', 'localhost'),
        user=os.environ.get('MYSQLUSER', 'root'),
        password=os.environ.get('MYSQLPASSWORD', ''),
        database=os.environ.get('MYSQLDATABASE', 'securetask'),
        port=int(os.environ.get('MYSQLPORT', 3306)),
        cursorclass=pymysql.cursors.DictCursor,
        charset='utf8mb4'
    )

def init_db():
    try:
        db = get_db()
        cursor = db.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nom VARCHAR(100),
                email VARCHAR(100) UNIQUE,
                mot_de_passe VARCHAR(255),
                role VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS taches (
                id INT AUTO_INCREMENT PRIMARY KEY,
                titre VARCHAR(200),
                description TEXT,
                priorite VARCHAR(50),
                echeance DATE,
                assigne_a VARCHAR(100),
                statut VARCHAR(50),
                labels VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            INSERT IGNORE INTO users (nom, email, mot_de_passe, role) VALUES
            ('Karim Alaoui', 'test@securetask.ma', 'password123', 'Lead Sécurité'),
            ('Ahmad', 'ahmad@securetask.ma', 'password123', 'Ingénieur SSI'),
            ('Sara', 'sara@securetask.ma', 'password123', 'Ingénieur SSI'),
            ('Laila', 'laila@securetask.ma', 'password123', 'Observateur')
        """)

        db.commit()
        db.close()
        print("✅ Base de données initialisée !")
    except Exception as e:
        print(f"⚠️ Erreur DB: {e}")

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
        for t in taches:
            if t.get('echeance'):
                t['echeance'] = str(t['echeance'])
        return jsonify(taches)
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
            data.get('assigneA', 'Non assigné'),
            data.get('statut', 'À faire'),
            ', '.join(data.get('labels', []))
        ))
        db.commit()
        new_id = cursor.lastrowid
        db.close()
        return jsonify({"success": True, "id": new_id})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/taches/<int:id>', methods=['PUT'])
def update_tache(id):
    try:
        data = request.json
        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE taches SET statut = %s WHERE id = %s", (data['statut'], id))
        db.commit()
        db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/taches/<int:id>', methods=['DELETE'])
def delete_tache(id):
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM taches WHERE id = %s", (id,))
        db.commit()
        db.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

# ── USERS ──
@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("SELECT id, nom, email, role FROM users")
        users = cursor.fetchall()
        db.close()
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

init_db()

if __name__ == '__main__':
    print("✅ SecureTask API démarrée sur http://localhost:5000")
    app.run(debug=True, port=5000)