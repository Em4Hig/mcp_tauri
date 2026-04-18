# 🔗 Guía de Usuario: Generar Links Temporales

## 📖 Manual de Usuario - Funcionalidad "Generar Link"

---

## 🎯 ¿Qué hace esta funcionalidad?

La funcionalidad **"Generar Link"** te permite crear URLs temporales de descarga para compartir archivos de backup almacenados en S3, **sin necesidad de que la otra persona tenga acceso a AWS**.

### **Ventajas:**
- ✅ No requiere credenciales AWS del destinatario
- ✅ Links temporales con expiración configurable
- ✅ Fácil de compartir por email, chat, etc.
- ✅ Validación del link antes de compartir

---

## 📋 **Paso a Paso**

### **1️⃣ Navega al Explorador de Archivos**

1. Inicia sesión con tu perfil AWS SSO
2. Selecciona el bucket que contiene el backup
3. Navega hasta el archivo que deseas compartir

### **2️⃣ Selecciona el Archivo**

- Haz **clic** en el archivo de backup deseado
- El botón **"📎 Generar Link"** se habilitará automáticamente
- Verás que el botón cambia de gris a **naranja**

```
Estado ANTES de seleccionar:
┌─────────────────────┐
│ 📎 Generar Link     │  ← Gris (deshabilitado)
└─────────────────────┘

Estado DESPUÉS de seleccionar:
┌─────────────────────┐
│ 📎 Generar Link     │  ← Naranja (habilitado)
└─────────────────────┘
```

### **3️⃣ Genera el Link**

1. Haz clic en el botón **"📎 Generar Link"**
2. Se abrirá un diálogo para configurar la duración del link:

```
┌───────────────────────────────────────┐
│   ⏱️ Tiempo de Validez del Link      │
│                                       │
│   Archivo: backup_12-10-2025.bak     │
│                                       │
│   ○ 1 hora                            │
│   ● 3 horas        ← Seleccionado    │
│   ○ 6 horas                           │
│   ○ 12 horas                          │
│   ○ 24 horas                          │
│   ○ 7 días (máximo permitido)        │
│                                       │
│   ┌────────────┐  ┌──────────────┐   │
│   │ ❌ Cancelar│  │🔗 Generar Link│   │
│   └────────────┘  └──────────────┘   │
└───────────────────────────────────────┘
```

3. Selecciona el tiempo de validez que necesites
4. Haz clic en **"🔗 Generar Link"**

### **4️⃣ Resultado: Link Generado**

Aparecerá un nuevo diálogo mostrando:

```
┌────────────────────────────────────────────────┐
│   ✅ Link Temporal Generado                    │
│                                                │
│   📄 backup_12-10-2025.bak                     │
│   ⏱️ Válido hasta: 15/10/2025 18:30:00        │
│                                                │
│   🔗 URL Temporal:                             │
│   ┌──────────────────────────────────────┐    │
│   │ https://bucket.s3.amazonaws.com/     │    │
│   │ file.bak?X-Amz-Algorithm=AWS4-      │    │
│   │ HMAC-SHA256&X-Amz-Credential=...    │    │
│   │ [Link completo scrollable]           │    │
│   └──────────────────────────────────────┘    │
│                                                │
│   ┌──────────┐ ┌───────────┐ ┌─────────┐     │
│   │🧪 Probar │ │📋 Copiar  │ │✅ Cerrar│     │
│   │  Link    │ │   Link    │ │         │     │
│   └──────────┘ └───────────┘ └─────────┘     │
│                                                │
│   ⚠️ IMPORTANTE: Este link es temporal y      │
│   cualquiera que lo tenga podrá descargar     │
│   el archivo. No lo compartas en lugares      │
│   públicos.                                    │
└────────────────────────────────────────────────┘
```

---

## 🧪 **Probar el Link (Recomendado)**

### **¿Por qué probar?**
Para asegurarte de que el link funciona **antes** de compartirlo.

### **Cómo probar:**

