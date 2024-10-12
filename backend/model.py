from flask import Flask, request, jsonify
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.metrics import accuracy_score
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
from sklearn.svm import SVC
from flask_cors import CORS


# Cargar archivo CSV
def cargar_datos(ruta_csv):
    datos = pd.read_csv(ruta_csv)
    return datos['pregunta'], datos['categoria'], datos['respuesta']

def limpiar_texto(texto):
    texto = texto.lower()  # Convertir a minúsculas
    texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar puntuación
    texto = texto.strip()  # Eliminar espacios en blanco adicionales
    return texto

# Entrenar Modelo usando SVC
def entrenar_modelo(preguntas, categorias, respuestas):
    preguntas = [limpiar_texto(pregunta) for pregunta in preguntas]
    stop_words = stopwords.words('spanish')
    modelo = make_pipeline(
        TfidfVectorizer(stop_words=stop_words),
        SVC(probability=True)  # SVM con probabilidad
    )
    modelo.fit(preguntas, respuestas)  # Entrenar con las preguntas procesadas
    return modelo

# Función para predecir respuesta
def predecir_respuesta(modelo, pregunta, umbral=0.1):  # Reducir el umbral
    pregunta = limpiar_texto(pregunta)  # Limpiar el texto de la pregunta
    proba = modelo.predict_proba([pregunta])
    mejor_prediccion = proba.max()
    enlace_ticket = "\n\nSi este mensaje no responde tu pregunta o deseas continuar hablando con un agente, puedes abrir un ticket de soporte en este siguiente enlace: https://clientes.koryfi.com/submitticket.php?step=2&deptid=1"
    
    if mejor_prediccion > umbral:
      respuesta = modelo.predict([pregunta])[0]
      return respuesta + " " + enlace_ticket
    else:
      return "No tengo la respuesta a esta pregunta, puedes intentar abrir un ticket aquí: https://clientes.koryfi.com/submitticket.php?step=2&deptid=1"
    
app = Flask(__name__)
CORS(app)

# Inicialización del modelo
modelo = None  # Declarar el modelo global

def inicializar_modelo():
    global modelo
    preguntas, categorias, respuestas = cargar_datos('./faq8.csv')
    modelo = entrenar_modelo(preguntas, categorias, respuestas)

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    pregunta = data.get('pregunta')
    respuesta = predecir_respuesta(modelo, pregunta)
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    inicializar_modelo()  # Inicializar el modelo antes de iniciar el servidor
    app.run(debug=True, port=5001)  # Servidor Flask corriendo en el puerto 5001