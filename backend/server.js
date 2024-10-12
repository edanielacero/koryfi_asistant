const express = require('express');
const cors = require('cors');
//const { spawn } = require('child_process');
const app = express();
const port = 3000;
const axios = require('axios');

app.use(cors());
app.use(express.json());

// Ruta para manejar las preguntas del chatbot
app.post('/api/chatbot', async (req, res) => {
  const { pregunta } = req.body;

  try {
    // Realiza la petición al servidor Flask en el puerto 5001
    const response = await axios.post('http://localhost:5001/api/chatbot', { pregunta });
    const respuestaChatbot = response.data.respuesta;

    res.json({ respuesta: respuestaChatbot });
  } catch (error) {
    console.error('Error al conectar con el chatbot:', error);
    res.status(500).json({ mensaje: 'Error al conectar con el chatbot.' });
  }
});

app.listen(port, () => {
  console.log(`Servidor Node.js corriendo en el puerto ${port}`);
});