@echo off
echo ======================================================
echo CONFIGURACION AUTOMATICA DE PERFILES AWS SSO
echo ======================================================
echo.

echo Este script configurara automaticamente todos los perfiles AWS SSO
echo necesarios para AWS Backup Manager.
echo.
echo Perfiles que se configuraran:
echo - BANCOPROMERICA
echo - BCP-NEW-INFRA  
echo - CAJA-PIURA
echo - CMB-REDENLACE
echo - WORLD-POS-SOLUTIONS
echo.

set /p confirm="Continuar? (S/N): "
if /i not "%confirm%"=="S" (
    echo Operacion cancelada.
    pause
    exit /b 0
)

echo.
echo [1/3] Verificando directorio AWS...

set AWS_CONFIG_DIR=%USERPROFILE%\.aws
set AWS_CONFIG_FILE=%AWS_CONFIG_DIR%\config

if not exist "%AWS_CONFIG_DIR%" (
    echo Creando directorio .aws...
    mkdir "%AWS_CONFIG_DIR%"
)

echo.
echo [2/3] Creando backup del archivo config existente...

if exist "%AWS_CONFIG_FILE%" (
    echo Respaldando configuracion actual...
    copy "%AWS_CONFIG_FILE%" "%AWS_CONFIG_FILE%.backup.%date:~-4,4%-%date:~-10,2%-%date:~-7,2%" >nul
    echo Backup creado: config.backup.%date:~-4,4%-%date:~-10,2%-%date:~-7,2%
) else (
    echo No existe configuracion previa.
)

echo.
echo [3/3] Escribiendo nueva configuracion...

(
echo # ==========================
echo # Sesion base (SSO^)
echo # ==========================
echo [sso-session backup]
echo sso_start_url = https://d-90679aec28.awsapps.com/start/#
echo sso_region = us-east-1
echo sso_registration_scopes = sso:account:access
echo.
echo # ==========================
echo # Perfiles por cuenta
echo # ==========================
echo.
echo [profile BANCOPROMERICA]
echo sso_session = backup
echo sso_account_id = 311141527518
echo sso_role_name = WPOSS-READ-ACCESS-S3
echo region = us-east-1
echo output = json
echo.
echo [profile BCP-NEW-INFRA]
echo sso_session = backup
echo sso_account_id = 889436889544
echo sso_role_name = WPOSS-READ-ACCESS-S3
echo region = us-east-1
echo output = json
echo.
echo [profile CAJA-PIURA]
echo sso_session = backup
echo sso_account_id = 548544614777
echo sso_role_name = WPOSS-READ-ACCESS-S3
echo region = us-east-1
echo output = json
echo.
echo [profile CMB-REDENLACE]
echo sso_session = backup
echo sso_account_id = 367343409451
echo sso_role_name = WPOSS-READ-ACCESS-S3
echo region = us-east-1
echo output = json
echo.
echo [profile WORLD-POS-SOLUTIONS]
echo sso_session = backup
echo sso_account_id = 361886795943
echo sso_role_name = WPOSS-READ-ACCESS-S3
echo region = us-east-1
echo output = json
) > "%AWS_CONFIG_FILE%"

echo.
echo ======================================================
echo       CONFIGURACION COMPLETADA EXITOSAMENTE
echo ======================================================
echo.
echo PERFILES CONFIGURADOS:
echo   - BANCOPROMERICA       (ID: 311141527518^)
echo   - BCP-NEW-INFRA        (ID: 889436889544^)
echo   - CAJA-PIURA           (ID: 548544614777^)
echo   - CMB-REDENLACE        (ID: 367343409451^)
echo   - WORLD-POS-SOLUTIONS  (ID: 361886795943^)
echo.
echo ARCHIVO CONFIGURADO: %AWS_CONFIG_FILE%
echo.
echo SIGUIENTES PASOS:
echo 1. Ejecutar: aws sso login --profile [NOMBRE_PERFIL]
echo 2. Se abrira el navegador para autenticacion
echo 3. Una vez autenticado, usar AWS Backup Manager
echo.
echo Ejemplo:
echo   aws sso login --profile BANCOPROMERICA
echo.
pause
