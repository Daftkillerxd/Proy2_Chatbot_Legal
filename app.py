from flask import Flask, request, jsonify
from openai import OpenAI
from flask_cors import CORS
import os
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)

# CORS: deja /chat y añade /api/chat (sin la barra final en los origins)
CORS(app, resources={
    r"/chat": {
        "origins": [
            "http://localhost:5173",
            "https://proy2-chatbot-legal-frontend.onrender.com"
        ]
    },
    r"/api/chat": {   # 👇 nuevo
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

# 👇 helper reutilizable para /chat y /api/chat
def handle_chat():
    data = request.json or {}
    user_msg = data.get('message', '')

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_msg}
            ]
        )
        return jsonify({"respuesta": response.choices[0].message.content})
    except Exception as e:
        print("OpenAI error:", e)  # log útil
        return jsonify({"error": "openai_error", "detail": str(e)}), 500

# (opcional) ping para probar conectividad rápida
@app.route('/ping', methods=['GET'])
def ping():
    return jsonify({"ok": True})

@app.route('/chat', methods=['POST', 'OPTIONS'])
def chat():
    if request.method == 'OPTIONS':
        return ('', 204)
    return handle_chat()         # 👈 usa el helper

# 👇 alias para que el front que llama /api/chat funcione igual
@app.route('/api/chat', methods=['POST', 'OPTIONS'])
def chat_api():
    if request.method == 'OPTIONS':
        return ('', 204)
    return handle_chat()         # 👈 usa el mismo helper

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)), debug=True)
