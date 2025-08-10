import requests
import os

# Script simple para probar la API
def test_api():
    url = "http://localhost:5001/api/analyze"
    
    # Buscar una imagen de prueba
    test_images = ["foto_lugar.jpg", "../foto_lugar.jpg", "test.jpg"]
    
    for img_path in test_images:
        if os.path.exists(img_path):
            print(f"Probando con imagen: {img_path}")
            
            with open(img_path, 'rb') as f:
                files = {'image': f}
                try:
                    response = requests.post(url, files=files)
                    print(f"Status Code: {response.status_code}")
                    print(f"Response: {response.json()}")
                    return
                except Exception as e:
                    print(f"Error: {e}")
            break
    else:
        print("No se encontró ninguna imagen de prueba")
        print("Coloca una imagen llamada 'foto_lugar.jpg' en la carpeta backend para probar")

if __name__ == "__main__":
    test_api()