# 🎵 Buscador de Música Libre & por Voz

Este proyecto permite buscar, filtrar y descargar música libre desde plataformas como Pixabay, y también reconocer canciones tarareadas usando inteligencia artificial.

## 🚀 Funcionalidades

- 🔍 Buscar música libre por palabra clave (Pixabay)
- 🎤 Reconocer canciones tarareadas (Audd API u otras similares)
- 🔊 Detectar automáticamente si las canciones tienen voz o no
- 📁 Guardado automático:
  - Carpeta `musica_con_voz/`: si se detecta voz en la canción
  - Carpeta `musica_sin_voz/`: si es solo instrumental

## 📦 Estructura

```bash
📁 Proyecto/
├── descarga_musica_libre.py
├── utils/
│   ├── clasificador_audio.py
│   ├── downloader_pixabay.py
│   ├── reconocimiento_tarareo.py
├── musica_con_voz/
├── musica_sin_voz/
├── README.md

=======================================
⚙️ Requisitos
Python 3.8+

Librerías:

requests

moviepy

pydub

torch (si usás modelo para detección de voz)

Instalación:

bash
Copiar
Editar
pip install -r requirements.txt

========================================

🧠 Inteligencia Artificial
Este sistema puede clasificar canciones descargadas según contengan voz o no. Utiliza herramientas como torch, pydub y moviepy para procesar el audio.

🔐 Claves API
Pixabay: Obtené tu clave aquí

Audd.io (para tarareo): Registrate en Audd.io

📈 Futuras mejoras
Integración con más fuentes como NCS.io

Interfaz gráfica simple

Clasificación por género automático (IA)

🧑‍💻 Autor
Damian Juarez


========================================
# 🎧 Buscador y Descargador de Música con Voz o Instrumental

Este proyecto es un sistema automatizado que permite:

- Buscar música libre de derechos por palabra clave (desde Pixabay).
- Descargar y clasificar música en dos carpetas:
  - `musica_con_voz/` 🎤
  - `musica_sin_voz/` 🎵
- Reproducir y filtrar si una canción tiene voz o no.
- (Próximamente) Buscar canciones por tarareo usando grabación de micrófono.

## 🚀 Cómo usar

1. **Instalá dependencias**

```bash
pip install -r requirements.txt

python descarga_musica_libre.py
Elegí la fuente

========================================
Opción 1: Buscar por palabra clave (Pixabay).

Opción 2: Buscar por tarareo (requiere implementación futura).

📁 Estructura de Carpetas
Copiar
Editar
📂 musica_con_voz/
📂 musica_sin_voz/
📂 grabaciones/
🧠 ¿Cómo se detecta la voz?
Se utiliza una red neuronal preentrenada para analizar la presencia de voz en el audio descargado. La clasificación es automática, aunque puede haber errores mínimos en canciones muy suaves o ambientales.

🔄 Próximamente
Integración con API de reconocimiento musical por tarareo (ACRCloud u otras).

Fuentes adicionales como NCS.io o FreeSound.

Interfaz gráfica (GUI).

🧑‍💻 Autor
Damian Juarez


## Requisitos

- Python 3.10+
- Selenium
- WebDriver para tu navegador (Chrome o Edge)

Instalación rápida:

```bash
pip install -r requirements.txt
Créditos
Pixabay: https://pixabay.com/music/

NCS.io: https://ncs.io