1. En el diálogo de resultado, haz clic en **"🧪 Probar Link"**
2. El botón mostrará "🔄 Probando..."
3. Resultado del test:

#### ✅ **Test Exitoso:**
```
┌─────────────────────────────────┐
│   ✅ Test Exitoso               │
│                                 │
│   El link funciona correctamente│
│                                 │
│   Estado: 200 OK                │
│   Tamaño: 125.50 MB             │
│                                 │
│          [ OK ]                 │
└─────────────────────────────────┘

Botón cambia a: "✅ Link Válido" (Verde)
```

#### ❌ **Test Fallido:**
```
┌─────────────────────────────────┐
│   ❌ Error en Test              │
│                                 │
│   HTTP 403: Forbidden           │
│                                 │
│   El link puede estar mal       │
│   generado o las credenciales   │
│   han expirado.                 │
│                                 │
│          [ OK ]                 │
└─────────────────────────────────┘

Botón cambia a: "❌ Error HTTP" (Rojo)
```

---

## 📋 **Copiar el Link**

### **Método 1: Botón de Copiar**

1. Haz clic en **"📋 Copiar Link"**
2. El link se copia automáticamente al portapapeles
3. El botón mostrará temporalmente: **"✅ Copiado!"**
4. Pega el link donde lo necesites (Ctrl+V)

### **Método 2: Selección Manual**

1. Haz clic dentro del área de texto con el link
2. Selecciona todo con Ctrl+A
3. Copia con Ctrl+C

---

## 🔄 **Compartir el Link**

Una vez copiado, puedes compartir el link por:

- 📧 **Email**
- 💬 **Teams / Slack / WhatsApp**
- 📝 **Documentos**
- 🌐 **Intranet**

### **Ejemplo de mensaje:**

```
Hola equipo,

Aquí está el backup solicitado:

📄 Archivo: backup_12-10-2025.bak
🔗 Link: https://bucket.s3.amazonaws.com/file.bak?X-Amz...
⏱️ Válido hasta: 15/10/2025 18:30:00

Para descargar, simplemente abre el link en tu navegador
o usa wget/curl desde terminal.

Saludos!
```

---

## 🖥️ **Descargar desde el Link**

### **Opción 1: Navegador Web**

1. Abre el link en cualquier navegador
2. El archivo comenzará a descargarse automáticamente

### **Opción 2: Terminal (Linux/Mac)**

```bash
# Usando wget
wget "https://bucket.s3.amazonaws.com/file.bak?X-Amz-Algorithm=..."

# Usando curl
curl -o backup.bak "https://bucket.s3.amazonaws.com/file.bak?X-Amz-Algorithm=..."
```

### **Opción 3: PowerShell (Windows)**

```powershell
# Descargar archivo
Invoke-WebRequest -Uri "https://bucket.s3.amazonaws.com/file.bak?X-Amz-Algorithm=..." `
                  -OutFile "backup.bak"
```

---

## ⏱️ **Duración y Expiración**

### **Opciones de Duración:**

| Opción | Duración | Uso Recomendado |
|--------|----------|-----------------|
| 1 hora | 3,600 seg | Compartir con compañero en la misma sesión |
| 3 horas | 10,800 seg | Descarga durante el horario laboral |
| 6 horas | 21,600 seg | Compartir con otros equipos |
| 12 horas | 43,200 seg | Descargas overnight |
| 24 horas | 86,400 seg | Descargas del día siguiente |
| 7 días | 604,800 seg | Proyectos de varios días |

### **¿Qué pasa cuando expira?**

```
❌ El link dejará de funcionar
❌ Mostrará error 403: Forbidden
✅ Puedes generar un nuevo link si lo necesitas
```

---

## ⚠️ **Advertencias de Seguridad**

### **🔒 IMPORTANTE:**

```
⚠️ El link generado permite descargar el archivo
   a CUALQUIERA que lo tenga.

⚠️ NO compartas el link en:
   • Redes sociales públicas
   • Foros públicos
   • Repositorios públicos de código

