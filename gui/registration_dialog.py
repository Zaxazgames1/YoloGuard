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
    QTabWidget  # Añadimos QTabWidget aquí
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont

from config.constants import BASE_PATH, TARGET_FPS, SEDES, EXTENSIONES_CARRERAS
from data.person import UniversityPersonData
from utils.camera import open_fastest_webcam

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
        self.captured_images = []
        self.person_data = None
        self.setup_ui()

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        main_layout = QHBoxLayout()
        
        # Panel izquierdo (formulario)
        left_panel = QVBoxLayout()
        
        # Header con logo y título
        header_layout = QHBoxLayout()
        logo_label = QLabel()
        # Crear una imagen placeholder verde con "UDEC"
        logo_pixmap = QPixmap(150, 60)
        logo_pixmap.fill(QColor(0, 102, 51))  # Verde institucional
        painter = QPainter(logo_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(logo_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "UDEC")
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        
        title_label = QLabel("Sistema de Control de Acceso\nUniversidad de Cundinamarca")
        title_label.setStyleSheet("""
            font-size: 20px;
            color: #006633;
            padding: 10px;
            font-weight: bold;
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
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
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(yologuard_logo)
        left_panel.addLayout(header_layout)

        # Formulario en tabs para mejor organización
        form_tabs = QTabWidget()
        
        # Tab 1: Información Personal
        personal_tab = QWidget()
        personal_layout = QVBoxLayout(personal_tab)
        
        form_group = QGroupBox("Información Personal")
        form_layout = QFormLayout()

        self.nombre_input = QLineEdit()
        self.nombre_input.setMinimumHeight(30)
        self.id_input = QLineEdit()
        self.id_input.setMinimumHeight(30)
        
        # Rol con selector mejorado
        self.rol_input = QComboBox()
        self.rol_input.setMinimumHeight(30)
        self.rol_input.addItems(["Estudiante", "Docente", "Administrativo", "Visitante", "Proveedor", "Contratista"])
        self.rol_input.currentIndexChanged.connect(self.on_rol_changed)
        
        # Tipo de acceso mejorado
        self.tipo_acceso = QComboBox()
        self.tipo_acceso.setMinimumHeight(30)
        self.tipo_acceso.addItems([
            "Completo", "Biblioteca", "Aulas", "Laboratorios", "Administrativo", 
            "Comedor", "Deportivo", "Cultural", "Restringido"
        ])
        
        # Semestre (para estudiantes)
        self.semestre_layout = QHBoxLayout()
        self.semestre_input = QComboBox()
        self.semestre_input.setMinimumHeight(30)
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
        self.sede_input.addItems(SEDES)
        self.sede_input.currentIndexChanged.connect(self.update_extensiones)
        
        # Selector de extensión
        self.extension_input = QComboBox()
        self.extension_input.setMinimumHeight(30)
        
        # Facultad con creación dinámica
        facultad_layout = QHBoxLayout()
        self.facultad_input = QComboBox()
        self.facultad_input.setMinimumHeight(30)
        self.cargar_facultades()
        self.nueva_facultad_btn = QPushButton("+")
        self.nueva_facultad_btn.setFixedWidth(40)
        self.nueva_facultad_btn.setMinimumHeight(30)
        self.nueva_facultad_btn.clicked.connect(self.crear_nueva_facultad)
        facultad_layout.addWidget(self.facultad_input)
        facultad_layout.addWidget(self.nueva_facultad_btn)
        
        # Programa dependiente de la sede y extensión
        programa_layout = QHBoxLayout()
        self.programa_input = QComboBox()
        self.programa_input.setMinimumHeight(30)
        self.programa_input.setEditable(True)  # Permitir entrada personalizada
        self.nuevo_programa_btn = QPushButton("+")
        self.nuevo_programa_btn.setFixedWidth(40)
        self.nuevo_programa_btn.setMinimumHeight(30)
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
        
        # Inicializar extensiones
        self.update_extensiones(0)
        
        # Añadir tabs al widget
        form_tabs.addTab(personal_tab, "Información Personal")
        form_tabs.addTab(academic_tab, "Información Académica")
        
        left_panel.addWidget(form_tabs)

        # Información de captura
        info_group = QGroupBox("Información de Captura")
        info_layout = QVBoxLayout()
        self.info_label = QLabel("Capture al menos 5 fotos desde diferentes ángulos")
        self.info_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.counter_label = QLabel("Fotos capturadas: 0/5")
        self.counter_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        info_layout.addWidget(self.info_label)
        info_layout.addWidget(self.counter_label)
        info_group.setLayout(info_layout)
        left_panel.addWidget(info_group)

        # Botones de control
        buttons_layout = QHBoxLayout()
        
        # Botón para cargar dataset existente
        self.load_dataset_btn = QPushButton("📁 Cargar Dataset")
        self.load_dataset_btn.setMinimumHeight(40)
        self.load_dataset_btn.clicked.connect(self.load_existing_dataset)
        
        self.guardar_btn = QPushButton("💾 Guardar")
        self.guardar_btn.setMinimumHeight(40)
        self.guardar_btn.clicked.connect(self.guardar_persona)
        self.guardar_btn.setEnabled(False)
        
        self.cancelar_btn = QPushButton("❌ Cancelar")
        self.cancelar_btn.setMinimumHeight(40)
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
        self.preview_label.setStyleSheet("""
            border: 2px solid #006633;
            background-color: #f0f0f0;
        """)
        preview_layout.addWidget(self.preview_label)
        
        self.capturar_btn = QPushButton("📸 Capturar Foto")
        self.capturar_btn.setMinimumHeight(40)
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

        main_layout.addLayout(left_panel, 1)
        main_layout.addLayout(right_panel, 2)
        self.setLayout(main_layout)

        # Inicializar cámara con método optimizado
        self.camera = open_fastest_webcam(0)
        if self.camera is None:
            QMessageBox.critical(self, "Error", "No se pudo inicializar la cámara")
            
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_preview)
        self.timer.start(1000 // TARGET_FPS)  # Ajustar para obtener el FPS deseado
        
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
            
        # Actualizar programas según la sede
        self.programa_input.clear()
        if sede_actual in EXTENSIONES_CARRERAS:
            self.programa_input.addItems(EXTENSIONES_CARRERAS[sede_actual])
    
    def crear_nuevo_programa(self):
        """Crear un nuevo programa académico."""
        programa, ok = QInputDialog.getText(
            self, 'Nuevo Programa', 
            'Ingrese el nombre del nuevo programa:'
        )
        if ok and programa:
            self.programa_input.addItem(programa)
            self.programa_input.setCurrentText(programa)
            
            # Añadir a la lista global de programas para esta sede
            sede_actual = self.sede_input.currentText()
            if sede_actual in EXTENSIONES_CARRERAS:
                if programa not in EXTENSIONES_CARRERAS[sede_actual]:
                    EXTENSIONES_CARRERAS[sede_actual].append(programa)
    
    def cargar_facultades(self):
        """Cargar facultades existentes."""
        self.facultad_input.clear()
        if os.path.exists(BASE_PATH):
            facultades = [d for d in os.listdir(BASE_PATH) 
                       if os.path.isdir(os.path.join(BASE_PATH, d))]
            if facultades:
                self.facultad_input.addItems(facultades)
            else:
                self.facultad_input.addItems([
                    "Ciencias Administrativas", "Ingeniería", 
                    "Ciencias Agropecuarias", "Ciencias del Deporte", 
                    "Educación", "Ciencias Sociales", "Ciencias de la Salud"
                ])

    def crear_nueva_facultad(self):
        """Crear una nueva facultad."""
        facultad, ok = QInputDialog.getText(
            self, 'Nueva Facultad', 
            'Ingrese el nombre de la nueva facultad:'
        )
        if ok and facultad:
            facultad_path = os.path.join(BASE_PATH, facultad)
            os.makedirs(facultad_path, exist_ok=True)
            self.facultad_input.addItem(facultad)
            self.facultad_input.setCurrentText(facultad)

    def update_preview(self):
        """Actualizar la vista previa de la cámara."""
        if not hasattr(self, 'camera') or self.camera is None:
            return
            
        ret, frame = self.camera.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = frame.shape
            bytes_per_line = ch * w
            qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qt_image).scaled(
                self.preview_label.size(), 
                Qt.AspectRatioMode.KeepAspectRatio
            )
            self.preview_label.setPixmap(pixmap)

    def capturar_foto(self):
        """Capturar una foto desde la cámara."""
        if not hasattr(self, 'camera') or self.camera is None:
            QMessageBox.warning(self, "Error", "Cámara no disponible")
            return
            
        ret, frame = self.camera.read()
        if ret:
            try:
                # Detectar rostro
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                faces = self.parent().mtcnn(rgb_frame)
                
                if faces is not None:
                    # Procesar el tensor de rostros
                    if isinstance(faces, list) and faces:
                        face_tensor = faces[0]
                    else:
                        face_tensor = faces
                        
                    if face_tensor is not None:
                        if face_tensor.ndim == 5:
                            face_tensor = face_tensor.squeeze(0)
                        if face_tensor.ndim == 4:
                            face_tensor = face_tensor.squeeze(0)
                        if face_tensor.ndim == 3:
                            face_tensor = face_tensor.unsqueeze(0)
                    
                    # Si se detectó un rostro correctamente, guardar la imagen
                    self.captured_images.append(frame.copy())  # Usar .copy() para evitar problemas de referencia
                    self.counter_label.setText(f"Fotos capturadas: {len(self.captured_images)}/5")
                    
                    # Crear y mostrar miniatura
                    h, w, ch = frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888)
                    pixmap = QPixmap.fromImage(qt_image).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                    
                    thumb_label = QLabel()
                    thumb_label.setPixmap(pixmap)
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
                            100, 100, Qt.AspectRatioMode.KeepAspectRatio)
                        
                        thumb_label = QLabel()
                        thumb_label.setPixmap(pixmap)
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
                    # Convertir a RGB
                    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                    
                    # Detectar y procesar rostro
                    faces = self.parent().mtcnn(rgb_image)
                    
                    if faces is not None:
                        # Procesar el tensor de rostros
                        if isinstance(faces, list) and faces:
                            face_tensor = faces[0]
                        else:
                            face_tensor = faces

                        if face_tensor is not None:
                            if face_tensor.ndim == 5:
                                face_tensor = face_tensor.squeeze(0)
                            if face_tensor.ndim == 4:
                                face_tensor = face_tensor.squeeze(0)
                            if face_tensor.ndim == 3:
                                face_tensor = face_tensor.unsqueeze(0)
                            
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
                QMessageBox.warning(self, "Error", "No se pudieron guardar rostros válidos")
                return

            # Obtener semestre si es estudiante
            semestre = ""
            if self.rol_input.currentText() == "Estudiante":
                semestre = self.semestre_input.currentText()

            # Guardar datos de la persona con los nuevos campos
            self.person_data = UniversityPersonData(
                nombre=self.nombre_input.text(),
                id=self.id_input.text(),
                facultad=self.facultad_input.currentText(),
                programa=self.programa_input.currentText(),
                rol=self.rol_input.currentText(),
                tipo=self.tipo_acceso.currentText(),
                sede=self.sede_input.currentText(),
                extension=self.extension_input.currentText(),
                semestre=semestre
            )

            # Guardar metadata
            metadata_path = os.path.join(person_path, "info.json")
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(self.person_data.to_dict(), f, indent=4, ensure_ascii=False)

            print("Metadata guardada exitosamente")

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
        
        super().closeEvent(event)