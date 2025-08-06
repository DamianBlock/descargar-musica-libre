@echo off
cd /d "D:\Programas_Python\Proyectos\descargar-musica-libre

echo Activando entorno virtual...
call env_test\Scripts\activate.bat

echo Ejecutando el script...
python descarga_musica_libre.py

echo.
echo Script finalizado. Presiona una tecla para cerrar.
pause >nul
