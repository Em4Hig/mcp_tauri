#!/usr/bin/env python3
"""
aws_backup_gui.py

Interfaz gráfica profesional para el Gestor de Backups AWS SSO.
Diseño corporativo elegante y moderno.

Autor: Emanuel Higuera Vanegas (2025)
"""

import os
import sys
import threading
import time
import math
from pathlib import Path
from datetime import datetime
from typing import List, Optional
import logging
import configparser
import subprocess

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText

try:
    import boto3
    import botocore
    import botocore.config
    import botocore.exceptions
    from tqdm import tqdm
except ImportError as e:
    messagebox.showerror("Error de Dependencias", 
                        f"Faltan dependencias requeridas:\n{e}\n\n"
                        "Instale con: pip install boto3 botocore tqdm")
    sys.exit(1)

# =========================
# CONFIGURACIÓN DE LOGGING
# =========================

# Suprimir logs verbosos de boto3/botocore para una salida más limpia
logging.getLogger('boto3').setLevel(logging.CRITICAL)
logging.getLogger('botocore').setLevel(logging.CRITICAL)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger('s3transfer').setLevel(logging.CRITICAL)

# Configurar logging del programa principal
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# =========================
# FUNCIONES DE AWS SSO AUTO-LOGIN
# =========================

def check_aws_cli_available():
    """Verifica si AWS CLI está disponible"""
    try:
        # Ejecutar sin mostrar consola
        startupinfo = None
        creationflags = 0
        if hasattr(subprocess, 'STARTUPINFO'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
        
        subprocess.run(['aws', '--version'], 
                      capture_output=True, 
                      check=True,
                      startupinfo=startupinfo,
                      creationflags=creationflags)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def get_available_profiles():
    """Obtiene los perfiles disponibles del archivo config de AWS"""
    config_path = Path.home() / '.aws' / 'config'
    if not config_path.exists():
        return []
    
    try:
        config = configparser.ConfigParser()
        config.read(config_path)
        profiles = []
        for section in config.sections():
            if section.startswith('profile '):
                profile_name = section.replace('profile ', '')
                profiles.append(profile_name)
        return profiles
    except Exception:
        return []

def is_sso_token_valid(profile_name):
    """Verifica si el token SSO está válido para el perfil dado"""
    try:
        session = boto3.Session(profile_name=profile_name)
        sts = session.client('sts')
        sts.get_caller_identity()
        return True
    except Exception:
        return False

def perform_sso_login(profile_name):
    """Ejecuta aws sso login para el perfil especificado"""
    try:
        if not check_aws_cli_available():
            return False, "AWS CLI no está instalado"
        
        # Ejecutar aws sso login SIN mostrar consola
        cmd = ['aws', 'sso', 'login', '--profile', profile_name]
        import subprocess
        
        # En Windows, evitar mostrar la consola
        startupinfo = None
        creationflags = 0
        if hasattr(subprocess, 'STARTUPINFO'):
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            startupinfo.wShowWindow = subprocess.SW_HIDE
            creationflags = subprocess.CREATE_NO_WINDOW
        
        result = subprocess.run(cmd, 
                              capture_output=True, 
                              text=True,
                              startupinfo=startupinfo,
                              creationflags=creationflags)
        
        if result.returncode == 0:
            return True, "Login SSO exitoso"
        else:
            return False, f"Error en login SSO: {result.stderr}"
    except Exception as e:
        return False, f"Error ejecutando login SSO: {str(e)}"

def auto_handle_sso_credentials(profile_name):
    """
    Maneja automáticamente las credenciales SSO:
    1. Verifica si el token es válido
    2. Si no es válido, ejecuta login SSO automáticamente
    3. Retorna True si las credenciales están disponibles
    """
    if is_sso_token_valid(profile_name):
        return True, "Credenciales válidas"
    
    # Token no válido, intentar login automático
    success, message = perform_sso_login(profile_name)
    if success:
        # Verificar nuevamente después del login
        if is_sso_token_valid(profile_name):
            return True, "Login SSO exitoso, credenciales válidas"
        else:
            return False, "Login SSO completado pero credenciales no válidas"
    else:
        return False, message

# =========================
# CONFIGURACIÓN GLOBAL
# =========================
VERSION = "2.0.0 GUI"
BACKUP_EXTENSIONS = [
    # SQL Server
    '.bak', '.trn', '.mdf', '.ldf',
    
    # PostgreSQL - TODAS las extensiones posibles
    '.dump', '.backup', '.psql', '.pg_dump', '.dmp', '.custom',
    '.pgdump', '.pgsql', '.postgresql', '.pg', '.pgbackup',
    '.bin', '.tar', '.directory', '.plain', '.out',
    
    # MySQL
    '.mysql', '.mysqldump', '.frm', '.ibd', '.ibdata',
    
    # Oracle
    '.ora', '.oracle', '.exp', '.dmp',
    
    # Genérico SQL y bases de datos
    '.sql', '.db', '.database', '.sqlite', '.sqlite3', '.db3',
    '.dbf', '.mdb', '.accdb',
    
    # Comprimidos y archivos
    '.gz', '.zip', '.tar', '.tar.gz', '.tar.bz2', '.tar.xz',
    '.7z', '.rar', '.bz2', '.xz', '.lz4', '.zst'
]

# 🎨 Paleta de colores corporativa elegante 2025
COLORS = {
    # Colores primarios - Tonos profesionales oscuros
    'primary': '#1A1D29',       # Navy oscuro corporativo (mantener fondo header)
    'primary_light': '#2C3E50', # Azul acero oscuro
    'secondary': '#34495E',     # Gris pizarra corporativo
    
    # Colores de acento - Corporativos y sofisticados
    'accent': '#3498DB',        # Azul corporativo brillante
    'accent_hover': '#2980B9',  # Azul corporativo oscuro (hover)
    'accent_light': '#5DADE2',  # Azul claro suave
    
    # Colores de estado - Serios y profesionales
    'success': '#27AE60',       # Verde corporativo
    'success_hover': '#229954', # Verde oscuro hover
    'warning': '#E67E22',       # Naranja corporativo serio
    'warning_hover': '#D35400', # Naranja oscuro hover
    'danger': '#E74C3C',        # Rojo corporativo
    'danger_hover': '#C0392B',  # Rojo oscuro hover
    
    # Colores de fondo - Mantener esquema claro
    'background': '#F7FAFC',    # Gris ultra claro (MANTENER)
    'surface': '#FFFFFF',       # Blanco puro
    'surface_hover': '#ECF0F1', # Gris platino hover
    
    # Colores de texto - Alta legibilidad
    'text_primary': '#2C3E50',  # Texto principal oscuro
    'text_secondary': '#7F8C8D', # Texto secundario gris
    
    # Colores de interfaz - Sutiles y elegantes
    'border': '#D5DBDB',        # Borde gris suave
    'border_focus': '#3498DB',  # Borde focus azul corporativo
    'shadow': 'rgba(44, 62, 80, 0.08)', # Sombra sutil azulada
    
    # Colores adicionales para botones especiales
    'info': '#5DADE2',          # Azul información
    'info_hover': '#3498DB',    # Azul información hover
}

class AWSBackupGUI:
    """Interfaz gráfica principal del AWS Backup Manager"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        
        # Sistema de pasos del wizard
        self.current_step = 1
        self.total_steps = 4
        self.steps = {
            1: "Autenticación AWS",
            2: "Selección de Bucket", 
            3: "Explorador S3",
            4: "Descarga de Archivos"
        }
        
        # Variables de estado
        self.session = None
        self.s3_client = None
        self.selected_profile = None
        self.selected_bucket = None
        self.selected_file_info = None
        self.download_directory = None
        self.current_path = ""
        self.navigation_history = []
        
        # Estado de descarga mejorado
        self.download_in_progress = False
        self.download_thread = None
        self.download_completed = False
        self.download_progress_data = {
            'progress': 0,
            'current_size': '0 B',
            'total_size': '0 B',
            'status': 'idle'
        }
        
        # Crear interfaz del wizard
        self.create_wizard_interface()
        
        # Configurar logging DESPUÉS de crear widgets
        self.setup_logging()
        
        # Cargar perfiles AWS al final
        self.load_aws_profiles()
        
    def setup_window(self):
        """Configura la ventana principal con estilo moderno"""
        self.root.title(f"AWS Backup Manager v{VERSION}")
        self.root.geometry("1200x750")  # Ventana más pequeña al inicio
        self.root.minsize(400, 300)  # Tamaño mínimo muy flexible
        self.root.configure(bg=COLORS['background'])
        
        # Configurar el icono (si existe)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass
            
        # Centrar la ventana
        self.center_window()
        
        # Configurar cierre de ventana
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def center_window(self):
        """Centra la ventana en la pantalla"""
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (1400 // 2)
        y = (self.root.winfo_screenheight() // 2) - (900 // 2)
        self.root.geometry(f"+{x}+{y}")
        
    def setup_styles(self):
        """Configura los estilos ttk modernos 2025"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # 📝 Estilos de texto corporativos - Tipografía profesional
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 32, 'bold'),
                       foreground=COLORS['primary'],
                       background=COLORS['surface'])
                       
        style.configure('Subtitle.TLabel',
                       font=('Segoe UI', 14),
                       foreground=COLORS['text_secondary'],
                       background=COLORS['surface'])
                       
        style.configure('Header.TLabel',
                       font=('Segoe UI', 16, 'bold'),
                       foreground=COLORS['primary'],
                       background=COLORS['surface'])
                       
        style.configure('Status.TLabel',
                       font=('Segoe UI', 11),
                       foreground=COLORS['text_secondary'],
                       background=COLORS['surface'])
                       
        style.configure('Connected.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=COLORS['success'],
                       background=COLORS['surface'])
                       
        style.configure('Disconnected.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=COLORS['danger'],
                       background=COLORS['surface'])
                       
        style.configure('Success.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=COLORS['success'])
                       
        style.configure('Warning.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=COLORS['warning'])
                       
        style.configure('Error.TLabel',
                       font=('Segoe UI', 11, 'bold'),
                       foreground=COLORS['danger'])
                       
        # 🎯 Botones primarios - Estilo corporativo elegante
        style.configure('Primary.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='white',
                       focuscolor='none',
                       borderwidth=0,
                       relief='flat')
        style.map('Primary.TButton',
                 background=[('active', COLORS['accent_hover']), 
                           ('!active', COLORS['accent']),
                           ('pressed', COLORS['primary_light']),
                           ('disabled', COLORS['border'])])
        
        # 🎯 Botones secundarios - Borde sutil corporativo
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 11),
                       foreground=COLORS['text_primary'],
                       focuscolor='none',
                       borderwidth=1,
                       relief='solid')
        style.map('Secondary.TButton',
                 background=[('active', COLORS['surface_hover']), 
                           ('!active', COLORS['surface'])],
                 bordercolor=[('active', COLORS['accent']), 
                            ('!active', COLORS['border'])],
                 foreground=[('active', COLORS['accent']),
                           ('!active', COLORS['text_primary'])])
                       
        # 📦 Cards modernas - Sombras sutiles corporativas
        style.configure('Card.TFrame',
                       background=COLORS['surface'],
                       borderwidth=0,
                       relief='flat')
                       
        style.configure('CardHeader.TFrame',
                       background=COLORS['surface'],
                       borderwidth=0,
                       relief='flat')
        
        # 🎛️ Combobox corporativo elegante
        style.configure('Modern.TCombobox',
                       font=('Segoe UI', 11),
                       fieldbackground=COLORS['surface'],
                       background=COLORS['surface'],
                       borderwidth=2,
                       focuscolor='none',
                       relief='solid')
        style.map('Modern.TCombobox',
                 bordercolor=[('focus', COLORS['accent']), 
                            ('!focus', COLORS['border'])],
                 lightcolor=[('focus', COLORS['accent_light']), 
                           ('!focus', COLORS['border'])],
                 darkcolor=[('focus', COLORS['accent']), 
                          ('!focus', COLORS['border'])])
        
        # 📊 Treeview corporativo profesional
        style.configure('Modern.Treeview',
                       font=('Segoe UI', 10),
                       background=COLORS['surface'],
                       foreground=COLORS['text_primary'],
                       fieldbackground=COLORS['surface'],
                       borderwidth=1,
                       relief='solid')
        style.configure('Modern.Treeview.Heading',
                       font=('Segoe UI', 11, 'bold'),
                       background=COLORS['primary_light'],
                       foreground='white',
                       borderwidth=0,
                       relief='flat')
        style.map('Modern.Treeview.Heading',
                 background=[('active', COLORS['primary'])])
        style.map('Modern.Treeview',
                 background=[('selected', COLORS['accent']),
                           ('!selected', COLORS['surface'])],
                 foreground=[('selected', 'white'),
                           ('!selected', COLORS['text_primary'])])
                           
        # 📈 Progressbar corporativo suave
        style.configure('Modern.Horizontal.TProgressbar',
                       background=COLORS['accent'],
                       troughcolor=COLORS['border'],
                       borderwidth=0,
                       lightcolor=COLORS['accent'],
                       darkcolor=COLORS['accent_hover'],
                       relief='flat')
        
        # 📜 Scrollbar corporativa elegante
        style.configure('Modern.Vertical.TScrollbar',
                       background=COLORS['border'],
                       troughcolor=COLORS['background'],
                       borderwidth=0,
                       relief='flat',
                       arrowcolor=COLORS['secondary'])
        style.map('Modern.Vertical.TScrollbar',
                 background=[('active', COLORS['secondary']),
                           ('!active', COLORS['border'])])
                 
        # ✍️ Entry corporativo limpio
        style.configure('Modern.TEntry',
                       font=('Segoe UI', 11),
                       fieldbackground=COLORS['surface'],
                       borderwidth=2,
                       relief='solid',
                       focuscolor='none')
        style.map('Modern.TEntry',
                 bordercolor=[('focus', COLORS['accent']), 
                            ('!focus', COLORS['border'])])
    
    def create_wizard_interface(self):
        """Crea la interfaz del wizard paso a paso"""
        # Frame principal del wizard
        self.main_frame = tk.Frame(self.root, bg=COLORS['background'])
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header del wizard (siempre visible)
        self.create_wizard_header()
        
        # Container scrollable para el contenido
        self.create_scrollable_content()
        
        # Footer con navegación (siempre visible)
        self.create_wizard_navigation()
        
        # Status bar
        self.create_modern_status_bar(self.main_frame)
        
        # Mostrar el primer paso
        self.show_step(1)
    
    def create_scrollable_content(self):
        """Crea un área de contenido con scroll condicional"""
        # Frame container principal
        self.content_container = tk.Frame(self.main_frame, bg=COLORS['background'])
        self.content_container.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Canvas para scroll (se usará en pasos 3 y 4)
        self.canvas = tk.Canvas(self.content_container, bg=COLORS['background'], highlightthickness=0)
        self.scrollbar = ttk.Scrollbar(self.content_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=COLORS['background'])
        
        # Frame estático para pasos sin scroll (1 y 2)
        self.static_frame = tk.Frame(self.content_container, bg=COLORS['background'])
        
        # Configurar scroll
        def _configure_scrollregion(event=None):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))
            # Verificar si necesita scrollbar
            self._update_scrollbar_visibility()
        
        def _configure_canvas_size(event=None):
            # Ajustar ancho del frame scrollable al canvas
            canvas_width = self.canvas.winfo_width()
            self.canvas.itemconfig(self.canvas_window_id, width=canvas_width)
            
        self.scrollable_frame.bind("<Configure>", _configure_scrollregion)
        self.canvas.bind("<Configure>", _configure_canvas_size)
        
        self.canvas_window_id = self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Por defecto, NO mostrar ningún frame (se activará según el paso)
        # El content_frame será dinámico según el paso
        self.content_frame = None
        
        # Bind eventos de mouse para scroll
        self.bind_mouse_scroll(self.canvas)
        
    def _update_scrollbar_visibility(self):
        """Muestra/oculta el scrollbar según sea necesario"""
        try:
            canvas_height = self.canvas.winfo_height()
            content_height = self.scrollable_frame.winfo_reqheight()
            
            if content_height > canvas_height:
                # Mostrar scrollbar
                if not self.scrollbar.winfo_ismapped():
                    self.scrollbar.pack(side="right", fill="y")
            else:
                # Ocultar scrollbar
                if self.scrollbar.winfo_ismapped():
                    self.scrollbar.pack_forget()
        except:
            # Si hay error, mejor mostrar scrollbar
            if not self.scrollbar.winfo_ismapped():
                self.scrollbar.pack(side="right", fill="y")
        
    def bind_mouse_scroll(self, widget):
        """Habilita scroll con rueda del mouse"""
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def _bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        def _unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        widget.bind('<Enter>', _bind_to_mousewheel)
        widget.bind('<Leave>', _unbind_from_mousewheel)
    
    def create_wizard_header(self):
        """Crea la cabecera del wizard - Diseño corporativo elegante"""
        header_frame = tk.Frame(self.main_frame, bg=COLORS['primary'], height=100)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Container interno con padding profesional
        header_content = tk.Frame(header_frame, bg=COLORS['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=40, pady=20)
        
        # Título principal con estilo corporativo
        title_label = tk.Label(header_content,
                              text="AWS Backup Manager",
                              font=('Segoe UI', 24, 'bold'),
                              fg='white',
                              bg=COLORS['primary'])
        title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Indicador de pasos con color de acento corporativo
        self.step_indicator = tk.Label(header_content,
                                      text=f"Paso {self.current_step} de {self.total_steps}: {self.steps[self.current_step]}",
                                      font=('Segoe UI', 14),
                                      fg=COLORS['accent_light'],
                                      bg=COLORS['primary'])
        self.step_indicator.pack(side=tk.RIGHT, anchor=tk.E)
    
    def create_wizard_navigation(self):
        """Crea los botones de navegación del wizard - Diseño corporativo profesional"""
        # Container elegante para los botones
        nav_frame = tk.Frame(self.main_frame, bg=COLORS['background'], height=80)
        nav_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=40, pady=20)
        nav_frame.pack_propagate(False)
        
        # 🔙 Botón Volver - Gris corporativo elegante
        self.back_button = tk.Button(nav_frame,
                                    text="← Volver",
                                    font=('Segoe UI', 12),
                                    bg=COLORS['secondary'],
                                    fg='white',
                                    activebackground=COLORS['primary_light'],
                                    activeforeground='white',
                                    bd=0,
                                    padx=30,
                                    pady=12,
                                    cursor='hand2',
                                    relief='flat',
                                    command=self.smart_go_back)
        self.back_button.pack(side=tk.LEFT)
        
        # ➡️ Botón Continuar - Azul corporativo vibrante
        self.next_button = tk.Button(nav_frame,
                                    text="Continuar →",
                                    font=('Segoe UI', 12, 'bold'),
                                    bg=COLORS['accent'],
                                    fg='white',
                                    activebackground=COLORS['accent_hover'],
                                    activeforeground='white',
                                    bd=0,
                                    padx=30,
                                    pady=12,
                                    cursor='hand2',
                                    relief='flat',
                                    command=self.go_to_next_step)
        self.next_button.pack(side=tk.RIGHT)
    
    # Método de progreso removido - no lo necesitamos para la interfaz limpia
    def create_progress_indicator(self, parent):
        """MÉTODO DESHABILITADO - Progreso visual removido"""
        pass  # No queremos barra de progreso fea
    
    def update_progress_indicator(self):
        """MÉTODO DESHABILITADO - No queremos indicador de progreso"""
        pass  # Método deshabilitado
    
    def show_step(self, step_number):
        """Muestra el contenido del paso especificado"""
        # Limpiar contenido anterior si existe
        if self.content_frame:
            for widget in self.content_frame.winfo_children():
                widget.destroy()
        
        # Actualizar paso actual
        self.current_step = step_number
        
        # Actualizar header
        self.step_indicator.config(text=f"Paso {self.current_step} de {self.total_steps}: {self.steps[self.current_step]}")
        
        # Actualizar botones de navegación
        self.update_navigation_buttons()
        
        # 🎯 DECISIÓN CRÍTICA: ¿Usar frame estático o scrollable?
        if step_number in [1, 2, 3]:  # ✅ PASO 3 TAMBIÉN SIN SCROLL GENERAL
            # ✅ PASOS 1, 2 y 3: SIN SCROLL GENERAL - Contenido estático
            # Ocultar canvas y scrollbar
            self.canvas.pack_forget()
            self.scrollbar.pack_forget()
            
            # Mostrar frame estático
            self.static_frame.pack(fill=tk.BOTH, expand=True)
            
            # Asignar content_frame al frame estático
            self.content_frame = self.static_frame
            
            # Desactivar eventos de scroll
            self.canvas.unbind_all("<MouseWheel>")
        else:
            # ✅ PASO 4: CON SCROLL - Contenido dinámico
            # Ocultar frame estático
            self.static_frame.pack_forget()
            
            # Mostrar canvas
            self.canvas.pack(side="left", fill="both", expand=True)
            
            # Asignar content_frame al frame scrollable
            self.content_frame = self.scrollable_frame
            
            # Resetear scroll al inicio
            self.canvas.yview_moveto(0)
            
            # Activar eventos de scroll
            self.bind_mouse_scroll(self.canvas)
        
        # Resetear botón "Generar Link" si existe (al cambiar de paso)
        if hasattr(self, 'generate_link_btn'):
            del self.generate_link_btn
        
        # Mostrar contenido del paso
        if step_number == 1:
            self.create_step1_login()
            # Cargar perfiles AWS cuando se muestra el paso 1
            self.root.after(100, self.load_aws_profiles)
        elif step_number == 2:
            self.create_step2_bucket_selection()
        elif step_number == 3:
            self.create_step3_file_explorer()
        elif step_number == 4:
            self.create_step4_download()
        
        # Actualizar visibilidad del scrollbar SOLO para paso 4
        if step_number == 4:
            self.root.after(100, self._update_scrollbar_visibility)
        
        # Actualizar progreso
        self.update_progress_indicator()
    
    def update_navigation_buttons(self):
        """Actualiza el estado de los botones de navegación - Con colores corporativos"""
        
        # Si hay descarga activa, BLOQUEAR TODA NAVEGACIÓN
        if self.download_in_progress:
            # Durante descarga activa: SOLO mostrar pantalla de descarga
            if self.current_step != 4:
                # Si no estamos en descarga, forzar ir a descarga
                self.show_step(4)
                return
            
            # En pantalla de descarga: BLOQUEAR todos los botones
            self.back_button.pack_forget()  # Ocultar botón volver
            self.next_button.pack_forget()  # Ocultar botón siguiente
            return
        
        # Navegación normal (sin descarga activa)
        # Botón Volver - Gris corporativo elegante
        if self.current_step == 1:
            self.back_button.pack_forget()  # Ocultar completamente
        else:
            self.back_button.pack(side=tk.LEFT, padx=(0, 10))  # Mostrar
            self.back_button.config(state='normal', 
                                   bg=COLORS['secondary'],
                                   activebackground=COLORS['primary_light'],
                                   text="← Volver")
        
        # Botón Continuar - Lógica específica por paso con colores corporativos
        if self.current_step == 1:
            # Asegurar que el botón esté empaquetado
            self.next_button.pack(side=tk.RIGHT, padx=(10, 0))
            # Habilitar solo si hay conexión exitosa - Verde corporativo
            if self.session and self.s3_client:
                self.next_button.config(state='normal', 
                                       bg=COLORS['success'],
                                       activebackground=COLORS['success_hover'],
                                       text="Continuar →", fg='white')
            else:
                self.next_button.config(state='disabled', 
                                       bg=COLORS['border'],
                                       activebackground=COLORS['border'],
                                       text="Continuar →", 
                                       fg=COLORS['text_secondary'])
        elif self.current_step == 2:
            # Asegurar que el botón esté empaquetado
            self.next_button.pack(side=tk.RIGHT, padx=(10, 0))
            # Habilitar solo si hay bucket seleccionado - Azul corporativo
            if self.selected_bucket:
                self.next_button.config(state='normal', 
                                       bg=COLORS['accent'],
                                       activebackground=COLORS['accent_hover'],
                                       text="Continuar →", fg='white')
            else:
                self.next_button.config(state='disabled', 
                                       bg=COLORS['border'],
                                       activebackground=COLORS['border'],
                                       text="Continuar →", 
                                       fg=COLORS['text_secondary'])
        elif self.current_step == 3:
            # Asegurar que el botón esté empaquetado
            self.next_button.pack(side=tk.RIGHT, padx=(10, 0))
            # En explorador: mostrar según archivo seleccionado - Azul corporativo
            if self.selected_file_info and not self.download_in_progress:
                # Hay archivo seleccionado y no hay descarga activa
                self.next_button.config(state='normal', 
                                       bg=COLORS['accent'],
                                       activebackground=COLORS['accent_hover'],
                                       text="🔽 Descargar", fg='white')
            else:
                # No hay archivo seleccionado
                self.next_button.config(state='disabled', 
                                       bg=COLORS['border'],
                                       activebackground=COLORS['border'],
                                       text="Seleccionar archivo", 
                                       fg=COLORS['text_secondary'])
        elif self.current_step == 4:
            # En descarga - asegurar que el botón esté empaquetado
            self.next_button.pack(side=tk.RIGHT, padx=(10, 0))
            # En descarga - siempre permite volver al explorador - Gris corporativo
            self.next_button.config(state='normal', 
                                   bg=COLORS['secondary'],
                                   activebackground=COLORS['primary_light'],
                                   text="← Volver al Explorador", fg='white')
        
        # Agregar indicador global de descarga si hay descarga activa
        self.update_global_download_indicator()
    
    def update_global_download_indicator(self):
        """Actualiza el indicador global de descarga en progreso"""
        # Verificar si ya existe el indicador
        if not hasattr(self, 'global_download_indicator'):
            # Crear indicador global en la barra de status
            self.global_download_indicator = None
        
        # Durante descarga activa ya no necesitamos indicador global
        # porque el usuario está forzado a estar en la pantalla de descarga
        # Ocultar indicador siempre
        if self.global_download_indicator:
            self.global_download_indicator.destroy()
            self.global_download_indicator = None
    
    def smart_go_back(self):
        """Navegación inteligente: va atrás en explorador o vuelve al step anterior - MEJORADO para PRE/"""
        # Durante descarga activa: BLOQUEAR TODA NAVEGACIÓN
        if self.download_in_progress:
            return  # No hacer nada durante descarga
        
        # Navegación normal (sin descarga activa)
        if self.current_step == 3:
            # En el explorador: verificar si hay historial de navegación
            if hasattr(self, 'navigation_history') and self.navigation_history:
                # Limpiar selección y desactivar botón "Generar Link" al navegar hacia atrás
                self.selected_file_info = None
                if hasattr(self, 'generate_link_btn'):
                    self.generate_link_btn.config(state='disabled', bg=COLORS['border'])
                
                # Hay historial - navegar una carpeta atrás en el explorador
                previous_path = self.navigation_history.pop()
                
                # SOLUCION: Limpiar prefijos problemáticos del historial
                if previous_path:
                    previous_path = previous_path.replace('//', '/').rstrip('/')
                    if previous_path:
                        previous_path += '/'
                
                self.log(f"⬅️ Volviendo a: '{previous_path or 'raíz'}'", "INFO")
                # Actualizar status al navegar hacia atrás
                self.update_status("📂 Cargando...")
                self.load_bucket_contents(previous_path)
            else:
                # No hay historial - volver al paso anterior (selección de buckets)
                self.log("⬅️ Sin historial, volviendo a selección de buckets", "INFO")
                self.show_step(self.current_step - 1)
        else:
            # Para otros pasos, comportamiento normal (incluyendo paso 4)
            self.go_to_previous_step()

    def go_to_previous_step(self):
        """Va al paso anterior"""
        # Durante descarga activa: BLOQUEAR TODA NAVEGACIÓN
        if self.download_in_progress:
            return  # No hacer nada durante descarga
            
        # Navegación normal (sin descarga)
        if self.current_step > 1:
            self.show_step(self.current_step - 1)
    
    def go_to_next_step(self):
        """Va al siguiente paso"""
        # Durante descarga activa: BLOQUEAR TODA NAVEGACIÓN
        if self.download_in_progress:
            return  # No hacer nada durante descarga
        
        # Navegación normal (sin descarga activa)
        if self.current_step == 1 and self.session and self.s3_client:
            # Paso 1 → 2: Login exitoso → Buckets
            self.show_step(2)
        elif self.current_step == 2 and self.selected_bucket:
            # Paso 2 → 3: Bucket seleccionado → Explorador
            self.show_step(3)
        elif self.current_step == 3:
            # Paso 3: Solo si hay archivo seleccionado y no hay descarga activa
            if self.selected_file_info and not self.download_in_progress:
                # Iniciar descarga
                self.show_step(4)
        elif self.current_step == 4:
            # Paso 4: Volver al explorador (solo si no hay descarga activa)
            if not self.download_in_progress:
                self.show_step(3)
        else:
            # Condiciones no cumplidas para navegación
            self.log(f"⚠️ No se puede navegar desde paso {self.current_step}", "WARNING")
    
    def create_step1_login(self):
        """Paso 1: Autenticación AWS SSO - Diseño corporativo elegante"""
        # Card principal centrada con sombra sutil
        card = tk.Frame(self.content_frame, bg=COLORS['surface'], relief='flat', bd=0)
        card.pack(expand=True)
        
        # Contenido de la card con espaciado profesional
        content = tk.Frame(card, bg=COLORS['surface'])
        content.pack(padx=60, pady=40)
        
        # Icono y título corporativo
        header_frame = tk.Frame(content, bg=COLORS['surface'])
        header_frame.pack(pady=(0, 30))
        
        icon_label = tk.Label(header_frame, text="🔐", font=('Segoe UI', 48), 
                             bg=COLORS['surface'])
        icon_label.pack()
        
        title_label = tk.Label(header_frame, text="Autenticación AWS",
                              font=('Segoe UI', 24, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(header_frame, text="Selecciona tu perfil AWS SSO para comenzar",
                                 font=('Segoe UI', 12),
                                 fg=COLORS['text_secondary'],
                                 bg=COLORS['surface'])
        subtitle_label.pack()
        
        # Formulario de login con estilo corporativo
        form_frame = tk.Frame(content, bg=COLORS['surface'])
        form_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Label del perfil con tipografía profesional
        profile_label = tk.Label(form_frame, text="Perfil AWS SSO:",
                                font=('Segoe UI', 12, 'bold'),
                                fg=COLORS['text_primary'],
                                bg=COLORS['surface'])
        profile_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Combobox del perfil con estilo corporativo
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(form_frame,
                                         textvariable=self.profile_var,
                                         state='readonly',
                                         font=('Segoe UI', 11),
                                         width=40)
        self.profile_combo.pack(pady=(0, 20))
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_selected)
        
        # 🎯 Botón conectar - Azul corporativo prominente
        self.connect_btn = tk.Button(form_frame,
                                    text="🔗 Conectar a AWS",
                                    font=('Segoe UI', 14, 'bold'),
                                    bg=COLORS['accent'],
                                    fg='white',
                                    activebackground=COLORS['accent_hover'],
                                    activeforeground='white',
                                    bd=0,
                                    padx=35,
                                    pady=14,
                                    cursor='hand2',
                                    relief='flat',
                                    command=self.connect_to_aws)
        self.connect_btn.pack(pady=10)
    
    def create_step2_bucket_selection(self):
        """Paso 2: Selección de Bucket S3 - Diseño corporativo elegante"""
        # Card principal centrada con estilo corporativo
        card = tk.Frame(self.content_frame, bg=COLORS['surface'], relief='flat', bd=0)
        card.pack(expand=True)
        
        # Contenido de la card con padding profesional
        content = tk.Frame(card, bg=COLORS['surface'])
        content.pack(padx=60, pady=40)
        
        # Icono y título corporativo
        header_frame = tk.Frame(content, bg=COLORS['surface'])
        header_frame.pack(pady=(0, 30))
        
        icon_label = tk.Label(header_frame, text="🪣", font=('Segoe UI', 48), 
                             bg=COLORS['surface'])
        icon_label.pack()
        
        title_label = tk.Label(header_frame, text="Selección de Bucket",
                              font=('Segoe UI', 24, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(pady=(10, 5))
        
        subtitle_label = tk.Label(header_frame, text="Elige el bucket S3 que contiene tus backups",
                                 font=('Segoe UI', 12),
                                 fg=COLORS['text_secondary'],
                                 bg=COLORS['surface'])
        subtitle_label.pack()
        
        # Formulario de selección con estilo profesional
        form_frame = tk.Frame(content, bg=COLORS['surface'])
        form_frame.pack(fill=tk.BOTH, expand=True, pady=20)
        
        # Label del bucket con tipografía corporativa
        bucket_label = tk.Label(form_frame, text="Bucket S3:",
                               font=('Segoe UI', 12, 'bold'),
                               fg=COLORS['text_primary'],
                               bg=COLORS['surface'])
        bucket_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Combobox del bucket con estilo corporativo
        self.bucket_var = tk.StringVar()
        self.bucket_combo = ttk.Combobox(form_frame,
                                        textvariable=self.bucket_var,
                                        state='readonly',
                                        font=('Segoe UI', 11),
                                        width=40)
        self.bucket_combo.pack(pady=(0, 20))
        self.bucket_combo.bind('<<ComboboxSelected>>', self.on_bucket_selected)
        
        # Status del bucket con colores corporativos
        self.bucket_status = tk.Label(form_frame, text="Cargando buckets...",
                                     font=('Segoe UI', 11),
                                     fg=COLORS['text_secondary'],
                                     bg=COLORS['surface'])
        self.bucket_status.pack(pady=(10, 0))
        
        # Cargar buckets automáticamente
        if self.session:
            self.load_buckets()
    
    def create_step3_file_explorer(self):
        """Paso 3: Explorador S3 - Diseño corporativo profesional"""
        # Título del paso con estilo corporativo
        title_frame = tk.Frame(self.content_frame, bg=COLORS['background'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(title_frame, text=f"📁 Explorador: {self.selected_bucket}",
                              font=('Segoe UI', 18, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['background'])
        title_label.pack()
        
        # Explorador principal con estilo corporativo
        explorer_frame = tk.Frame(self.content_frame, bg=COLORS['surface'])
        explorer_frame.pack(fill=tk.BOTH, expand=True)
        
        # Treeview para archivos con altura optimizada
        tree_frame = tk.Frame(explorer_frame, bg=COLORS['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(20, 10))
        
        self.tree = ttk.Treeview(tree_frame, 
                                height=12,
                                selectmode='extended')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar corporativa
        tree_scroll = ttk.Scrollbar(tree_frame, 
                                   orient="vertical", 
                                   command=self.tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Configurar columnas con iconos profesionales
        self.tree['columns'] = ('size', 'type')
        self.tree.column('#0', width=300, minwidth=200)
        self.tree.column('size', width=100, minwidth=80)
        self.tree.column('type', width=100, minwidth=80)
        
        self.tree.heading('#0', text='📄 Nombre', anchor=tk.W)
        self.tree.heading('size', text='📊 Tamaño', anchor=tk.W)
        self.tree.heading('type', text='🏷️ Tipo', anchor=tk.W)
        
        # Binds para interacción intuitiva
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Breadcrumb y controles corporativos (SIEMPRE VISIBLE)
        controls_frame = tk.Frame(explorer_frame, bg=COLORS['surface'])
        controls_frame.pack(fill=tk.X, padx=20, pady=(10, 20), side=tk.BOTTOM)
        
        # Breadcrumb con tipografía profesional
        self.breadcrumb_label = tk.Label(controls_frame,
                                        text="📍 Ruta: /",
                                        font=('Segoe UI', 10),
                                        fg=COLORS['text_secondary'],
                                        bg=COLORS['surface'])
        self.breadcrumb_label.pack(side=tk.LEFT)
        
        # 🎯 Botón generar link - Naranja corporativo elegante
        self.generate_link_btn = tk.Button(controls_frame,
                               text="⚡ Generar Link",
                               font=('Segoe UI', 10, 'bold'),
                               bg=COLORS['warning'],
                               fg='white',
                               activebackground=COLORS['warning_hover'],
                               activeforeground='white',
                               bd=0,
                               padx=20,
                               pady=7,
                               cursor='hand2',
                               relief='flat',
                               state='disabled',
                               command=self.generate_presigned_url)
        self.generate_link_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # 🎯 Botón actualizar - Azul corporativo vibrante
        refresh_btn = tk.Button(controls_frame,
                               text="↻ Actualizar",
                               font=('Segoe UI', 10, 'bold'),
                               bg=COLORS['accent'],
                               fg='white',
                               activebackground=COLORS['accent_hover'],
                               activeforeground='white',
                               bd=0,
                               padx=20,
                               pady=7,
                               cursor='hand2',
                               relief='flat',
                               command=self.refresh_tree)
        refresh_btn.pack(side=tk.RIGHT, padx=(15, 0))
        
        # Cargar contenido del bucket
        if self.selected_bucket:
            # Limpiar historial de navegación al iniciar exploración
            self.navigation_history = []
            self.current_path = ""
            
            # Asegurar que no hay archivo seleccionado y botón desactivado al inicio
            self.selected_file_info = None
            if hasattr(self, 'generate_link_btn'):
                self.generate_link_btn.config(state='disabled', bg=COLORS['border'])
            
            self.load_bucket_contents()
    
    def create_step4_download(self):
        """Paso 4: Descarga de archivos - Diseño corporativo elegante"""
        if not self.selected_file_info:
            return
        
        # Card principal centrada con estilo corporativo
        card = tk.Frame(self.content_frame, bg=COLORS['surface'], relief='flat', bd=0)
        card.pack(expand=True)
        
        # Contenido de la card con padding profesional
        content = tk.Frame(card, bg=COLORS['surface'])
        content.pack(padx=60, pady=40)
        
        # Icono y título corporativo
        header_frame = tk.Frame(content, bg=COLORS['surface'])
        header_frame.pack(pady=(0, 30))
        
        icon_label = tk.Label(header_frame, text="⬇️", font=('Segoe UI', 48), 
                             bg=COLORS['surface'])
        icon_label.pack()
        
        title_label = tk.Label(header_frame, text="Descarga en Progreso",
                              font=('Segoe UI', 24, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(pady=(10, 5))
        
        # Información del archivo con tipografía profesional
        file_info_frame = tk.Frame(content, bg=COLORS['surface'])
        file_info_frame.pack(pady=20)
        
        file_name_label = tk.Label(file_info_frame, text=f"📄 {self.selected_file_info['name']}",
                                  font=('Segoe UI', 14, 'bold'),
                                  fg=COLORS['text_primary'],
                                  bg=COLORS['surface'])
        file_name_label.pack()
        
        file_size_label = tk.Label(file_info_frame, text=f"📊 Tamaño: {self.selected_file_info.get('size', 'Desconocido')}",
                                  font=('Segoe UI', 11),
                                  fg=COLORS['text_secondary'],
                                  bg=COLORS['surface'])
        file_size_label.pack(pady=(5, 0))
        
        # Progress bar corporativa elegante
        progress_frame = tk.Frame(content, bg=COLORS['surface'])
        progress_frame.pack(fill=tk.X, pady=30)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           maximum=100,
                                           length=400)
        self.progress_bar.pack()
        
        self.progress_label = tk.Label(progress_frame, text="Preparando descarga...",
                                      font=('Segoe UI', 11),
                                      fg=COLORS['text_secondary'],
                                      bg=COLORS['surface'])
        self.progress_label.pack(pady=(10, 0))
        
        # Mensaje de navegación bloqueada con estilo corporativo
        if self.download_in_progress:
            lock_frame = tk.Frame(progress_frame, bg=COLORS['surface'])
            lock_frame.pack(pady=(20, 0))
            
            lock_label = tk.Label(lock_frame, text="🔒 Navegación bloqueada durante descarga",
                                font=('Segoe UI', 10, 'italic'),
                                fg=COLORS['warning'],
                                bg=COLORS['surface'])
            lock_label.pack()
        
        # Manejar diferentes estados de descarga profesionalmente
        if self.download_completed:
            # Descarga ya completada - Verde corporativo
            self.progress_var.set(100)
            self.progress_label.config(text="✅ Descarga completada", 
                                      fg=COLORS['success'])
            title_label.config(text="Descarga Completada")
        elif self.download_in_progress:
            # Descarga en progreso - Azul corporativo
            title_label.config(text="Descarga en Progreso")
            # Los valores de progreso se mantendrán actualizados por el thread
        else:
            # Nueva descarga - Iniciar automáticamente
            title_label.config(text="Iniciando Descarga")
            self.root.after(500, self.start_download)
    
    def on_profile_selected(self, event=None):
        """Callback cuando se selecciona un perfil"""
        if self.profile_var.get():
            self.connect_btn.configure(state='normal')
    
    def connect_to_aws(self):
        """Conectar con AWS usando el perfil seleccionado - TODO EN HILO SEPARADO"""
        profile_name = self.profile_var.get()
        if not profile_name:
            messagebox.showwarning("Advertencia", "Selecciona un perfil AWS SSO")
            return
        
        # Cambiar UI inmediatamente para mostrar que está procesando
        self.connect_btn.configure(text="⏳ Conectando...", state='disabled')
        self.update_status("🔑 Verificando credenciales...")
        self.log_message(f"Iniciando conexión para perfil: {profile_name}")
        
        # Ejecutar TODO en hilo separado para evitar bloquear la UI
        threading.Thread(target=self._perform_aws_connection_thread, 
                        args=(profile_name,), 
                        daemon=True).start()
    
    def _perform_aws_connection_thread(self, profile_name):
        """Ejecuta toda la conexión AWS en hilo separado para evitar bloquear UI"""
        try:
            # Actualizar UI de forma thread-safe con animación
            for i in range(3):
                dots = "." * (i + 1)
                self.root.after(0, lambda d=dots: self.update_status(f"🔑 Verificando credenciales{d}"))
                time.sleep(0.5)
            
            # Intentar manejar automáticamente las credenciales SSO
            success, message = auto_handle_sso_credentials(profile_name)
            
            if not success:
                # Manejar error de credenciales en hilo principal
                self.root.after(0, lambda: self._handle_credentials_error(message, profile_name))
                return
            
            # Credenciales OK, proceder con la conexión
            self.root.after(0, lambda: self.update_status("⏳ Estableciendo conexión AWS..."))
            self.root.after(0, lambda: self.log_message(f"Credenciales válidas, conectando..."))
            
            # Crear sesión
            session = boto3.Session(profile_name=profile_name)
            s3_client = session.client('s3')
            
            # Verificar conexión
            s3_client.list_buckets()
            
            # Actualizar instancia con conexión exitosa
            self.session = session
            self.s3_client = s3_client
            
            # Actualizar UI en hilo principal con éxito
            self.root.after(0, lambda: self._handle_connection_success(profile_name))
            
        except Exception as e:
            # Manejar error de conexión en hilo principal
            self.root.after(0, lambda: self._handle_connection_error(str(e), profile_name))
    
    def _handle_credentials_error(self, message, profile_name):
        """Maneja errores de credenciales en el hilo principal"""
        self.log_message(f"Error en credenciales SSO: {message}")
        
        # Preguntar si quiere intentar login manual
        result = messagebox.askyesno(
            "Credenciales SSO", 
            f"Error con credenciales SSO: {message}\n\n"
            "¿Quieres intentar hacer login SSO manualmente?\n"
            "(Se abrirá una ventana del navegador para autenticarte)"
        )
        
        if result:
            self.connect_btn.configure(text="🔐 Iniciando sesión SSO...", state='disabled')
            self.log_message("Iniciando login SSO manual...")
            
            # Ejecutar login SSO en thread separado
            threading.Thread(target=self._sso_login_thread, args=(profile_name,), daemon=True).start()
        else:
            self.connect_btn.configure(text="🔗 Conectar a AWS", state='normal')
    
    def _handle_connection_success(self, profile_name):
        """Maneja conexión exitosa en el hilo principal - Estilo corporativo"""
        self.log_message(f"✅ Conectado exitosamente con perfil: {profile_name}")
        
        # 🎯 Botón de éxito con verde corporativo elegante
        self.connect_btn.configure(text="✅ Conectado", 
                                 bg=COLORS['success'],
                                 activebackground=COLORS['success_hover'],
                                 state='disabled')
        
        # Habilitar navegación al siguiente paso
        self.update_navigation_buttons()
        self.update_status("✅ Conectado exitosamente")
    
    def _handle_connection_error(self, error_msg, profile_name):
        """Maneja errores de conexión en el hilo principal"""
        self.log_message(f"❌ Error de conexión: {error_msg}")
        
        # Detectar errores específicos de SSO
        if any(keyword in error_msg.lower() for keyword in ['token', 'credentials', 'sso', 'unauthorized', 'expired']):
            messagebox.showerror(
                "Error de Credenciales", 
                f"Error de credenciales AWS SSO:\n{error_msg}\n\n"
                "Posibles soluciones:\n"
                "1. Ejecuta: aws sso login --profile " + profile_name + "\n"
                "2. Verifica que tengas permisos en AWS\n"
                "3. Comprueba tu conexión a internet"
            )
        else:
            messagebox.showerror("Error", f"Error conectando con AWS:\n{error_msg}")
        
        self.connect_btn.configure(text="🔗 Conectar a AWS", state='normal')
        self.update_status("❌ Error de conexión")
    
    def _sso_login_thread(self, profile_name):
        """Ejecuta el login SSO en un thread separado"""
        try:
            success, message = perform_sso_login(profile_name)
            
            # Actualizar UI en el thread principal
            self.root.after(0, lambda: self._handle_sso_login_result(success, message, profile_name))
            
        except Exception as e:
            self.root.after(0, lambda: self._handle_sso_login_result(False, f"Error: {str(e)}", profile_name))
    
    def _handle_sso_login_result(self, success, message, profile_name):
        """Maneja el resultado del login SSO"""
        if success:
            self.log_message(f"✅ {message}")
            messagebox.showinfo("Login SSO", f"Login SSO exitoso!\n\nIntentando conectar nuevamente...")
            
            # Reintentar conexión automáticamente
            self.root.after(1000, self.connect_to_aws)
        else:
            self.log_message(f"❌ {message}")
            messagebox.showerror(
                "Error Login SSO", 
                f"Error en login SSO:\n{message}\n\n"
                "Por favor, ejecuta manualmente:\n"
                f"aws sso login --profile {profile_name}"
            )
            self.connect_btn.configure(text="🔗 Conectar a AWS", state='normal')
    
    def load_buckets(self):
        """Cargar buckets S3 disponibles"""
        if not self.session:
            return
        
        try:
            self.bucket_status.configure(text="Cargando buckets...", fg=COLORS['text_secondary'])
            
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            
            self.bucket_combo['values'] = buckets
            
            if buckets:
                self.bucket_status.configure(text=f"✅ {len(buckets)} buckets disponibles", 
                                           fg=COLORS['success'])
            else:
                self.bucket_status.configure(text="⚠️ No se encontraron buckets", 
                                           fg=COLORS['warning'])
                
            self.log_message(f"Cargados {len(buckets)} buckets")
            
        except Exception as e:
            self.bucket_status.configure(text="❌ Error cargando buckets", fg=COLORS['danger'])
            self.log_message(f"Error cargando buckets: {str(e)}")
            messagebox.showerror("Error", f"Error cargando buckets:\n{str(e)}")
    
    def on_bucket_selected(self, event=None):
        """Callback cuando se selecciona un bucket"""
        bucket_name = self.bucket_var.get()
        if bucket_name:
            self.selected_bucket = bucket_name
            self.log_message(f"Bucket seleccionado: {bucket_name}")
            self.update_navigation_buttons()
    
    def load_bucket_contents(self, prefix=''):
        """Cargar contenido del bucket S3 - MEJORADO para navegación robusta y carpetas PRE/"""
        if not self.s3_client or not self.selected_bucket:
            return
        
        # Normalizar prefijo para evitar problemas de navegación
        if prefix:
            # Asegurar que el prefijo termine en '/' para navegación de carpetas
            if not prefix.endswith('/'):
                prefix = prefix + '/'
            # Limpiar barras dobles
            prefix = prefix.replace('//', '/')
        
        # NUEVO: Actualizar current_path para navegación consistente
        self.current_path = prefix
        
        self.log(f"🔍 Cargando contenido: s3://{self.selected_bucket}/{prefix}", "INFO")
        
        try:
            self.tree.delete(*self.tree.get_children())
            
            # Limpiar el diccionario de claves de archivos
            if hasattr(self, '_file_keys'):
                self._file_keys.clear()
            else:
                self._file_keys = {}
            
            # SOLUCION: Usar list_objects_v2 con Delimiter para obtener CommonPrefixes
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.selected_bucket,
                Prefix=prefix,
                Delimiter='/'  # ← CRITICO: Esto separa carpetas de archivos
            )
            
            folders_found = []
            files_found = []
            
            for page in page_iterator:
                # SOLUCION PARTE 1: Procesar CommonPrefixes (SUBCARPETAS)
                # Esto resuelve el problema de carpetas vacías y PRE/
                for prefix_info in page.get('CommonPrefixes', []):
                    full_prefix = prefix_info['Prefix']
                    # Extraer solo el nombre de la carpeta (último segmento)
                    folder_name = full_prefix.rstrip('/').split('/')[-1]
                    
                    # SOLUCION CRITICA: Manejar el caso especial "PRE /" (con barra)
                    if not folder_name or folder_name == '':
                        # Este es el caso específico de "PRE /" - una subcarpeta oculta
                        # Ejemplo: s3://bucket/path/ → CommonPrefix: "path//" → folder_name = ""
                        
                        # Intentar detectar subcarpetas ocultas explorando un nivel más profundo
                        try:
                            # Hacer una consulta adicional para ver qué hay en este prefijo
                            deep_response = self.s3_client.list_objects_v2(
                                Bucket=self.selected_bucket,
                                Prefix=full_prefix,
                                Delimiter='/',
                                MaxKeys=10
                            )
                            
                            # Si encontramos CommonPrefixes, son las subcarpetas reales
                            deep_prefixes = deep_response.get('CommonPrefixes', [])
                            if deep_prefixes:
                                self.log(f"🔍 Detectado prefijo oculto '{full_prefix}' con {len(deep_prefixes)} subcarpetas", "WARNING")
                                
                                # Agregar cada subcarpeta encontrada
                                for deep_prefix_info in deep_prefixes:
                                    deep_full_prefix = deep_prefix_info['Prefix']
                                    deep_folder_name = deep_full_prefix.rstrip('/').split('/')[-1]
                                    
                                    if deep_folder_name and deep_folder_name not in folders_found:
                                        folders_found.append(deep_folder_name)
                                        
                                        # Icono especial para carpetas encontradas via exploración profunda
                                        self.tree.insert('', 'end', 
                                                        text=f"🔍 {deep_folder_name}",
                                                        values=('--', 'Carpeta (detectada)'),
                                                        tags=('folder',))
                                        
                                        # Guardar el prefijo completo para navegación correcta
                                        if not hasattr(self, '_folder_prefixes'):
                                            self._folder_prefixes = {}
                                        # CORRECCION CRITICA: Mantener la estructura de doble barra
                                        self._folder_prefixes[deep_folder_name] = deep_full_prefix
                                        
                                        self.log(f"🔍 Subcarpeta detectada profunda: '{deep_folder_name}' → '{deep_full_prefix}'", "SUCCESS")
                                        self.log(f"💾 Prefijo guardado: '{deep_folder_name}' = '{deep_full_prefix}'", "INFO")
                            
                        except Exception as e:
                            self.log(f"⚠️ Error explorando prefijo oculto '{full_prefix}': {e}", "WARNING")
                            # Si falla, crear una entrada genérica
                            folder_name = "Carpetas (explorar manualmente)"
                            
                        # Si aún no hay nombre, saltar este prefijo
                        if not folder_name or folder_name == '':
                            self.log(f"⚠️ Prefijo sin nombre detectado: '{full_prefix}' - omitido", "WARNING")
                            continue
                    
                    # SOLUCION ADICIONAL: Manejar nombres de carpetas normales
                    if folder_name and folder_name not in folders_found:
                        folders_found.append(folder_name)
                        
                        # MEJORA: Iconos especiales para diferentes tipos de carpetas
                        if folder_name.upper() in ['PRE', 'PREFIX']:
                            icon = "🔧"
                        elif folder_name in getattr(self, '_folder_prefixes', {}):
                            icon = "🔍"  # Carpetas detectadas por exploración profunda
                        else:
                            icon = "📁"
                        
                        self.tree.insert('', 'end', 
                                        text=f"{icon} {folder_name}",
                                        values=('--', 'Carpeta'),
                                        tags=('folder',))
                        
                        # Log para navegación
                        if folder_name.upper() in ['PRE', 'PREFIX']:
                            self.log(f"🔧 Carpeta especial: '{folder_name}' → '{full_prefix}'", "WARNING")
                        else:
                            self.log(f"📁 Subcarpeta: '{folder_name}' → '{full_prefix}'", "INFO")
                
                # SOLUCION PARTE 2: Procesar Contents (ARCHIVOS DIRECTOS)
                for obj in page.get('Contents', []):
                    file_key = obj['Key']
                    
                    # Verificar que no sea el directorio mismo
                    if file_key.endswith('/'):
                        continue
                        
                    # Extraer nombre del archivo
                    file_name = file_key.split('/')[-1]
                    if not file_name:  # Skip si no hay nombre
                        continue
                        
                    # Verificar que sea un archivo de backup válido
                    if not any(file_name.lower().endswith(ext) for ext in BACKUP_EXTENSIONS):
                        self.log(f"📄 Archivo ignorado (no es backup): '{file_name}'", "INFO")
                        continue
                        
                    size = self.format_size(obj['Size'])
                    file_type = file_name.split('.')[-1].upper() if '.' in file_name else 'Archivo'
                    
                    # Crear item y guardar la clave completa
                    item_id = self.tree.insert('', 'end',
                                    text=f"📄 {file_name}",
                                    values=(size, file_type),
                                    tags=('file',))
                    
                    # Guardar la clave completa del objeto S3
                    if not hasattr(self, '_file_keys'):
                        self._file_keys = {}
                    self._file_keys[item_id] = file_key
                    files_found.append(file_name)
                    
                    # Log del archivo encontrado
                    self.log(f"📄 Archivo válido: '{file_name}' → '{file_key}'", "INFO")
            
            # Actualizar breadcrumb con indicador especial para PRE/
            display_path = prefix.rstrip('/') if prefix else 'Raíz'
            breadcrumb_text = f"📍 Ruta: {display_path}"
            if 'pre' in display_path.lower():
                breadcrumb_text += " 🔧"
            
            self.breadcrumb_label.configure(text=breadcrumb_text)
            
            # Log resumen de lo encontrado con indicadores especiales
            summary_msg = f"📂 Contenido cargado: {len(folders_found)} carpetas, {len(files_found)} archivos"
            if any('pre' in f.lower() for f in folders_found):
                summary_msg += " (incluye carpetas PRE especiales) 🔧"
            
            self.log(summary_msg, "SUCCESS")
            
            # Mostrar mensaje si no hay contenido
            if len(folders_found) == 0 and len(files_found) == 0:
                self.log(f"⚠️ No se encontró contenido en: {self.selected_bucket}/{prefix}", "WARNING")
                # Mostrar un mensaje en el tree
                self.tree.insert('', 'end',
                               text="💭 No hay archivos de backup en esta ubicación",
                               values=('', 'Probar navegación directa'),
                               tags=('info',))
            
        except Exception as e:
            self.log(f"❌ Error cargando contenido: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Error cargando contenido del bucket:\n{str(e)}")
    
    def on_tree_double_click(self, event=None):
        """Callback para doble click en el árbol - SOLUCIONADO para navegación PRE/ y prefijos S3"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            item_text = self.tree.item(item, 'text')
            
            if any(item_text.startswith(icon) for icon in ['📁', '🔧', '🔍']):
                # Es una carpeta (normal, PRE, o detectada por exploración profunda)
                folder_name = item_text[2:].strip()  # Remover emoji y espacios
                
                # SOLUCION NUEVA: Verificar si tenemos un prefijo prealmacenado (exploración profunda)
                if hasattr(self, '_folder_prefixes') and folder_name in self._folder_prefixes:
                    # Usar el prefijo exacto detectado por exploración profunda
                    new_prefix = self._folder_prefixes[folder_name]
                    self.log(f"🔍 Usando prefijo detectado: '{folder_name}' → '{new_prefix}'", "SUCCESS")
                else:
                    # Log si no encuentra prefijo almacenado
                    if hasattr(self, '_folder_prefixes'):
                        available_prefixes = list(self._folder_prefixes.keys())
                        self.log(f"⚠️ Prefijo para '{folder_name}' no encontrado. Disponibles: {available_prefixes}", "WARNING")
                    else:
                        self.log(f"⚠️ No hay prefijos almacenados (_folder_prefixes no existe)", "WARNING")
                    # Construcción tradicional de prefijo
                    current_prefix = getattr(self, 'current_path', '')
                    
                    # Construir el nuevo prefijo S3 de manera inteligente
                    if not current_prefix or current_prefix == '':
                        # Estamos en la raíz del bucket
                        new_prefix = folder_name + "/"
                    else:
                        # Estamos en una subcarpeta
                        if current_prefix.endswith('/'):
                            new_prefix = current_prefix + folder_name + "/"
                        else:
                            new_prefix = current_prefix + "/" + folder_name + "/"
                    
                    # SOLUCION CRITICA: Casos especiales para carpetas PRE/
                    if folder_name in ['PRE', 'pre', 'Pre']:
                        self.log(f"🔧 Detectada carpeta PRE especial. Construyendo prefijo con estrategia adaptativa.", "WARNING")
                        # Para carpetas PRE, usar estrategias múltiples
                        potential_prefixes = [
                            current_prefix + "PRE/",
                            current_prefix + "/" + "PRE/",
                            current_prefix + "pre/",
                            current_prefix + "/" + "pre/",
                            current_prefix + "/",  # Caso especial: doble barra
                            current_prefix + "//"   # Caso específico encontrado en CLI
                        ]
                        
                        # Probar cuál prefijo devuelve contenido
                        for test_prefix in potential_prefixes:
                            test_prefix = test_prefix.replace('///', '//').replace('////', '//')  # Limpiar múltiples barras
                            
                            try:
                                # Verificación rápida de contenido
                                response = self.s3_client.list_objects_v2(
                                    Bucket=self.selected_bucket,
                                    Prefix=test_prefix,
                                    Delimiter='/',
                                    MaxKeys=1  # Solo queremos saber si hay algo
                                )
                                
                                # Si encontramos contenido, usar este prefijo
                                if (response.get('Contents') or response.get('CommonPrefixes')):
                                    new_prefix = test_prefix
                                    self.log(f"✅ Prefijo PRE exitoso: '{new_prefix}'", "SUCCESS")
                                    break
                            except Exception as e:
                                self.log(f"❌ Error probando prefijo '{test_prefix}': {e}", "ERROR")
                                continue
                
                # CASO ESPECIAL: Carpetas con nombres vacíos o problemáticos
                if not folder_name or folder_name in ['/', '']:
                    self.log(f"⚠️ Carpeta con nombre problemático detectada. Usando navegación alternativa.", "WARNING")
                    # En estos casos, intentar ir un nivel más profundo
                    current_prefix = getattr(self, 'current_path', '')
                    new_prefix = current_prefix + "/"
                
                # Limpiar el prefijo final para evitar barras problemáticas
                new_prefix = new_prefix.replace('///', '//').replace('////', '//')
                
                # Guardar historial para navegación hacia atrás
                if not hasattr(self, 'navigation_history'):
                    self.navigation_history = []
                current_prefix = getattr(self, 'current_path', '')
                self.navigation_history.append(current_prefix)
                
                # Actualizar current_path para próximas navegaciones
                self.current_path = new_prefix
                
                self.log(f"📂 Navegando: '{folder_name}' → Prefijo S3: '{new_prefix}'", "INFO")
                self.update_status("📂 Cargando contenido...")
                
                # Limpiar selección y desactivar botones al navegar
                self.selected_file_info = None
                if hasattr(self, 'generate_link_btn'):
                    self.generate_link_btn.config(state='disabled', bg=COLORS['border'])
                
                self.load_bucket_contents(new_prefix)
                
            elif item_text.startswith('📄'):
                # Es un archivo - Solo mostrar información, NO navegar automáticamente
                self.log(f"� Archivo seleccionado: {item_text[2:].strip()}", "INFO")
                # No hacer nada más - la descarga debe hacerse solo con el botón DESCARGAR
    
    def refresh_tree(self):
        """Refrescar el árbol de archivos"""
        current_prefix = self.breadcrumb_label.cget('text').replace('📍 Ruta: /', '')
        if current_prefix == '':
            prefix = ''
        else:
            prefix = current_prefix
        self.load_bucket_contents(prefix)
    
    def generate_presigned_url(self):
        """Genera una URL pre-firmada temporal para descargar el archivo seleccionado"""
        if not self.selected_file_info:
            messagebox.showwarning(
                "⚠️ Advertencia",
                "Debes seleccionar un archivo primero."
            )
            return
        
        if not self.s3_client or not self.selected_bucket:
            messagebox.showerror(
                "❌ Error",
                "No hay conexión activa con S3."
            )
            return
        
        try:
            file_info = self.selected_file_info
            file_key = file_info['key']
            file_name = file_info['name']
            
            self.log(f"🔗 Generando link temporal para: {file_name}", "INFO")
            self.update_status("🔗 Generando link...")
            
            # 🎨 Crear diálogo de configuración ELEGANTE y CORPORATIVO
            expiration_dialog = tk.Toplevel(self.root)
            expiration_dialog.title("⏱️ Configuración del Link")
            expiration_dialog.geometry("580x340")  # Más ancho y alto para mejor apariencia
            expiration_dialog.resizable(False, False)
            expiration_dialog.configure(bg=COLORS['background'])
            expiration_dialog.transient(self.root)
            expiration_dialog.grab_set()
            
            # 🎯 SOLUCIÓN: Centrar sobre la ventana PRINCIPAL, no en la pantalla
            expiration_dialog.update_idletasks()
            
            # Obtener posición y tamaño de la ventana principal
            parent_x = self.root.winfo_x()
            parent_y = self.root.winfo_y()
            parent_width = self.root.winfo_width()
            parent_height = self.root.winfo_height()
            
            # Calcular posición centrada sobre la ventana principal
            dialog_width = 580
            dialog_height = 340
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            expiration_dialog.geometry(f"+{x}+{y}")
            
            # 🎨 Contenido del diálogo con diseño corporativo elegante
            content_frame = tk.Frame(expiration_dialog, bg=COLORS['surface'])
            content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
            
            # 🎯 Título con icono corporativo
            title_label = tk.Label(content_frame,
                                  text="⏱️ Tiempo de Validez del Link",
                                  font=('Segoe UI', 18, 'bold'),
                                  fg=COLORS['primary'],
                                  bg=COLORS['surface'])
            title_label.pack(pady=(0, 8))
            
            # 📄 Subtítulo con nombre de archivo más destacado
            subtitle_label = tk.Label(content_frame,
                                     text=f"📄 {file_name}",
                                     font=('Segoe UI', 11),
                                     fg=COLORS['text_secondary'],
                                     bg=COLORS['surface'])
            subtitle_label.pack(pady=(0, 20))
            
            # 🎨 Frame para selector con mejor separación
            selector_frame = tk.Frame(content_frame, bg=COLORS['surface'])
            selector_frame.pack(fill=tk.X, pady=(0, 18))
            
            # 📝 Label del selector con estilo corporativo
            duration_label = tk.Label(selector_frame,
                                     text="Duración del link:",
                                     font=('Segoe UI', 12, 'bold'),
                                     fg=COLORS['text_primary'],
                                     bg=COLORS['surface'])
            duration_label.pack(anchor=tk.W, pady=(0, 10))
            
            # 🎯 Combobox desplegable profesional
            expiration_var = tk.StringVar(value="1 hora")  # Valor por defecto
            
            # Mapeo de opciones legibles a segundos
            duration_options = {
                "1 hora": 3600,
                "3 horas": 10800,
                "6 horas": 21600,
                "12 horas": 43200,
                "24 horas (1 día)": 86400,
                "7 días (máximo permitido)": 604800
            }
            
            # Crear combobox moderno con mejor tamaño
            duration_combo = ttk.Combobox(
                selector_frame,
                textvariable=expiration_var,
                values=list(duration_options.keys()),
                state='readonly',
                font=('Segoe UI', 11),
                style='Modern.TCombobox',
                width=42
            )
            duration_combo.pack(fill=tk.X, ipady=8)  # Mayor altura para mejor UX
            
            # 💡 Descripción útil con mejor estilo
            help_label = tk.Label(selector_frame,
                                 text="💡 Tip: Usa la duración más corta necesaria para mayor seguridad",
                                 font=('Segoe UI', 9, 'italic'),
                                 fg=COLORS['info'],
                                 bg=COLORS['surface'])
            help_label.pack(anchor=tk.W, pady=(8, 0))
            
            # Variable para almacenar el resultado
            result_url = {'url': None}
            
            def generate_and_show():
                """Genera el link y muestra el resultado"""
                try:
                    # Obtener los segundos desde el mapeo de opciones
                    selected_text = expiration_var.get()
                    expiration_seconds = duration_options[selected_text]
                    
                    self.log(f"🔧 Obteniendo credenciales actuales...", "INFO")
                    
                    # SOLUCIÓN: Detectar la región correcta del bucket
                    try:
                        # Obtener la región real del bucket
                        bucket_location = self.s3_client.get_bucket_location(Bucket=self.selected_bucket)
                        bucket_region = bucket_location.get('LocationConstraint')
                        
                        # LocationConstraint es None para us-east-1
                        if bucket_region is None:
                            bucket_region = 'us-east-1'
                        
                        self.log(f"📍 Región del bucket detectada: {bucket_region}", "INFO")
                        
                    except Exception as e:
                        self.log(f"⚠️ No se pudo detectar región, usando región de sesión", "WARNING")
                        bucket_region = self.session.region_name or 'us-east-1'
                    
                    # SOLUCIÓN: Crear un cliente S3 fresco con credenciales actualizadas
                    # Y LA REGIÓN CORRECTA del bucket
                    try:
                        # Obtener credenciales actuales de la sesión
                        credentials = self.session.get_credentials()
                        
                        # Verificar que las credenciales sean válidas
                        if not credentials:
                            raise Exception("No se pudieron obtener credenciales válidas")
                        
                        # Crear un nuevo cliente S3 con las credenciales frescas
                        # Y LA REGIÓN CORRECTA (esto es CRÍTICO para evitar el error)
                        fresh_s3_client = self.session.client(
                            's3',
                            region_name=bucket_region,  # ← CRÍTICO: Usar región del bucket
                            config=botocore.config.Config(
                                signature_version='s3v4',  # Usar signature version 4 (requerido)
                                s3={'addressing_style': 'virtual'}
                            )
                        )
                        
                        self.log(f"✅ Cliente S3 creado con región: {bucket_region}", "SUCCESS")
                        
                    except Exception as e:
                        self.log(f"⚠️ Error obteniendo credenciales: {e}", "WARNING")
                        # Fallback: usar el cliente existente
                        fresh_s3_client = self.s3_client
                    
                    # Generar URL pre-firmada con parámetros correctos
                    self.log(f"🔗 Generando URL pre-firmada...", "INFO")
                    
                    presigned_url = fresh_s3_client.generate_presigned_url(
                        ClientMethod='get_object',
                        Params={
                            'Bucket': self.selected_bucket,
                            'Key': file_key,
                            'ResponseContentDisposition': 'inline'
                        },
                        ExpiresIn=expiration_seconds,
                        HttpMethod='GET'
                    )
                    
                    # Validar que la URL tenga los parámetros requeridos
                    if not all(param in presigned_url for param in ['X-Amz-Algorithm', 'X-Amz-Credential', 'X-Amz-Signature']):
                        self.log(f"⚠️ URL generada sin parámetros completos, regenerando...", "WARNING")
                        
                        # Intentar regenerar con método alternativo
                        presigned_url = fresh_s3_client.generate_presigned_url(
                            'get_object',
                            Params={
                                'Bucket': self.selected_bucket,
                                'Key': file_key
                            },
                            ExpiresIn=expiration_seconds
                        )
                    
                    # Verificar que la URL sea válida
                    if not presigned_url or len(presigned_url) < 100:
                        raise Exception("URL generada inválida o incompleta")
                    
                    result_url['url'] = presigned_url
                    
                    # Calcular tiempo de expiración
                    from datetime import datetime, timedelta
                    expiration_time = datetime.now() + timedelta(seconds=expiration_seconds)
                    expiration_str = expiration_time.strftime('%d/%m/%Y %H:%M:%S')
                    
                    # Log de éxito con información de la URL
                    url_length = len(presigned_url)
                    self.log(f"✅ Link generado exitosamente ({url_length} caracteres). Expira: {expiration_str}", "SUCCESS")
                    
                    # COPIAR AUTOMÁTICAMENTE AL PORTAPAPELES
                    try:
                        self.root.clipboard_clear()
                        self.root.clipboard_append(presigned_url)
                        self.root.update()  # Actualizar portapapeles
                        self.log(f"📋 Link copiado al portapapeles automáticamente", "SUCCESS")
                    except Exception as e:
                        self.log(f"⚠️ Error copiando al portapapeles: {e}", "WARNING")
                    
                    # Cerrar diálogo de configuración
                    expiration_dialog.destroy()
                    
                    # Mostrar mensaje de confirmación compacto
                    messagebox.showinfo(
                        "✅ Link Generado",
                        f"🔗 Link copiado al portapapeles\n\n"
                        f"📄 Archivo: {file_name}\n"
                        f"⏱️ Duración: {selected_text}\n"
                        f"📅 Expira: {expiration_str}\n\n"
                        f"💡 El link ya está en tu portapapeles, listo para pegar."
                    )
                    
                except botocore.exceptions.NoCredentialsError:
                    self.log(f"❌ No hay credenciales disponibles", "ERROR")
                    messagebox.showerror(
                        "❌ Error de Credenciales",
                        "No se encontraron credenciales válidas.\n\n"
                        "Por favor, reconéctate usando el botón de conexión."
                    )
                    expiration_dialog.destroy()
                    
                except botocore.exceptions.ClientError as e:
                    error_code = e.response.get('Error', {}).get('Code', 'Unknown')
                    error_msg = e.response.get('Error', {}).get('Message', str(e))
                    self.log(f"❌ Error de AWS: {error_code} - {error_msg}", "ERROR")
                    messagebox.showerror(
                        "❌ Error de AWS",
                        f"No se pudo generar el link:\n\n"
                        f"Código: {error_code}\n"
                        f"Mensaje: {error_msg}\n\n"
                        "Posibles soluciones:\n"
                        "• Verifica que tengas permisos de lectura en el bucket\n"
                        "• Reconéctate con AWS SSO\n"
                        "• Verifica que el archivo aún exista"
                    )
                    expiration_dialog.destroy()
                    
                except Exception as e:
                    self.log(f"❌ Error generando link: {str(e)}", "ERROR")
                    messagebox.showerror(
                        "❌ Error",
                        f"No se pudo generar el link:\n\n{str(e)}\n\n"
                        "Intenta reconectarte con AWS SSO."
                    )
                    expiration_dialog.destroy()
            
            # 🎯 Botones corporativos con diseño mejorado
            buttons_frame = tk.Frame(content_frame, bg=COLORS['surface'])
            buttons_frame.pack(pady=(18, 0))
            
            # Botón Cancelar - Gris corporativo sutil
            cancel_btn = tk.Button(buttons_frame,
                                  text="✖ Cancelar",
                                  font=('Segoe UI', 11),
                                  bg=COLORS['secondary'],
                                  fg='white',
                                  activebackground=COLORS['primary_light'],
                                  activeforeground='white',
                                  bd=0,
                                  padx=28,
                                  pady=11,
                                  cursor='hand2',
                                  relief='flat',
                                  command=expiration_dialog.destroy)
            cancel_btn.pack(side=tk.LEFT, padx=(0, 12))
            
            # Botón Generar Link - Azul corporativo prominente
            generate_btn = tk.Button(buttons_frame,
                                    text="🔗 Generar Link",
                                    font=('Segoe UI', 11, 'bold'),
                                    bg=COLORS['accent'],
                                    fg='white',
                                    activebackground=COLORS['accent_hover'],
                                    activeforeground='white',
                                    bd=0,
                                    padx=28,
                                    pady=11,
                                    cursor='hand2',
                                    relief='flat',
                                    command=generate_and_show)
            generate_btn.pack(side=tk.LEFT)
            
            # Actualizar status y limpiar después
            try:
                self.update_status("Listo")
                self.root.after(1500, lambda: self.update_status(""))
            except Exception:
                pass
            
        except Exception as e:
            self.log(f"❌ Error en generación de link: {str(e)}", "ERROR")
            messagebox.showerror(
                "❌ Error",
                f"Error generando link:\n{str(e)}"
            )
            try:
                self.update_status("")
            except Exception:
                pass
    
    def _show_presigned_url_dialog(self, url, file_name, expiration_str):
        """Muestra un diálogo con la URL pre-firmada generada - Diseño corporativo"""
        # Crear diálogo de resultado corporativo
        result_dialog = tk.Toplevel(self.root)
        result_dialog.title("✅ Link Generado")
        result_dialog.geometry("700x500")
        result_dialog.configure(bg=COLORS['background'])
        result_dialog.transient(self.root)
        result_dialog.grab_set()
        
        # Centrar el diálogo
        result_dialog.update_idletasks()
        x = (result_dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (result_dialog.winfo_screenheight() // 2) - (500 // 2)
        result_dialog.geometry(f"+{x}+{y}")
        
        # Contenido con estilo corporativo
        content_frame = tk.Frame(result_dialog, bg=COLORS['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Título con color corporativo
        title_label = tk.Label(content_frame,
                              text="✅ Link Temporal Generado",
                              font=('Segoe UI', 18, 'bold'),
                              fg=COLORS['success'],
                              bg=COLORS['surface'])
        title_label.pack(pady=(0, 10))
        
        # Info del archivo con tipografía profesional
        info_label = tk.Label(content_frame,
                             text=f"📄 {file_name}",
                             font=('Segoe UI', 12),
                             fg=COLORS['text_primary'],
                             bg=COLORS['surface'])
        info_label.pack()
        
        # Expiración con color de advertencia corporativo
        expiration_label = tk.Label(content_frame,
                                   text=f"⏱️ Válido hasta: {expiration_str}",
                                   font=('Segoe UI', 11),
                                   fg=COLORS['warning'],
                                   bg=COLORS['surface'])
        expiration_label.pack(pady=(5, 20))
        
        # URL en área de texto scrollable con estilo corporativo
        url_frame = tk.Frame(content_frame, bg=COLORS['surface'])
        url_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        url_label = tk.Label(url_frame,
                            text="🔗 URL Temporal:",
                            font=('Segoe UI', 11, 'bold'),
                            fg=COLORS['text_primary'],
                            bg=COLORS['surface'])
        url_label.pack(anchor=tk.W, pady=(0, 5))
        
        url_text = ScrolledText(url_frame,
                               height=8,
                               font=('Consolas', 9),
                               bg=COLORS['background'],
                               fg=COLORS['text_primary'],
                               wrap=tk.WORD)
        url_text.pack(fill=tk.BOTH, expand=True)
        url_text.insert(tk.END, url)
        url_text.config(state=tk.DISABLED)  # Solo lectura
        
        # 🎯 Botones de acción corporativos
        buttons_frame = tk.Frame(content_frame, bg=COLORS['surface'])
        buttons_frame.pack(pady=(10, 0))
        
        def copy_to_clipboard():
            """Copia la URL al portapapeles"""
            self.root.clipboard_clear()
            self.root.clipboard_append(url)
            self.root.update()
            copy_btn.config(text="✅ Copiado!", 
                           bg=COLORS['success'],
                           activebackground=COLORS['success_hover'])
            self.log(f"📋 Link copiado al portapapeles", "SUCCESS")
            result_dialog.after(2000, lambda: copy_btn.config(
                text="📋 Copiar Link", 
                bg=COLORS['accent'],
                activebackground=COLORS['accent_hover']))
        
        # Botón copiar - Azul corporativo prominente
        copy_btn = tk.Button(buttons_frame,
                            text="📋 Copiar Link",
                            font=('Segoe UI', 12, 'bold'),
                            bg=COLORS['accent'],
                            fg='white',
                            activebackground=COLORS['accent_hover'],
                            activeforeground='white',
                            bd=0,
                            padx=28,
                            pady=13,
                            cursor='hand2',
                            relief='flat',
                            command=copy_to_clipboard)
        copy_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón cerrar - Gris corporativo sutil
        close_btn = tk.Button(buttons_frame,
                             text="✅ Cerrar",
                             font=('Segoe UI', 11),
                             bg=COLORS['border'],
                             fg=COLORS['text_primary'],
                             activebackground=COLORS['surface_hover'],
                             activeforeground=COLORS['text_primary'],
                             bd=0,
                             padx=22,
                             pady=13,
                             cursor='hand2',
                             relief='flat',
                             command=result_dialog.destroy)
        close_btn.pack(side=tk.LEFT)
        
        # Nota de seguridad con estilo corporativo
        note_frame = tk.Frame(content_frame, bg=COLORS['background'])
        note_frame.pack(fill=tk.X, pady=(15, 0))
        
        note_label = tk.Label(note_frame,
                             text="⚠️ IMPORTANTE: Este link es temporal y cualquiera que lo tenga podrá descargar el archivo.\n"
                                  "No lo compartas en lugares públicos y revoca el acceso si es necesario.",
                             font=('Segoe UI', 9),
                             fg=COLORS['warning'],
                             bg=COLORS['background'],
                             justify=tk.LEFT,
                             wraplength=620)
        note_label.pack(padx=10, pady=10)
    
    def start_download(self):
        """Iniciar la descarga del archivo seleccionado"""
        if not self.selected_file_info:
            return
        
        # Verificar si ya hay una descarga en progreso (solo una a la vez)
        if self.download_in_progress:
            messagebox.showwarning(
                "⚠️ Descarga en Progreso", 
                "Ya hay una descarga activa. Solo se permite una descarga a la vez."
            )
            return
        
        # Marcar descarga como iniciada
        self.download_in_progress = True
        self.download_completed = False
        
        file_name = self.selected_file_info['name']
        
        # Seleccionar carpeta de destino
        download_path = filedialog.askdirectory(title="Seleccionar carpeta de descarga")
        if not download_path:
            # Usuario canceló
            self.download_in_progress = False
            self.show_step(3)  # Volver al explorador
            return
        
        # Guardar información de descarga
        self.download_directory = download_path
        self.local_file_path = os.path.join(download_path, file_name)
        
        # Verificar si el archivo ya existe
        if os.path.exists(self.local_file_path):
            result = messagebox.askyesno(
                "📁 Archivo Existe",
                f"El archivo '{file_name}' ya existe en:\n{download_path}\n\n¿Deseas sobreescribirlo?",
                icon='question'
            )
            if not result:
                # Usuario decidió no sobreescribir
                self.download_in_progress = False
                self.show_step(3)  # Volver al explorador
                return
        
        # Actualizar UI para mostrar preparación
        self.progress_label.configure(text="Preparando descarga...")
        self.log(f"🚀 Iniciando descarga: {file_name}", "INFO")
        
        # Actualizar botones en todos los pasos
        self.update_navigation_buttons()
        
        # Ejecutar descarga en hilo separado para no bloquear UI
        import threading
        self.download_thread = threading.Thread(target=self._download_thread_wizard, daemon=True)
        self.download_thread.start()
    
    def _download_thread_wizard(self):
        """Hilo de descarga para el wizard"""
        try:
            file_info = self.selected_file_info
            file_path = self.local_file_path
            
            self.log(f"Iniciando descarga: {file_info['name']}", "SUCCESS")
            
            # Obtener tamaño del archivo
            s3_client = self.session.client('s3') if self.session else self.s3_client
            file_key = file_info.get('key', self.current_path + file_info['name'])
            
            self.log(f"🚀 Iniciando descarga: {file_info['name']}", "INFO")
            
            obj_info = s3_client.head_object(Bucket=self.selected_bucket, Key=file_key)
            total_size = obj_info['ContentLength']
            total_size = obj_info['ContentLength']
            
            # Variables de progreso
            self.downloaded_bytes = 0
            
            def progress_callback(bytes_transferred):
                self.downloaded_bytes += bytes_transferred
                progress = (self.downloaded_bytes / total_size) * 100
                current_size = self.format_size(self.downloaded_bytes)
                total_size_str = self.format_size(total_size)
                
                # Actualizar UI en el hilo principal
                self.root.after(0, lambda: self._update_progress_wizard(progress, current_size, total_size_str))
            
            # Realizar descarga
            s3_client.download_file(
                Bucket=self.selected_bucket,
                Key=file_key,
                Filename=str(file_path),
                Callback=progress_callback
            )
            
            # Descarga completada
            self.log(f"Descarga completada: {file_path}", "SUCCESS")
            self.root.after(0, self._download_completed_wizard)
            
        except Exception as e:
            error_message = str(e)  # Capturar el mensaje antes del lambda
            self.log(f"Error en descarga: {error_message}", "ERROR")
            self.root.after(0, lambda: self._download_failed_wizard(error_message))
    
    def _update_progress_wizard(self, progress, current, total):
        """Actualiza la barra de progreso del wizard"""
        try:
            # Verificar que estemos en el paso correcto Y que los widgets existan
            if (self.current_step == 4 and 
                hasattr(self, 'progress_var') and hasattr(self, 'progress_label') and
                self.progress_var is not None and self.progress_label is not None):
                
                # Verificar que los widgets no hayan sido destruidos
                try:
                    self.progress_var.set(progress)
                    self.progress_label.config(text=f"📥 {progress:.1f}% - {current} / {total}")
                except tk.TclError:
                    # Los widgets fueron destruidos, no hacer nada
                    pass
        except Exception as e:
            # Cualquier error en actualización de progreso, ignorar silenciosamente
            pass
    
    def _download_completed_wizard(self):
        """Maneja la finalización exitosa de descarga del wizard"""
        try:
            # Actualizar estado
            self.download_in_progress = False
            self.download_completed = True
            self.download_thread = None
            
            # Verificar widgets antes de actualizar
            if (hasattr(self, 'progress_var') and hasattr(self, 'progress_label') 
                and self.progress_var is not None and self.progress_label is not None
                and self.current_step == 4):
                try:
                    self.progress_var.set(100)
                    self.progress_label.config(text="✅ Descarga completada")
                except tk.TclError:
                    # Widgets destruidos, no hacer nada
                    pass
            
            messagebox.showinfo("🎉 Éxito", f"📥 Archivo descargado exitosamente a:\n{self.download_directory}")
            
            # Resetear para permitir nueva descarga ANTES de actualizar botones
            self.selected_file_info = None
            self.download_completed = False
            
            # Actualizar botones en todos los pasos (después del reset)
            self.update_navigation_buttons()
            # Actualizar status y limpiar después
            try:
                self.update_status("Listo")
                self.root.after(1500, lambda: self.update_status(""))
            except Exception:
                pass

            # Volver automáticamente al explorador después de completar
            self.root.after(1000, lambda: self.show_step(3))
        except Exception as e:
            # Error en completion, ignorar silenciosamente
            pass
    
    def _download_failed_wizard(self, error):
        """Maneja el fallo de descarga del wizard"""
        try:
            # Resetear estado de descarga
            self.download_in_progress = False
            self.download_completed = False
            self.download_thread = None
            self.selected_file_info = None  # Permitir nueva selección
            
            # Verificar widgets antes de actualizar
            if (hasattr(self, 'progress_var') and hasattr(self, 'progress_label') 
                and self.progress_var is not None and self.progress_label is not None
                and self.current_step == 4):
                try:
                    self.progress_var.set(0)
                    self.progress_label.config(text="❌ Error en descarga")
                except tk.TclError:
                    # Widgets destruidos, no hacer nada
                    pass
            
            # Actualizar botones en todos los pasos
            self.update_navigation_buttons()
            
            messagebox.showerror("⚠️ Error", f"❌ Error durante la descarga:\n{error}")
            
            # Volver al explorador
            try:
                self.update_status("")
            except Exception:
                pass
            self.show_step(3)
        except Exception as e:
            # Error en failure handler, ignorar silenciosamente
            pass
    
    def _cancel_download(self):
        """Cancela la descarga en progreso"""
        try:
            self.log("🛑 Cancelando descarga...", "WARNING")
            
            # Resetear variables de estado
            self.download_in_progress = False
            self.download_completed = False
            
            # El thread continuará ejecutándose pero ya no actualizará la UI
            if self.download_thread and self.download_thread.is_alive():
                # No podemos forzar detener el thread, pero sí evitar updates
                pass
                
            self.log("✅ Descarga cancelada", "INFO")
            
        except Exception as e:
            self.log(f"Error cancelando descarga: {e}", "ERROR")
    
    def can_return_to_download(self):
        """Verifica si se puede volver a la sección de descargas"""
        return (self.selected_file_info is not None and 
                (self.download_in_progress or self.download_completed))
    
    def download_with_progress_legacy(self, s3_key, local_path, file_size):
        """Descargar archivo con barra de progreso (LEGACY - NO USAR)"""
        # MÉTODO LEGACY DESACTIVADO - usar _download_thread_wizard
        return
        def progress_callback(bytes_transferred):
            progress = (bytes_transferred / file_size) * 100
            self.progress_var.set(progress)
            self.progress_label.configure(text=f"Descargando... {progress:.1f}%")
            self.root.update_idletasks()
        
        try:
            self.s3_client.download_file(
                self.selected_bucket,
                s3_key,
                local_path,
                Callback=progress_callback
            )
            
            self.progress_var.set(100)
            self.progress_label.configure(text="✅ Descarga completada")
            self.log_message(f"Archivo descargado: {local_path}")
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Éxito", f"Archivo descargado exitosamente:\n{local_path}")
            
            # Volver al explorador después de un momento
            self.root.after(2000, lambda: self.show_step(3))
            
        except Exception as e:
            raise e
    
    def format_size(self, size_bytes):
        """Formatear tamaño de archivo"""
        if isinstance(size_bytes, str):
            return size_bytes
        
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return f"{s} {size_names[i]}"
        
    def create_modern_header(self, parent):
        """Crea la cabecera moderna con gradiente visual"""
        header_frame = tk.Frame(parent, bg=COLORS['surface'], height=120)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        # Container interno con padding
        header_content = tk.Frame(header_frame, bg=COLORS['surface'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # Lado izquierdo - Título y descripción
        left_frame = tk.Frame(header_content, bg=COLORS['surface'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)
        
        # Título principal moderno
        title_label = tk.Label(left_frame, 
                              text="AWS Backup Manager", 
                              font=('Inter', 28, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(anchor=tk.W)
        
        # Subtítulo elegante
        subtitle_label = tk.Label(left_frame,
                                 text="Descarga profesional de backups desde Amazon S3 con autenticación SSO",
                                 font=('Inter', 12),
                                 fg=COLORS['text_secondary'],
                                 bg=COLORS['surface'])
        subtitle_label.pack(anchor=tk.W, pady=(5, 0))
        
        # Lado derecho - Versión y estado
        right_frame = tk.Frame(header_content, bg=COLORS['surface'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Badge de versión moderno
        version_frame = tk.Frame(right_frame, bg=COLORS['accent'], relief='flat')
        version_frame.pack(anchor=tk.E, pady=(10, 5))
        
        version_label = tk.Label(version_frame,
                               text=f"v{VERSION}",
                               font=('Inter', 10, 'bold'),
                               fg='white',
                               bg=COLORS['accent'],
                               padx=12, pady=6)
        version_label.pack()
        
        # Separador visual
        separator = tk.Frame(parent, bg=COLORS['border'], height=1)
        separator.pack(fill=tk.X)
    
    def create_modern_layout(self, parent):
        """Crea el layout principal moderno con pack"""
        # Container para los dos paneles
        panels_container = tk.Frame(parent, bg=COLORS['background'])
        panels_container.pack(fill=tk.BOTH, expand=True)
        
        # Columna izquierda - Panel de configuración moderno
        left_panel = self.create_modern_card(panels_container, "Configuración")
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 15))
        
        # Columna derecha - Panel de log moderno
        right_panel = self.create_modern_card(panels_container, "Registro de Actividad")
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(15, 0))
        
        # Crear contenido de los paneles
        self.create_modern_config_panel(left_panel)
        self.create_modern_log_panel(right_panel)
    
    def create_modern_card(self, parent, title):
        """Crea una card moderna con sombra visual"""
        # Frame principal de la card con fondo y borde redondeado
        card_frame = tk.Frame(parent, bg=COLORS['surface'], relief='flat', bd=0)
        
        # Header de la card
        header_frame = tk.Frame(card_frame, bg=COLORS['surface'], height=60)
        header_frame.pack(fill=tk.X, padx=20, pady=(20, 0))
        header_frame.pack_propagate(False)
        
        # Título de la card
        title_label = tk.Label(header_frame,
                              text=title,
                              font=('Inter', 16, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(side=tk.LEFT, pady=15)
        
        # Contenido de la card
        content_frame = tk.Frame(card_frame, bg=COLORS['surface'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))
        
        # CRUCIAL: Empaquetar el card_frame
        card_frame.pack(fill=tk.BOTH, expand=True)
        
        return content_frame
    
    def create_modern_config_panel(self, parent):
        """Crea el panel de configuración moderno"""
        # Configurar scrollable frame
        canvas = tk.Canvas(parent, bg=COLORS['surface'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview, style='Modern.Vertical.TScrollbar')
        scrollable_frame = tk.Frame(canvas, bg=COLORS['surface'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar y canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Sección 1: Perfil AWS SSO
        self.create_profile_section_modern(scrollable_frame)
        
        # Separador
        self.create_separator(scrollable_frame)
        
        # Sección 2: Buckets
        self.create_bucket_section_modern(scrollable_frame)
        
        # Separador
        self.create_separator(scrollable_frame)
        
        # Sección 3: Navegación
        self.create_navigation_section_modern(scrollable_frame)
        
        # Separador
        self.create_separator(scrollable_frame)
        
        # Sección 4: Descarga
        self.create_download_section_modern(scrollable_frame)
        
    def create_separator(self, parent):
        """Crea un separador visual moderno"""
        separator = tk.Frame(parent, bg=COLORS['border'], height=1)
        separator.pack(fill=tk.X, pady=20)
    
    def create_profile_section_modern(self, parent):
        """Crea la sección de perfiles AWS moderna"""
        section_frame = tk.Frame(parent, bg=COLORS['surface'])
        section_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Label con icono
        header_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Icono + título
        icon_label = tk.Label(header_frame, text="🔐", font=('Inter', 16), 
                             bg=COLORS['surface'], fg=COLORS['accent'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, text="Perfil AWS SSO",
                              font=('Inter', 14, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para controles
        controls_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Combobox moderno
        self.profile_var = tk.StringVar()
        self.profile_combo = ttk.Combobox(controls_frame, textvariable=self.profile_var,
                                         state='readonly', 
                                         font=('Inter', 11),
                                         style='Modern.TCombobox',
                                         height=8)
        self.profile_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.profile_combo.bind('<<ComboboxSelected>>', self.on_profile_selected)
        
        # Botón conectar moderno
        self.connect_btn = tk.Button(controls_frame, 
                                    text="Conectar",
                                    font=('Inter', 11, 'bold'),
                                    fg='white',
                                    bg=COLORS['accent'],
                                    activebackground=COLORS['accent_hover'],
                                    activeforeground='white',
                                    relief='flat',
                                    cursor='hand2',
                                    padx=25, pady=12,
                                    command=self.connect_to_aws)
        self.connect_btn.pack(side=tk.RIGHT)
        
        # Status de conexión moderno
        status_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        status_frame.pack(fill=tk.X)
        
        status_icon_label = tk.Label(status_frame, text="●", 
                                    font=('Inter', 14),
                                    fg=COLORS['danger'],
                                    bg=COLORS['surface'])
        status_icon_label.pack(side=tk.LEFT)
        
        self.connection_status = tk.Label(status_frame, text="Desconectado",
                                         font=('Inter', 11),
                                         fg=COLORS['text_secondary'],
                                         bg=COLORS['surface'])
        self.connection_status.pack(side=tk.LEFT, padx=(5, 0))
        
        # Guardar referencia al icono para poder cambiarlo
        self.status_icon = status_icon_label
    
    def create_bucket_section_modern(self, parent):
        """Crea la sección de buckets moderna"""
        section_frame = tk.Frame(parent, bg=COLORS['surface'])
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header con icono
        header_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = tk.Label(header_frame, text="🪣", font=('Inter', 16), 
                             bg=COLORS['surface'], fg=COLORS['accent'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, text="Bucket S3",
                              font=('Inter', 14, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Combobox para buckets
        controls_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        controls_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Variables
        self.bucket_var = tk.StringVar()
        
        # Crear combobox personalizado usando ttk
        self.bucket_combo = ttk.Combobox(controls_frame,
                                        textvariable=self.bucket_var,
                                        state='readonly',
                                        style='Modern.TCombobox',
                                        font=('Inter', 11))
        self.bucket_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        self.bucket_combo.bind('<<ComboboxSelected>>', self.on_bucket_selected)
        
        # Status del bucket
        status_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        status_frame.pack(fill=tk.X)
        
        self.bucket_status = tk.Label(status_frame, text="No hay buckets disponibles",
                                     font=('Inter', 10),
                                     fg=COLORS['text_secondary'],
                                     bg=COLORS['surface'])
        self.bucket_status.pack(side=tk.LEFT)
    
    def create_navigation_section_modern(self, parent):
        """Crea la sección de navegación moderna"""
        section_frame = tk.Frame(parent, bg=COLORS['surface'])
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header con icono
        header_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = tk.Label(header_frame, text="📁", font=('Inter', 16), 
                             bg=COLORS['surface'], fg=COLORS['warning'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, text="Explorador",
                              font=('Inter', 14, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Frame para el treeview y scrollbar
        tree_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        tree_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Treeview moderno
        style = ttk.Style()
        
        self.tree = ttk.Treeview(tree_frame, 
                                height=8,
                                style='Modern.Treeview',
                                selectmode='extended')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Scrollbar
        tree_scroll = ttk.Scrollbar(tree_frame, 
                                   orient="vertical", 
                                   command=self.tree.yview,
                                   style='Modern.Vertical.TScrollbar')
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=tree_scroll.set)
        
        # Configurar columnas
        self.tree['columns'] = ('size', 'type')
        self.tree.column('#0', width=250, minwidth=200)
        self.tree.column('size', width=100, minwidth=80)
        self.tree.column('type', width=100, minwidth=80)
        
        self.tree.heading('#0', text='📄 Nombre', anchor=tk.W)
        self.tree.heading('size', text='📊 Tamaño', anchor=tk.W)
        self.tree.heading('type', text='🏷️ Tipo', anchor=tk.W)
        
        # Binds para interacción
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        self.tree.bind('<Double-1>', self.on_tree_double_click)
        
        # Botones de navegación modernos
        nav_buttons = tk.Frame(section_frame, bg=COLORS['surface'])
        nav_buttons.pack(fill=tk.X, pady=(10, 0))
        
        # Botón actualizar
        self.refresh_btn = tk.Button(nav_buttons, 
                                    text="🔄 Actualizar",
                                    font=('Inter', 10),
                                    bg=COLORS['accent'],
                                    fg='white',
                                    bd=0,
                                    padx=15,
                                    pady=8,
                                    cursor='hand2',
                                    command=self.refresh_tree)
        self.refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # NUEVO: Botón de diagnóstico para carpetas problemáticas
        self.diagnostic_btn = tk.Button(nav_buttons,
                                       text="🔧 Diagnóstico", 
                                       font=('Inter', 9),
                                       bg=COLORS['warning'],
                                       fg='white',
                                       bd=0,
                                       padx=12,
                                       pady=8,
                                       cursor='hand2',
                                       command=self.show_diagnostic_info)
        self.diagnostic_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Botón atrás
        self.back_btn = tk.Button(nav_buttons,
                                 text="⬅️ Atrás", 
                                 font=('Inter', 10),
                                 bg=COLORS['border'],
                                 fg=COLORS['text_primary'],
                                 bd=0,
                                 padx=15,
                                 pady=8,
                                 cursor='hand2',
                                 command=self.go_back)
        self.back_btn.pack(side=tk.LEFT)
        
        # Breadcrumb para mostrar ruta actual
        self.breadcrumb_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        self.breadcrumb_frame.pack(fill=tk.X, pady=(10, 0))
        
        self.breadcrumb_label = tk.Label(self.breadcrumb_frame,
                                        text="📍 Ruta: /",
                                        font=('Inter', 9),
                                        fg=COLORS['text_secondary'],
                                        bg=COLORS['surface'])
        self.breadcrumb_label.pack(side=tk.LEFT)
    
    def create_download_section_modern(self, parent):
        """Crea la sección de descarga moderna"""
        section_frame = tk.Frame(parent, bg=COLORS['surface'])
        section_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Header con icono
        header_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        icon_label = tk.Label(header_frame, text="⬇️", font=('Inter', 16), 
                             bg=COLORS['surface'])
        icon_label.pack(side=tk.LEFT)
        
        title_label = tk.Label(header_frame, text="Descarga",
                              font=('Inter', 14, 'bold'),
                              fg=COLORS['primary'],
                              bg=COLORS['surface'])
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Información del archivo seleccionado - Card moderna
        info_card = tk.Frame(section_frame, bg=COLORS['background'], relief='flat', bd=0)
        info_card.pack(fill=tk.X, pady=(0, 15))
        
        info_content = tk.Frame(info_card, bg=COLORS['background'])
        info_content.pack(fill=tk.X, padx=15, pady=15)
        
        # Icono de archivo
        file_icon = tk.Label(info_content, text="📄", font=('Inter', 16),
                            bg=COLORS['background'])
        file_icon.pack(side=tk.LEFT)
        
        # Info del archivo
        file_info_frame = tk.Frame(info_content, bg=COLORS['background'])
        file_info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))
        
        self.file_info_label = tk.Label(file_info_frame, 
                                       text="Ningún archivo seleccionado",
                                       font=('Inter', 11),
                                       fg=COLORS['text_secondary'],
                                       bg=COLORS['background'],
                                       anchor=tk.W)
        self.file_info_label.pack(fill=tk.X)
        
        self.file_size_label = tk.Label(file_info_frame,
                                       text="",
                                       font=('Inter', 10),
                                       fg=COLORS['text_secondary'],
                                       bg=COLORS['background'],
                                       anchor=tk.W)
        self.file_size_label.pack(fill=tk.X)
        
        # Botón de descarga moderno con gradiente visual
        download_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        download_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.download_btn = tk.Button(download_frame,
                                     text="🚀 Descargar Archivo",
                                     font=('Inter', 12, 'bold'),
                                     fg='white',
                                     bg=COLORS['accent'],
                                     activebackground=COLORS['accent_hover'],
                                     activeforeground='white',
                                     relief='flat',
                                     cursor='hand2',
                                     padx=30, pady=15,
                                     state='disabled',
                                     command=self.start_download)
        self.download_btn.pack(fill=tk.X)
        
        # Progress section moderna
        progress_frame = tk.Frame(section_frame, bg=COLORS['surface'])
        progress_frame.pack(fill=tk.X, pady=(10, 0))
        
        # Barra de progreso moderna
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           variable=self.progress_var,
                                           style='Modern.Horizontal.TProgressbar',
                                           length=400)
        self.progress_bar.pack(fill=tk.X, pady=(0, 10))
        
        # Labels de progreso
        progress_info_frame = tk.Frame(progress_frame, bg=COLORS['surface'])
        progress_info_frame.pack(fill=tk.X)
        
        self.progress_label = tk.Label(progress_info_frame,
                                      text="",
                                      font=('Inter', 10),
                                      fg=COLORS['text_secondary'],
                                      bg=COLORS['surface'])
        self.progress_label.pack(side=tk.LEFT)
        
        self.speed_label = tk.Label(progress_info_frame,
                                   text="",
                                   font=('Inter', 10),
                                   fg=COLORS['text_secondary'],
                                   bg=COLORS['surface'])
        self.speed_label.pack(side=tk.RIGHT)
    
    def create_modern_log_panel(self, parent):
        """Crea el panel de logs moderno"""
        # Área de texto para logs con estilo moderno
        log_frame = tk.Frame(parent, bg=COLORS['surface'])
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Container para el texto y scrollbar
        text_container = tk.Frame(log_frame, bg=COLORS['surface'])
        text_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.log_text = ScrolledText(text_container,
                                    height=30,
                                    font=('JetBrains Mono', 9),
                                    bg=COLORS['primary'],
                                    fg='#E2E8F0',
                                    insertbackground=COLORS['accent'],
                                    selectbackground=COLORS['accent'],
                                    relief='flat',
                                    bd=0,
                                    padx=15, pady=15,
                                    wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags de colores para diferentes tipos de log
        self.log_text.tag_configure('info', foreground='#A0AEC0')
        self.log_text.tag_configure('success', foreground=COLORS['success'])
        self.log_text.tag_configure('warning', foreground=COLORS['warning'])
        self.log_text.tag_configure('error', foreground=COLORS['danger'])
        self.log_text.tag_configure('timestamp', foreground=COLORS['accent'])
        
        # Botones de control modernos
        buttons_frame = tk.Frame(log_frame, bg=COLORS['surface'])
        buttons_frame.pack(fill=tk.X)
        
        clear_btn = tk.Button(buttons_frame,
                             text="🗑️ Limpiar Log",
                             font=('Inter', 10),
                             fg=COLORS['text_primary'],
                             bg=COLORS['surface'],
                             activebackground=COLORS['surface_hover'],
                             relief='flat',
                             cursor='hand2',
                             padx=15, pady=8,
                             command=self.clear_log)
        clear_btn.pack(side=tk.LEFT)
        
        save_log_btn = tk.Button(buttons_frame,
                                text="💾 Guardar Log",
                                font=('Inter', 10),
                                fg=COLORS['text_primary'],
                                bg=COLORS['surface'],
                                activebackground=COLORS['surface_hover'],
                                relief='flat',
                                cursor='hand2',
                                padx=15, pady=8,
                                command=self.save_log)
        save_log_btn.pack(side=tk.LEFT, padx=(10, 0))
    
    def create_modern_status_bar(self, parent):
        """Crea la barra de estado moderna"""
        status_frame = tk.Frame(parent, bg=COLORS['primary'], height=40)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)
        
        # Container interno
        status_content = tk.Frame(status_frame, bg=COLORS['primary'])
        status_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        # Status izquierda
        self.status_label = tk.Label(status_content,
                                    text="Listo",
                                    font=('Inter', 10),
                                    fg='white',
                                    bg=COLORS['primary'])
        self.status_label.pack(side=tk.LEFT)
        
        # Información derecha (REMOVIDA - no queremos contador ni reloj)
        # right_info = tk.Frame(status_content, bg=COLORS['primary'])
        # right_info.pack(side=tk.RIGHT)
        
        # Contador de archivos (REMOVIDO)
        # self.file_count_label = tk.Label(right_info,
        #                                 text="0 archivos disponibles",
        #                                 font=('Inter', 10),
        #                                 fg='#A0AEC0',
        #                                 bg=COLORS['primary'])
        # self.file_count_label.pack(side=tk.LEFT, padx=(0, 20))
        
        # Reloj (REMOVIDO)
        # self.time_label = tk.Label(right_info,
        #                           text=datetime.now().strftime('%H:%M:%S'),
        #                           font=('Inter', 10, 'bold'),
        #                           fg='white',
        #                           bg=COLORS['primary'])
        # self.time_label.pack(side=tk.RIGHT)
        
        # Actualizar tiempo cada segundo (REMOVIDO)
        # self.update_time()
    
    def setup_logging(self):
        """Configura el sistema de logging"""
        # Crear directorio de logs
        Path("logs").mkdir(exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)s] %(message)s",
            handlers=[
                logging.FileHandler("logs/aws_backup_gui.log", encoding="utf-8"),
                logging.StreamHandler()
            ]
        )
        
        # Redirigir logs a la GUI solo si el widget existe
        if hasattr(self, 'log_text'):
            self.log_handler = GUILogHandler(self.log_text)
            logging.getLogger().addHandler(self.log_handler)
            
            self.log("AWS Backup Manager GUI iniciado")
        else:
            logging.info("AWS Backup Manager GUI iniciado")
    
    def log(self, message, level="INFO"):
        """Agrega un mensaje al log de la GUI con estilo moderno"""
        # Si no existe el widget de log, usar logging estándar
        if not hasattr(self, 'log_text'):
            if level == "ERROR":
                logging.error(message)
            elif level == "WARNING":
                logging.warning(message)
            else:
                logging.info(message)
            return
            
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        # Configurar formato según el nivel
        if level == "ERROR":
            tag = "error"
            prefix = "❌"
        elif level == "WARNING":
            tag = "warning"  
            prefix = "⚠️"
        elif level == "SUCCESS":
            tag = "success"
            prefix = "✅"
        else:
            tag = "info"
            prefix = "ℹ️"
        
        # Insertar timestamp
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        
        # Insertar prefijo con color
        self.log_text.insert(tk.END, f"{prefix} ", tag)
        
        # Insertar mensaje
        self.log_text.insert(tk.END, f"{message}\n", tag)
        
        # Auto-scroll al final
        self.log_text.see(tk.END)
        
        # También log al sistema
        if level == "ERROR":
            logging.error(message)
        elif level == "WARNING":
            logging.warning(message)
        else:
            logging.info(message)
    
    def log_message(self, message, level="INFO"):
        """Alias para el método log para compatibilidad con el wizard"""
        self.log(message, level)
    
    def save_log(self):
        """Guarda el log actual a un archivo"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".log",
                filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")],
                title="Guardar registro de actividad"
            )
            if filename:
                content = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.log(f"Log guardado en: {filename}", "SUCCESS")
        except Exception as e:
            self.log(f"Error guardando log: {e}", "ERROR")
    
    def clear_log(self):
        """Limpia el área de log"""
        if hasattr(self, 'log_text'):
            self.log_text.delete(1.0, tk.END)
            self.log("Log limpiado", "INFO")
    
    def update_time(self):
        """MÉTODO DESHABILITADO - No queremos mostrar la hora"""
        pass  # Método deshabilitado
    
    def update_status(self, message):
        """Actualiza el mensaje de estado"""
        if hasattr(self, 'status_label'):
            self.status_label.config(text=message)
    
    def update_file_count(self, count):
        """MÉTODO DESHABILITADO - No queremos mostrar contador de archivos"""
        pass  # Método deshabilitado
    
    def load_aws_profiles(self):
        """Carga los perfiles AWS SSO disponibles usando la función mejorada"""
        try:
            self.log_message("Cargando perfiles AWS SSO...")
            
            # Usar la nueva función para obtener perfiles
            profiles = get_available_profiles()
            
            if profiles:
                # Actualizar el combobox en el paso 1 si existe
                if hasattr(self, 'profile_combo'):
                    self.profile_combo['values'] = sorted(profiles)
                self.log_message(f"✅ Encontrados {len(profiles)} perfiles SSO: {', '.join(sorted(profiles))}")
            else:
                self.log_message("⚠️ No se encontraron perfiles SSO configurados", "WARNING")
                
                # Mostrar mensaje de ayuda si no hay perfiles
                if hasattr(self, 'profile_combo'):
                    self.profile_combo['values'] = []
                    
                messagebox.showwarning(
                    "Sin Perfiles AWS", 
                    "No se encontraron perfiles AWS SSO configurados.\n\n"
                    "Para configurar AWS SSO:\n"
                    "1. Ejecuta: Configurar_AWS_SSO.bat\n"
                    "2. O manualmente: aws configure sso\n"
                    "3. Luego reinicia esta aplicación"
                )
                
        except Exception as e:
            self.log_message(f"❌ Error cargando perfiles: {str(e)}", "ERROR")
    


    def _connect_to_aws_thread(self):
        """Hilo para conectar a AWS - ESTE ES EL QUE SE ESTÁ EJECUTANDO"""
        try:
            self.log(f"Conectando con AWS usando perfil: {self.profile_combobox.get()}", "INFO")
            self.log(f"Iniciando autenticación SSO para: {self.selected_profile}")
            self.update_status("Conectando...")
            
            # Cambiar estado del botón
            self.root.after(0, lambda: self.connect_btn.config(text="Conectando...", state='disabled'))
            
            # Realizar login SSO SIN mostrar consola
            startupinfo = None
            creationflags = 0
            if hasattr(subprocess, 'STARTUPINFO'):
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                creationflags = subprocess.CREATE_NO_WINDOW
            
            result = subprocess.run(
                ["aws", "sso", "login", "--profile", self.selected_profile],
                capture_output=True, 
                text=True, 
                timeout=300,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            
            if result.returncode != 0:
                self.log("Error en comando aws sso login", "ERROR")
                self.root.after(0, self._connection_failed)
                return
            
            # Crear sesión y verificar
            session = boto3.Session(profile_name=self.selected_profile)
            sts_client = session.client('sts')
            identity = sts_client.get_caller_identity()
            
            self.session = session
            self.s3_client = session.client('s3')  # ← AGREGADO: Crear s3_client
            self.log("Autenticación SSO exitosa", "SUCCESS")
            self.log(f"Usuario: {identity.get('Arn', 'Desconocido')}")
            
            # Actualizar UI
            self.root.after(0, self._connection_successful)
            
            # Cargar buckets
            self.load_buckets()
            
        except Exception as e:
            self.log(f"Error de conexión: {e}", "ERROR")
            self.root.after(0, self._connection_failed)
    
    def _connection_successful(self):
        """Actualiza UI tras conexión exitosa"""
        self.connect_btn.config(text="🔄 Reconectar", state='normal',
                               bg=COLORS['success'])
        if hasattr(self, 'connection_status'):
            self.connection_status.config(text="Conectado", fg=COLORS['success'])
        if hasattr(self, 'status_icon'):
            self.status_icon.config(fg=COLORS['success'])
        self.update_status("✅ Conectado a AWS")
    
    def _connection_failed(self):
        """Actualiza UI tras fallo de conexión"""
        self.connect_btn.config(text="🔄 Reintentar", state='normal',
                               bg=COLORS['danger'])
        if hasattr(self, 'connection_status'):
            self.connection_status.config(text="Error de conexión", fg=COLORS['danger'])
        if hasattr(self, 'status_icon'):
            self.status_icon.config(fg=COLORS['danger'])
        self.update_status("❌ Error de conexión")
    
    def load_buckets(self):
        """Cargar buckets S3 disponibles - VERSION WIZARD"""
        if not self.session:
            return
        
        try:
            # Actualizar status si existe
            if hasattr(self, 'bucket_status'):
                self.bucket_status.configure(text="Cargando buckets...", fg=COLORS['text_secondary'])
            
            response = self.s3_client.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]
            
            # Actualizar el combobox si existe
            if hasattr(self, 'bucket_combo'):
                self.bucket_combo['values'] = buckets
            
            if buckets:
                if hasattr(self, 'bucket_status'):
                    self.bucket_status.configure(text=f"✅ {len(buckets)} buckets disponibles", 
                                               fg=COLORS['success'])
                # Actualizar status general y limpiar
                try:
                    self.update_status("Listo")
                    self.root.after(1500, lambda: self.update_status(""))
                except Exception:
                    pass
            else:
                if hasattr(self, 'bucket_status'):
                    self.bucket_status.configure(text="⚠️ No se encontraron buckets", 
                                               fg=COLORS['warning'])
                    try:
                        self.update_status("")
                    except Exception:
                        pass
                
            self.log_message(f"Cargados {len(buckets)} buckets")
            
        except Exception as e:
            if hasattr(self, 'bucket_status'):
                self.bucket_status.configure(text="❌ Error cargando buckets", fg=COLORS['danger'])
            self.log_message(f"Error cargando buckets: {str(e)}")
            messagebox.showerror("Error", f"Error cargando buckets:\n{str(e)}")
            try:
                self.update_status("")
            except Exception:
                pass
    
    # Método heredado del sistema anterior - Ya no se usa


    def load_bucket_contents(self, prefix=""):
        """Carga el contenido de un bucket"""
        if not self.session or not self.selected_bucket:
            return
            
        threading.Thread(target=self._load_bucket_contents_thread, 
                        args=(prefix,), daemon=True).start()
    
    def _load_bucket_contents_thread(self, prefix):
        """Hilo para cargar contenido del bucket - MEJORADO para barras dobles S3"""
        try:
            self.log(f"Cargando contenido de {self.selected_bucket}/{prefix}")
            s3_client = self.session.client('s3')
            
            # SOLUCION: Usar paginator para manejo robusto de listas grandes
            paginator = s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.selected_bucket,
                Prefix=prefix,
                Delimiter="/"  # ← CRITICO: Esto permite obtener CommonPrefixes
            )
            
            folders = []
            files = []
            
            # Procesar todas las páginas de resultados
            for page in page_iterator:
                # SOLUCION PARTE 1: Procesar CommonPrefixes (SUBCARPETAS)
                # Esto resuelve el problema reportado de carpetas "vacías"
                for common_prefix in page.get('CommonPrefixes', []):
                    full_prefix = common_prefix['Prefix']
                    # Extraer solo el nombre de la carpeta sin el prefijo actual
                    folder_name = full_prefix[len(prefix):].rstrip('/')
                    if folder_name and folder_name not in folders:
                        folders.append(folder_name)
                        self.log(f"📁 Subcarpeta encontrada: '{folder_name}'", "INFO")
                
                # CASO ESPECIAL: Detectar barras dobles y rutas problemáticas
                # Si encontramos un CommonPrefix que es solo "/", significa barras dobles
                if page.get('CommonPrefixes'):
                    for cp in page.get('CommonPrefixes', []):
                        cp_prefix = cp['Prefix']
                        if cp_prefix == prefix + '/' and prefix.endswith('/'):
                            # Detectamos barra doble, explorar más profundo
                            self.log(f"⚠️ Detectada barra doble en prefijo: '{prefix}' -> Explorando '{prefix}/'")
                            # Hacer una consulta adicional con la barra doble
                            extra_response = s3_client.list_objects_v2(
                                Bucket=self.selected_bucket,
                                Prefix=prefix + '/',
                                Delimiter="/"
                            )
                            
                            # Procesar los resultados de la consulta adicional
                            for extra_cp in extra_response.get('CommonPrefixes', []):
                                extra_prefix = extra_cp['Prefix']
                                extra_folder = extra_prefix[len(prefix + '/'):].rstrip('/')
                                if extra_folder and extra_folder not in folders:
                                    folders.append(extra_folder)
                                    self.log(f"📁 Subcarpeta detectada: '{extra_folder}'")
                                    
                                    # SOLUCION CRITICA: Guardar prefijo para navegación posterior
                                    if not hasattr(self, '_folder_prefixes'):
                                        self._folder_prefixes = {}
                                    self._folder_prefixes[extra_folder] = extra_prefix
                                    self.log(f"💾 Prefijo de doble barra guardado: '{extra_folder}' = '{extra_prefix}'", "SUCCESS")
                            
                            # Procesar archivos en la consulta adicional
                            for extra_obj in extra_response.get('Contents', []):
                                extra_key = extra_obj['Key']
                                if not extra_key.endswith('/'):
                                    extra_file = extra_key[len(prefix + '/'):]
                                    if extra_file and '/' not in extra_file:
                                        if any(extra_file.lower().endswith(ext) for ext in BACKUP_EXTENSIONS):
                                            files.append({
                                                'name': extra_file,
                                                'size': extra_obj['Size'],
                                                'key': extra_key
                                            })
                                            self.log(f"Archivo en barra doble: '{extra_file}' -> clave: '{extra_key}'", "INFO")
                
                # SOLUCION PARTE 2: Procesar Contents (ARCHIVOS DIRECTOS)
                for obj in page.get('Contents', []):
                    file_key = obj['Key']
                    
                    # Verificar que no sea el directorio mismo
                    if file_key.endswith('/'):
                        continue
                        
                    # Extraer nombre del archivo sin el prefijo
                    file_name = file_key[len(prefix):]
                    if not file_name or '/' in file_name:  # Solo archivos directos en este nivel
                        continue
                        
                    # IMPORTANTE: Filtrar solo archivos de backup válidos
                    if any(file_name.lower().endswith(ext) for ext in BACKUP_EXTENSIONS):
                        files.append({
                            'name': file_name,
                            'size': obj['Size'],
                            'key': file_key  # ← CRITICO: Guardar clave completa
                        })
                        self.log(f"Archivo de backup encontrado: '{file_name}' -> clave: '{file_key}'", "INFO")
                    else:
                        self.log(f"Archivo ignorado (no es backup): '{file_name}'", "INFO")
            
            # Actualizar ruta actual
            self.current_path = prefix
            
            # Log resumen
            self.log(f"Thread - Procesado completo: {len(folders)} carpetas, {len(files)} archivos de backup", "SUCCESS")
            
            # Actualizar UI en el hilo principal
            self.root.after(0, lambda: self._update_tree_ui(folders, files))
            
        except Exception as e:
            error_msg = str(e)
            self.log(f"Error en thread cargando contenido: {error_msg}", "ERROR")
            # Mostrar error en UI principal
            self.root.after(0, lambda: messagebox.showerror("Error", f"Error cargando contenido del bucket:\n{error_msg}"))
    
    def _update_tree_ui(self, folders, files):
        """Actualiza el árbol de navegación con estilo moderno - CORREGIDO para claves S3"""
        # VERIFICAR si estamos en el paso correcto y si existe el tree
        if not hasattr(self, 'tree') or self.current_step != 3:
            self.log(f"⚠️ _update_tree_ui llamado en momento incorrecto - Step: {self.current_step}, tree exists: {hasattr(self, 'tree')}", "WARNING")
            return  # No hacer nada si no estamos en el paso correcto
        
        # Limpiar árbol
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Limpiar diccionario de claves
        if not hasattr(self, '_file_keys'):
            self._file_keys = {}
        else:
            self._file_keys.clear()
        
        # Agregar carpetas con iconos modernos
        for folder in sorted(folders):
            self.tree.insert('', 'end', 
                           values=('—', 'Carpeta'), 
                           text=f"📁 {folder}",
                           tags=('folder',))
            self.log(f"Carpeta agregada: '{folder}'", "INFO")
        
        # Agregar archivos con información detallada
        total_files = 0
        for file_info in sorted(files, key=lambda x: x['name']):
            file_name = file_info['name']
            file_key = file_info['key']  # ← CRITICO: Usar clave completa del S3
            size_str = self.format_size(file_info['size'])
            file_ext = file_name.split('.')[-1].upper() if '.' in file_name else 'FILE'
            
            # Iconos específicos por tipo de archivo
            if file_ext.lower() in ['zip', 'rar', '7z']:
                icon = "🗜️"
            elif file_ext.lower() in ['sql', 'dump', 'psql', 'pg_dump']:
                icon = "🗄️"
            elif file_ext.lower() in ['bak', 'trn']:
                icon = "💾"
            elif file_ext.lower() in ['tar', 'gz']:
                icon = "📦"
            else:
                icon = "📄"
                
            # Crear item en el tree
            item_id = self.tree.insert('', 'end',
                           values=(size_str, file_ext),
                           text=f"{icon} {file_name}",
                           tags=('file',))
            
            # SOLUCION CRITICA: Guardar la clave completa S3 para descarga
            self._file_keys[item_id] = file_key
            total_files += 1
            
            self.log(f"Archivo agregado: '{file_name}' -> clave: '{file_key}'", "INFO")
        
        # Actualizar contador
        self.update_file_count(total_files)
        
        # Log resumen final
        self.log(f"📂 UI actualizada: {len(folders)} carpetas, {len(files)} archivos de backup", "SUCCESS")
        
        # Si no hay contenido, mostrar mensaje informativo
        if len(folders) == 0 and len(files) == 0:
            self.log(f"📭 Carpeta vacía o sin archivos de backup válidos", "WARNING")
            # Agregar un mensaje informativo en el tree
            self.tree.insert('', 'end',
                           values=('', ''),
                           text="📭 No hay archivos de backup en esta ubicación",
                           tags=('info',))
        
        # Actualizar la barra de estado: indicar que se completó la carga y limpiar después
        try:
            self.update_status("Listo")
            # Limpiar el status después de 2 segundos para dejar la barra limpia
            self.root.after(2000, lambda: self.update_status(""))
        except Exception:
            pass
    
    def on_tree_select(self, event=None):
        """Manejador de selección en el árbol con UI moderna"""
        # Solo funcionar si estamos en step 3 y tenemos el tree widget
        if self.current_step != 3 or not hasattr(self, 'tree'):
            return
            
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            text = self.tree.item(item, 'text')
            values = self.tree.item(item, 'values')
            
            if text and any(text.startswith(icon) for icon in ["📄", "🗜️", "🗄️", "💾", "📦"]):  # Es un archivo
                # Extraer nombre del archivo (quitar icono) y limpiar espacios
                file_name = text[2:].strip()  # Quitar emoji, espacio y espacios extra
                size = values[0] if values else "Desconocido"
                file_type = values[1] if len(values) > 1 else "Archivo"
                
                # Obtener la clave completa guardada
                file_key = None
                if hasattr(self, '_file_keys') and item in self._file_keys:
                    file_key = self._file_keys[item]
                    self.log(f"Usando clave guardada: '{file_key}'", "INFO")
                else:
                    # Fallback al método anterior si no hay clave guardada
                    file_key = self.current_path + file_name
                    self.log(f"Usando clave construida: '{file_key}' (verificar si es correcta)", "WARNING")
                
                self.selected_file_info = {
                    'name': file_name,
                    'size': size,
                    'key': file_key,
                    'type': file_type
                }
                
                # Actualizar navegación para habilitar botón siguiente
                self.update_navigation_buttons()
                
                # Habilitar botón "Generar Link"
                if hasattr(self, 'generate_link_btn'):
                    self.generate_link_btn.config(state='normal', bg=COLORS['warning'])
                
                self.log(f"🔍 Seleccionado: {file_name} ({size})", "INFO")
            else:
                # Reset si no es archivo válido
                self.selected_file_info = None
                self.update_navigation_buttons()
                
                # Deshabilitar botón "Generar Link"
                if hasattr(self, 'generate_link_btn'):
                    self.generate_link_btn.config(state='disabled', bg=COLORS['border'])
    
    def format_size(self, bytes_size):
        """Formatea el tamaño en bytes con emojis modernos"""
        # Si ya es un string formateado, devolverlo tal como está
        if isinstance(bytes_size, str):
            return bytes_size
        
        # Si es None o 0, devolver valor por defecto
        if not bytes_size or bytes_size == 0:
            return "0 B"
        
        # Convertir a float si es necesario
        try:
            bytes_size = float(bytes_size)
        except (ValueError, TypeError):
            return "Desconocido"
        
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                if unit == 'B':
                    return f"{bytes_size:.0f} {unit}"
                else:
                    return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"
                
    def on_tree_double_click(self, event=None):
        """Manejador de doble click en el árbol moderno - CORREGIDO para navegación S3"""
        selection = self.tree.selection()
        if selection:
            item = selection[0]
            text = self.tree.item(item, 'text')
            
            if text.startswith('📁'):  # Es una carpeta
                folder_name = text[2:].strip()  # Quitar emoji y espacios
                
                # SOLUCION CRITICA: Verificar si tenemos prefijo prealmacenado
                if hasattr(self, '_folder_prefixes') and folder_name in self._folder_prefixes:
                    # Usar el prefijo exacto guardado (incluye doble barras si es necesario)
                    new_prefix = self._folder_prefixes[folder_name]
                    self.log(f"🔍 Usando prefijo guardado: '{folder_name}' → '{new_prefix}'", "SUCCESS")
                else:
                    # Log en caso de no encontrar prefijo almacenado
                    if hasattr(self, '_folder_prefixes'):
                        available_prefixes = list(self._folder_prefixes.keys())
                        self.log(f"⚠️ Prefijo para '{folder_name}' no encontrado. Disponibles: {available_prefixes}", "WARNING")
                    
                    # Construcción tradicional de prefijo
                    if self.current_path.endswith('/'):
                        new_prefix = self.current_path + folder_name + "/"
                    elif self.current_path == "":
                        new_prefix = folder_name + "/"
                    else:
                        new_prefix = self.current_path + "/" + folder_name + "/"
                
                # Guardar en historial para navegación hacia atrás
                self.navigation_history.append(self.current_path)
                
                self.log(f"📂 Navegando a carpeta: '{folder_name}' (nuevo prefijo: '{new_prefix}')", "INFO")
                self.update_status(f"📂 Cargando {folder_name}...")
                
                # Cargar contenido de la subcarpeta
                self.load_bucket_contents(new_prefix)
                
            elif any(text.startswith(icon) for icon in ["📄", "🗜️", "🗄️", "💾", "📦"]):
                # Archivo seleccionado - Solo mostrar información, NO iniciar descarga
                file_name = text[2:].strip() if len(text) > 2 else text
                self.log(f"� Archivo seleccionado: {file_name}", "INFO")
                # No hacer nada más - la descarga debe hacerse solo con el botón DESCARGAR
    
    def go_back(self):
        """Navegar hacia atrás - CORREGIDO para navegación S3 robusta"""
        current_prefix = self.breadcrumb_label.cget('text').replace('📍 Ruta: /', '')
        
        # Limpiar selección y desactivar botones al navegar hacia atrás
        self.selected_file_info = None
        if hasattr(self, 'generate_link_btn'):
            self.generate_link_btn.config(state='disabled', bg=COLORS['border'])
        
        # Si tenemos historial de navegación, usarlo
        if hasattr(self, 'navigation_history') and self.navigation_history:
            previous_path = self.navigation_history.pop()
            self.log(f"⬅️ Navegando hacia atrás: '{current_prefix}' → '{previous_path}'", "INFO")
            self.update_status("📂 Cargando...")
            self.load_bucket_contents(previous_path)
        else:
            # Sin historial: ir un nivel arriba basado en la ruta actual
            if current_prefix and current_prefix != '/':
                # Dividir la ruta y quitar el último segmento
                path_parts = current_prefix.strip('/').split('/')
                if len(path_parts) > 1:
                    # Hay más de un segmento, ir un nivel arriba
                    parent_path = '/'.join(path_parts[:-1]) + '/'
                    self.log(f"⬅️ Subiendo un nivel: '{current_prefix}' → '{parent_path}'", "INFO")
                    self.update_status("📂 Cargando...")
                    self.load_bucket_contents(parent_path)
                else:
                    # Solo un segmento, ir a la raíz
                    self.log(f"⬅️ Volviendo a la raíz del bucket", "INFO")
                    self.update_status("📂 Cargando raíz...")
                    self.load_bucket_contents('')
            else:
                # Ya estamos en la raíz
                self.log(f"ℹ️ Ya estás en la raíz del bucket", "INFO")
    
    def refresh_tree(self):
        """Actualiza el contenido actual"""
        if self.selected_bucket:
            # Limpiar selección al actualizar
            self.selected_file_info = None
            if hasattr(self, 'generate_link_btn'):
                self.generate_link_btn.config(state='disabled', bg=COLORS['border'])
            
            # Actualizar status al refrescar
            self.update_status("🔄 Actualizando...")
            self.load_bucket_contents(self.current_path)
    
    def show_diagnostic_info(self):
        """Muestra información de diagnóstico para carpetas problemáticas como PRE/"""
        if not self.s3_client or not self.selected_bucket:
            messagebox.showwarning("⚠️ Diagnóstico", "No hay bucket seleccionado")
            return
        
        current_prefix = getattr(self, 'current_path', '')
        
        try:
            # Obtener información detallada del prefijo actual
            response = self.s3_client.list_objects_v2(
                Bucket=self.selected_bucket,
                Prefix=current_prefix,
                MaxKeys=50  # Limitar para el diagnóstico
            )
            
            # Preparar información de diagnóstico
            info_lines = []
            info_lines.append(f"🔧 DIAGNÓSTICO DE CARPETA")
            info_lines.append(f"Bucket: {self.selected_bucket}")
            info_lines.append(f"Prefijo actual: '{current_prefix or '(raíz)'}'")
            info_lines.append("")
            
            # Contar elementos
            objects = response.get('Contents', [])
            total_objects = len(objects)
            backup_files = 0
            folders = set()
            
            # Analizar objetos
            for obj in objects:
                key = obj['Key']
                if key.endswith('/'):
                    # Es una carpeta
                    folder_name = key.rstrip('/').split('/')[-1]
                    if folder_name:
                        folders.add(folder_name)
                else:
                    # Es un archivo
                    file_name = key.split('/')[-1]
                    if any(file_name.lower().endswith(ext) for ext in BACKUP_EXTENSIONS):
                        backup_files += 1
            
            # Obtener CommonPrefixes también
            response_with_delimiter = self.s3_client.list_objects_v2(
                Bucket=self.selected_bucket,
                Prefix=current_prefix,
                Delimiter='/',
                MaxKeys=50
            )
            
            common_prefixes = response_with_delimiter.get('CommonPrefixes', [])
            
            # Mostrar resultados
            info_lines.append(f"📊 RESUMEN:")
            info_lines.append(f"  • Total objetos: {total_objects}")
            info_lines.append(f"  • Archivos de backup: {backup_files}")
            info_lines.append(f"  • Subcarpetas (CommonPrefixes): {len(common_prefixes)}")
            info_lines.append("")
            
            if common_prefixes:
                info_lines.append("📁 SUBCARPETAS DETECTADAS:")
                for i, prefix_info in enumerate(common_prefixes[:10]):  # Solo primeras 10
                    full_prefix = prefix_info['Prefix']
                    folder_name = full_prefix.rstrip('/').split('/')[-1]
                    info_lines.append(f"  {i+1}. '{folder_name}' → {full_prefix}")
                    if folder_name.upper() in ['PRE', 'PREFIX']:
                        info_lines.append(f"     ⚠️ Carpeta PRE especial detectada")
            
            if backup_files > 0:
                info_lines.append("")
                info_lines.append("📄 ARCHIVOS DE BACKUP:")
                count = 0
                for obj in objects:
                    if count >= 5:  # Solo primeros 5
                        info_lines.append(f"     ... y {backup_files - count} más")
                        break
                    key = obj['Key']
                    if not key.endswith('/'):
                        file_name = key.split('/')[-1]
                        if any(file_name.lower().endswith(ext) for ext in BACKUP_EXTENSIONS):
                            size = self.format_size(obj['Size'])
                            info_lines.append(f"  • {file_name} ({size})")
                            count += 1
            
            # Sugerencias si no hay contenido visible
            if len(common_prefixes) == 0 and backup_files == 0:
                info_lines.append("")
                info_lines.append("💡 SUGERENCIAS:")
                info_lines.append("  • Probar navegar sin delimiter (exploración profunda)")
                info_lines.append("  • Verificar permisos del bucket")
                info_lines.append("  • La carpeta puede estar realmente vacía")
            
            # Mostrar el diagnóstico
            diagnostic_text = "\n".join(info_lines)
            
            # Crear ventana de diagnóstico
            diag_window = tk.Toplevel(self.root)
            diag_window.title("🔧 Diagnóstico de Carpeta S3")
            diag_window.geometry("600x500")
            diag_window.configure(bg=COLORS['background'])
            
            # Texto scrolleable
            text_frame = tk.Frame(diag_window, bg=COLORS['background'])
            text_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            text_widget = ScrolledText(text_frame, 
                                     font=('Consolas', 10),
                                     bg=COLORS['surface'],
                                     fg=COLORS['text_primary'],
                                     wrap=tk.WORD)
            text_widget.pack(fill=tk.BOTH, expand=True)
            text_widget.insert(tk.END, diagnostic_text)
            text_widget.config(state=tk.DISABLED)  # Solo lectura
            
            # Botón cerrar
            close_btn = tk.Button(diag_window,
                                text="✅ Cerrar",
                                font=('Inter', 11),
                                bg=COLORS['accent'],
                                fg='white',
                                command=diag_window.destroy)
            close_btn.pack(pady=(10, 20))
            
            self.log(f"🔧 Diagnóstico mostrado para: {current_prefix}", "INFO")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Error en diagnóstico:\n{str(e)}")
            self.log(f"❌ Error en diagnóstico: {e}", "ERROR")
    
    def start_download_legacy(self):
        """Inicia la descarga del archivo seleccionado con UI moderna (LEGACY - NO USAR)"""
        # MÉTODO LEGACY DESACTIVADO - usar start_download del wizard
        return
        
        if not self.selected_file_info:
            messagebox.showerror("⚠️ Error", "📁 Seleccione un archivo primero")
            return
        
        # Seleccionar directorio de destino con mensaje moderno
        download_dir = filedialog.askdirectory(
            title="📂 Seleccionar directorio de descarga",
            initialdir=os.getcwd()
        )
        
        if not download_dir:
            return
        
        self.download_directory = download_dir
        self.log(f"📂 Directorio de descarga: {download_dir}", "INFO")
        
        # Confirmar descarga con diálogo moderno
        response = messagebox.askyesno(
            "🚀 Confirmar Descarga", 
            f"📥 ¿Descargar {self.selected_file_info['name']} a:\n📂 {download_dir}?",
            icon='question'
        )
        
        if response:
            self.log(f"🚀 Iniciando descarga: {self.selected_file_info['name']}", "INFO")
            self.update_status("📥 Preparando descarga...")
            # Ejecutar descarga en hilo separado
            threading.Thread(target=self._download_thread, daemon=True).start()
    
    def _download_thread(self):
        """Hilo para realizar la descarga"""
        try:
            file_info = self.selected_file_info
            file_path = Path(self.download_directory) / file_info['name']
            
            self.log(f"Iniciando descarga: {file_info['name']}", "SUCCESS")
            self.root.after(0, lambda: self.update_status("Descargando..."))
            
            # Obtener tamaño del archivo
            s3_client = self.session.client('s3')
            obj_info = s3_client.head_object(Bucket=self.selected_bucket, Key=file_info['key'])
            total_size = obj_info['ContentLength']
            
            # Variables de progreso
            self.downloaded_bytes = 0
            
            def progress_callback(bytes_transferred):
                self.downloaded_bytes += bytes_transferred
                progress = (self.downloaded_bytes / total_size) * 100
                current_size = self.format_size(self.downloaded_bytes)
                total_size_str = self.format_size(total_size)
                
                self.root.after(0, lambda: self._update_progress(progress, current_size, total_size_str))
            
            # Realizar descarga
            s3_client.download_file(
                Bucket=self.selected_bucket,
                Key=file_info['key'],
                Filename=str(file_path),
                Callback=progress_callback
            )
            
            # Descarga completada
            self.log(f"Descarga completada: {file_path}", "SUCCESS")
            self.root.after(0, self._download_completed)
            
        except Exception as e:
            self.log(f"Error en descarga: {e}", "ERROR")
            self.root.after(0, self._download_failed)
    
    def _update_progress(self, progress, current, total):
        """Actualiza la barra de progreso con estilo moderno"""
        # Solo actualizar si estamos en el paso 4 y los widgets existen
        if (hasattr(self, 'progress_var') and hasattr(self, 'progress_label') 
            and self.current_step == 4):
            self.progress_var.set(progress)
            self.progress_label.config(text=f"📥 {progress:.1f}% - {current} / {total}")
            self.update_status(f"📥 Descargando... {progress:.1f}%")
    
    def _download_completed(self):
        """Maneja la finalización exitosa de descarga con UI moderna"""
        if (hasattr(self, 'progress_var') and hasattr(self, 'progress_label') 
            and self.current_step == 4):
            self.progress_var.set(100)
            self.progress_label.config(text="✅ Descarga completada")
        # Establecer estado y limpiar luego para UX más limpio
        try:
            self.update_status("Listo")
            self.root.after(1500, lambda: self.update_status(""))
        except Exception:
            pass
        self.log(f"✅ Descarga exitosa: {self.selected_file_info['name']}", "SUCCESS")
        messagebox.showinfo("🎉 Éxito", "📥 Archivo descargado exitosamente")
    
    def _download_failed(self):
        """Maneja el fallo de descarga con UI moderna"""
        if (hasattr(self, 'progress_var') and hasattr(self, 'progress_label') 
            and self.current_step == 4):
            self.progress_var.set(0)
            self.progress_label.config(text="❌ Error en descarga")
        try:
            self.update_status("❌ Error en descarga")
            self.root.after(2500, lambda: self.update_status(""))
        except Exception:
            pass
        self.log("❌ Error durante la descarga", "ERROR")
        messagebox.showerror("⚠️ Error", "❌ Error durante la descarga")
    
    def on_closing(self):
        """Manejador de cierre de ventana con diálogo moderno"""
        response = messagebox.askokcancel(
            "👋 Salir", 
            "❓ ¿Desea cerrar AWS Backup Manager?",
            icon='question'
        )
        if response:
            self.log("👋 Cerrando aplicación", "INFO")
            self.update_status("👋 Cerrando...")
            self.root.quit()
            self.root.destroy()
    
    def run(self):
        """Ejecuta la aplicación"""
        self.log("Interfaz gráfica iniciada")
        self.root.mainloop()

class GUILogHandler(logging.Handler):
    """Handler personalizado para mostrar logs en la GUI"""
    
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    
    def emit(self, record):
        """Emite un registro de log"""
        try:
            msg = self.format(record)
            # No agregar aquí porque ya se maneja en el método log de la GUI
        except Exception:
            self.handleError(record)

def main():
    """Función principal"""
    try:
        app = AWSBackupGUI()
        app.run()
    except KeyboardInterrupt:
        logging.info("Aplicación cerrada por el usuario")
    except Exception as e:
        logging.error(f"Error crítico: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
