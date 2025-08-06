import time
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

# 📁 Carpeta raíz del proyecto
ROOT_DIR = Path(__file__).resolve().parent

# 📁 Estructura de carpetas por fuente
CARPETAS = {
    "pixabay": ROOT_DIR / "Musica_Pixabay",
    "ncs": ROOT_DIR / "Musica_NCS",
    "tararear": ROOT_DIR / "Musica_Tarareada"
}

def crear_carpetas():
    """Crea las carpetas necesarias dentro del proyecto."""
    for carpeta_base in CARPETAS.values():
        (carpeta_base / "con_voz").mkdir(parents=True, exist_ok=True)
        (carpeta_base / "sin_voz").mkdir(parents=True, exist_ok=True)
    print("[DEBUG] Carpetas creadas/verificadas en la carpeta raíz del proyecto.")

def descargar_desde_pixabay():
    options = Options()
    # options.add_argument("--headless")  # Opcional: modo sin interfaz
    options.add_argument("--disable-gpu")

    # 📥 Carpeta de descargas con voz
    download_dir = CARPETAS["pixabay"] / "con_voz"
    download_dir.mkdir(parents=True, exist_ok=True)

    prefs = {
        "download.default_directory": str(download_dir),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safeBrowsing.enabled": True
    }
    options.add_experimental_option("prefs", prefs)

    service = Service(executable_path=str(ROOT_DIR / "Drivers" / "msedgedriver.exe"))
    driver = webdriver.Edge(service=service, options=options)

    print("🔍 Buscando música en Pixabay...")

    try:
        driver.get("https://pixabay.com/es/music/")
        time.sleep(5)

        # --- Manejo de cookies
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'Aceptar todas') or contains(.,'Aceptar')]"))
            )
            driver.execute_script("arguments[0].click();", cookie_btn)
            print("✅ Cookies aceptadas.")
        except:
            try:
                ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                print("✅ Cerrado banner de cookies con Escape.")
            except:
                print("⚠️ No se pudo manejar el banner de cookies.")

        termino = input("🔤 Ingresá una palabra clave para buscar música (ej. épico, triste...): ").strip()

        # Buscar
        barra_busqueda = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "search"))
        )
        barra_busqueda.clear()
        barra_busqueda.send_keys(termino)
        barra_busqueda.submit()

        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "audioRow--nAm4Z")))
        time.sleep(2)

        resultados = driver.find_elements(By.CLASS_NAME, "audioRow--nAm4Z")[:5]

        if not resultados:
            print("❌ No se encontraron resultados.")
            return

        for i, resultado in enumerate(resultados):
            try:
                titulo = resultado.find_element(By.CLASS_NAME, "title--7N7Nr").text.strip()
            except:
                titulo = "Título no disponible"

            print(f"🎵 Descargando pista {i+1}: {titulo}")
            driver.execute_script("arguments[0].scrollIntoView(true);", resultado)
            time.sleep(1)

            try:
                download_btn = WebDriverWait(resultado, 10).until(
                    EC.element_to_be_clickable((By.XPATH, ".//button[.//div[@aria-label='Download']]"))
                )
                driver.execute_script("arguments[0].scrollIntoView({block:'center'});", download_btn)
                time.sleep(0.5)
                download_btn.click()
                print("✅ Descarga iniciada.")
            except Exception as e:
                print(f"⚠️ Error al descargar {titulo}: {e}")

            time.sleep(5)

    except Exception as e:
        print(f"❌ Error en la descarga: {e}")
    finally:
        driver.quit()
        print("[DEBUG] Navegador cerrado.")

def descargar_por_tarareo():
    print("\n🎙️ Esta función permite buscar canciones tarareando.")
    print("🔧 Aún no implementado. Requiere integración con API (como Audd.io).")

def menu():
    crear_carpetas()

    while True:
        print("\n🎵 Menú principal:")
        print("1. Descargar música desde Pixabay")
        print("2. NCS.io (próximamente)")
        print("3. Buscar música por tarareo")
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
            print("❌ Opción inválida. Probá con 0 a 3.")

    print("\n👋 ¡Gracias por usar el descargador!")
    input("Presioná Enter para cerrar.")

if __name__ == "__main__":
    menu()
