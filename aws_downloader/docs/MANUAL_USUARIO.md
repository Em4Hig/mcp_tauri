# Manual de Usuario - AWS Backup Manager

## Desarrollado por
**EMANUEL HIGUERA VANEGAS**

## Introduccion

AWS Backup Manager es una aplicacion profesional que permite descargar archivos de backup desde Amazon S3 de manera segura y eficiente, con soporte completo para AWS SSO y configuracion automatica de perfiles empresariales.

## Instalacion y Configuracion Inicial

### Paso 1: Instalacion de AWS CLI

Ejecutar como **Administrador**:
```
setup-scripts\Instalar_AWS_CLI.bat
```

Este script:
- Descarga la ultima version de AWS CLI
- Instala automaticamente sin intervencion del usuario
- Verifica que la instalacion sea correcta
- Configura las variables de entorno necesarias

### Paso 2: Configuracion de Perfiles (OPCIONAL)

**IMPORTANTE**: Esta configuracion es OPCIONAL. La aplicacion funcionara con cualquier perfil AWS que tengas configurado.

#### Opcion A: Usar Perfiles Existentes
Si ya tienes perfiles AWS configurados, la aplicacion los detectara automaticamente y podras usarlos sin problemas.

#### Opcion B: Configuracion Automatica de Perfiles Empresariales
Si deseas configurar automaticamente los perfiles empresariales estandar, ejecutar:
```
setup-scripts\Configurar_Perfiles_Automatico.bat
```

**NOTA DE SEGURIDAD**: Este script:
- Crea un BACKUP automatico de tu configuracion actual con fecha
- Ejemplo: config.backup.2025-01-09
- Tu configuracion original queda COMPLETAMENTE PROTEGIDA
- Puedes restaurar tu configuracion original en cualquier momento

#### Perfiles que Configura Automaticamente:
- **BANCOPROMERICA** - Cuenta: 311141527518
- **BCP-NEW-INFRA** - Cuenta: 889436889544  
- **CAJA-PIURA** - Cuenta: 548544614777
- **CMB-REDENLACE** - Cuenta: 367343409451
- **WORLD-POS-SOLUTIONS** - Cuenta: 361886795943

### Paso 3: Compilacion de la Aplicacion

Ejecutar:
```
build-tools\build.bat
```

Este proceso:
- Instala dependencias Python necesarias
- Compila la aplicacion a ejecutable (.exe)
- Elimina archivos temporales automaticamente
- Genera el ejecutable final listo para distribuir

### Resultado Final

Ejecutable disponible en:
```
build-tools\dist\AWS_Backup_Manager\AWS_Backup_Manager.exe
```

## Distribucion e Instalacion

### IMPORTANTE: Reglas de Distribucion

#### ✅ PERMITIDO:
- **Mover TODA la carpeta completa** `AWS_Backup_Manager/` a cualquier ubicacion
- **Crear accesos directos** que apunten al ejecutable EN SU UBICACION ORIGINAL
- **Copiar la carpeta completa** a diferentes equipos
- **Cambiar el nombre de la carpeta** contenedora (opcional)

#### ❌ PROHIBIDO:
- **Separar** el archivo `AWS_Backup_Manager.exe` de la carpeta `_internal/`
- **Mover solo el .exe** a otra ubicacion sin `_internal/`
- **Borrar o modificar** la carpeta `_internal/`

#### 🚨 ¿Por que NO se pueden separar?

La carpeta `_internal/` contiene:
- **Python 3.10 completo** (motor de la aplicacion)
- **AWS SDK (boto3/botocore)** (conexion a S3)
- **Interfaz grafica (tkinter)** (ventanas y botones)
- **3,578 archivos** esenciales (~124 MB)

**Sin `_internal/`, la aplicacion NO ARRANCA**. Error tipico:
```
"python310.dll no encontrado"
"No se puede importar boto3"
```

#### 📁 Estructura Correcta de Distribucion:
```
AWS_Backup_Manager/                    ← TODA esta carpeta se mueve junta
├── AWS_Backup_Manager.exe             ← Ejecutable principal
├── _internal/                         ← CRITICO: No tocar ni separar
│   ├── python310.dll
│   ├── boto3/
│   ├── botocore/
│   └── [3,574 archivos mas...]
└── logs/                              ← Se crea automaticamente
```

#### 🎯 Distribución Correcta:

**Para Administradores de Sistema:**
```
1. Copiar TODA la carpeta: build-tools\dist\AWS_Backup_Manager\
2. Pegar en: C:\Programas\AWS_Backup_Manager\
3. Crear acceso directo EN DESKTOP que apunte a: C:\Programas\AWS_Backup_Manager\AWS_Backup_Manager.exe
4. Distribuir el acceso directo (EL .EXE NUNCA SALE DE SU CARPETA)
```

**Para Usuarios Finales:**
```
1. Copiar carpeta completa recibida a: C:\MisAplicaciones\AWS_Backup_Manager\
2. Crear acceso directo en Desktop que apunte a: C:\MisAplicaciones\AWS_Backup_Manager\AWS_Backup_Manager.exe
3. EL EJECUTABLE SIEMPRE permanece junto a _internal/
```

#### 🔗 Como Funcionan los Accesos Directos:
- **Acceso directo**: Un archivo .lnk que "apunta" al ejecutable original
- **Ejecutable**: Permanece SIEMPRE en su carpeta junto a _internal/
- **Al hacer doble clic**: El acceso directo ejecuta el .exe desde su ubicación original
- **Resultado**: La aplicación funciona porque encuentra _internal/ en la misma carpeta

