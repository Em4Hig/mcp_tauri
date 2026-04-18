# Documentacion Tecnica - AWS Backup Manager

**Desarrollado por**: EMANUEL HIGUERA VANEGAS  
**Version**: 1.0 - Septiembre 2025

## Arquitectura del Sistema

AWS Backup Manager es una aplicacion Python basada en Tkinter que proporciona una interfaz grafica para descargar archivos de backup desde Amazon S3, con autenticacion AWS SSO automatizada y configuracion de perfiles empresariales.

## Estructura de Archivos

### Codigo Fuente
```
src/
└── aws_backup_gui.py           # Aplicacion principal con GUI y logica
```

### Scripts de Construccion
```
build-tools/
├── aws_backup_gui.spec         # Configuracion PyInstaller
└── build.bat                   # Script de compilacion automatizada
```

### Scripts de Configuracion
```
setup-scripts/
├── Instalar_AWS_CLI.bat                # Instalacion AWS CLI
└── Configurar_Perfiles_Automatico.bat  # Configuracion automatica de perfiles
```

### Documentacion
```
docs/
├── MANUAL_USUARIO.md           # Manual de usuario final
└── DOCUMENTACION_TECNICA.md    # Este archivo
```

### Archivos de Configuracion
```
requirements.txt                # Dependencias Python
README.md                      # Documentacion principal
```

## Dependencias del Sistema

### Dependencias Python
- **boto3**: Cliente AWS SDK para Python
- **botocore**: Core del SDK AWS
- **tkinter**: Interfaz grafica (incluida en Python)
- **threading**: Manejo de hilos para descargas
- **subprocess**: Ejecucion de comandos del sistema
- **logging**: Sistema de logs
- **os, sys, json**: Modulos estandar de Python

### Dependencias del Sistema
- **AWS CLI**: Requerido para autenticacion SSO
- **Windows 10/11**: Sistema operativo soportado
- **Python 3.8+**: Para desarrollo (no necesario para ejecutable)

## Componentes Principales

### 1. Clase AWSBackupGUI

Clase principal que maneja toda la interfaz y logica:

#### Metodos de Inicializacion
- `__init__()`: Configuracion inicial de la interfaz
- `setup_ui()`: Construccion de la interfaz grafica
- `setup_logging()`: Configuracion del sistema de logs

#### Metodos de Autenticacion
- `refresh_aws_profiles()`: Actualiza lista de perfiles AWS
- `auto_sso_login()`: Login automatico AWS SSO
- `check_aws_credentials()`: Verifica validez de credenciales

#### Metodos de Navegacion S3
- `list_buckets()`: Lista buckets disponibles
- `list_objects()`: Lista objetos en bucket/prefijo
- `is_backup_file()`: Filtro de archivos de backup
- `navigate_back()`: Navegacion hacia atras

#### Metodos de Descarga
- `download_file()`: Descarga de archivos con progreso
- `download_thread()`: Hilo de descarga
- `update_progress()`: Actualizacion de barra de progreso

#### Metodos de Interfaz
- `show_page()`: Navegacion entre paginas
- `set_buttons_enabled()`: Control de estado de botones
- `update_status()`: Actualizacion de barra de estado

### 2. Sistema de Logs

#### Configuracion
- **Nivel**: INFO y superior
- **Formato**: Timestamp + Nivel + Mensaje
- **Archivo**: `logs/aws_backup_manager.log`
- **Rotacion**: Manual (no automatica)

#### Eventos Registrados
- Inicio y cierre de aplicacion
- Autenticacion SSO (exito/error)
- Navegacion S3
- Inicios y finalizacion de descargas
- Errores y excepciones

### 3. Configuracion de Perfiles AWS (OPCIONAL)

La aplicacion detecta automaticamente TODOS los perfiles AWS configurados, incluyendo:
- Perfiles existentes (configurados previamente por el usuario)
- Perfiles corporativos (configurados por el departamento IT)
- Perfiles empresariales (configurados via script automatico)
- Perfiles manuales (configurados directamente por el usuario)