✅ SÍ compártelo en:
   • Email corporativo
   • Chat interno de empresa
   • Documentación privada
```

### **Recomendaciones:**

1. ✅ Usa la duración más corta necesaria
2. ✅ Verifica la identidad del destinatario
3. ✅ Prueba el link antes de compartir
4. ✅ Notifica cuando el link expire
5. ❌ No incluyas el link en emails masivos

---

## 🔧 **Solución de Problemas**

### **Problema: El botón "Generar Link" está gris**

**Causa:** No has seleccionado un archivo

**Solución:**
1. Haz clic en un archivo de backup en el explorador
2. El botón se habilitará automáticamente

---

### **Problema: Error "No se pudieron obtener credenciales válidas"**

**Causa:** Tu sesión AWS SSO ha expirado

**Solución:**
1. Ve al **Paso 1: Autenticación AWS**
2. Haz clic en **"🔄 Reconectar"**
3. Completa el login SSO
4. Vuelve al explorador y genera el link nuevamente

---

### **Problema: El test del link falla con 403**

**Causa:** Link mal generado o credenciales expiradas

**Solución:**
1. Reconéctate con AWS SSO (Paso 1)
2. Genera un nuevo link
3. Prueba el link nuevamente

---

### **Problema: El link no descarga en el navegador**

**Causa:** Configuración del navegador o link expirado

**Solución:**
1. Verifica que el link no haya expirado
2. Prueba en modo incógnito
3. Intenta con otro navegador
4. Usa wget/curl como alternativa

---

## 💡 **Consejos y Trucos**

### **Tip 1: Verifica siempre el link**
```
Antes de compartir:
1. Genera el link
2. Haz clic en "🧪 Probar Link"
3. Espera confirmación verde
4. Copia y comparte
```

### **Tip 2: Elige la duración correcta**
```
Para reunión inmediata → 1 hora
Para el mismo día → 6 horas
Para proyecto largo → 7 días
```

### **Tip 3: Incluye contexto al compartir**
```
Siempre incluye:
• Nombre del archivo
• Tamaño aproximado
• Fecha de expiración
• Instrucciones de descarga
```

---

## 📊 **Ejemplo Completo de Uso**

### **Escenario: Compartir backup con equipo remoto**

```
1. Usuario en oficina central
   ├─ Inicia sesión: perfil "BANCOPROMERICA"
   ├─ Selecciona bucket: "sqlserver-backup-rds"
   ├─ Navega a: HiveTrxServerMedianet/
   └─ Selecciona: Backup_12-10-2025.bak

2. Genera link temporal
   ├─ Clic en "📎 Generar Link"
   ├─ Selecciona: 12 horas
   └─ Clic en "🔗 Generar Link"

3. Valida el link
   ├─ Clic en "🧪 Probar Link"
   ├─ Resultado: ✅ Link Válido
   └─ Tamaño: 2.5 GB

4. Comparte por Teams
   ├─ Clic en "📋 Copiar Link"
   ├─ Pega en chat de Teams
   └─ Envía mensaje

5. Equipo remoto descarga
   ├─ Abre link en navegador
   ├─ Descarga automática inicia
   └─ Backup restaurado exitosamente
```

---

## ✅ **Checklist de Uso**

Antes de compartir un link, verifica:

- [ ] Archivo correcto seleccionado
- [ ] Duración apropiada configurada
- [ ] Link probado exitosamente (🧪 verde)
- [ ] Link copiado al portapapeles
- [ ] Destinatario verificado
- [ ] Mensaje con contexto preparado
- [ ] Fecha de expiración comunicada

---

## 🆘 **Soporte**

Si encuentras problemas:

1. 📖 Revisa esta guía
2. 📋 Consulta los logs en la aplicación
3. 🔄 Intenta reconectarte
4. 📧 Contacta al administrador del sistema

---

**¡Listo! Ya puedes compartir backups de forma segura y temporal.** 🎉
