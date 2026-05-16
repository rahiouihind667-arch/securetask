const express = require('express');
const path = require('path');
const app = express();

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'public', 'connexion.html'));
});

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
    console.log(`SecureTask démarré sur le port ${PORT}`);
});