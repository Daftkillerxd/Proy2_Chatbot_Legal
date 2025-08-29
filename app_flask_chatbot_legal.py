from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

system_prompt = """Eres un asistente jurídico informativo para Perú.
- Explica en español claro.
- Cita normas con artículo y nombre (ej.: Constitución, art. 2).
- Advierte siempre: "no es asesoria legal, es una orientación".
- Si el usuario pide aperturar o reabrir carpeta fiscal, guía con pasos y requisitos según el CPP y lineamientos del MP, sin inventar artículos.

Restricciones:
- Solamente vas a responder sobre temas de derechos civiles, en materia de herencia intestada.
- En caso recibas una pregunta de otro tema, responde: "no che".

Salida:
- Tu respuesta debe ser breve, tipo conversación de chat.
- Todas tus respuestas deben estar basadas en la Constitución.
- Importante: indica el número de artículo o código de donde sale la respuesta según la Constitución y, luego, añade tu conocimiento adicional.
"""

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_msg = data.get('message', '')

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_msg}
        ]
    )

    return jsonify({"respuesta": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True)
