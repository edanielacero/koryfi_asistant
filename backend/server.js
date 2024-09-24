const express = require('express');
const cors = require('cors');
const { spawn } = require('child_process');

const app = express();
app.use(cors());
app.use(express.json());

app.post('/ask', (req, res) => {
  const question = req.body.question;

  // Ejecuta el modelo de Python
  const python = spawn('python3', ['./model.py', question]);

  python.stdout.on('data', (data) => {
    res.json({ answer: data.toString() });
  });

  python.stderr.on('data', (data) => {
    console.error(`Error: ${data}`);
    res.status(500).send('Error en el servidor');
  });
});

app.listen(3000, () => {
  console.log('Servidor corriendo en http://localhost:3000');
});
