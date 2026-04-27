@echo off
echo ===================================================
echo     ELEKTRA - Sistema Multi-Agente Evolutivo
echo ===================================================
echo.
echo Comprobando dependencias...
pip install -r requirements_web.txt >nul 2>&1
echo Iniciando el servidor local...
echo (El navegador se abrira automaticamente)
echo.
python elektra_server.py
pause
