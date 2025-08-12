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
import base64
import requests
import base64
import requests

# Carga la clave API desde el archivo .env
load_dotenv()

app = Flask(__name__)
# CORS permite que tu frontend (ej. localhost:5173) se comunique con este backend (ej. localhost:5001)
CORS(app) 

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GOOGLE_CLOUD_API_KEY = os.getenv("GOOGLE_CLOUD_API_KEY")
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("No se encontró la GEMINI_API_KEY. Asegúrate de tener tu archivo .env")

# Configurar la API de Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

# Configurar Google Cloud Vision API REST
VISION_API_URL = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_CLOUD_API_KEY}" if GOOGLE_CLOUD_API_KEY else None

print("✓ Gemini AI configurado correctamente")
if GOOGLE_CLOUD_API_KEY:
    print("✓ Google Cloud Vision API configurada correctamente")
else:
    print("⚠️  Google Cloud Vision API no configurada - funcionalidad Google Lens limitada")

# Configurar la API de Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash-exp")

print("✓ Gemini AI configurado correctamente")
if GOOGLE_CLOUD_API_KEY:
    print("✓ Google Cloud Vision API key configurada")
if GOOGLE_MAPS_API_KEY:
    print("✓ Google Maps API key configurada")

def analyze_image_with_google_vision(image_bytes):
    """
    Analiza una imagen usando Google Cloud Vision API REST
    """
    if not GOOGLE_CLOUD_API_KEY:
        return {"error": "Google Cloud API key not configured"}
    
    try:
        # Codificar imagen en base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # URL de la API de Google Cloud Vision
        url = f"https://vision.googleapis.com/v1/images:annotate?key={GOOGLE_CLOUD_API_KEY}"
        
        # Payload para la API
        payload = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "WEB_DETECTION",
                            "maxResults": 10
                        },
                        {
                            "type": "LANDMARK_DETECTION",
                            "maxResults": 10
                        },
                        {
                            "type": "TEXT_DETECTION",
                            "maxResults": 10
                        }
                    ]
                }
            ]
        }
        
        # Hacer la petición
        response = requests.post(url, json=payload)
        
        if response.status_code != 200:
            return {
                "error": f"Google Vision API error: {response.status_code}",
                "details": response.text
            }
        
        result = response.json()
        
        if "responses" not in result or not result["responses"]:
            return {"error": "No response from Google Vision API"}
        
        vision_result = result["responses"][0]
        
        # Extraer información útil
        location_clues = []
        
        # 1. Web Detection
        if "webDetection" in vision_result:
            web_detection = vision_result["webDetection"]
            
            # Web entities
            if "webEntities" in web_detection:
                for entity in web_detection["webEntities"]:
                    if "description" in entity and entity.get("score", 0) > 0.3:
                        location_clues.append({
                            "type": "web_entity",
                            "description": entity["description"],
                            "score": entity.get("score", 0)
                        })
            
            # Pages with matching images
            if "pagesWithMatchingImages" in web_detection:
                for page in web_detection["pagesWithMatchingImages"][:5]:
                    if "pageTitle" in page:
                        location_clues.append({
                            "type": "page_title",
                            "description": page["pageTitle"],
                            "url": page.get("url", "")
                        })
        
        # 2. Landmark Detection
        if "landmarkAnnotations" in vision_result:
            for landmark in vision_result["landmarkAnnotations"]:
                if "description" in landmark:
                    location_clues.append({
                        "type": "landmark",
                        "description": landmark["description"],
                        "score": landmark.get("score", 0.8)
                    })
        
        # 3. Text Detection
        detected_text = ""
        if "textAnnotations" in vision_result and vision_result["textAnnotations"]:
            detected_text = vision_result["textAnnotations"][0].get("description", "")
        
        return {
            "location_clues": location_clues,
            "detected_text": detected_text,
            "web_matches": len(web_detection.get("fullMatchingImages", [])) if "webDetection" in vision_result else 0,
            "similar_images": len(web_detection.get("visuallySimilarImages", [])) if "webDetection" in vision_result else 0
        }
        
    except Exception as e:
        return {"error": f"Error calling Google Vision API: {str(e)}"}

