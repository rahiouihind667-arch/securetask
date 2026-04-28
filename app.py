from flask import Flask, request, jsonify, session
from flask_mysqldb import MySQL
from flask_cors import CORS
import bcrypt

app = Flask(__name__)
app.secret_key = "securetask_cle_secrete_2024"
CORS(app)

# ── Connexion MySQL ──
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'securetask'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

# ════════════════════════════
#  AUTH
# ════════════════════════════

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if user and user['mot_de_passe'] == password:
        return jsonify({
            "success": True,
            "user": {
                "id": user['id'],
                "nom": user['nom'],
                "email": user['email'],
                "role": user['role']
            }
        })
    else:
        return jsonify({
            "success": False,
            "message": "Email ou mot de passe incorrect"
        }), 401

# ════════════════════════════
#  TÂCHES
# ════════════════════════════

@app.route('/api/taches', methods=['GET'])
def get_taches():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM taches ORDER BY created_at DESC")
    taches = cursor.fetchall()
    return jsonify(taches)

@app.route('/api/taches', methods=['POST'])
def create_tache():
    data = request.json
    cursor = mysql.connection.cursor()
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
    mysql.connection.commit()
    return jsonify({"success": True, "id": cursor.lastrowid})

@app.route('/api/taches/<int:id>', methods=['PUT'])
def update_tache(id):
    data = request.json
    cursor = mysql.connection.cursor()
    cursor.execute("""
        UPDATE taches SET statut = %s WHERE id = %s
    """, (data['statut'], id))
    mysql.connection.commit()
    return jsonify({"success": True})

@app.route('/api/taches/<int:id>', methods=['DELETE'])
def delete_tache(id):
    cursor = mysql.connection.cursor()
    cursor.execute("DELETE FROM taches WHERE id = %s", (id,))
    mysql.connection.commit()
    return jsonify({"success": True})

# ════════════════════════════
#  UTILISATEURS
# ════════════════════════════

@app.route('/api/users', methods=['GET'])
def get_users():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT id, nom, email, role FROM users")
    users = cursor.fetchall()
    return jsonify(users)

# ── Créer les tables automatiquement ──
def init_db():
    with app.app_context():
        try:
            cursor = mysql.connection.cursor()
            
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
            
            mysql.connection.commit()
            print("✅ Base de données initialisée !")
            
        except Exception as e:
            print(f"⚠️ Erreur DB: {e}")

init_db()
# ════════════════════════════
#  LANCEMENT
# ════════════════════════════

if __name__ == '__main__':
    print("✅ SecureTask API démarrée sur http://localhost:5000")
    # Railway donne le port via la variable d'environnement PORT
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

# ── Configuration base de données ──
# En local → utilise XAMPP
# En ligne → utilise les variables Railway

import os

app.config['MYSQL_HOST'] = os.environ.get('MYSQLHOST', 'localhost')
app.config['MYSQL_USER'] = os.environ.get('MYSQLUSER', 'root')
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQLPASSWORD', '')
app.config['MYSQL_DB'] = os.environ.get('MYSQLDATABASE', 'securetask')
app.config['MYSQL_PORT'] = int(os.environ.get('MYSQLPORT', 3306))
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'