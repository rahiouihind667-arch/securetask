const { neon } = require('@neondatabase/serverless');

const sql = neon(process.env.DATABASE_URL);

async function initDB() {
    await sql`
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            nom TEXT,
            email TEXT UNIQUE,
            mot_de_passe TEXT,
            role TEXT
        )
    `;
    await sql`
        CREATE TABLE IF NOT EXISTS taches (
            id SERIAL PRIMARY KEY,
            titre TEXT,
            description TEXT,
            priorite TEXT,
            echeance TEXT,
            assigne_a TEXT,
            statut TEXT,
            labels TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `;
    const count = await sql`SELECT COUNT(*) as c FROM users`;
    if (count[0].c == 0) {
        await sql`INSERT INTO users (nom, email, mot_de_passe, role) VALUES ('Hind Rahioui', 'hind_rahioui@securetask.ma', 'password123', 'Lead Securite')`;
        await sql`INSERT INTO users (nom, email, mot_de_passe, role) VALUES ('Hajar Fadil', 'hajar_fadil@securetask.ma', 'password123', 'Ingenieur SSI')`;
        await sql`INSERT INTO users (nom, email, mot_de_passe, role) VALUES ('Sara Jalal', 'sara_jalal@securetask.ma', 'password123', 'Ingenieur SSI')`;
        await sql`INSERT INTO users (nom, email, mot_de_passe, role) VALUES ('Laila Filali', 'laila_filali@securetask.ma', 'password123', 'Observateur')`;
    }
}

module.exports = async (req, res) => {
    res.setHeader('Access-Control-Allow-Origin', '*');
    res.setHeader('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
    if (req.method === 'OPTIONS') return res.status(200).end();

    await initDB();

    const url = req.url;
    const method = req.method;

    try {
        // LOGIN
        if (url.includes('/login') && method === 'POST') {
            const { email, password } = req.body;
            const users = await sql`SELECT * FROM users WHERE email = ${email}`;
            const user = users[0];
            if (user && user.mot_de_passe === password) {
                return res.json({ success: true, user: { id: user.id, nom: user.nom, email: user.email, role: user.role } });
            }
            return res.status(401).json({ success: false, message: 'Email ou mot de passe incorrect' });
        }

        // GET TACHES
        if (url.includes('/taches') && method === 'GET' && !url.match(/\/taches\/\d+/)) {
            const taches = await sql`SELECT * FROM taches ORDER BY created_at DESC`;
            return res.json(taches);
        }

        // CREATE TACHE
        if (url.includes('/taches') && method === 'POST') {
            const { titre, description, priorite, echeance, assigneA, statut, labels } = req.body;
            await sql`
                INSERT INTO taches (titre, description, priorite, echeance, assigne_a, statut, labels)
                VALUES (${titre}, ${description || ''}, ${priorite || 'Moyenne'}, ${echeance || ''}, ${assigneA || 'Non assigne'}, ${statut || 'A faire'}, ${(labels || []).join(', ')})
            `;
            return res.json({ success: true });
        }

        // UPDATE TACHE
        if (url.match(/\/taches\/\d+/) && method === 'PUT') {
            const id = url.split('/').pop();
            await sql`UPDATE taches SET statut = ${req.body.statut} WHERE id = ${id}`;
            return res.json({ success: true });
        }

        // DELETE TACHE
        if (url.match(/\/taches\/\d+/) && method === 'DELETE') {
            const id = url.split('/').pop();
            await sql`DELETE FROM taches WHERE id = ${id}`;
            return res.json({ success: true });
        }

        // GET USERS
        if (url.includes('/users') && method === 'GET') {
            const users = await sql`SELECT id, nom, email, role FROM users`;
            return res.json(users);
        }

        return res.status(404).json({ error: 'Route non trouvee' });

    } catch (error) {
        return res.status(500).json({ error: error.message });
    }
};