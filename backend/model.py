import sys

def load_model():
    # Aquí carga tu modelo o base de datos de preguntas
    return {
        "¿Cuál es tu horario?": "Nuestro horario es de 9am a 6pm.",
        "¿Dónde están ubicados?": "Estamos ubicados en Madrid, España.",
        "hola": "hola Dani"
    }

def main(question):
    model = load_model()
    answer = model.get(question, "Lo siento, no tengo la respuesta a esa pregunta.")
    print(answer)

if __name__ == '__main__':
    question = sys.argv[1]
    main(question)
