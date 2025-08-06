Funcionalidades:
Descarga música desde Pixabay (por ahora solo esta opción activa).

Usa Selenium para obtener el enlace de descarga.

Clasifica las canciones según tengan o no voz (speech o vocals).

Guarda los archivos en:

Musica_Pixabay/con_voz/ si tiene voz

Musica_Pixabay/sin_voz/ si no tiene voz

Puedes cambiar fácilmente la fuente a NCS cuando se implemente.

📁 Estructura esperada de carpetas:
Debés tener creada esta estructura base:

bash
Copiar
Editar
descargar-musica-libre/
├── descarga_musica_libre.py  # (este script)
├── Musica_Pixabay/
│   ├── con_voz/
│   └── sin_voz/
├── Musica_NCS/
│   ├── con_voz/
│   └── sin_voz/