**IMPORTANTE**: No es obligatorio usar los perfiles preconfigurados. La aplicacion funcionara con cualquier perfil AWS valido.

#### Archivo de Configuracion
- **Ubicacion**: `%USERPROFILE%\.aws\config`
- **Formato**: INI estilo AWS

#### Perfiles Empresariales OPCIONALES
Si se ejecuta el script `Configurar_Perfiles_Automatico.bat`, se configuran los siguientes perfiles:

```ini
[sso-session backup]
sso_start_url = https://d-90679aec28.awsapps.com/start/#
sso_region = us-east-1
sso_registration_scopes = sso:account:access

[profile BANCOPROMERICA]
sso_session = backup
sso_account_id = 311141527518
sso_role_name = WPOSS-READ-ACCESS-S3
region = us-east-1
output = json

[profile BCP-NEW-INFRA]
sso_session = backup
sso_account_id = 889436889544
sso_role_name = WPOSS-READ-ACCESS-S3
region = us-east-1
output = json

[profile CAJA-PIURA]
sso_session = backup
sso_account_id = 548544614777
sso_role_name = WPOSS-READ-ACCESS-S3
region = us-east-1
output = json

[profile CMB-REDENLACE]
sso_session = backup
sso_account_id = 367343409451
sso_role_name = WPOSS-READ-ACCESS-S3
region = us-east-1
output = json

[profile WORLD-POS-SOLUTIONS]
sso_session = backup
sso_account_id = 361886795943
sso_role_name = WPOSS-READ-ACCESS-S3
region = us-east-1
output = json
```

### Backup de Configuracion Automatico

#### Comportamiento del Script `Configurar_Perfiles_Automatico.bat`:
```batch
# 1. Detecta configuracion existente
IF EXIST "%USERPROFILE%\.aws\config" (
    # 2. Crea backup con timestamp
    copy "%USERPROFILE%\.aws\config" "%USERPROFILE%\.aws\config.backup.%date:~-4,4%-%date:~-7,2%-%date:~-10,2%"
    echo Backup creado: config.backup.2025-01-09
)

# 3. Escribe nueva configuracion (no destructivo)
# 4. Preserva configuracion original
```

#### Recuperacion de Configuracion:
```batch
# Restaurar configuracion original
cd %USERPROFILE%\.aws
copy config.backup.2025-01-09 config
```

**SEGURIDAD**: El proceso es completamente REVERSIBLE y NO DESTRUCTIVO.

## Filtrado de Archivos

### Extensiones de Backup Soportadas
```python
BACKUP_EXTENSIONS = [
    # SQL Server
    '.bak', '.trn', '.dif',
    # PostgreSQL
    '.sql', '.dump', '.backup', '.pg_dump',
    # MySQL
    '.sql', '.dump',
    # Archivos comprimidos
    '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'
]
```

### Logica de Filtrado
- Solo archivos con extensiones validas son mostrados
- Carpetas siempre son mostradas para navegacion
- Filtrado insensible a mayusculas/minusculas

## Proceso de Compilacion

### PyInstaller Configuracion
```python
# aws_backup_gui.spec
a = Analysis(['../src/aws_backup_gui.py'])
pyz = PYZ(a.pure, a.zipped_data)
exe = EXE(pyz, a.scripts, [], exclude_binaries=True)
coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas)
```

### Script de Compilacion Automatizada
```batch
# build.bat
1. Instalar dependencias: pip install -r requirements.txt
2. Compilar: pyinstaller aws_backup_gui.spec --clean --noconfirm
3. Limpiar: Eliminar build/, __pycache__, *.pyc
4. Verificar: Confirmar ejecutable generado
```

## Distribucion y Deployment

### Estructura de Distribucion Critica

