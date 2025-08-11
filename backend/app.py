# /backend/app.py

import os
import google.generativeai as genai
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io
import json
import re

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

def parse_osint_response(response_text):
    """
    Parsea la respuesta estructurada del análisis OSINT forense
    """
    try:
        # Extraer información básica
        country_match = re.search(r'Country:\s*(.+)', response_text)
        city_match = re.search(r'City/Region:\s*(.+)', response_text)
        confidence_match = re.search(r'Confidence Level:\s*(.+)', response_text)
        
        # Extraer coordenadas primarias
        primary_coords_match = re.search(r'Primary Location:\s*([-\d.]+),\s*([-\d.]+)', response_text)
        
        # Extraer coordenadas alternativas
        alt1_coords_match = re.search(r'Alternative Location 1:\s*([-\d.]+),\s*([-\d.]+)', response_text)
        alt2_coords_match = re.search(r'Alternative Location 2:\s*([-\d.]+),\s*([-\d.]+)', response_text)
        
        # Extraer evidencia clave
        signage_match = re.search(r'Signage:\s*(.+)', response_text)
        infrastructure_match = re.search(r'Infrastructure:\s*(.+)', response_text)
        architecture_match = re.search(r'Architecture:\s*(.+)', response_text)
        environment_match = re.search(r'Environment:\s*(.+)', response_text)
        cultural_match = re.search(r'Cultural Elements:\s*(.+)', response_text)
        
        # Extraer evaluación final
        location_match = re.search(r'Most Probable Location:\s*(.+)', response_text)
        certainty_match = re.search(r'Certainty Level:\s*(\d+)%', response_text)
        landmark_match = re.search(r'Primary Landmark:\s*(.+)', response_text)
        
        # Construir objeto de respuesta estructurado
        parsed_data = {
            "country": country_match.group(1).strip() if country_match else "Unknown",
            "region_or_city": city_match.group(1).strip() if city_match else "Unknown",
            "confidence": confidence_match.group(1).strip() if confidence_match else "Medium",
            "coordinates": f"{primary_coords_match.group(1)}, {primary_coords_match.group(2)}" if primary_coords_match else "N/A",
            "reasoning": response_text,
            "detailed_analysis": {
                "primary_coordinates": {
                    "lat": float(primary_coords_match.group(1)) if primary_coords_match else None,
                    "lng": float(primary_coords_match.group(2)) if primary_coords_match else None
                },
                "alternative_locations": [
                    {
                        "lat": float(alt1_coords_match.group(1)) if alt1_coords_match else None,
                        "lng": float(alt1_coords_match.group(2)) if alt1_coords_match else None
                    },
                    {
                        "lat": float(alt2_coords_match.group(1)) if alt2_coords_match else None,
                        "lng": float(alt2_coords_match.group(2)) if alt2_coords_match else None
                    }
                ],
                "evidence": {
                    "signage": signage_match.group(1).strip() if signage_match else "Not specified",
                    "infrastructure": infrastructure_match.group(1).strip() if infrastructure_match else "Not specified",
                    "architecture": architecture_match.group(1).strip() if architecture_match else "Not specified",
                    "environment": environment_match.group(1).strip() if environment_match else "Not specified",
                    "cultural_elements": cultural_match.group(1).strip() if cultural_match else "Not specified"
                },
                "final_assessment": {
                    "most_probable_location": location_match.group(1).strip() if location_match else "Not specified",
                    "certainty_percentage": int(certainty_match.group(1)) if certainty_match else 50,
                    "primary_landmark": landmark_match.group(1).strip() if landmark_match else "Not specified"
                }
            }
        }
        
        return parsed_data
        
    except Exception as e:
        # Si falla el parsing, devolver estructura básica con el texto completo
        return {
            "country": "Parsing Error",
            "region_or_city": "Could not extract location",
            "coordinates": "N/A",
            "confidence": "Low",
            "reasoning": response_text,
            "error": f"Parsing failed: {str(e)}"
        }

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
        
        # Prompt profesional de análisis forense OSINT
        prompt_text = """Eres un analista forense de geolocalización OSINT de élite mundial especializado en análisis 360° de ubicaciones. Tu misión es identificar la ubicación EXACTA con precisión militar.

ESPECIALIZACIÓN EN ANÁLISIS 360°:
Cuando analices múltiples imágenes de la misma ubicación, considera que pueden ser:
- Diferentes ángulos del mismo punto
- Vista panorámica completa (360°)
- Diferentes momentos del día
- Diferentes alturas/perspectivas

ENTRENAMIENTO AVANZADO OSINT
Eres una IA de geolocalización forense de nivel militar, entrenada en:
- Análisis geoespacial profesional
- Técnicas OSINT avanzadas  
- Reconocimiento de patrones globales
- Triangulación de coordenadas precisas

Tu misión: Identificar la ubicación EXACTA de cualquier imagen con precisión de metros, no kilómetros.

PROTOCOLO DE ANÁLISIS FORENSE EXHAUSTIVO

NIVEL 1: SEÑALIZACIÓN CRÍTICA (PRIORIDAD MÁXIMA)
- Señales de tráfico: Forma (circular/octagonal/triangular/rectangular)
- Colores oficiales: Rojo, azul, amarillo, verde según estándares nacionales
- Tipografía: Fuente específica por país (DIN, Highway Gothic, etc.)
- Idioma y caracteres: Latino, cirílico, árabe, chino, japonés, coreano
- Códigos de carretera: Numeración de autopistas y rutas
- Señales de límite de velocidad: km/h vs mph
- Direcciones y nombres de calles visibles

NIVEL 2: INFRAESTRUCTURA ÚNICA POR PAÍS
- Postes eléctricos: Madera (EE.UU./Canadá), concreto (Europa), metal (Asia)
- Aisladores: Forma de campana, disco, polímero según región
- Cables: Configuración, altura, tipo de soporte
- Pavimento: Asfalto negro (América), concreto gris (Europa), adoquines (Europa histórica)
- Líneas viales: Blancas (mayoría), amarillas (EE.UU.), azules (algunos países)
- Guardarraíles: Diseño W-beam (EE.UU.), barreras de concreto (Europa)
- Alcantarillas y drenajes: Diseño específico por país

NIVEL 3: VEHÍCULOS Y TRANSPORTE
- Matrículas: Color, formato, posición (frontal/trasera)
- Modelos de vehículos: Predominancia por región (Toyota en Asia, VW en Europa)
- Lado de conducción: Izquierda (Reino Unido, Japón, Australia) vs derecha
- Vehículos comerciales: Diseño de camiones, autobuses, taxis
- Bicicletas: Tipo holandés, mountain bike, scooters eléctricos
- Vehículos de emergencia: Colores y diseños específicos por país

NIVEL 4: BIOGEOGRAFÍA Y CLIMA
- Flora específica: Palmeras (tropical), coníferas (boreal), eucaliptos (Australia)
- Especies endémicas: Baobabs (África), cactus saguaro (Arizona), bambú (Asia)
- Estacionalidad: Hojas verdes/amarillas/sin hojas según hemisferio
- Topografía: Montañas, colinas, llanuras, costas, desiertos
- Suelo: Color rojizo (Australia/África), negro volcánico (Islandia), arenoso (desiertos)
- Cuerpos de agua: Océanos, lagos, ríos, fiordos, características únicas

NIVEL 5: ARQUITECTURA REGIONAL
- Estilos de techos: A dos aguas (Europa/América), planos (Mediterráneo), pagoda (Asia)
- Materiales: Ladrillo rojo (Reino Unido), madera (Escandinavia), adobe (México)
- Ventanas: Guillotina (EE.UU.), basculantes (Europa), persianas (Mediterráneo)
- Colores: Casas coloridas (Caribe), blancas (Grecia), rojas (Suecia)
- Elementos religiosos: Cruces (cristiano), mezquitas (islámico), templos (budista)
- Mobiliario urbano: Bancos, papeleras, paradas de bus específicos por país

NIVEL 6: ELEMENTOS CULTURALES ÚNICOS
- Banderas nacionales o regionales visibles
- Símbolos patrios en edificios públicos
- Uniformes escolares característicos
- Vestimenta tradicional o moderna típica
- Actividades comerciales: Mercados, puestos callejeros
- Deportes: Canchas de fútbol, basketball, cricket según región
- Grafitis y arte urbano con características locales

NIVEL 7: MICRODETALLES FORENSES
- Buzones: Forma, color, diseño específico por servicio postal nacional
- Contenedores de basura: Colores del sistema de reciclaje local
- Luminarias: Diseño de farolas y semáforos
- Numeración: Sistema de direcciones (123 Main St vs Calle Principal 123)
- Moneda visible: Billetes, monedas en carteles de precios
- Códigos QR: Presencia indica países con alta adopción tecnológica
- Enchufes y cables: Estándares eléctricos visibles en exteriores

REGLAS DE ANÁLISIS FORENSE

MENTALIDAD DE EXPERTO:
- Actúa como un detective geoespacial con 20 años de experiencia
- Cada detalle es una pista potencial - no ignores nada
- Usa lógica deductiva: elimina imposibilidades, quédate con lo probable
- Triangula información: combina múltiples pistas para mayor precisión

PROHIBIDO ABSOLUTO:
- NUNCA digas "no lo sé" o "no tengo información suficiente"
- NUNCA des ubicaciones genéricas como "Europa" o "Asia"
- NUNCA omitas las 3 coordenadas obligatorias
- NUNCA uses menos de 6 decimales en coordenadas

OBLIGATORIO:
- SIEMPRE proporciona país y ciudad específicos
- SIEMPRE da 3 ubicaciones candidatas con coordenadas exactas
- SIEMPRE justifica cada coordenada con evidencia visual
- SIEMPRE usa el formato exacto especificado

PROCESO MENTAL:
1. Escanea la imagen sistemáticamente (izquierda a derecha, arriba a abajo)
2. Identifica el elemento más distintivo regionalmente
3. Elimina países/regiones incompatibles con la evidencia
4. Reduce progresivamente el área geográfica posible
5. Triangula la posición exacta usando landmarks visibles

RESPONSE FORMAT (ALWAYS IN ENGLISH):

LOCATION ANALYSIS:
Country: [Country name only]
City/Region: [Specific city or region name]
Confidence Level: [High/Medium/Low]

COORDINATES:
Primary Location: [XX.XXXXXX, YY.YYYYYY]
Confidence: [High/Medium/Low] - [Brief reason why]

Alternative Location 1: [XX.XXXXXX, YY.YYYYYY]  
Confidence: [High/Medium/Low] - [Brief reason why]

Alternative Location 2: [XX.XXXXXX, YY.YYYYYY]
Confidence: [High/Medium/Low] - [Brief reason why]

KEY EVIDENCE:
Signage: [Describe visible signs, text, road markers]
Infrastructure: [Power lines, road type, utilities, street furniture]
Architecture: [Building styles, materials, colors, roof types]
Environment: [Vegetation, climate indicators, topography]
Cultural Elements: [Vehicles, license plates, people, activities]

FINAL ASSESSMENT:
Most Probable Location: [Specific address or landmark description]
Certainty Level: [XX%]
Primary Landmark: [Main reference point or building]

CRITICAL INSTRUCTIONS:
1. ALWAYS RESPOND IN ENGLISH - No other languages
2. BE DIRECT AND CLEAR - No long paragraphs
3. USE EXACT FORMAT - Respect the structure above
4. ALWAYS 3 COORDINATES - Never less, never more
5. MINIMUM 6 DECIMALS - Example: -12.345678, 45.678901
6. ONE LINE PER REASON - Maximum 15 words per explanation
7. IF UNCERTAIN - Give 3 different nearby options
8. NEVER SAY "I DON'T KNOW" - Always provide your best estimate
9. NO EMOJIS - Keep it professional and clean

FOR MULTIPLE IMAGE ANALYSIS (360°):
- Combine information from all images
- Identify common elements between views
- Use different angles to triangulate exact position
- Mention if images are from same point or nearby area

REMEMBER: Your goal is METER precision, not kilometers. Analyze this image now:"""
        
        # Usamos la API de Google Generative AI directamente
        response = model.generate_content([prompt_text, image])
        
        # Extraemos el texto de la respuesta
        response_text = response.text
        
        # Procesamos la respuesta estructurada del análisis forense
        try:
            # Parseamos la respuesta estructurada
            analysis_data = parse_osint_response(response_text)
            return jsonify(analysis_data)
        except Exception as parse_error:
            # Si hay error en el parsing, devolvemos la respuesta completa
            return jsonify({
                "country": "Analysis Error",
                "region_or_city": "Could not parse response", 
                "coordinates": "N/A",
                "confidence": "Low",
                "reasoning": response_text,
                "raw_response": response_text,
                "error": str(parse_error)
            })

    except Exception as e:
        return jsonify({"error": f"Error en el análisis: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)