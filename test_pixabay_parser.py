import requests
from bs4 import BeautifulSoup

# URL de la primera página de música en Pixabay
url = "https://pixabay.com/music/search/?order=latest"

# Simular un navegador real con User-Agent
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

print(f"🔍 Descargando página: {url}")
response = requests.get(url, headers=headers)

if response.status_code != 200:
    print(f"❌ Error al acceder a la página. Código: {response.status_code}")
    exit()

# Guardar el HTML en un archivo para inspección manual si hace falta
with open("pixabay_test_page.html", "w", encoding="utf-8") as f:
    f.write(response.text)
print("✅ HTML guardado como pixabay_test_page.html")

# Analizar el contenido con BeautifulSoup
soup = BeautifulSoup(response.text, "html.parser")

# Buscar tarjetas de música
tracks = soup.select("div[data-type='audio']")

print(f"🎵 Cantidad de pistas detectadas: {len(tracks)}")

# Extraer nombres y enlaces
for i, track in enumerate(tracks, 1):
    title_tag = track.select_one("div.title")
    download_button = track.select_one("a[download]")

    title = title_tag.text.strip() if title_tag else "Sin título"
    download_url = download_button["href"] if download_button else "Sin enlace"

    print(f"{i}. 🎶 {title} - {download_url}")
