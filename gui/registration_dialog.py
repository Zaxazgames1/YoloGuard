# -*- coding: utf-8 -*-
"""Módulo para el diálogo de registro de personas."""

import os
import gc
import cv2
import json
import torch
import shutil
import traceback
import numpy as np
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QFormLayout, QGroupBox, QPushButton, QComboBox, QMessageBox,
    QFileDialog, QProgressDialog, QScrollArea, QWidget, QInputDialog,
    QTabWidget, QSizePolicy  # Añadimos QSizePolicy para responsive
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont

# Esta importación puede fallar si se ejecuta el archivo directamente
try:
    from config.constants import BASE_PATH, TARGET_FPS, SEDES, EXTENSIONES_CARRERAS
except ImportError:
    # Valores predeterminados en caso de que no se pueda importar
    BASE_PATH = "dataset_ucundinamarca"
    TARGET_FPS = 30
    SEDES = ["Fusagasugá", "Girardot", "Ubaté", "Facatativá", "Chía", "Chocontá", "Zipaquirá", "Soacha"]
    EXTENSIONES_CARRERAS = {}

class RegistroPersonaDialog(QDialog):
    """Diálogo para el registro de personas."""
    
    def __init__(self, parent=None):
        """
        Inicializa el diálogo de registro.
        
        Args:
            parent: Widget padre
        """
        super().__init__(parent)
        self.setWindowTitle("Registro de Persona - Universidad de Cundinamarca")
        self.setMinimumWidth(1000)
        self.setMinimumHeight(800)
        
        # Políticas de tamaño para hacer la ventana responsive
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        self.captured_images = []
        self.person_data = None
        
        # Lista completa de facultades
        self.todas_facultades = [
            "Ciencias Administrativas", 
            "Ingeniería", 
            "Ciencias Agropecuarias", 
            "Ciencias del Deporte", 
            "Educación", 
            "Ciencias Sociales", 
            "Ciencias de la Salud",
            "Artes",
            "Ciencias Exactas y Naturales",
            "Ciencias Humanas",
            "Ciencias Económicas",
            "Derecho y Ciencias Políticas"
        ]
        
        # Programas académicos por facultad
        self.programas_por_facultad = {
            "Ciencias Administrativas": [
                "Administración de Empresas", 
                "Contaduría Pública", 
                "Administración Turística y Hotelera",
                "Administración Financiera",
                "Administración Logística"
            ],
            "Ingeniería": [
                "Ingeniería de Sistemas", 
                "Ingeniería Electrónica", 
                "Ingeniería Industrial",
                "Ingeniería Ambiental",
                "Tecnología en Desarrollo de Software"
            ],
            "Ciencias Agropecuarias": [
                "Ingeniería Agronómica", 
                "Zootecnia", 
                "Medicina Veterinaria"
            ],
            "Ciencias del Deporte": [
                "Licenciatura en Educación Física", 
                "Ciencias del Deporte y la Educación Física",
                "Profesional en Ciencias del Deporte"
            ],
            "Educación": [
                "Licenciatura en Matemáticas", 
                "Licenciatura en Ciencias Sociales",
                "Licenciatura en Educación Básica", 
                "Licenciatura en Lengua Castellana",
                "Licenciatura en Inglés"
            ],
            "Ciencias Sociales": [
                "Psicología", 
                "Trabajo Social", 
                "Sociología"
            ],
            "Ciencias de la Salud": [
                "Enfermería", 
                "Medicina"
            ],
            "Artes": [
                "Música", 
                "Artes Plásticas"
            ],
            "Ciencias Exactas y Naturales": [
                "Matemáticas Aplicadas", 
                "Física",
                "Biología"
            ],
            "Ciencias Humanas": [
                "Filosofía", 
                "Historia"
            ],
            "Ciencias Económicas": [
                "Economía", 
                "Comercio Internacional"
            ],
            "Derecho y Ciencias Políticas": [
                "Derecho", 
                "Ciencias Políticas"
            ]
        }
        
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        main_layout = QHBoxLayout()
        
        # Panel izquierdo (formulario)
        left_panel = QVBoxLayout()
        
        # Header con logo y título
        header_layout = QHBoxLayout()
        
        # CAMBIO AQUÍ: Usar la imagen del logo de UDEC en lugar de dibujarla
        logo_label = QLabel()
        logo_udec_path = "resources/images/Logo_YoloGuard.jpg"  # Ruta al logo actualizada
        
        if os.path.exists(logo_udec_path):
            # Si existe el archivo de imagen, lo cargamos
            logo_pixmap = QPixmap(logo_udec_path)
            # Escalamos el logo a un tamaño adecuado
            logo_pixmap = logo_pixmap.scaled(150, 60, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        else:
            # Si no existe, creamos un logo placeholder
            logo_pixmap = QPixmap(150, 60)
            logo_pixmap.fill(QColor(0, 102, 51))  # Verde institucional
            painter = QPainter(logo_pixmap)
            painter.setPen(QColor(255, 255, 255))
            painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
            painter.drawText(logo_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "UDEC")
            painter.end()
            
        logo_label.setPixmap(logo_pixmap)
        logo_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        title_label = QLabel("Sistema de Control de Acceso\nUniversidad de Cundinamarca")
        title_label.setStyleSheet("""
            font-size: 20px;
            color: #006633;
            padding: 10px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        # Agregar logo de YoloGuard
        yologuard_logo = QLabel("YoloGuard")
        yologuard_logo.setStyleSheet("""
            font-size: 16px;
            color: #006633;
            font-weight: bold;
            border: 2px solid #006633;
            border-radius: 8px;
            padding: 5px 10px;
        """)
        yologuard_logo.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(yologuard_logo)
        left_panel.addLayout(header_layout)

        # Formulario en tabs para mejor organización
        form_tabs = QTabWidget()
        form_tabs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Tab 1: Información Personal
        personal_tab = QWidget()
        personal_layout = QVBoxLayout(personal_tab)
        
        form_group = QGroupBox("Información Personal")
        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.nombre_input.setMinimumHeight(30)
        self.nombre_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.id_input = QLineEdit()
        self.id_input.setMinimumHeight(30)
        self.id_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Rol con selector mejorado
        self.rol_input = QComboBox()
        self.rol_input.setMinimumHeight(30)
        self.rol_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.rol_input.addItems([
            "Estudiante", 
            "Docente", 
            "Administrativo", 
            "Visitante", 
            "Proveedor", 
            "Contratista",
            "Investigador",
            "Directivo",
            "Egresado"
        ])
        self.rol_input.currentIndexChanged.connect(self.on_rol_changed)
        
        # Tipo de acceso mejorado
        self.tipo_acceso = QComboBox()
        self.tipo_acceso.setMinimumHeight(30)
        self.tipo_acceso.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.tipo_acceso.addItems([
            "Completo", 
            "Biblioteca", 
            "Aulas", 
            "Laboratorios", 
            "Administrativo", 
            "Comedor", 
            "Deportivo", 
            "Cultural", 
            "Restringido",
            "Temporal",
            "Eventos"
        ])
        
        # Semestre (para estudiantes)
        self.semestre_layout = QHBoxLayout()
        self.semestre_input = QComboBox()
        self.semestre_input.setMinimumHeight(30)
        self.semestre_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.semestre_input.addItems(["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Egresado"])
        self.semestre_label = QLabel("Semestre:")
        self.semestre_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.semestre_layout.addWidget(self.semestre_label)
        self.semestre_layout.addWidget(self.semestre_input)
        self.semestre_widget = QWidget()
        self.semestre_widget.setLayout(self.semestre_layout)
        self.semestre_widget.setVisible(False)  # Inicialmente oculto

        # Estilo de etiquetas de formulario
        form_label_style = "font-size: 14px; font-weight: bold;"
        
        # Crear etiquetas con estilo
        nombre_label = QLabel("Nombre completo:")
        nombre_label.setStyleSheet(form_label_style)
        id_label = QLabel("ID/Código:")
        id_label.setStyleSheet(form_label_style)
        rol_label = QLabel("Rol:")
        rol_label.setStyleSheet(form_label_style)
        tipo_label = QLabel("Tipo de Acceso:")
        tipo_label.setStyleSheet(form_label_style)
        
        form_layout.addRow(nombre_label, self.nombre_input)
        form_layout.addRow(id_label, self.id_input)
        form_layout.addRow(rol_label, self.rol_input)
        form_layout.addRow(tipo_label, self.tipo_acceso)
        form_layout.addRow("", self.semestre_widget)
        
        form_group.setLayout(form_layout)
        personal_layout.addWidget(form_group)
        
        # Tab 2: Información Académica
        academic_tab = QWidget()
        academic_layout = QVBoxLayout(academic_tab)
        
        academic_group = QGroupBox("Información Académica")
        academic_form = QFormLayout()
        
        # Selector de sede
        self.sede_input = QComboBox()
        self.sede_input.setMinimumHeight(30)
        self.sede_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.sede_input.addItems(SEDES)
        self.sede_input.currentIndexChanged.connect(self.update_extensiones)
        
        # Selector de extensión
        self.extension_input = QComboBox()
        self.extension_input.setMinimumHeight(30)
        self.extension_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Facultad con creación dinámica
        facultad_layout = QHBoxLayout()
        self.facultad_input = QComboBox()
        self.facultad_input.setMinimumHeight(30)
        self.facultad_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.facultad_input.addItems(self.todas_facultades)
        self.facultad_input.currentIndexChanged.connect(self.update_programas)
        
        self.nueva_facultad_btn = QPushButton("+")
        self.nueva_facultad_btn.setFixedWidth(40)
        self.nueva_facultad_btn.setMinimumHeight(30)
        self.nueva_facultad_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.nueva_facultad_btn.clicked.connect(self.crear_nueva_facultad)
        facultad_layout.addWidget(self.facultad_input)
        facultad_layout.addWidget(self.nueva_facultad_btn)
        
        # Programa dependiente de la facultad
        programa_layout = QHBoxLayout()
        self.programa_input = QComboBox()
        self.programa_input.setMinimumHeight(30)
        self.programa_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.programa_input.setEditable(True)  # Permitir entrada personalizada
        
        self.nuevo_programa_btn = QPushButton("+")
        self.nuevo_programa_btn.setFixedWidth(40)
        self.nuevo_programa_btn.setMinimumHeight(30)
        self.nuevo_programa_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        self.nuevo_programa_btn.clicked.connect(self.crear_nuevo_programa)
        programa_layout.addWidget(self.programa_input)
        programa_layout.addWidget(self.nuevo_programa_btn)
        
        # Etiquetas con estilo mejorado
        sede_label = QLabel("Sede:")
        sede_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        extension_label = QLabel("Extensión:")
        extension_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        facultad_label = QLabel("Facultad:")
        facultad_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        programa_label = QLabel("Programa:")
        programa_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        academic_form.addRow(sede_label, self.sede_input)
        academic_form.addRow(extension_label, self.extension_input)
        academic_form.addRow(facultad_label, facultad_layout)
        academic_form.addRow(programa_label, programa_layout)
        
        academic_group.setLayout(academic_form)
        academic_layout.addWidget(academic_group)
        
        # Inicializar extensiones y programas
        self.update_extensiones(0)
        self.update_programas(0)
        
        # Añadir tabs al widget
        form_tabs.addTab(personal_tab, "Información Personal")
        form_tabs.addTab(academic_tab, "Información Académica")
        
        left_panel.addWidget(form_tabs)

        # Información de captura
        info_group = QGroupBox("Información de Captura")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Capture al menos 5 fotos desde diferentes ángulos")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.info_label.setWordWrap(True)
        
        self.counter_label = QLabel("Fotos capturadas: 0/5")
        self.counter_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.counter_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        
        info_layout.addWidget(self.info_label)
        info_layout.addWidget(self.counter_label)
        info_group.setLayout(info_layout)
        left_panel.addWidget(info_group)

        # Botones de control
        buttons_layout = QHBoxLayout()
        
        # Botón para cargar dataset existente
        self.load_dataset_btn = QPushButton("📁 Cargar Dataset")
        self.load_dataset_btn.setMinimumHeight(40)
        self.load_dataset_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.load_dataset_btn.clicked.connect(self.load_existing_dataset)
        
        self.guardar_btn = QPushButton("💾 Guardar")
        self.guardar_btn.setMinimumHeight(40)
        self.guardar_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.guardar_btn.clicked.connect(self.guardar_persona)
        self.guardar_btn.setEnabled(False)
        
        self.cancelar_btn = QPushButton("❌ Cancelar")
        self.cancelar_btn.setMinimumHeight(40)
        self.cancelar_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.cancelar_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.load_dataset_btn)
        buttons_layout.addWidget(self.guardar_btn)
        buttons_layout.addWidget(self.cancelar_btn)
        left_panel.addLayout(buttons_layout)

        # Panel derecho (preview y captura)
        right_panel = QVBoxLayout()
        
        # Preview
        preview_group = QGroupBox("Vista Previa")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(640, 480)
        self.preview_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.preview_label.setStyleSheet("""
            border: 2px solid #006633;
            background-color: #f0f0f0;
        """)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)
        
        self.capturar_btn = QPushButton("📸 Capturar Foto")
        self.capturar_btn.setMinimumHeight(40)
        self.capturar_btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.capturar_btn.clicked.connect(self.capturar_foto)
        preview_layout.addWidget(self.capturar_btn)
        
        preview_group.setLayout(preview_layout)
        right_panel.addWidget(preview_group)

        # Miniaturas de fotos capturadas
        thumbnails_group = QGroupBox("Fotos Capturadas")
        thumbnails_scroll = QScrollArea()
        thumbnails_scroll.setWidgetResizable(True)
        thumbnails_widget = QWidget()
        self.thumbnails_layout = QHBoxLayout(thumbnails_widget)
        thumbnails_scroll.setWidget(thumbnails_widget)
        thumbnails_layout = QVBoxLayout()
        thumbnails_layout.addWidget(thumbnails_scroll)
        thumbnails_group.setLayout(thumbnails_layout)
        right_panel.addWidget(thumbnails_group)

        # Establecer proporciones para los paneles
        left_widget = QWidget()
        left_widget.setLayout(left_panel)
        left_widget.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        
        right_widget = QWidget()
        right_widget.setLayout(right_panel)
        right_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        main_layout.addWidget(left_widget, 1)
        main_layout.addWidget(right_widget, 2)
        self.setLayout(main_layout)

        # Inicializar cámara con método optimizado
        self.camera = None
        try:
            # Intentamos importar la función para abrir la cámara
            try:
                from utils.camera import open_fastest_webcam
                # Usamos el índice de cámara por defecto (0)
                self.camera = open_fastest_webcam(0)
            except ImportError:
                # Si no podemos importar la función, usamos OpenCV directamente
                self.camera = cv2.VideoCapture(0)
        except Exception as e:
            print(f"Error al inicializar la cámara: {str(e)}")
                
        if self.camera is None or not self.camera.isOpened():
            QMessageBox.warning(self, "Advertencia", "No se pudo inicializar la cámara. Algunas funciones pueden no estar disponibles.")
        
        # Definir FPS objetivo en caso de que no se pueda importar
        target_fps = TARGET_FPS if 'TARGET_FPS' in globals() else 30
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(1000 // target_fps)  # Ajustar para obtener el FPS deseado
        
    def on_rol_changed(self, index):
        """Muestra u oculta campos dependiendo del rol seleccionado."""
        if self.rol_input.currentText() == "Estudiante":
            self.semestre_widget.setVisible(True)
        else:
            self.semestre_widget.setVisible(False)
            
    def update_extensiones(self, index):
        """Actualiza las extensiones y programas según la sede seleccionada."""
        sede_actual = self.sede_input.currentText()
        
        # Limpiar y actualizar extensiones (son las mismas que sedes para simplificar)
        self.extension_input.clear()
        self.extension_input.addItems(SEDES)
        # Por defecto seleccionar la misma que la sede
        extension_index = self.extension_input.findText(sede_actual)
        if extension_index >= 0:
            self.extension_input.setCurrentIndex(extension_index)
            
    def update_programas(self, index):
        """Actualiza los programas según la facultad seleccionada."""
        facultad_actual = self.facultad_input.currentText()
        
        # Limpiar el combo de programas
        self.programa_input.clear()
        
        # Agregar programas según la facultad seleccionada
        if facultad_actual in self.programas_por_facultad:
            self.programa_input.addItems(self.programas_por_facultad[facultad_actual])
        
    def crear_nuevo_programa(self):
        """Crear un nuevo programa académico."""
        programa, ok = QInputDialog.getText(
            self, 'Nuevo Programa', 
            'Ingrese el nombre del nuevo programa:'
        )
        if ok and programa:
            self.programa_input.addItem(programa)
            self.programa_input.setCurrentText(programa)
            
            # Añadir a la lista de programas para esta facultad
            facultad_actual = self.facultad_input.currentText()
            if facultad_actual in self.programas_por_facultad:
                if programa not in self.programas_por_facultad[facultad_actual]:
                    self.programas_por_facultad[facultad_actual].append(programa)
            else:
                self.programas_por_facultad[facultad_actual] = [programa]
    
    def crear_nueva_facultad(self):
        """Crear una nueva facultad."""
        facultad, ok = QInputDialog.getText(
            self, 'Nueva Facultad', 
            'Ingrese el nombre de la nueva facultad:'
        )
        if ok and facultad:
            # Verificar si la facultad ya existe
            if facultad in self.todas_facultades:
                QMessageBox.warning(self, "Advertencia", "Esta facultad ya existe.")
                return
                
            # Añadir la facultad a la lista
            self.todas_facultades.append(facultad)
            self.facultad_input.addItem(facultad)
            self.facultad_input.setCurrentText(facultad)
            
            # Crear estructura de directorios
            try:
                facultad_path = os.path.join(BASE_PATH, facultad)
                os.makedirs(facultad_path, exist_ok=True)
            except Exception as e:
                print(f"Error al crear directorio para la facultad: {str(e)}")
            
            # Inicializar lista de programas para esta facultad
            self.programas_por_facultad[facultad] = []
            
            # Solicitar programa inicial
            self.crear_nuevo_programa()

    def update_preview(self):
        """Actualizar la vista previa de la cámara."""
        if not hasattr(self, 'camera') or self.camera is None or not self.camera.isOpened():
            return
            
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            
            # Escalar la imagen manteniendo la proporción
            pixmap = QPixmap.fromImage(qt_image)
            scaled_pixmap = pixmap.scaled(
                self.preview_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.preview_label.setPixmap(scaled_pixmap)

    def capturar_foto(self):
        """Capturar una foto desde la cámara."""
        if not hasattr(self, 'camera') or self.camera is None or not self.camera.isOpened():
            QMessageBox.warning(self, "Error", "Cámara no disponible")
            return
            
        ret, frame = self.camera.read()
        if ret:
            try:
                # Detectar rostro
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Si el padre tiene MTCNN, usarlo
                mtcnn = None
                parent_widget = self.parent()
                if parent_widget is not None and hasattr(parent_widget, 'mtcnn'):
                    mtcnn = parent_widget.mtcnn
                
                faces_detected = True
                if mtcnn is not None:
                    faces = mtcnn(rgb_frame)
                    faces_detected = faces is not None
                else:
                    # Si no hay MTCNN, asumimos que hay un rostro
                    faces_detected = True
                
                if faces_detected:
                    # Guardar la imagen
                    self.captured_images.append(frame.copy())  # Usar .copy() para evitar problemas de referencias
                    self.counter_label.setText(f"Fotos capturadas: {len(self.captured_images)}/5")
                    
                    # Crear y mostrar miniatura
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
                    pixmap = QPixmap.fromImage(qt_image).scaled(
                        100, 100, 
                        Qt.AspectRatioMode.KeepAspectRatio, 
                        Qt.TransformationMode.SmoothTransformation
                    )
                    
                    thumb_label = QLabel()
                    thumb_label.setPixmap(pixmap)
                    thumb_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                    self.thumbnails_layout.addWidget(thumb_label)
                    
                    # Habilitar guardado si hay suficientes fotos
                    if len(self.captured_images) >= 5:
                        self.guardar_btn.setEnabled(True)
                        self.info_label.setText("¡Listo para guardar!")
                        self.info_label.setStyleSheet("color: #006633; font-size: 14px; font-weight: bold;")
                    
                    # Efecto de flash
                    flash = QLabel(self.preview_label)
                    flash.resize(self.preview_label.size())
                    flash.setStyleSheet("background-color: rgba(255, 255, 255, 0.7);")
                    flash.show()
                    QTimer.singleShot(100, flash.deleteLater)
                else:
                    QMessageBox.warning(self, "Advertencia", "No se detectó ningún rostro en la imagen")
            
            except Exception as e:
                print(f"Error al capturar foto: {str(e)}")
                traceback.print_exc()
                QMessageBox.warning(self, "Error", f"Error al procesar la imagen: {str(e)}")

    def load_existing_dataset(self):
        """Cargar un dataset existente de imágenes."""
        try:
            # Abrir diálogo para seleccionar directorio
            dataset_dir = QFileDialog.getExistingDirectory(
                self, "Seleccionar Directorio del Dataset"
            )
            
            if dataset_dir:
                # Verificar si el directorio contiene imágenes
                valid_extensions = ('.jpg', '.jpeg', '.png')
                image_files = [f for f in os.listdir(dataset_dir) 
                             if f.lower().endswith(valid_extensions)]
                
                if not image_files:
                    QMessageBox.warning(self, "Error", 
                        "No se encontraron imágenes en el directorio seleccionado")
                    return
                    
                # Limpiar imágenes existentes
                for i in reversed(range(self.thumbnails_layout.count())): 
                    widget = self.thumbnails_layout.itemAt(i).widget()
                    if widget:
                        widget.setParent(None)
                self.captured_images.clear()
                
                # Mostrar diálogo de progreso
                progress = QProgressDialog("Cargando imágenes...", "Cancelar", 0, len(image_files), self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(0)
                
                # Limitar a cargar máximo 10 imágenes para mejor rendimiento
                max_images = min(10, len(image_files))
                
                # Cargar las imágenes
                for i, img_file in enumerate(image_files[:max_images]):
                    if progress.wasCanceled():
                        break
                        
                    img_path = os.path.join(dataset_dir, img_file)
                    img = cv2.imread(img_path)
                    if img is not None:
                        # Reducir tamaño si es muy grande
                        if img.shape[0] > 800 or img.shape[1] > 800:
                            ratio = min(800 / img.shape[0], 800 / img.shape[1])
                            new_size = (int(img.shape[1] * ratio), int(img.shape[0] * ratio))
                            img = cv2.resize(img, new_size)
                            
                        self.captured_images.append(img)
                        
                        # Crear y mostrar miniatura
                        h, w, ch = img.shape
                        bytes_per_line = ch * w
                        qt_image = QImage(img.data, w, h, bytes_per_line, 
                                        QImage.Format.Format_BGR888)
                        pixmap = QPixmap.fromImage(qt_image).scaled(
                            100, 100, 
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.SmoothTransformation
                        )
                        
                        thumb_label = QLabel()
                        thumb_label.setPixmap(pixmap)
                        thumb_label.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
                        self.thumbnails_layout.addWidget(thumb_label)
                    
                    progress.setValue(i + 1)
                
                # Cerrar diálogo de progreso
                progress.setValue(len(image_files))
                
                # Actualizar contador
                self.counter_label.setText(
                    f"Fotos cargadas: {len(self.captured_images)}/{max_images}")
                
                if len(self.captured_images) >= 5:
                    self.guardar_btn.setEnabled(True)
                    self.info_label.setText("¡Dataset cargado correctamente!")
                    self.info_label.setStyleSheet("color: #006633; font-size: 14px; font-weight: bold;")
                    
                QMessageBox.information(self, "Éxito", 
                    f"Se cargaron {len(self.captured_images)} imágenes")
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", 
                f"Error al cargar dataset: {str(e)}")
                
    def guardar_persona(self):
        """Guardar datos de la persona y sus fotos."""
        if not self.validate_inputs():
            return

        try:
            # Asegurarse de que existe el directorio base
            os.makedirs(BASE_PATH, exist_ok=True)
            
            # Crear estructura de directorios
            facultad_path = os.path.join(BASE_PATH, self.facultad_input.currentText())
            os.makedirs(facultad_path, exist_ok=True)
            
            person_path = os.path.join(facultad_path, self.nombre_input.text())
            if os.path.exists(person_path):
                if QMessageBox.question(self, "Confirmar", 
                    "Ya existe una persona con este nombre. ¿Desea sobrescribir?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.No:
                    return
                shutil.rmtree(person_path)
            
            os.makedirs(person_path, exist_ok=True)

            # Mostrar diálogo de progreso
            progress = QProgressDialog("Procesando imágenes...", "Cancelar", 0, len(self.captured_images), self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Procesar y guardar fotos
            saved_images = 0
            print("Procesando imágenes para guardar...")
            
            for i, image in enumerate(self.captured_images):
                if progress.wasCanceled():
                    break
                    
                try:
                    # Guardar imagen original
                    img_path = os.path.join(person_path, f"foto_{i+1}.jpg")
                    cv2.imwrite(img_path, image)
                    saved_images += 1
                    print(f"Imagen {i+1} guardada exitosamente")
                    
                except Exception as e:
                    print(f"Error al procesar imagen {i+1}: {str(e)}")
                    traceback.print_exc()
                    continue
                    
                progress.setValue(i + 1)

            # Cerrar diálogo de progreso
            progress.setValue(len(self.captured_images))
            
            if saved_images == 0:
                QMessageBox.warning(self, "Error", "No se pudieron guardar ninguna foto")
                return

            # Obtener semestre si es estudiante
            semestre = ""
            if self.rol_input.currentText() == "Estudiante":
                semestre = self.semestre_input.currentText()

            # Crear un diccionario con los datos de la persona
            person_dict = {
                "nombre": self.nombre_input.text(),
                "id": self.id_input.text(),
                "facultad": self.facultad_input.currentText(),
                "programa": self.programa_input.currentText(),
                "rol": self.rol_input.currentText(),
                "tipo": self.tipo_acceso.currentText(),
                "sede": self.sede_input.currentText(),
                "extension": self.extension_input.currentText(),
                "semestre": semestre,
                "fecha_registro": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Guardar metadata como JSON
            metadata_path = os.path.join(person_path, "info.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(person_dict, f, indent=4, ensure_ascii=False)
            
            print("Metadata guardada exitosamente")
            
            # Intentar crear el objeto UniversityPersonData si la clase está disponible
            try:
                from data.person import UniversityPersonData
                self.person_data = UniversityPersonData.from_dict(person_dict)
            except ImportError:
                # Si no se puede importar, usar el diccionario directamente
                self.person_data = person_dict
                
            QMessageBox.information(self, "Éxito", 
                f"Persona registrada correctamente\nSe guardaron {saved_images} fotos")
            self.accept()

        except Exception as e:
            print(f"Error al guardar persona: {str(e)}")
            traceback.print_exc()
            QMessageBox.critical(self, "Error", f"Error al guardar: {str(e)}")

    def validate_inputs(self):
        """Validar que todos los campos requeridos estén completos."""
        if not self.nombre_input.text().strip():
            QMessageBox.warning(self, "Error", "El nombre es obligatorio")
            self.nombre_input.setFocus()
            return False
        
        if not self.id_input.text().strip():
            QMessageBox.warning(self, "Error", "El ID/Código es obligatorio")
            self.id_input.setFocus()
            return False
        
        if not self.facultad_input.currentText().strip():
            QMessageBox.warning(self, "Error", "La facultad es obligatoria")
            self.facultad_input.setFocus()
            return False
        
        if not self.programa_input.currentText().strip():
            QMessageBox.warning(self, "Error", "El programa académico es obligatorio")
            self.programa_input.setFocus()
            return False
        
        if len(self.captured_images) < 5:
            QMessageBox.warning(self, "Error", "Se requieren al menos 5 fotos")
            return False
        
        return True

    def closeEvent(self, event):
        """Limpiar recursos al cerrar el diálogo."""
        self.timer.stop()
        if hasattr(self, 'camera') and self.camera is not None:
            self.camera.release()
            self.camera = None
        
        # Liberar memoria
        self.captured_images.clear()
        gc.collect()
        
        # Llamar al evento original
        super().closeEvent(event)