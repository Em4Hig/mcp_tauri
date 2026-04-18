# AWS Backup Manager

**Desarrollado por**: EMANUEL HIGUERA VANEGAS

Sistema de descarga de backups desde Amazon S3 con autenticacion AWS SSO y configuracion automatica de perfiles.

## Estructura del Proyecto

```
AWS-BACKUP-MANAGER-PRODUCTION/
├── src/
│   └── aws_backup_gui.py                    # Aplicacion principal
├── build-tools/
│   ├── aws_backup_gui.spec                  # Configuracion PyInstaller
│   └── build.bat                            # Script de compilacion
├── setup-scripts/
│   ├── Instalar_AWS_CLI.bat                 # Instalacion AWS CLI
│   └── Configurar_Perfiles_Automatico.bat  # Configuracion automatica de perfiles SSO
├── docs/
│   ├── MANUAL_USUARIO.md                    # Manual completo de usuario
│   └── DOCUMENTACION_TECNICA.md             # Documentacion para desarrolladores
└── requirements.txt                         # Dependencias Python
```

## Inicio Rapido

### Para Usuarios Finales (Primera Instalacion)
1. Ejecutar `setup-scripts/Instalar_AWS_CLI.bat` como administrador
2. (OPCIONAL) Ejecutar `setup-scripts/Configurar_Perfiles_Automatico.bat` para configurar perfiles empresariales
3. Compilar con `build-tools/build.bat`
4. Usar el ejecutable: `build-tools/dist/AWS_Backup_Manager/AWS_Backup_Manager.exe`

**IMPORTANTE**: La aplicacion funciona con CUALQUIER perfil AWS configurado. No es necesario usar los perfiles preconfigurados.

### Perfiles AWS SSO (OPCIONALES)
El sistema incluye configuracion automatica OPCIONAL para:
- **BANCOPROMERICA** (ID: 311141527518)
- **BCP-NEW-INFRA** (ID: 889436889544) 
- **CAJA-PIURA** (ID: 548544614777)
- **CMB-REDENLACE** (ID: 367343409451)
- **WORLD-POS-SOLUTIONS** (ID: 361886795943)

**NOTA**: Estos perfiles son opcionales. La aplicacion detectara automaticamente cualquier perfil AWS que tengas configurado.

### Para Desarrolladores
1. `pip install -r requirements.txt`
2. `python src/aws_backup_gui.py`
3. Para compilar: `build-tools/build.bat`

## Distribucion y Deployment

### Reglas Criticas de Distribucion

#### ✅ PERMITIDO:
- Mover **TODA la carpeta** `AWS_Backup_Manager/` completa
- Crear **accesos directos** que apunten al .exe en su ubicacion original
- Copiar la carpeta a diferentes equipos
- Cambiar el nombre de la carpeta contenedora

#### ❌ PROHIBIDO:
- Separar `AWS_Backup_Manager.exe` de la carpeta `_internal/`
- Mover solo el .exe sin `_internal/`
- Modificar o borrar la carpeta `_internal/`

### Estructura de Distribucion:
```
AWS_Backup_Manager/          ← Toda esta carpeta se mueve junta
├── AWS_Backup_Manager.exe   ← Ejecutable principal
├── _internal/               ← CRITICO: 3,578 archivos (~124 MB)
│   ├── python310.dll
│   ├── boto3/
│   └── [...]
└── logs/                    ← Se crea automaticamente
```

### Por que es Importante:
- `_internal/` contiene Python completo + AWS SDK + todas las dependencias
- Sin estos archivos, la aplicacion NO ARRANCA
- Error tipico si se separan: "python310.dll no encontrado"

## Configuracion de Perfiles (Automatica vs Manual)

### Opcion A: Deteccion Automatica
La aplicacion detecta automaticamente:
- Perfiles existentes (configurados previamente)
- Perfiles corporativos (configurados por IT)
- Perfiles manuales (configurados por el usuario)

### Opcion B: Configuracion Automatica Empresarial
Si deseas los perfiles empresariales estandar:
```
setup-scripts\Configurar_Perfiles_Automatico.bat
```

**Seguridad**: Crea backup automatico de tu configuracion actual (ej: `config.backup.2025-01-09`)

## Caracteristicas Principales

- **Interfaz grafica moderna** tipo wizard con navegacion intuitiva
- **Autenticacion automatica AWS SSO** con renovacion de tokens
- **Configuracion automatica de perfiles** para todas las cuentas empresariales
- **Explorador S3 inteligente** con filtrado automatico de archivos de backup
- **Descarga multihilo** con barra de progreso en tiempo real
- **Soporte completo** para SQL Server, PostgreSQL y archivos comprimidos
- **Sistema de logs avanzado** y manejo robusto de errores
- **Ejecutable Windows independiente** sin dependencias externas
- **Confirmacion de sobrescritura** para archivos existentes
- **Bloqueo de navegacion** durante descargas para evitar errores

## Tipos de Archivo Soportados

### Bases de Datos
- SQL Server: .bak, .trn, .dif
- PostgreSQL: .sql, .dump, .backup, .pg_dump
- MySQL: .sql, .dump

### Archivos Comprimidos
- .zip, .rar, .7z, .tar, .gz, .bz2

## Documentacion Completa

- **Manual de Usuario**: `docs/MANUAL_USUARIO.md`
- **Documentacion Tecnica**: `docs/DOCUMENTACION_TECNICA.md`

## Proceso de Instalacion Automatizada

1. **Instalacion AWS CLI**: Script automatizado con verificacion
2. **Configuracion de Perfiles**: Creacion automatica de todos los perfiles empresariales
3. **Backup de Configuracion**: Respaldo automatico de configuraciones existentes
4. **Compilacion**: Generacion del ejecutable con limpieza automatica

## Soporte y Distribucion

**Desarrollador**: EMANUEL HIGUERA VANEGAS

Version de produccion completamente automatizada y lista para distribucion empresarial.
Incluye deteccion automatica de perfiles y acceso a cuentas AWS corporativas.

**Version**: 1.0 - Septiembre 2025

## Requisitos del Sistema

- Windows 10/11
- Python 3.8+ (para desarrollo)
- AWS CLI (instalado automaticamente)
- Acceso a AWS SSO corporativo