#### Archivos Generados por PyInstaller:
```
dist/AWS_Backup_Manager/
├── AWS_Backup_Manager.exe      # Ejecutable principal (~ 2 MB)
├── _internal/                  # CRITICO: NO SEPARAR
│   ├── base_library.zip        # Python standard library
│   ├── python310.dll          # Interprete Python
│   ├── _bz2.pyd               # Compresion
│   ├── _ctypes.pyd            # C extensions
│   ├── _decimal.pyd           # Decimales
│   ├── _hashlib.pyd           # Hash functions
│   ├── _lzma.pyd              # LZMA compression
│   ├── _queue.pyd             # Queue operations
│   ├── _socket.pyd            # Socket operations
│   ├── _ssl.pyd               # SSL/TLS
│   ├── boto3/                 # AWS SDK
│   ├── botocore/              # AWS Core
│   ├── certifi/               # SSL certificates
│   ├── charset_normalizer/     # Character encoding
│   ├── dateutil/              # Date utilities
│   ├── idna/                  # Internationalized domains
│   ├── jmespath/              # JSON query language
│   ├── s3transfer/            # S3 transfer utilities
│   ├── six/                   # Python 2/3 compatibility
│   ├── urllib3/               # HTTP client
│   └── ... [3,564 archivos adicionales]
└── logs/                       # Se crea en tiempo de ejecucion
```

#### Estadisticas de la Carpeta _internal:
- **Total de archivos**: 3,578
- **Tamaño total**: ~124 MB
- **Componentes criticos**: Python 3.10 + AWS SDK + SSL + Networking

### Reglas de Distribucion OBLIGATORIAS

#### ✅ PERMITIDO:
- Mover TODA la carpeta `AWS_Backup_Manager/` completa
- Crear accesos directos del .exe
- Copiar la carpeta a otros equipos
- Renombrar la carpeta contenedora

#### ❌ PROHIBIDO (Causa fallo de aplicacion):
- Separar `AWS_Backup_Manager.exe` de `_internal/`
- Mover solo el ejecutable
- Borrar o modificar archivos en `_internal/`
- Distribuir solo el .exe

#### 🚨 Consecuencias de Separacion Incorrecta:
```
# Errores tipicos cuando se separa incorrectamente:
"python310.dll no se pudo encontrar"
"ImportError: No module named 'boto3'"
"SSL: CERTIFICATE_VERIFY_FAILED"
"ModuleNotFoundError: No module named 'botocore'"
```

### Proceso de Distribucion Correcto

#### Para Administradores de Sistema:
```batch
# 1. Compilar aplicacion
build-tools\build.bat

# 2. Copiar TODA la carpeta generada
copy /E build-tools\dist\AWS_Backup_Manager\ "C:\Program Files\AWS_Backup_Manager\"

# 3. Crear acceso directo (NO copiar el ejecutable)
mklink "C:\Users\Public\Desktop\AWS Backup Manager.lnk" "C:\Program Files\AWS_Backup_Manager\AWS_Backup_Manager.exe"
```

#### Para Usuarios Finales:
```
1. Recibir TODA la carpeta AWS_Backup_Manager/
2. Copiar a: C:\MisAplicaciones\AWS_Backup_Manager\
3. Crear acceso directo en Desktop (opcional)
4. NUNCA mover solo el .exe
```

## Seguridad y Mejores Practicas

### Manejo de Credenciales
- **Sin almacenamiento local**: Credenciales manejadas por AWS CLI
- **Tokens temporales**: AWS SSO usa tokens con expiracion
- **Renovacion automatica**: Login SSO cuando es necesario

### Validacion de Entrada
- **Perfiles AWS**: Validacion de existencia antes de uso
- **Paths de descarga**: Verificacion de permisos de escritura
- **Archivos existentes**: Confirmacion antes de sobrescribir

### Manejo de Errores
- **Try-catch comprehensivos**: Todos los metodos criticos protegidos
- **Logging detallado**: Errores registrados para debugging
- **Mensajes de usuario**: Errores traducidos a mensajes comprensibles

## APIs y Integracion

