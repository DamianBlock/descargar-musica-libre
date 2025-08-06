import os
import time
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import yt_dlp

CARPETAS = {
    "pixabay": "Musica_Pixabay",
    "ncs": "Musica_NCS",
    "tararear": "Musica_Tarareada"
}

DESCARGADOS_FILE = "descargados.txt"

def cargar_descargados():
    if not os.path.exists(DESCARGADOS_FILE):
        return set()
    with open(DESCARGADOS_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f.readlines())

def guardar_descargado(titulo):
    with open(DESCARGADOS_FILE, "a", encoding="utf-8") as f:
        f.write(titulo + "\n")

def crear_carpetas():
    for fuente, carpeta_base in CARPETAS.items():
        os.makedirs(carpeta_base, exist_ok=True)
        os.makedirs(os.path.join(carpeta_base, "con_voz"), exist_ok=True)
        os.makedirs(os.path.join(carpeta_base, "sin_voz"), exist_ok=True)
    print("[DEBUG] Carpetas verificadas/creadas exitosamente.")

def descargar_desde_pixabay():
    descargados = cargar_descargados()
    
    options = Options()
    # options.add_argument("--headless")  # Descomenta para modo sin interfaz
    options.add_argument("--disable-gpu")

    download_dir = os.path.join(os.getcwd(), CARPETAS["pixabay"], "con_voz")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safeBrowse.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path="Drivers/msedgedriver.exe")
    driver = webdriver.Edge(service=service, options=options)

    print("🔍 Buscando música en Pixabay...")

    try:
        driver.get("https://pixabay.com/es/music/")
        time.sleep(5)

        # Manejo de cookies
        try:
            cookie_button_text = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Aceptar todas') or contains(.,'Aceptar')]"))
            )
            driver.execute_script("arguments[0].click();", cookie_button_text)
            print("✅ Cookies aceptadas.")
            time.sleep(1)
        except:
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            except:
                pass

        termino = input("🔤 Ingresá una palabra clave para buscar música (ej. 'épico', 'triste', etc.): ").strip()

        barra_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search"))
        )
        barra_busqueda.clear()
        barra_busqueda.send_keys(termino)
        barra_busqueda.submit()
        time.sleep(3)

        resultados = driver.find_elements(By.CLASS_NAME, "audioRow--nAm4Z")
        if len(resultados) > 5:
            resultados = resultados[:5]

        print(f"🎵 Resultados encontrados: {len(resultados)}")

        if not resultados:
            print("❌ No se encontraron resultados.")
            return

        for i, resultado in enumerate(resultados):
            titulo = "Título no disponible"
            try:
                titulo_elemento = resultado.find_element(By.CLASS_NAME, "title--7N7Nr")
                titulo = titulo_elemento.text.strip()
            except:
                pass

            if titulo in descargados:
                print(f"⚠️ La canción '{titulo}' ya fue descargada anteriormente. Se omite.")
                continue

            print(f"[DEBUG] Procesando pista {i+1}: {titulo}")

            driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
            time.sleep(1)

            actions = ActionChains(driver)
            actions.move_to_element(resultado).perform()
            time.sleep(2)

            try:
                download_button = WebDriverWait(resultado, 15).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button[.//div[@aria-label='Download']]"))
                )
            except:
                download_button = None

            if download_button:
                try:
                    overlay = driver.find_element(By.CSS_SELECTOR, "div.backdrop--6flEt, div.overlay--2sfQc")
                    driver.execute_script("arguments[0].style.display='none';", overlay)
                except:
                    pass

                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", download_button)
                time.sleep(0.5)

                try:
                    download_button.click()
                except:
                    driver.execute_script("arguments[0].click();", download_button)

                time.sleep(5)

                try:
                    pop_up_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Entendido') or contains(.,'Cerrar') or contains(.,'Aceptar')]"))
                    )
                    driver.execute_script("arguments[0].click();", pop_up_button)
                    time.sleep(2)
                except:
                    pass

                print(f"✅ Descarga de '{titulo}' completada.")
                guardar_descargado(titulo)
            else:
                print(f"❌ No se pudo encontrar botón de descarga para: {titulo}")

    except Exception as e_general:
        print("❌ Error general en la búsqueda:", e_general)
    finally:
        driver.quit()

def descargar_ncs(url, output_dir=None):
    if output_dir is None:
        output_dir = os.path.join(os.getcwd(), CARPETAS["ncs"], "con_voz")
    os.makedirs(output_dir, exist_ok=True)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': False,
        'no_warnings': True,
    }

    descargados = cargar_descargados()

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        entries = info.get('entries', [info])  # Si es playlist, entries es lista; si no, lista con 1 elemento

        for entry in entries:
            titulo = entry.get('title', 'Desconocido').strip()
            if titulo in descargados:
                print(f"⚠️ La canción '{titulo}' ya fue descargada anteriormente. Se omite.")
                continue

            print(f"⬇️ Descargando '{titulo}' ...")
            ydl.download([entry['webpage_url']])
            guardar_descargado(titulo)
            print(f"✅ Descarga de '{titulo}' completada.")

def descargar_por_tarareo():
    print("\n🎙️ Esta función te permitirá buscar canciones tarareando.")
    print("🔧 Actualmente no implementado. Se requiere integrar Audd.io u otra API de identificación.")
    print("🔑 Ya tenés tu API Key, así que podés integrarlo más adelante.\n")

def menu():
    crear_carpetas()

    while True:
        print("\n🎵 Elegí fuente:")
        print("1. Pixabay Music (por palabras clave)")
        print("2. NCS.io (descarga vía YouTube)")
        print("3. Tararear canción para buscar (requiere API)")
        print("0. Salir")

        opcion = input("Opción (0-3): ").strip()

        if opcion == "1":
            descargar_desde_pixabay()
        elif opcion == "2":
            url = input("🔗 Ingresá la URL del video o playlist de NCS en YouTube: ").strip()
            descargar_ncs(url)
        elif opcion == "3":
            descargar_por_tarareo()
        elif opcion == "0":
            break
        else:
            print("❌ Opción inválida. Elegí 0, 1, 2 o 3.")

    print("\n👋 Script finalizado. Presioná una tecla para cerrar.")
    input()

if __name__ == "__main__":
    print("Activando entorno virtual...\nEjecutando el script...")
    menu()
