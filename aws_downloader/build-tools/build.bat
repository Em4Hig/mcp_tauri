@echo off
echo ======================================================
echo AWS BACKUP MANAGER - COMPILACION Y LIMPIEZA AUTOMATICA
echo ======================================================
echo.

echo [1/4] Instalando dependencias...
pip install -r ..\requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: No se pudieron instalar las dependencias
    pause
    exit /b 1
)

echo.
echo [2/4] Compilando aplicacion con PyInstaller...
pyinstaller aws_backup_gui.spec --clean --noconfirm
if %errorlevel% neq 0 (
    echo ERROR: Fallo la compilacion
    pause
    exit /b 1
)

echo.
echo [3/4] Limpiando archivos temporales...

REM Eliminar carpeta build (archivos temporales de PyInstaller)
if exist build (
    echo   - Eliminando build\
    rmdir /s /q build
)

REM Eliminar cache de Python
if exist __pycache__ (
    echo   - Eliminando __pycache__\
    rmdir /s /q __pycache__
)

if exist ..\src\__pycache__ (
    echo   - Eliminando cache del codigo fuente
    rmdir /s /q ..\src\__pycache__
)

REM Eliminar archivos .pyc
if exist *.pyc (
    echo   - Eliminando archivos .pyc
    del /q *.pyc
)

echo.
echo [4/4] Verificando resultado...
if exist dist\AWS_Backup_Manager\AWS_Backup_Manager.exe (
    echo.
    echo ======================================================
    echo          COMPILACION EXITOSA Y LIMPIEZA COMPLETA
    echo ======================================================
    echo.
    echo APLICACION FINAL:
    echo   Ubicacion: build-tools\dist\AWS_Backup_Manager\
    echo   Ejecutable: AWS_Backup_Manager.exe
    echo   Tamano: 
    for %%I in (dist\AWS_Backup_Manager\AWS_Backup_Manager.exe) do echo   %%~zI bytes
    echo.
    echo PARA DISTRIBUIR:
    echo   - Copiar TODA la carpeta: dist\AWS_Backup_Manager\
    echo   - La aplicacion funciona sin Python instalado
    echo   - Incluye todas las dependencias necesarias
    echo.
    echo ARCHIVOS ELIMINADOS:
    echo   - build\ ^(archivos temporales^)
    echo   - __pycache__\ ^(cache Python^)
    echo   - *.pyc ^(archivos compilados^)
    echo.
    echo La aplicacion esta lista para usar y distribuir.
) else (
    echo.
    echo ======================================================
    echo                    ERROR DE COMPILACION
    echo ======================================================
    echo.
    echo No se encontro el ejecutable final.
    echo Revisa los mensajes de error anteriores.
)

echo.
pause
