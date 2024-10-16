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
    return datos['pregunta'], datos['pregunta_normalizada'], datos['intención'], datos['categoria'], datos['respuesta']

def limpiar_texto(texto):
    texto = texto.lower()  # Convertir a minúsculas
    texto = re.sub(r'[^\w\s]', '', texto)  # Eliminar puntuación
    texto = texto.strip()  # Eliminar espacios en blanco adicionales
    return texto

# Entrenar Modelo usando SVC
def entrenar_modelo(preguntas_normalizadas, intenciones, categorias, respuestas):
    # Concatenamos las preguntas normalizadas con las categorías para incluir más contexto en el entrenamiento
    preguntas_con_categoria = [f"{pregunta} {categoria}" for pregunta, categoria in zip(preguntas_normalizadas, categorias)]
    stop_words = stopwords.words('spanish')
    # Creamos el pipeline con TfidfVectorizer y SVC
    modelo = make_pipeline(
        TfidfVectorizer(stop_words=stop_words),
        SVC(probability=True)  # SVM con probabilidad
    )
    # Entrenamos el modelo usando las preguntas con categoría y la intención como etiquetas
    modelo.fit(preguntas_con_categoria, intenciones)  # Entrenamos con preguntas y categorías
    return modelo

# Función para manejar saltos de línea en respuestas
def formatear_respuesta(texto):
    # Convertir saltos de línea "\n" en etiquetas <br> para mostrarlos en HTML
    return texto.replace('\n', '<br>')


# Función para detectar URLs en una cadena de texto y convertirlas en enlaces clickeables
def hacer_urls_clickeables(texto):
    # Expresión regular para detectar URLs
    url_regex = r'(https?://[^\s]+)'
    
    # Reemplazar cada URL por una etiqueta <a> HTML
    texto_con_enlaces = re.sub(url_regex, r'<a href="\1" target="_blank">\1</a>', texto)
    return texto_con_enlaces

# Función para predecir respuesta
def predecir_respuesta(modelo, pregunta, datos, umbral=0.05):  # Reducir el umbral
    pregunta_limpia = limpiar_texto(pregunta)  # Limpiar el texto de la pregunta
    proba = modelo.predict_proba([pregunta])
    mejor_prediccion = proba.max()

    enlace_ticket = '\n\nSi este mensaje no responde tu pregunta o deseas continuar hablando con un agente, puedes <a href="https://clientes.koryfi.com/submitticket.php?step=2&deptid=1" target="_blank">abrir un ticket de soporte</a>.'

    if mejor_prediccion > umbral:
        # Obtener la intención predicha y la respuesta correspondiente
        intencion_predicha = modelo.predict([pregunta])[0]
        respuesta = datos.loc[datos['intención'] == intencion_predicha, 'respuesta'].values[0]
        
        # Aplicar formateo de URLs y saltos de línea solo a la respuesta del CSV
        respuesta_formateada = formatear_respuesta(respuesta)
        enlace_ticket_formateado = formatear_respuesta(enlace_ticket)
        respuesta_con_enlaces = hacer_urls_clickeables(respuesta_formateada)
        
        # Concatenar la respuesta con el enlace del ticket
        return respuesta_con_enlaces + " " + enlace_ticket_formateado
    else:
        # Respuesta cuando no se encuentra una intención con suficiente confianza
        return 'No tengo la respuesta a esta pregunta, puedes intentar <a href="https://clientes.koryfi.com/submitticket.php?step=2&deptid=1" target="_blank">abrir un ticket aquí</a>.'


class Chatbot:
    def __init__(self, ruta_csv):
        # Cargar y procesar los datos
        self.preguntas, self.preguntas_normalizadas, self.intenciones, self.categorias, self.respuestas = cargar_datos(ruta_csv)
        # Entrenar el modelo
        self.modelo = entrenar_modelo(self.preguntas_normalizadas, self.intenciones, self.categorias, self.respuestas)
        # Guardar el CSV cargado para mapear las respuestas
        self.datos_csv = pd.read_csv(ruta_csv)
    
    def responder(self, pregunta):
        # Usar la función predecir_respuesta para obtener la respuesta
        respuesta = predecir_respuesta(self.modelo, pregunta, self.datos_csv)
        # Asegurarse de que los saltos de línea y URLs sean formateados correctamente
        #respuesta_formateada = formatear_respuesta(respuesta)
        #respuesta_con_enlaces = hacer_urls_clickeables(respuesta_formateada)
        #return respuesta_con_enlaces
        return respuesta


app = Flask(__name__)
CORS(app)

# Inicializar el chatbot globalmente
bot = Chatbot('./faq12.csv')

@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    # Recibir la pregunta en formato JSON desde el frontend
    data = request.get_json()
    pregunta = data.get('pregunta')
    
    if not pregunta:
        return jsonify({"respuesta": "Por favor, ingresa una pregunta válida."}), 400
    
    # Obtener la respuesta del chatbot
    respuesta = bot.responder(pregunta)
    
    # Enviar la respuesta de vuelta al frontend
    return jsonify({"respuesta": respuesta})

if __name__ == "__main__":
    app.run(debug=True, port=5001)  # Servidor Flask corriendo en el puerto 5001