from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS   # 👈 nuevo
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# 👇 Ajusta los orígenes a los que realmente usarás:
# - En local (Vite): http://localhost:5173
# - En producción (tu dominio de Render del frontend): https://tu-frontend.onrender.com
CORS(app, resources={
    r"/chat": {
        "origins": [
            "http://localhost:5173",
            "https://proy2-chatbot-legal-frontend.onrender.com"
        ]
    }
})

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

@app.route('/chat', methods=['POST', 'OPTIONS'])  # 👈 OPTIONS para preflight
def chat():
    if request.method == 'OPTIONS':
        return ('', 204)

    data = request.json or {}
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
    # En Render se usa gunicorn, pero para local está bien:
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
