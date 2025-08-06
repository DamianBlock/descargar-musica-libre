import os
import re
import shutil
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ========== CONFIGURACIÓN GENERAL ==========
carpeta_proyecto = os.path.dirname(os.path.abspath(__file__))
carpeta_descargas_temp = os.path.join(carpeta_proyecto, "temp_descargas")
fuente_actual = "Pixabay"  # Puedes cambiar a "NCS" cuando se implemente

carpetas_destino = {
    "Pixabay": {
        "voz": os.path.join(carpeta_proyecto, "Musica_Pixabay", "con_voz"),
        "sin_voz": os.path.join(carpeta_proyecto, "Musica_Pixabay", "sin_voz"),
    },
    "NCS": {
        "voz": os.path.join(carpeta_proyecto, "Musica_NCS", "con_voz"),
        "sin_voz": os.path.join(carpeta_proyecto, "Musica_NCS", "sin_voz"),
    }
}

# ========== PALABRAS CLAVE ==========
palabras_clave = [
    "epic", "cinematic", "mistery", "sad", "drama", "emotional", "ambient",
    "tense", "dark", "suspense", "dream", "fantasy", "creepy", "investigation"
]

# ========== SETUP DE CARPETAS ==========
def crear_carpetas():
    os.makedirs(carpeta_descargas_temp, exist_ok=True)
    for fuente in carpetas_destino.values():
        os.makedirs(fuente["voz"], exist_ok=True)
        os.makedirs(fuente["sin_voz"], exist_ok=True)
    print("📁 Carpetas listas.\n")

# ========== DETECTAR VOZ ==========
def detectar_voz(nombre_archivo):
    nombre_minusculas = nombre_archivo.lower()
    patrones_voz = [
        "vocals", "vocal", "voice", "sing", "with vocals", "vocal version", "feat", "ft."
    ]
    return any(re.search(pat, nombre_minusculas) for pat in patrones_voz)

# ========== DESCARGAR DESDE PIXABAY ==========
def descargar_pixabay(palabra):
    print(f"🔍 Buscando: {palabra}")
    url = f"https://pixabay.com/music/search/{palabra.replace(' ', '%20')}/"

    options = Options()
    prefs = {"download.default_directory": carpeta_descargas_temp}
    options.add_experimental_option("prefs", prefs)
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")

    driver = webdriver.Edge(options=options)
    driver.get(url)

    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button[download]"))
        )
        botones = driver.find_elements(By.CSS_SELECTOR, "button[download]")
        if not botones:
            print("❌ No se encontró botón de descarga.")
            driver.quit()
            return

        botones[0].click()
        print("⬇️ Descargando canción...")
        time.sleep(5)

    except Exception as e:
        print(f"⚠️ Error: {e}")
    finally:
        driver.quit()

# ========== MOVER Y CLASIFICAR ==========
def mover_y_clasificar():
    archivos = os.listdir(carpeta_descargas_temp)
    if not archivos:
        print("📭 No se descargó ningún archivo.\n")
        return

    for archivo in archivos:
        if not archivo.lower().endswith(".mp3"):
            continue

        origen = os.path.join(carpeta_descargas_temp, archivo)
        tiene_voz = detectar_voz(archivo)
        destino = carpetas_destino[fuente_actual]["voz" if tiene_voz else "sin_voz"]
        shutil.move(origen, os.path.join(destino, archivo))
        print(f"✅ Guardado en: {'con_voz' if tiene_voz else 'sin_voz'} → {archivo}")

# ========== BUSCAR MUSICA POR TARAREO ==========

def buscar_musica_por_tarareo(api_key: str, ruta_audio: str):
    import requests

    url = "https://api.audd.io/"
    data = {
        'api_token': api_key,
        'return': 'spotify,deezer',
    }
    files = {
        'file': open(ruta_audio, 'rb')
    }

    print("🎶 Analizando el tarareo...")
    response = requests.post(url, data=data, files=files)
    result = response.json()

    if result.get("status") == "success" and result.get("result"):
        cancion = result["result"]
        print(f"✅ Canción reconocida: {cancion['title']} - {cancion['artist']}")
        return cancion
    else:
        print("❌ No se pudo reconocer la canción.")
        return None


# ========== MENÚ PRINCIPAL ==========
def menu():
    crear_carpetas()

    print("🎵 Elegí fuente:")
    print("1. Pixabay Music (por palabras clave)")
    print("2. NCS.io (próximamente)")
    print("0. Salir")

    while True:
        opcion = input("Opción (0-3): ").strip()
        if opcion == "0":
            break
        elif opcion == "1":
            for palabra in palabras_clave:
                descargar_pixabay(palabra)
                mover_y_clasificar()
        elif opcion == "2":
            print("🔧 Fuente NCS aún no disponible.")
        else:
            print("❌ Opción inválida.")

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    print("Activando entorno virtual...\nEjecutando el script...\n")
    menu()
