# Configuración de Google Cloud para GeoSINT v2

Para usar la funcionalidad de Google Lens, necesitas configurar Google Cloud Vision API y Google Maps API.

## Paso 1: Crear un Proyecto en Google Cloud

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Anota el ID del proyecto

## Paso 2: Habilitar las APIs necesarias

1. En Google Cloud Console, ve a "APIs & Services" > "Library"
2. Busca y habilita estas APIs:
   - **Cloud Vision API**
   - **Maps JavaScript API**
   - **Geocoding API**

## Paso 3: Crear Credenciales

### Para Google Cloud Vision API:
1. Ve a "APIs & Services" > "Credentials"
2. Haz clic en "Create Credentials" > "Service Account"
3. Completa los detalles del service account
4. Descarga el archivo JSON de credenciales
5. Guarda el archivo como `google-cloud-credentials.json` en la carpeta `backend/`

### Para Google Maps API:
1. En "Credentials", haz clic en "Create Credentials" > "API Key"
2. Copia la API key generada
3. (Opcional) Restringe la API key a las APIs específicas que necesitas

## Paso 4: Configurar Variables de Entorno

Actualiza tu archivo `backend/.env`:

```env
GEMINI_API_KEY=tu_gemini_api_key
GOOGLE_MAPS_API_KEY=tu_google_maps_api_key
GOOGLE_APPLICATION_CREDENTIALS=./google-cloud-credentials.json
```

## Paso 5: Instalar Dependencias

```bash
cd backend
pip install -r requirements.txt
```

## Paso 6: Probar la Configuración

Ejecuta el backend y prueba el endpoint de Google Lens:

```bash
python app.py
```

## Notas Importantes

- **Costos**: Google Cloud Vision API tiene costos por uso. Revisa la [página de precios](https://cloud.google.com/vision/pricing)
- **Límites**: Hay límites de cuota por defecto. Puedes solicitar aumentos si es necesario
- **Seguridad**: Nunca subas el archivo de credenciales JSON a repositorios públicos
- **Alternativa**: Puedes usar variables de entorno en lugar del archivo JSON para producción

## Estructura de Archivos

```
backend/
├── .env
├── google-cloud-credentials.json  # No subir a Git
├── app.py
└── requirements.txt
```

## Troubleshooting

- Si obtienes errores de autenticación, verifica que el archivo de credenciales esté en la ruta correcta
- Si las APIs no funcionan, asegúrate de que estén habilitadas en Google Cloud Console
- Para errores de cuota, revisa los límites en la consola de Google Cloud