## Uso de la Aplicacion

### 1. Autenticacion AWS SSO

Al abrir la aplicacion:

1. **Seleccionar Perfil**: La aplicacion detecta AUTOMATICAMENTE todos los perfiles configurados
2. **Login Automatico**: La aplicacion detecta si necesitas autenticarte
3. **Navegador Web**: Se abre automaticamente para autenticacion SSO
4. **Token Automatico**: Una vez autenticado, el token se guarda automaticamente

#### Deteccion Automatica de Perfiles:
La aplicacion funciona con CUALQUIER perfil AWS que tengas configurado:
- Perfiles existentes (los que ya tenias)
- Perfiles empresariales (si ejecutaste el configurador automatico)
- Perfiles manuales (configurados por ti)
- Perfiles corporativos (configurados por IT)

### 2. Exploracion de Buckets S3

**Navegacion Intuitiva**:
- **Lista de Buckets**: Visualizacion automatica de todos los buckets accesibles
- **Navegacion de Carpetas**: Click en carpetas para navegar
- **Filtrado Automatico**: Solo muestra archivos de backup relevantes
- **Informacion Detallada**: Tamaño, fecha de modificacion por archivo

### 3. Descarga de Archivos

**Proceso de Descarga**:
1. **Seleccionar Archivo**: Click en el archivo deseado
2. **Elegir Destino**: Seleccionar carpeta de descarga
3. **Confirmacion**: Confirmar si el archivo ya existe
4. **Progreso en Tiempo Real**: Barra de progreso con porcentaje
5. **Descarga Multihilo**: Descargas rapidas y eficientes

**Tipos de Archivo Soportados**:

#### Bases de Datos:
- **SQL Server**: .bak, .trn, .dif
- **PostgreSQL**: .sql, .dump, .backup, .pg_dump
- **MySQL**: .sql, .dump

#### Archivos Comprimidos:
- .zip, .rar, .7z, .tar, .gz, .bz2

### 4. Funciones Avanzadas

#### Navegacion Protegida
- **Bloqueo de Botones**: Durante descarga no puedes navegar
- **Estado Visual**: Botones deshabilitados indican proceso en curso
- **Finalizacion Automatica**: Botones se reactivan al completar

#### Manejo de Conflictos
- **Deteccion Automatica**: Identifica archivos existentes
- **Confirmacion de Usuario**: Pregunta antes de sobrescribir
- **Backup Opcional**: Opcion de mantener ambas versiones

#### Sistema de Logs
- **Logs Automaticos**: Cada accion se registra
- **Carpeta de Logs**: `logs/` en el directorio del ejecutable
- **Informacion Detallada**: Timestamp, accion, resultado

## Solucion de Problemas Comunes

### Error de Autenticacion SSO

**Problema**: "Token expirado" o "Error de autenticacion"

**Solucion**:
```bash
aws sso login --profile [NOMBRE_PERFIL]
```

Ejemplo:
```bash
aws sso login --profile BANCOPROMERICA
```

### Error de Conexion S3

**Problema**: No se muestran buckets o archivos

**Solucion**:
1. Verificar conexion a internet
2. Confirmar que el perfil tiene permisos S3
3. Re-autenticar con SSO si es necesario

### Error: "python310.dll no encontrado"

**Problema**: Aplicacion no arranca, aparece error de DLL

**Causa**: El ejecutable fue separado de la carpeta `_internal/`

**Solucion**:
1. Verificar que `AWS_Backup_Manager.exe` este en la MISMA carpeta que `_internal/`
2. Si fueron separados, volver a copiar la estructura completa
3. Crear acceso directo en lugar de mover el ejecutable

### Archivos No Visibles

**Problema**: No aparecen archivos en el bucket

**Solucion**:
La aplicacion solo muestra **archivos de backup**. Verifica que los archivos tengan las extensiones soportadas (.bak, .sql, .dump, .zip, etc.)

### Error de Descarga

**Problema**: Descarga se interrumpe o falla

**Solucion**:
1. Verificar espacio en disco
2. Confirmar permisos de escritura en carpeta destino
3. Re-intentar la descarga

## Configuracion Avanzada

### Recuperacion de Configuracion Original

Si ejecutaste el configurador automatico y quieres volver a tu configuracion anterior:

```batch
# Ir a la carpeta AWS
cd %USERPROFILE%\.aws

# Restaurar backup (ajusta la fecha segun tu backup)
copy config.backup.2025-01-09 config
```

### Configuracion Manual de Perfiles

Si prefieres configurar perfiles manualmente, edita:
```
%USERPROFILE%\.aws\config
```

La aplicacion detectara automaticamente cualquier perfil que agregues.

## Soporte Tecnico

Para soporte tecnico, consultar:
- **Documentacion Tecnica**: `DOCUMENTACION_TECNICA.md`
- **Logs de la Aplicacion**: Carpeta `logs/` 
- **Configuracion AWS**: `%USERPROFILE%\.aws\config`

## Creditos

**Desarrollador**: EMANUEL HIGUERA VANEGAS

La aplicacion esta diseñada para uso empresarial y incluye todas las herramientas necesarias para una implementacion exitosa en entornos corporativos.

**Version**: 1.0 - Septiembre 2025
