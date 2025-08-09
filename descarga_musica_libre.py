import os
import re
import shutil
import time
import requests
import sounddevice as sd
import scipy.io.wavfile as wav
from urllib.parse import quote
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# ========== CONFIGURACIÓN GENERAL ==========
carpeta_proyecto = os.path.dirname(os.path.abspath(__file__))
carpeta_descargas_temp = os.path.join(carpeta_proyecto, "temp_descargas")
fuente_actual = "Pixabay"  # Cambiar a "NCS" si se implementa

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
    nombre_minusculas = nombre_archivo.lower().replace("-", " ").replace("_", " ")
    patrones_voz = [
        "vocals", "vocal", "voice", "sing", "with vocals", "vocal version", "feat", "ft", "lyrics"
    ]
    return any(pat in nombre_minusculas for pat in patrones_voz)

# ========== ESPERAR DESCARGA COMPLETA ==========
def esperar_descarga_completa(carpeta, timeout=30):
    """
    Espera que finalicen las descargas en la carpeta.
    Retorna True si no quedan archivos temporales (.crdownload, .part).
    """
    tiempo_inicial = time.time()
    while True:
        archivos_temp = [f for f in os.listdir(carpeta) if f.endswith(".crdownload") or f.endswith(".part")]
        if not archivos_temp:
            return True
        if time.time() - tiempo_inicial > timeout:
            return False
        time.sleep(1)

# ========== DESCARGAR DESDE PIXABAY ==========
"""def descargar_desde_pixabay(termino):
    options = Options()
    # options.add_argument("--headless")  # modo sin GUI (opcional)
    options.add_argument("--disable-gpu")

    download_dir = carpeta_descargas_temp
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path="Drivers/msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)

    try:
        print("🔍 Buscando música en Pixabay...")
        driver.get("https://pixabay.com/es/music/")
        time.sleep(5)  # espera carga

        # Manejo de cookies
        cookie_banner_handled = False
        try:
            cookie_button_text = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Aceptar todas') or contains(.,'Aceptar')]"))
            )
            driver.execute_script("arguments[0].click();", cookie_button_text)
            print("✅ Cookies aceptadas.")
            cookie_banner_handled = True
            time.sleep(1)
        except Exception as e_xpath_click:
            print(f"⚠️ No se pudo aceptar cookies (por XPATH): {e_xpath_click}")
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                print("✅ Banner de cookies intentado cerrar con ESCAPE.")
                cookie_banner_handled = True
            except Exception as e_escape:
                print(f"❌ No se pudo cerrar banner con ESCAPE: {e_escape}")

        if cookie_banner_handled:
            try:
                driver.execute_script(
                    "var element = document.getElementById('onetrust-consent-sdk');"
                    "if(element) { element.style.display = 'none'; element.style.visibility = 'hidden'; }"
                )
                print("✅ Banner cookies ocultado con JS.")
                time.sleep(1)
            except Exception as e_hide:
                print(f"❌ Error al ocultar banner cookies: {e_hide}")
        else:
            print("❗ Advertencia: El banner de cookies no pudo ser manejado.")

        print(f"[DEBUG] Término de búsqueda: '{termino}'")
        barra_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search"))
        )
        barra_busqueda.clear()
        barra_busqueda.send_keys(termino)
        barra_busqueda.submit()

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "audioRow--nAm4Z")))
        time.sleep(3)

        resultados = driver.find_elements(By.CLASS_NAME, "audioRow--nAm4Z")
        if len(resultados) > 5:
            resultados = resultados[:5]

        print(f"🎵 Resultados encontrados: {len(resultados)}")

        for i, resultado in enumerate(resultados):
            titulo = "Título no disponible"
            try:
                titulo = resultado.find_element(By.CLASS_NAME, "title--7N7Nr").text.strip()
            except:
                pass

            print(f"[DEBUG] Descargando pista {i+1}: {titulo}")

            driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
            time.sleep(1)

            actions = ActionChains(driver)
            actions.move_to_element(resultado).perform()
            time.sleep(2)

            try:
                download_button = WebDriverWait(resultado, 15).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button[.//div[@aria-label='Download']]"))
                )
            except Exception as e:
                print(f"⚠️ No se encontró botón de descarga: {e}")
                continue

            # Ocultar overlays que bloquean clic
            try:
                overlay = driver.find_element(By.CSS_SELECTOR, "div.backdrop--6flEt, div.overlay--2sfQc")
                driver.execute_script("arguments[0].style.display='none';", overlay)
            except:
                pass

            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
            time.sleep(0.5)

            try:
                download_button.click()
                print("✅ Clic normal en botón de descarga exitoso.")
            except Exception as e_click:
                print(f"⚠️ Error clic normal, intentando clic JS: {e_click}")
                driver.execute_script("arguments[0].click();", download_button)
                print("✅ Clic con JavaScript exitoso.")

            if esperar_descarga_completa(carpeta_descargas_temp, timeout=30):
                print(f"✅ Descarga completada: {titulo}")
            else:
                print(f"⚠️ Tiempo de espera excedido para descarga: {titulo}")

            # Intentar cerrar pop-ups si aparecen
            try:
                pop_up_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Entendido') or contains(.,'Cerrar') or contains(.,'Aceptar')]"))
                )
                driver.execute_script("arguments[0].click();", pop_up_button)
                time.sleep(2)
            except:
                pass

        print("✅ Descargas completadas.")

    except Exception as e:
        print("❌ Error general:", e)
    finally:
        driver.quit()
"""

