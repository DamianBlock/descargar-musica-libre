import os
import time
import urllib.request 
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

CARPETAS = {
    "pixabay": "Musica_Pixabay",
    "ncs": "Musica_NCS",
    "tararear": "Musica_Tarareada"
}

def crear_carpetas():
    """Crea las estructuras de carpetas necesarias si no existen."""
    for fuente, carpeta_base in CARPETAS.items():
        os.makedirs(carpeta_base, exist_ok=True)
        os.makedirs(os.path.join(carpeta_base, "con_voz"), exist_ok=True)
        os.makedirs(os.path.join(carpeta_base, "sin_voz"), exist_ok=True)
    print("[DEBUG] Carpetas verificadas/creadas exitosamente.")
    
def descargar_desde_pixabay():
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
        print("[DEBUG] Abriendo URL: https://pixabay.com/es/music/")
        driver.get("https://pixabay.com/es/music/")
        print("[DEBUG] Esperando que la página cargue completamente antes de buscar cookies...")
        time.sleep(5)

        # Manejo de cookies
        cookie_banner_handled = False
        try:
            print("[DEBUG] Intentando encontrar y aceptar cookies por XPATH (texto 'Aceptar todas' o 'Aceptar')...")
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

        termino = input("🔤 Ingresá una palabra clave para buscar música (ej. 'épico', 'triste', etc.): ").strip()
        print(f"[DEBUG] Término de búsqueda: '{termino}'")

        print("[DEBUG] Intentando encontrar la barra de búsqueda por nombre 'search'...")
        barra_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search"))
        )
        barra_busqueda.clear()
        barra_busqueda.send_keys(termino)
        barra_busqueda.submit()
        print("[DEBUG] Búsqueda enviada.")

        print("[DEBUG] Resultados cargados.")
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "audioRow--nAm4Z")))
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
                print(f"⚠️ No se pudo obtener el título para el resultado {i+1}.")

            print(f"[DEBUG] Procesando pista {i+1}: {titulo}")

            driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
            time.sleep(1)

            actions = ActionChains(driver)
            actions.move_to_element(resultado).perform()
            time.sleep(2)

            print(f"[DEBUG] Buscando botón de descarga para: {titulo}")

            download_button = None
            try:
                download_button = WebDriverWait(resultado, 15).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button[.//div[@aria-label='Download']]"))
                )
                print("[DEBUG] Botón de descarga encontrado con XPath aria-label='Download'.")
            except Exception as e:
                print(f"⚠️ No se encontró botón de descarga o no es clickeable: {e}")
                download_button = None

            if download_button:
                print(f"⬇️ Intentando clic para descargar ({i+1}/{len(resultados)}): {titulo}")

                # --- FIX: ocultar overlays o backdrops que bloquean clic ---
                try:
                    overlay = driver.find_element(By.CSS_SELECTOR, "div.backdrop--6flEt, div.overlay--2sfQc")
                    driver.execute_script("arguments[0].style.display='none';", overlay)
                    print("✅ Overlay/backdrop ocultado para permitir clic.")
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

                time.sleep(5)

                # Manejo pop-ups (ej. "Entendido", "Cerrar", etc.)
                time.sleep(2)
                try:
                    pop_up_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Entendido') or contains(.,'Cerrar') or contains(.,'Aceptar')]"))
                    )
                    print("ℹ️ Se detectó pop-up, intentando cerrar...")
                    driver.execute_script("arguments[0].click();", pop_up_button)
                    print("✅ Pop-up cerrado/aceptado.")
                    time.sleep(2)
                except:
                    print("✅ No se detectó pop-up o no se pudo cerrar (continuando).")

                print("✅ Intento de descarga completado.")
            else:
                print(f"❌ No se pudo encontrar botón de descarga para: {titulo}")

    except Exception as e_general:
        print("❌ Error general en la búsqueda:", e_general)
        try:
            print(f"[DEBUG] URL actual en el momento del error: {driver.current_url}")
        except:
            pass
    finally:
        print("[DEBUG] Cerrando el navegador...")
        driver.quit()

def descargar_por_tarareo():
    print("\n🎙️ Esta función te permitirá buscar canciones tarareando.")
    print("🔧 Actualmente no implementado. Se requiere integrar Audd.io u otra API de identificación.")
    print("🔑 Ya tenés tu API Key, así que podés integrarlo más adelante.\n")

def menu():
    crear_carpetas()

    while True:
        print("\n🎵 Elegí fuente:")
        print("1. Pixabay Music (por palabras clave)")
        print("2. NCS.io (próximamente)")
        print("3. Tararear canción para buscar (requiere API)")
        print("0. Salir")

        opcion = input("Opción (0-3): ").strip()

        if opcion == "1":
            descargar_desde_pixabay()
        elif opcion == "2":
            print("🕐 NCS.io se integrará próximamente.")
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
