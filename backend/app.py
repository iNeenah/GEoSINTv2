# /backend/app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io
import json

# Carga la clave API desde el archivo .env
load_dotenv()

app = Flask(__name__)
# CORS permite que tu frontend (ej. localhost:5173) se comunique con este backend (ej. localhost:5001)
CORS(app) 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("No se encontró la GEMINI_API_KEY. Asegúrate de tener tu archivo .env")

# Configurar la API de Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")
print("API:") 
print(GEMINI_API_KEY) 

@app.route("/",methods=["GET"])
def mauri():
    return "hola"
    
@app.route("/api/analyze", methods=["POST"])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({"error": "No se adjuntó archivo de imagen"}), 400

    image_file = request.files['image']
    
    try:
        # Guardamos temporalmente la imagen
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Este es el "prompt" o instrucción que le damos a la IA
        prompt_text = "Analyze this image for its geographical location. Identify the country, city/region, and provide specific coordinates if possible. Also, describe any distinctive architectural styles, landmarks, or vegetation. Present the result as a single, minified JSON object with keys: 'country', 'region_or_city', 'coordinates', 'confidence', 'reasoning'."
        
        # Usamos la API de Google Generative AI directamente
        response = model.generate_content([prompt_text, image])
        
        # Extraemos el texto de la respuesta
        response_text = response.text
        
        # Limpiamos y convertimos el string a un objeto JSON real
        clean_json_text = response_text.strip().replace("```json", "").replace("```", "")
        
        try:
            json_data = json.loads(clean_json_text)
            return jsonify(json_data)
        except json.JSONDecodeError:
            # Si no es JSON válido, devolvemos el texto tal como está
            return jsonify({
                "country": "No determinado",
                "region_or_city": "No determinado", 
                "coordinates": "No disponibles",
                "confidence": "Baja",
                "reasoning": response_text
            })

    except Exception as e:
        return jsonify({"error": f"Error en el análisis: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)