def descargar_desde_pixabay(palabras_clave, carpeta_destino="musica_sin_voz", cantidad=1, api_key="51179546-66eb000c8c8f54135a9253538"):
    """
    Descarga música instrumental desde Pixabay usando su API.
    - palabras_clave: string, por ejemplo "piano triste"
    - carpeta_destino: carpeta donde guardar los MP3
    - cantidad: número máximo de resultados a descargar
    - api_key: tu clave de API de Pixabay
    """
    os.makedirs(carpeta_destino, exist_ok=True)

    print(f"🔎 Buscando: {palabras_clave}")
    url = f"https://pixabay.com/api/audio/?key={api_key}&q={quote(palabras_clave)}&per_page={cantidad}&order=popular"

    try:
        respuesta = requests.get(url)
        datos = respuesta.json()

        if "hits" not in datos or not datos["hits"]:
            print("❌ No se encontraron resultados.")
            return []

        archivos_descargados = []

        for i, item in enumerate(datos["hits"][:cantidad]):
            url_mp3 = item["audio_url"]
            nombre = item["id"]
            archivo_mp3 = os.path.join(carpeta_destino, f"{nombre}.mp3")

            r = requests.get(url_mp3)
            with open(archivo_mp3, "wb") as f:
                f.write(r.content)

            print(f"✅ Descargado: {archivo_mp3}")
            archivos_descargados.append(archivo_mp3)

        return archivos_descargados

    except Exception as e:
        print(f"⚠️ Error al descargar música: {e}")
        return []
    
# ========== MOVER Y CLASIFICAR ==========
def mover_y_clasificar(palabra_clave):
    palabra_clave = palabra_clave.lower().strip()
    archivos = os.listdir(carpeta_descargas_temp)
    if not archivos:
        print("📭 No se descargó ningún archivo.\n")
        return

    for archivo in archivos:
        if not archivo.lower().endswith(".mp3"):
            continue

        origen = os.path.join(carpeta_descargas_temp, archivo)
        tiene_voz = detectar_voz(archivo)

        # Carpeta base según si tiene voz o no
        carpeta_base = carpetas_destino[fuente_actual]["voz" if tiene_voz else "sin_voz"]

        # Crear subcarpeta con la palabra clave
        carpeta_destino = os.path.join(carpeta_base, palabra_clave)
        os.makedirs(carpeta_destino, exist_ok=True)

        # Mover archivo
        shutil.move(origen, os.path.join(carpeta_destino, archivo))
        print(f"✅ Guardado en: {'con_voz' if tiene_voz else 'sin_voz'} / {palabra_clave} → {archivo}")

def buscar_musica_por_tarareo(api_key: str, ruta_audio: str):
    """
    Usa la API de Audd.io para reconocer música a partir de un archivo de audio (tarareo).
    Retorna el diccionario con info de la canción si la reconoce, o None.
    """
    url = "https://api.audd.io/"
    data = {
        'api_token': api_key,
        'return': 'spotify,deezer',
    }
    with open(ruta_audio, 'rb') as f:
        files = {'file': f}
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

# ========== DESCARGAR DESDE NCS (PLANTILLA BÁSICA) ==========

def descargar_desde_ncs(termino):
    """
    Plantilla para descargar música desde NCS (NoCopyrightSounds).
    Actualmente solo imprime que no está implementada.
    Podés adaptar este código para hacer scraping o usar APIs según cómo funcione NCS.
    """
    print(f"🔧 Descarga desde NCS para término '{termino}' aún no implementada.")
    # Aquí podés implementar scraping o acceso a la API de NCS cuando esté disponible.
    # Por ejemplo, podrías usar selenium para buscar en https://ncs.io o usar alguna API externa.        

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
            palabra = input("🔤 Ingresá una palabra clave para buscar música (ej. 'épico', 'triste', etc.): ").strip()
            descargar_desde_pixabay(palabra)
            mover_y_clasificar(palabra)
        elif opcion == "2":
            print("🔧 Fuente NCS aún no disponible.")
        else:
            print("❌ Opción inválida.")

# ========== EJECUCIÓN ==========
if __name__ == "__main__":
    print("Activando entorno virtual...\nEjecutando el script...\n")
    menu()