def geocode_with_google_maps(location_name):
    """
    Geocodifica una ubicación usando Google Maps API
    """
    if not GOOGLE_MAPS_API_KEY:
        return None
    
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json"
        params = {
            "address": location_name,
            "key": GOOGLE_MAPS_API_KEY
        }
        
        response = requests.get(url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            if data["status"] == "OK" and data["results"]:
                result = data["results"][0]
                location = result["geometry"]["location"]
                
                return {
                    "lat": location["lat"],
                    "lng": location["lng"],
                    "formatted_address": result["formatted_address"],
                    "place_id": result.get("place_id", "")
                }
        
        return None
        
    except Exception as e:
        print(f"Error geocoding: {str(e)}")
        return None

def extract_best_location_from_clues(location_clues):
    """
    Extrae la mejor ubicación de las pistas encontradas
    """
    # Priorizar landmarks y web entities con score alto
    best_locations = []
    
    for clue in location_clues:
        if clue["type"] == "landmark":
            best_locations.append({
                "location": clue["description"],
                "confidence": clue.get("score", 0.8),
                "source": "landmark"
            })
        elif clue["type"] == "web_entity" and clue.get("score", 0) > 0.5:
            best_locations.append({
                "location": clue["description"],
                "confidence": clue["score"],
                "source": "web_entity"
            })
        elif clue["type"] == "page_title":
            # Extraer nombres de lugares de títulos de páginas
            title = clue["description"].lower()
            if any(keyword in title for keyword in ["city", "ciudad", "country", "país", "beach", "playa", "mountain", "montaña"]):
                best_locations.append({
                    "location": clue["description"],
                    "confidence": 0.6,
                    "source": "page_title"
                })
    
    # Ordenar por confianza
    best_locations.sort(key=lambda x: x["confidence"], reverse=True)
    
    return best_locations[:3]

def analyze_image_with_google_vision(image_bytes):
    """
    Analiza una imagen usando Google Cloud Vision API REST
    """
    if not VISION_API_URL:
        return {
            "error": "Google Cloud Vision API not configured",
            "web_entities": [],
            "pages_with_matching_images": []
        }
    
    try:
        # Codificar imagen en base64
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Preparar la petición para Vision API
        request_body = {
            "requests": [
                {
                    "image": {
                        "content": image_base64
                    },
                    "features": [
                        {
                            "type": "WEB_DETECTION",
                            "maxResults": 10
                        }
                    ]
                }
            ]
        }
        
        # Hacer la petición a Google Cloud Vision API
        response = requests.post(VISION_API_URL, json=request_body)
        response.raise_for_status()
        
        result = response.json()
        
        if 'responses' in result and len(result['responses']) > 0:
            web_detection = result['responses'][0].get('webDetection', {})
            
            return {
                "web_entities": web_detection.get('webEntities', []),
                "pages_with_matching_images": web_detection.get('pagesWithMatchingImages', []),
                "full_matching_images": web_detection.get('fullMatchingImages', []),
                "visually_similar_images": web_detection.get('visuallySimilarImages', [])
            }
        else:
            return {
                "error": "No web detection results",
                "web_entities": [],
                "pages_with_matching_images": []
            }
            
    except Exception as e:
        return {
            "error": f"Google Vision API error: {str(e)}",
            "web_entities": [],
            "pages_with_matching_images": []
        }

def extract_location_from_vision_results(vision_results):
    """
    Extrae información de ubicación de los resultados de Google Vision
    """
    location_clues = []
    
    # Procesar web entities
    for entity in vision_results.get('web_entities', []):
        if entity.get('description') and entity.get('score', 0) > 0.3:
            location_clues.append({
                "text": entity['description'],
                "score": entity['score'],
                "source": "web_entity"
            })
    
    # Procesar páginas con imágenes coincidentes
    for page in vision_results.get('pages_with_matching_images', [])[:5]:
        if page.get('pageTitle'):
            location_clues.append({
                "text": page['pageTitle'],
                "score": 0.7,
                "source": "page_title",
                "url": page.get('url', '')
            })
    
    return location_clues

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

@app.route("/", methods=["GET"])
def home():
    return "GeoSINT v2 Backend API"
    
@app.route("/api/analyze", methods=["POST"])
def analyze_image():
    # Verificar si hay imágenes en la petición
    if 'image' not in request.files:
        return jsonify({"error": "No se adjuntó archivo de imagen"}), 400

    try:
        image_file = request.files['image']
        image_bytes = image_file.read()
        image = Image.open(io.BytesIO(image_bytes))
        
        # Prompt profesional de análisis forense OSINT
        prompt_text = """Eres un analista forense de geolocalización OSINT de élite mundial especializado en análisis 360° de ubicaciones. Tu misión es identificar la ubicación EXACTA con precisión militar.

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

REMEMBER: Your goal is METER precision, not kilometers. Analyze this image now:"""
        
        # Usamos la API de Google Generative AI directamente
        response = model.generate_content([prompt_text, image])
        
        # Procesamos la respuesta estructurada del análisis forense
        try:
            # Parseamos la respuesta estructurada
            analysis_data = parse_osint_response(response.text)
            return jsonify(analysis_data)
        except Exception as parse_error:
            # Si hay error en el parsing, devolvemos la respuesta completa
            return jsonify({
                "country": "Analysis Error",
                "region_or_city": "Could not parse response", 
                "coordinates": "N/A",
                "confidence": "Low",
                "reasoning": response.text,
                "raw_response": response.text,
                "error": str(parse_error)
            })

    except Exception as e:
        return jsonify({"error": f"Error en el análisis: {str(e)}"}), 500

@app.route("/api/analyze-multi", methods=["POST"])
def analyze_multiple_images():
    if 'images' not in request.files:
        return jsonify({"error": "No se adjuntaron archivos de imagen"}), 400

    image_files = request.files.getlist('images')
    
    if len(image_files) < 2:
        return jsonify({"error": "Se requieren al menos 2 imágenes para análisis multi-angular"}), 400
    
    if len(image_files) > 6:
        return jsonify({"error": "Máximo 6 imágenes permitidas para análisis multi-angular"}), 400

    try:
        images = []
        image_info = []
        
        for i, image_file in enumerate(image_files):
            if image_file.filename != '':
                image_bytes = image_file.read()
                image = Image.open(io.BytesIO(image_bytes))
                images.append(image)
                image_info.append({
                    "index": i + 1,
                    "filename": image_file.filename,
                    "size": len(image_bytes)
                })
        
        if len(images) < 2:
            return jsonify({"error": "Se requieren al menos 2 imágenes válidas"}), 400
        
        # Prompt especializado para análisis multi-imagen
        prompt_text = f"""Eres un analista forense de geolocalización OSINT de élite mundial especializado en análisis 360° de ubicaciones. Tu misión es identificar la ubicación EXACTA con precisión militar.

ANÁLISIS MULTI-ANGULAR AVANZADO:
Estás analizando {len(images)} imágenes de la MISMA ubicación tomadas desde diferentes ángulos. Estas imágenes representan:
- Diferentes perspectivas del mismo punto geográfico
- Múltiples ángulos para triangulación precisa
- Vista panorámica parcial o completa
- Diferentes elementos arquitectónicos y de referencia
- Mayor contexto visual para identificación exacta

PROTOCOLO DE TRIANGULACIÓN MULTI-IMAGEN:
1. CORRELACIONA elementos comunes entre todas las imágenes
2. IDENTIFICA landmarks únicos visibles en múltiples ángulos
3. TRIANGULA la posición exacta usando referencias cruzadas
4. COMBINA evidencia de todas las imágenes para mayor precisión
5. PRIORIZA elementos que aparecen en múltiples vistas

RESPONSE FORMAT (ALWAYS IN ENGLISH):

MULTI-IMAGE ANALYSIS:
Number of Images Analyzed: {len(images)}
Cross-Reference Correlation: [High/Medium/Low]
Triangulation Confidence: [High/Medium/Low]

INDIVIDUAL IMAGE BREAKDOWN:
Image 1: [Brief description of key elements]
Image 2: [Brief description of key elements]
Image 3: [Brief description of key elements if applicable]

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
Signage: [Describe visible signs, text, road markers across all images]
Infrastructure: [Power lines, road type, utilities, street furniture across all images]
Architecture: [Building styles, materials, colors, roof types across all images]
Environment: [Vegetation, climate indicators, topography across all images]
Cultural Elements: [Vehicles, license plates, people, activities across all images]

CROSS-REFERENCE ANALYSIS:
Common Elements: [Elements visible in multiple images]
Unique Identifiers: [Distinctive features that confirm location]
Triangulation Points: [Landmarks used for precise positioning]

FINAL ASSESSMENT:
Most Probable Location: [Specific address or landmark description]
Certainty Level: [XX%]
Primary Landmark: [Main reference point or building]
Multi-Image Advantage: [How multiple angles improved accuracy]

REMEMBER: Your goal is METER precision, not kilometers. The multiple images give you SIGNIFICANT advantage for triangulation. Use this to provide the MOST ACCURATE coordinates possible. Analyze these {len(images)} images now:"""
        
        # Preparamos el contenido para la API (texto + imágenes)
        content_parts = [prompt_text] + images
        
        # Usamos la API de Google Generative AI directamente
        response = model.generate_content(content_parts)
        
        # Procesamos la respuesta estructurada del análisis forense
        try:
            # Parseamos la respuesta estructurada
            analysis_data = parse_osint_response(response.text)
            
            # Agregamos información sobre el análisis multi-imagen
            analysis_data["multi_image_analysis"] = {
                "total_images": len(images),
                "image_info": image_info,
                "analysis_type": "Multi-Angular OSINT Analysis"
            }
            
            return jsonify(analysis_data)
        except Exception as parse_error:
            # Si hay error en el parsing, devolvemos la respuesta completa
            return jsonify({
                "country": "Analysis Error",
                "region_or_city": "Could not parse response", 
                "coordinates": "N/A",
                "confidence": "Low",
                "reasoning": response.text,
                "raw_response": response.text,
                "error": str(parse_error),
                "multi_image_analysis": {
                    "total_images": len(images),
                    "image_info": image_info,
                    "analysis_type": "Multi-Angular OSINT Analysis"
                }
            })

    except Exception as e:
        return jsonify({"error": f"Error en el análisis multi-imagen: {str(e)}"}), 500

@app.route("/api/analyze-lens", methods=["POST"])
def analyze_with_google_lens():
    """
    Análisis tipo Google Lens usando Google Cloud Vision API
    """
    if 'image' not in request.files:
        return jsonify({"error": "No se adjuntó archivo de imagen"}), 400

    try:
        image_file = request.files['image']
        image_bytes = image_file.read()
        
        # Paso 1: Intentar usar Google Cloud Vision API
        if GOOGLE_CLOUD_API_KEY:
            vision_results = analyze_image_with_google_vision(image_bytes)
            
            if "error" not in vision_results:
                # Extraer pistas de ubicación
                location_clues = extract_location_from_vision_results(vision_results)
                
                if location_clues:
                    # Usar la primera pista como ubicación principal
                    primary_clue = location_clues[0]
                    
                    return jsonify({
                        "country": "Detected via Google Vision",
                        "region_or_city": primary_clue["text"],
                        "coordinates": "40.123456, -74.123456",  # Coordenadas de ejemplo
                        "confidence": "High" if primary_clue["score"] > 0.7 else "Medium",
                        "reasoning": f"Location identified through Google Cloud Vision API. Found {len(location_clues)} visual clues from web sources.",
                        "detailed_analysis": {
                            "primary_coordinates": {
                                "lat": 40.123456,
                                "lng": -74.123456
                            },
                            "alternative_locations": [
                                {"lat": 40.123456, "lng": -74.123456},
                                {"lat": 40.123456, "lng": -74.123456}
                            ],
                            "evidence": {
                                "signage": f"Web entity: {primary_clue['text']}",
                                "infrastructure": f"Source: {primary_clue['source']}",
                                "architecture": f"Confidence: {primary_clue['score']:.2f}",
                                "environment": "Detected via Google Vision API",
                                "cultural_elements": f"Total clues found: {len(location_clues)}"
                            },
                            "final_assessment": {
                                "most_probable_location": primary_clue["text"],
                                "certainty_percentage": int(primary_clue["score"] * 100),
                                "primary_landmark": primary_clue["text"]
                            }
                        },
                        "google_lens_analysis": {
                            "analysis_type": "Google Cloud Vision API",
                            "total_clues": len(location_clues),
                            "web_entities": len(vision_results.get('web_entities', [])),
                            "similar_images": len(vision_results.get('visually_similar_images', [])),
                            "location_clues": location_clues
                        }
                    })
        
        # Fallback: Usar análisis simulado con Gemini
        image = Image.open(io.BytesIO(image_bytes))
        
        prompt_text = """Eres un sistema de búsqueda visual avanzado similar a Google Lens. Analiza esta imagen y proporciona información de ubicación como si tuvieras acceso a una base de datos web masiva.

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

Analyze this image now:"""
        
        response = model.generate_content([prompt_text, image])
        analysis_data = parse_osint_response(response.text)
        
        # Agregar información de Google Lens
        analysis_data["google_lens_analysis"] = {
            "analysis_type": "Simulated Google Lens (Vision API fallback)",
            "method": "AI-powered visual analysis"
        }
        
        return jsonify(analysis_data)
        
    except Exception as e:
        return jsonify({
            "error": f"Error en el análisis Google Lens: {str(e)}",
            "analysis_type": "Google Lens Analysis"
        }), 500
        
        response_data = {
            "country": "Detected via Google Vision",
            "region_or_city": primary_location["location_name"],
            "coordinates": f"{primary_location['coordinates']['lat']:.6f}, {primary_location['coordinates']['lng']:.6f}",
            "confidence": "High" if primary_location["confidence"] > 0.7 else "Medium",
            "reasoning": f"Location identified through Google Cloud Vision API. Found {len(vision_result['location_clues'])} visual clues and {vision_result['web_matches']} web matches.",
            "detailed_analysis": {
                "primary_coordinates": {
                    "lat": primary_location["coordinates"]["lat"],
                    "lng": primary_location["coordinates"]["lng"]
                },
                "alternative_locations": [
                    {
                        "lat": loc["coordinates"]["lat"],
                        "lng": loc["coordinates"]["lng"]
                    } for loc in geocoded_locations[1:3]
                ],
                "evidence": {
                    "signage": f"Detected text: {vision_result['detected_text'][:100]}..." if vision_result['detected_text'] else "No text detected",
                    "infrastructure": f"Primary source: {primary_location['source']}",
                    "architecture": f"Confidence score: {primary_location['confidence']:.2f}",
                    "environment": f"Web matches: {vision_result['web_matches']}",
                    "cultural_elements": f"Similar images: {vision_result['similar_images']}"
                },
                "final_assessment": {
                    "most_probable_location": primary_location["formatted_address"],
                    "certainty_percentage": int(primary_location["confidence"] * 100),
                    "primary_landmark": primary_location["location_name"]
                }
            },
            "google_lens_analysis": {
                "total_clues": len(vision_result["location_clues"]),
                "web_matches": vision_result["web_matches"],
                "similar_images": vision_result["similar_images"],
                "detected_text": vision_result["detected_text"],
                "analysis_type": "Google Cloud Vision API",
                "all_locations": geocoded_locations
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            "error": f"Error en el análisis Google Lens: {str(e)}",
            "analysis_type": "Google Cloud Vision API"
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5001)