### AWS Boto3 Integration
```python
import boto3
from botocore.exceptions import NoCredentialsError, ClientError

# Cliente S3 con perfil especifico
session = boto3.Session(profile_name=profile)
s3_client = session.client('s3')
```

### AWS CLI Integration
```python
import subprocess

# Login SSO automatico
subprocess.run(['aws', 'sso', 'login', '--profile', profile])
```

## Configuracion de Desarrollo

### Entorno de Desarrollo
```bash
# Clonar repositorio
git clone [repository-url]

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicacion
python src/aws_backup_gui.py

# Compilar para distribucion
build-tools/build.bat
```

### Testing Local
- **Perfiles AWS**: Configurar perfiles de prueba
- **Buckets S3**: Usar buckets de desarrollo
- **Logs**: Monitorear `logs/aws_backup_manager.log`

## Implementacion y Distribucion

### Distribucion del Ejecutable
1. **Compilar**: Ejecutar `build-tools/build.bat`
2. **Verificar**: Probar ejecutable en maquina limpia
3. **Empaquetar**: Copiar toda la carpeta `dist/AWS_Backup_Manager/`
4. **Distribuir**: Mantener estructura de carpetas intacta

### Implementacion Empresarial
- **Configuracion Centralizada**: Scripts de configuracion automatica
- **Perfiles Estandarizados**: Configuracion uniforme AWS SSO
- **Documentacion**: Manuales para usuarios finales
- **Soporte**: Logs para diagnostico de problemas

### Requisitos del Sistema de Destino
- **SO**: Windows 10/11 (64-bit)
- **Memoria**: 512MB RAM minimo
- **Disco**: 100MB espacio libre
- **Red**: Conexion a internet para AWS
- **Permisos**: Acceso AWS SSO corporativo

## Mantenimiento y Actualizaciones

### Actualizacion de Dependencias
```bash
pip list --outdated              # Ver dependencias desactualizadas
pip install --upgrade [package]  # Actualizar dependencia especifica
pip freeze > requirements.txt    # Actualizar requirements.txt
```

### Versionado
- **Codigo Fuente**: Control de version con Git
- **Ejecutables**: Numeracion manual en builds
- **Documentacion**: Sincronizada con codigo

### Monitoring
- **Logs de Aplicacion**: Monitoreo de errores recurrentes
- **Feedback de Usuario**: Reportes de bugs y mejoras
- **Metricas de Uso**: Tracking de funcionalidades utilizadas

## Solucion de Problemas Tecnicos

### Problemas Comunes de Compilacion
- **Modulos Faltantes**: Verificar requirements.txt
- **Path Issues**: Usar rutas absolutas en scripts
- **Permisos**: Ejecutar como administrador si es necesario

### Problemas de AWS
- **Credenciales Expiradas**: Re-ejecutar `aws sso login`
- **Permisos S3**: Verificar roles y politicas IAM
- **Conectividad**: Validar acceso a internet y AWS endpoints

### Debugging
- **Logs Detallados**: Revisar `logs/aws_backup_manager.log`
- **Modo Verbose**: Habilitar logging DEBUG si es necesario
- **Testing Manual**: Probar componentes individualmente

## Creditos y Version

**Desarrollador**: EMANUEL HIGUERA VANEGAS  
**Version**: 1.0  
**Fecha**: Septiembre 2025  
**Proposito**: Aplicacion empresarial para descarga de backups desde AWS S3  
**Licencia**: Uso empresarial interno  

### Historial de Versiones
- **v1.0** (Septiembre 2025): Version inicial con GUI completa, SSO automatico, navegacion S3, descarga multihilo, y distribucion lista para produccion.

### Soporte Tecnico
Para consultas tecnicas o modificaciones, contactar al desarrollador.  
Toda modificacion debe mantener la integridad de la estructura de distribucion y las reglas de deployment.

Esta documentacion tecnica debe mantenerse actualizada con cada cambio significativo en el codigo o la arquitectura del sistema.