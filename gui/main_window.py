# -*- coding: utf-8 -*-
"""Módulo para la ventana principal de la aplicación."""

import os
import gc
import time
import shutil
import traceback
from datetime import datetime

import cv2
import torch
import numpy as np
import pandas as pd

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, 
    QMenuBar, QMenu, QLabel, QPushButton, QTextEdit, QStatusBar, QProgressDialog,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QTabWidget,
    QLineEdit, QFormLayout, QScrollArea, QDialog, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QPainter, QColor, QFont, QTextCharFormat, QTextCursor, QAction

from config.constants import BASE_PATH, VERSION, TARGET_FPS, SEDES
from data.database import PersonDatabase
from data.access_log import AccessLogManager
from utils.camera import open_fastest_webcam
from utils.frame_processor import FrameProcessor
from utils.theme import UCundinamarcaTheme
from gui.registration_dialog import RegistroPersonaDialog
from gui.search_dialog import SearchDialog
from gui.stats_dialog import StatisticsDialog
from gui.settings_dialog import SettingsDialog

class AccessControlSystem(QMainWindow):
    """Ventana principal del sistema de control de acceso."""
    
    def __init__(self, yolo, mtcnn, facenet, device, logger):
        """
        Inicializa la ventana principal.
        
        Args:
            yolo: Modelo YOLO para detección de personas
            mtcnn: Modelo MTCNN para detección de rostros
            facenet: Modelo FaceNet para reconocimiento facial
            device: Dispositivo de procesamiento (CPU/GPU)
            logger: Logger para registrar mensajes
        """
        # Añadir después de inicializar las variables de estado en __init__
       
        super().__init__()
        self.setWindowTitle("Sistema de Control de Acceso - Universidad de Cundinamarca con YoloGuard")
        self.setGeometry(100, 100, 1400, 900)
        
        # Inicializar variables de estado primero
        self.is_camera_running = False
        self.camera = None
        self.yolo = yolo
        self.mtcnn = mtcnn
        self.facenet = facenet
        self.device = device
        self.logger = logger
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.last_detection_time = 0
        self.detection_cooldown = 3.0  # Segundos entre detecciones para evitar duplicados
        self.process_every_n_frames = 2  # Procesar solo cada n frames para mejor rendimiento
        self.frame_count = 0

        self.camera_settings = {
        'camera_index': 0,
        'resolution': '1280x720',
        'process_every_n_frames': 2,
        'detection_cooldown': 3.0
    }

        # Inicializar componentes de datos
        self.database_manager = PersonDatabase(mtcnn, facenet)
        self.person_database = self.database_manager.load_database(self)
        self.access_log_manager = AccessLogManager()

        # Crear log_text antes de cualquier operación
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            padding: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
        """)
        
        # Asignar el widget al logger
        self.logger.set_log_widget(self.log_text)

        # Status bar con información adicional
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.status_label = QLabel(f"Sistema de Control de Acceso v{VERSION} | YoloGuard")
        self.statusBar.addPermanentWidget(self.status_label)
        
        # Configurar UI
        self.setup_ui()
        self.setStyleSheet(UCundinamarcaTheme.get_style())

        print("\nInicializando Sistema de Control de Acceso UDEC con YoloGuard...")
        
        # Inicializar el procesador de frames
        self.frame_processor = FrameProcessor(
            self.yolo, self.mtcnn, self.facenet, 
            self.device, self.person_database, self
        )
        self.frame_processor.frame_processed.connect(self.on_frame_processed)

        self.create_menubar()
        self.update_stats()
        print("Inicialización completa del sistema")

    def setup_ui(self):
        """Configura la interfaz de usuario."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Panel izquierdo (Video y Control)
        left_panel = QVBoxLayout()
        
        # Título y logo
        header_layout = QHBoxLayout()
        
        # Crear un logo placeholder
        logo_label = QLabel()
        logo_pixmap = QPixmap(150, 60)
        logo_pixmap.fill(QColor(0, 102, 51))  # Verde institucional
        painter = QPainter(logo_pixmap)
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        painter.drawText(logo_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "UDEC")
        painter.end()
        logo_label.setPixmap(logo_pixmap)
        
        # Título principal con YoloGuard
        title_label = QLabel("Sistema de Control de Acceso\nUniversidad de Cundinamarca")
        title_label.setStyleSheet("""
            font-size: 24px;
            color: #006633;
            font-weight: bold;
        """)
        
        # Logo YoloGuard
        yologuard_label = QLabel("YoloGuard")
        yologuard_label.setStyleSheet("""
            font-size: 18px;
            color: #006633;
            font-weight: bold;
            border: 2px solid #006633;
            border-radius: 8px;
            padding: 5px 10px;
        """)
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label, 1)
        header_layout.addWidget(yologuard_label)
        left_panel.addLayout(header_layout)
        
        # Monitor en tiempo real
        video_container = QGroupBox("Control de Acceso en Tiempo Real")
        video_layout = QVBoxLayout()
        
        self.video_label = QLabel()
        self.video_label.setMinimumSize(800, 600)
        self.video_label.setStyleSheet("""
            background-color: #1E1E1E;
            border-radius: 15px;
            padding: 10px;
            border: 3px solid #006633;
        """)
        video_layout.addWidget(self.video_label)
        
        # Información de detección
        self.detection_info = QLabel("Esperando detecciones...")
        self.detection_info.setStyleSheet("""
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            font-size: 16px;
        """)
        video_layout.addWidget(self.detection_info)
        
        video_container.setLayout(video_layout)
        left_panel.addWidget(video_container)

        # Panel de control
        control_container = QGroupBox("Panel de Control")
        control_layout = QVBoxLayout()
        
        # Primera fila de botones
        buttons_row1 = QHBoxLayout()
        
        self.start_button = QPushButton("🎥 Iniciar Monitoreo")
        self.start_button.setMinimumHeight(45)
        self.start_button.clicked.connect(self.toggle_camera)
        
        self.register_button = QPushButton("👤 Nuevo Registro")
        self.register_button.setMinimumHeight(45)
        self.register_button.clicked.connect(self.show_registro_persona)
        
        self.report_button = QPushButton("📊 Generar Informe")
        self.report_button.setMinimumHeight(45)
        self.report_button.clicked.connect(self.generate_report)
        
        buttons_row1.addWidget(self.start_button)
        buttons_row1.addWidget(self.register_button)
        buttons_row1.addWidget(self.report_button)
        
        # Segunda fila de botones
        buttons_row2 = QHBoxLayout()
        
        self.delete_button = QPushButton("🗑️ Eliminar Registro")
        self.delete_button.setMinimumHeight(45)
        self.delete_button.clicked.connect(self.show_delete_person_dialog)
        
        self.search_button = QPushButton("🔍 Buscar Persona")
        self.search_button.setMinimumHeight(45)
        self.search_button.clicked.connect(self.show_search_dialog)
        
        self.stats_button = QPushButton("📈 Estadísticas")
        self.stats_button.setMinimumHeight(45)
        self.stats_button.clicked.connect(self.show_statistics_dialog)
        
        buttons_row2.addWidget(self.delete_button)
        buttons_row2.addWidget(self.search_button)
        buttons_row2.addWidget(self.stats_button)
        
        control_layout.addLayout(buttons_row1)
        control_layout.addLayout(buttons_row2)
        
        # Agregar todos los botones con el mismo estilo
        control_container.setLayout(control_layout)
        left_panel.addWidget(control_container)

        # Panel derecho (Dashboard y Logs)
        right_panel = QVBoxLayout()
        
        # Dashboard
        stats_container = QTabWidget()
        
        # Tab de estadísticas generales
        stats_tab = QWidget()
        stats_layout = QVBoxLayout(stats_tab)
        
        self.stats_label = QLabel()
        self.stats_label.setStyleSheet("""
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
        """)
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)
        
        # Tab de distribucion por sedes
        sedes_tab = QWidget()
        sedes_layout = QVBoxLayout(sedes_tab)
        
        self.sedes_label = QLabel("Cargando estadísticas por sede...")
        self.sedes_label.setStyleSheet("""
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            font-size: 14px;
        """)
        sedes_layout.addWidget(self.sedes_label)
        
        stats_container.addTab(stats_tab, "Dashboard General")
        stats_container.addTab(sedes_tab, "Estadísticas por Sede")
        
        right_panel.addWidget(stats_container)

        # Log de actividad
        log_container = QGroupBox("Registro de Actividad")
        log_layout = QVBoxLayout()

        # Botones de control del log
        log_buttons_layout = QHBoxLayout()

        clear_log_btn = QPushButton("🗑️ Limpiar Log")
        clear_log_btn.setMinimumHeight(35)
        clear_log_btn.clicked.connect(self.clear_log)

        save_log_btn = QPushButton("💾 Guardar Log")
        save_log_btn.setMinimumHeight(35)
        save_log_btn.clicked.connect(self.save_log)

        # Buscar en el log
        search_log_layout = QHBoxLayout()
        self.search_log_input = QLineEdit()
        self.search_log_input.setPlaceholderText("Buscar en el log...")
        self.search_log_input.setMinimumHeight(35)
        search_log_btn = QPushButton("🔍")
        search_log_btn.clicked.connect(self.search_log)
        search_log_btn.setMinimumHeight(35)
        search_log_btn.setFixedWidth(40)
        search_log_layout.addWidget(self.search_log_input)
        search_log_layout.addWidget(search_log_btn)
        
        # Estilo específico para los botones del log
        for btn in [clear_log_btn, save_log_btn, search_log_btn]:
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #004d25;
                    color: #FFFFFF;
                    border: none;
                    padding: 8px;
                    border-radius: 4px;
                    font-size: 13px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #003519;
                    color: #FFFFFF;
                }
                QPushButton:pressed {
                    background-color: #002510;
                    color: #FFFFFF;
                }
            """)

        log_buttons_layout.addWidget(clear_log_btn)
        log_buttons_layout.addWidget(save_log_btn)

        # Estilo para el QTextEdit del log
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 14px;
                color: #212529;
                line-height: 1.5;
            }
        """)

        log_layout.addLayout(log_buttons_layout)
        log_layout.addLayout(search_log_layout)
        log_layout.addWidget(self.log_text)

        # Estilo para el contenedor del log
        log_container.setStyleSheet("""
            QGroupBox {
                border: 2px solid #006633;
                border-radius: 6px;
                margin-top: 1em;
                font-weight: bold;
                color: #006633;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                color: #006633;
            }
        """)

        log_container.setLayout(log_layout)
        right_panel.addWidget(log_container)

        # Agregar paneles al layout principal
        main_layout.addLayout(left_panel, 2)
        main_layout.addLayout(right_panel, 1)

    def create_menubar(self):
        """Crea la barra de menú de la aplicación."""
        menubar = self.menuBar()
        
        # Menú Sistema
        system_menu = menubar.addMenu("Sistema")
        
        refresh_action = QAction("🔄 Actualizar Base de Datos", self)
        refresh_action.setStatusTip("Recargar base de datos de personas")
        refresh_action.triggered.connect(self.reload_database)
        
        export_action = QAction("📊 Exportar Registros", self)
        export_action.setStatusTip("Exportar registros de acceso a Excel")
        export_action.triggered.connect(self.generate_report)
        
        backup_action = QAction("💾 Crear Respaldo", self)
        backup_action.setStatusTip("Crear un respaldo de la base de datos")
        backup_action.triggered.connect(self.create_backup)
        
        restore_action = QAction("📂 Restaurar Respaldo", self)
        restore_action.setStatusTip("Restaurar un respaldo previo")
        restore_action.triggered.connect(self.restore_backup)
        
        system_menu.addAction(refresh_action)
        system_menu.addAction(export_action)
        system_menu.addSeparator()
        system_menu.addAction(backup_action)
        system_menu.addAction(restore_action)
        
        # Menú Personas
        people_menu = menubar.addMenu("Registros")
        
        add_person = QAction("➕ Registrar Persona", self)
        add_person.setStatusTip("Registrar nueva persona")
        add_person.triggered.connect(self.show_registro_persona)
        
        delete_person = QAction("🗑️ Eliminar Persona", self)
        delete_person.setStatusTip("Eliminar persona existente")
        delete_person.triggered.connect(self.show_delete_person_dialog)
        
        search_person = QAction("🔍 Buscar Persona", self)
        search_person.setStatusTip("Buscar persona en la base de datos")
        search_person.triggered.connect(self.show_search_dialog)
        
        verify_db = QAction("🔍 Verificar Base de Datos", self)
        verify_db.setStatusTip("Verificar integridad de la base de datos")
        verify_db.triggered.connect(self.verify_database)
        
        people_menu.addAction(add_person)
        people_menu.addAction(delete_person)
        people_menu.addAction(search_person)
        people_menu.addSeparator()
        people_menu.addAction(verify_db)
        
        # Menú de Estadísticas
        stats_menu = menubar.addMenu("Estadísticas")
        
        general_stats = QAction("📊 Estadísticas Generales", self)
        general_stats.setStatusTip("Ver estadísticas generales del sistema")
        general_stats.triggered.connect(self.show_statistics_dialog)
        
        sede_stats = QAction("🏢 Estadísticas por Sede", self)
        sede_stats.setStatusTip("Ver estadísticas por sede")
        sede_stats.triggered.connect(self.show_sede_statistics)
        
        export_stats = QAction("📑 Exportar Estadísticas", self)
        export_stats.setStatusTip("Exportar estadísticas a Excel")
        export_stats.triggered.connect(self.export_statistics)
        
        stats_menu.addAction(general_stats)
        stats_menu.addAction(sede_stats)
        stats_menu.addAction(export_stats)
        
        # Menú de Configuración
        config_menu = menubar.addMenu("Configuración")
        
        cam_settings = QAction("📹 Configurar Cámara", self)
        cam_settings.setStatusTip("Configurar parámetros de la cámara")
        cam_settings.triggered.connect(self.show_camera_settings)
        
        advanced_settings = QAction("⚙️ Configuración Avanzada", self)
        advanced_settings.setStatusTip("Configuración avanzada del sistema")
        advanced_settings.triggered.connect(self.show_advanced_settings)
        
        config_menu.addAction(cam_settings)
        config_menu.addAction(advanced_settings)
        
        # Menú de Ayuda
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = QAction("ℹ️ Acerca de", self)
        about_action.triggered.connect(self.show_about)
        
        help_action = QAction("❓ Ayuda", self)
        help_action.triggered.connect(self.show_help)
        
        help_menu.addAction(help_action)
        help_menu.addAction(about_action)

    def reload_database(self):
        """Recarga la base de datos de personas."""
        try:
            self.logger.log_message("🔄 Recargando base de datos...")
            old_count = len(self.person_database)
        
            # Limpiar la base de datos actual
            self.person_database = {}
        
            # Recargar
            self.person_database = self.database_manager.load_database(self)
        
            # Actualizar la base de datos en el procesador de frames
            if hasattr(self, 'frame_processor'):
                self.frame_processor.person_database = self.person_database
            
            new_count = len(self.person_database)
            self.update_stats()
            self.logger.log_message(f"✅ Base de datos recargada: {new_count} personas ({new_count - old_count} nuevas)")
        
            return True
        except Exception as e:
            self.logger.log_message(f"❌ Error al recargar base de datos: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al recargar base de datos: {str(e)}")
            return False

    def verify_database(self):
        """Verifica la integridad de la base de datos."""
        try:
            total, valid, invalid = self.database_manager.verify_images(BASE_PATH, self, self.logger)
            
            summary = f"""
            📊 Resumen de verificación:
            • Total de imágenes: {total}
            • Imágenes válidas: {valid}
            • Imágenes inválidas: {invalid}
            """
            self.logger.log_message(summary)
            
            QMessageBox.information(self, "Verificación Completada", summary)
        except Exception as e:
            self.logger.log_message(f"❌ Error durante la verificación: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error durante la verificación: {str(e)}")

    def show_help(self):
        """Muestra el diálogo de ayuda."""
        help_text = """
        <div style='text-align: center;'>
            <h2 style='color: #006633;'>Ayuda del Sistema de Control de Acceso</h2>
            <p><b>Universidad de Cundinamarca con YoloGuard</b></p>
        </div>
        
        <h3>Funciones Principales:</h3>
        <ul>
            <li><b>Monitoreo en Tiempo Real:</b> Inicie/detenga la cámara con el botón "Iniciar Monitoreo".</li>
            <li><b>Registro de Personas:</b> Agregue nuevas personas con "Nuevo Registro".</li>
            <li><b>Generación de Informes:</b> Exporte datos de acceso con "Generar Informe".</li>
            <li><b>Búsqueda:</b> Busque personas registradas con "Buscar Persona".</li>
            <li><b>Estadísticas:</b> Visualice estadísticas de uso del sistema.</li>
        </ul>
        
        <h3>Consejos:</h3>
        <ul>
            <li>Capture al menos 5 fotos desde diferentes ángulos para un mejor reconocimiento.</li>
            <li>Mantenga una buena iluminación para mejorar la precisión.</li>
            <li>Realice respaldos periódicos de la base de datos.</li>
        </ul>
        
        <p>Para más información, contacte al administrador del sistema.</p>
        """
        
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Ayuda del Sistema")
        help_dialog.setMinimumSize(600, 450)
        
        layout = QVBoxLayout()
        help_label = QLabel(help_text)
        help_label.setWordWrap(True)
        help_label.setTextFormat(Qt.TextFormat.RichText)
        help_label.setStyleSheet("font-size: 14px; line-height: 1.5;")
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(help_label)
        
        close_btn = QPushButton("Cerrar")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(help_dialog.accept)
        
        layout.addWidget(scroll_area)
        layout.addWidget(close_btn)
        help_dialog.setLayout(layout)
        help_dialog.exec()

    def show_about(self):
        """Muestra el diálogo 'Acerca de'."""
        about_text = """
        <div style='text-align: center;'>
            <h2 style='color: #006633;'>Sistema de Control de Acceso</h2>
            <h3>Universidad de Cundinamarca con YoloGuard</h3>
            <p>Versión 2.0</p>
            <p>Desarrollado por el grupo de Seguridad Informática</p>
            <p>Facultad de Ingeniería</p>
            <p>&copy; 2025 Universidad de Cundinamarca</p>
            <p>Tecnología de reconocimiento por YoloGuard</p>
        </div>
        """
        
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("Acerca del Sistema")
        about_dialog.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        about_label = QLabel(about_text)
        about_label.setStyleSheet("font-size: 14px; line-height: 1.5;")
        about_label.setTextFormat(Qt.TextFormat.RichText)
        about_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        close_btn = QPushButton("Cerrar")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(about_dialog.accept)
        
        layout.addWidget(about_label)
        layout.addWidget(close_btn)
        
        about_dialog.setLayout(layout)
        about_dialog.exec()

    def show_statistics_dialog(self):
        """Muestra un diálogo con estadísticas detalladas."""
        try:
            dialog = StatisticsDialog(self.person_database, self.access_log_manager.access_logs, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al mostrar estadísticas: {str(e)}")

    def show_sede_statistics(self):
        """Muestra estadísticas específicas por sede."""
        try:
            stats_dialog = QDialog(self)
            stats_dialog.setWindowTitle("Estadísticas por Sede")
            stats_dialog.setMinimumSize(700, 500)
            
            layout = QVBoxLayout()
            
            # Selector de sede
            sede_selector_layout = QHBoxLayout()
            sede_selector_label = QLabel("Seleccionar Sede:")
            sede_selector_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            self.sede_selector = QComboBox()
            self.sede_selector.setMinimumHeight(35)
            self.sede_selector.addItems(["Todas"] + SEDES)
            self.sede_selector.currentIndexChanged.connect(self.update_sede_stats_view)
            
            sede_selector_layout.addWidget(sede_selector_label)
            sede_selector_layout.addWidget(self.sede_selector)
            
            # Área para mostrar estadísticas
            self.sede_stats_view = QTextEdit()
            self.sede_stats_view.setReadOnly(True)
            self.sede_stats_view.setStyleSheet("""
                font-size: 14px;
                line-height: 1.5;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 10px;
            """)
            
            # Inicializar con todas las sedes
            self.update_sede_stats_view(0)
            
            # Agregar todo al layout
            layout.addLayout(sede_selector_layout)
            layout.addWidget(self.sede_stats_view)
            
            close_btn = QPushButton("Cerrar")
            close_btn.setMinimumHeight(40)
            close_btn.clicked.connect(stats_dialog.accept)
            layout.addWidget(close_btn)
            
            stats_dialog.setLayout(layout)
            stats_dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al mostrar estadísticas por sede: {str(e)}")
            traceback.print_exc()

    def update_sede_stats_view(self, index):
        """
        Actualiza la vista de estadísticas por sede según la selección.
        
        Args:
            index (int): Índice de la sede seleccionada en el combo box
        """
        try:
            selected_sede = self.sede_selector.currentText()
            
            if selected_sede == "Todas":
                # Mostrar estadísticas para todas las sedes
                self.sede_stats_view.setHtml(self.generate_sede_stats_html())
            else:
                # Filtrar por sede específica
                # Contar personas de esta sede
                sede_persons = 0
                for person_data in self.person_database.values():
                    if person_data['data'].sede == selected_sede:
                        sede_persons += 1
                
                # Filtrar accesos de esta sede
                access_logs = self.access_log_manager.access_logs
                if not access_logs.empty:
                    sede_logs = access_logs[access_logs['Sede'] == selected_sede]
                    sede_accesos = len(sede_logs)
                    
                    # Calcular estadísticas específicas
                    if not sede_logs.empty:
                        avg_confidence = sede_logs['Confianza'].mean()
                        roles_distribution = sede_logs.groupby('Rol').size().to_dict()
                        extension_distribution = sede_logs.groupby('Extension').size().to_dict()
                    else:
                        avg_confidence = 0
                        roles_distribution = {}
                        extension_distribution = {}
                else:
                    sede_accesos = 0
                    avg_confidence = 0
                    roles_distribution = {}
                    extension_distribution = {}
                
                # Generar HTML
                html = f"""
                    <h2 style='color: #006633; text-align: center;'>Estadísticas: Sede {selected_sede}</h2>
                    
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>📊 Resumen General</h3>
                        <p>• Personas Registradas: <b>{sede_persons}</b></p>
                        <p>• Accesos Registrados: <b>{sede_accesos}</b></p>
                        <p>• Confianza Promedio: <b>{avg_confidence:.2f}%</b></p>
                    </div>
                """
                
                if roles_distribution:
                    html += """
                        <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                            <h3>👥 Distribución por Rol</h3>
                            <ul>
                    """
                    
                    for rol, count in sorted(roles_distribution.items(), key=lambda x: x[1], reverse=True):
                        html += f"<li><b>{rol}:</b> {count} accesos</li>"
                        
                    html += """
                            </ul>
                        </div>
                    """
                
                if extension_distribution:
                    html += """
                        <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                            <h3>🏢 Distribución por Extensión</h3>
                            <ul>
                    """
                    
                    for ext, count in sorted(extension_distribution.items(), key=lambda x: x[1], reverse=True):
                        if ext:  # Asegurarse de que no sea nulo
                            html += f"<li><b>{ext}:</b> {count} accesos</li>"
                        else:
                            html += f"<li><b>No especificada:</b> {count} accesos</li>"
                        
                    html += """
                            </ul>
                        </div>
                    """
                
                self.sede_stats_view.setHtml(html)
        except Exception as e:
            self.sede_stats_view.setHtml(f"<h3>Error al actualizar estadísticas: {str(e)}</h3>")
            traceback.print_exc()

    def generate_sede_stats_html(self):
        """
        Genera el HTML para las estadísticas por sede.
        
        Returns:
            str: HTML con las estadísticas por sede
        """
        try:
            # Contar personas por sede
            sede_counts = {}
            for person_data in self.person_database.values():
                sede = person_data['data'].sede if person_data['data'].sede else "No especificada"
                sede_counts[sede] = sede_counts.get(sede, 0) + 1
            
            # Calcular accesos por sede
            sede_accesos = {}
            access_logs = self.access_log_manager.access_logs
            if not access_logs.empty:
                # Manejar valores nulos en Sede
                access_logs['Sede'].fillna("No especificada", inplace=True)
                sede_accesos = access_logs.groupby('Sede').size().to_dict()
            
            # HTML para mostrar estadísticas
            sede_html = "<h2 style='color: #006633; text-align: center;'>Estadísticas por Sede</h2>"
            
            if sede_counts:
                sede_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>🏢 Distribución de Personas por Sede</h3>
                        <ul>
                """
                
                for sede, count in sorted(sede_counts.items(), key=lambda x: x[1], reverse=True):
                    sede_html += f"<li><b>{sede}:</b> {count} personas</li>"
                    
                sede_html += """
                        </ul>
                    </div>
                """
            
            if sede_accesos:
                sede_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>🚪 Distribución de Accesos por Sede</h3>
                        <ul>
                """
                
                for sede, count in sorted(sede_accesos.items(), key=lambda x: x[1], reverse=True):
                    sede_html += f"<li><b>{sede}:</b> {count} accesos</li>"
                    
                sede_html += """
                        </ul>
                    </div>
                """
                
            return sede_html
        except Exception as e:
            print(f"Error al generar estadísticas de sede: {str(e)}")
            traceback.print_exc()
            return "<h3>Error al generar estadísticas</h3>"

    def export_statistics(self):
        """Exporta estadísticas a Excel."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Estadísticas", "", 
                "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if filename:
                success = self.access_log_manager.export_statistics(filename, self.logger)
                if success:
                    QMessageBox.information(self, "Éxito", "Estadísticas exportadas correctamente")
                
        except Exception as e:
            error_msg = f"Error al exportar estadísticas: {str(e)}"
            self.logger.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)

    def show_camera_settings(self):
        """Muestra diálogo para configurar los parámetros de la cámara."""
        try:
            settings_dialog = SettingsDialog(self, camera_settings=self.camera_settings)
        
            if settings_dialog.exec() == QDialog.DialogCode.Accepted:
                # Aplicar configuraciones
                new_settings = settings_dialog.get_settings()
            
                # Actualizar configuraciones de cámara
                self.camera_settings = {
                    'camera_index': new_settings.get('camera_index', 0),
                    'resolution': new_settings.get('resolution', '1280x720'),
                    'process_every_n_frames': new_settings.get('process_every_n_frames', 2),
                    'detection_cooldown': new_settings.get('detection_cooldown', 3.0)
                }
            
                # Actualizar variables de la clase
                self.process_every_n_frames = new_settings.get('process_every_n_frames', 2)
                self.detection_cooldown = new_settings.get('detection_cooldown', 3.0)
            
                # Actualizar configuración en el procesador de frames
                if hasattr(self, 'frame_processor'):
                    self.frame_processor.process_every_n_frames = self.process_every_n_frames
            
                self.logger.log_message("✅ Configuración de cámara actualizada")
            
                # Reiniciar la cámara si está activa
                if self.is_camera_running:
                    self.toggle_camera()  # Detener
                    self.toggle_camera()  # Iniciar con nueva configuración
                
        except Exception as e:
            self.logger.log_message(f"❌ Error en configuración de cámara: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en configuración de cámara: {str(e)}")

    def show_advanced_settings(self):
        """Muestra configuración avanzada del sistema."""
        try:
            # Implementación pendiente - se delegará a la clase SettingsDialog
            QMessageBox.information(
                self, "Información",
                "La configuración avanzada será implementada en una próxima actualización"
            )
        except Exception as e:
            self.logger.log_message(f"❌ Error en configuración avanzada: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error en configuración avanzada: {str(e)}")

    def create_backup(self):
        """Crea un respaldo de la base de datos."""
        try:
            # Solicitar directorio de respaldo
            backup_dir = QFileDialog.getExistingDirectory(
                self, "Seleccionar Directorio para Respaldo"
            )
            
            if not backup_dir:
                return
                
            # Crear nombre para el respaldo con la fecha actual
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"backup_ucundinamarca_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # Crear directorio de respaldo
            os.makedirs(backup_path, exist_ok=True)
            
            # Mostrar diálogo de progreso
            progress = QProgressDialog("Creando respaldo...", "Cancelar", 0, 2, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
            
            # Copiar archivos
            shutil.copytree(BASE_PATH, os.path.join(backup_path, "dataset"), dirs_exist_ok=True)
            progress.setValue(1)
            
            if progress.wasCanceled():
                return
            
            # Guardar logs de acceso
            access_logs = self.access_log_manager.access_logs
            if not access_logs.empty:
                log_file = os.path.join(backup_path, "access_logs.csv")
                access_logs.to_csv(log_file, index=False)
            
            progress.setValue(2)
            
            self.logger.log_message(f"✅ Respaldo creado en: {backup_path}")
            QMessageBox.information(self, "Éxito", f"Respaldo creado correctamente en:\n{backup_path}")
            
        except Exception as e:
            error_msg = f"Error al crear respaldo: {str(e)}"
            self.logger.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)
    
    def restore_backup(self):
        """Restaura un respaldo de la base de datos."""
        try:
            # Solicitar directorio del respaldo
            backup_dir = QFileDialog.getExistingDirectory(
                self, "Seleccionar Directorio de Respaldo"
            )
            
            if not backup_dir:
                return
                
            # Verificar si es un respaldo válido
            dataset_path = os.path.join(backup_dir, "dataset")
            if not os.path.exists(dataset_path):
                QMessageBox.warning(
                    self, "Respaldo Inválido",
                    "El directorio seleccionado no parece contener un respaldo válido."
                )
                return
                
            # Confirmar restauración
            confirm = QMessageBox.question(
                self, "Confirmar Restauración",
                "¿Está seguro de restaurar este respaldo? Los datos actuales serán reemplazados.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm != QMessageBox.StandardButton.Yes:
                return
                
            # Detener la cámara si está activa
            if self.is_camera_running:
                self.toggle_camera()
                
            # Mostrar diálogo de progreso
            progress = QProgressDialog("Restaurando respaldo...", "Cancelar", 0, 3, self)
            progress.setWindowModality(Qt.WindowModality.WindowModal)
            progress.setMinimumDuration(0)
            progress.setValue(0)
                
            # Reemplazar directorio actual
            if os.path.exists(BASE_PATH):
                shutil.rmtree(BASE_PATH)
            
            # Copiar respaldo
            shutil.copytree(dataset_path, BASE_PATH)
            progress.setValue(1)
            
            if progress.wasCanceled():
                return
            
            # Cargar logs si existen
            log_file = os.path.join(backup_dir, "access_logs.csv")
            if os.path.exists(log_file):
                self.access_log_manager.access_logs = pd.read_csv(log_file)
            progress.setValue(2)
            
            if progress.wasCanceled():
                return
            
            # Recargar base de datos
            self.reload_database()
            progress.setValue(3)
            
            self.logger.log_message("✅ Respaldo restaurado correctamente")
            QMessageBox.information(self, "Éxito", "Respaldo restaurado correctamente")
            
        except Exception as e:
            error_msg = f"Error al restaurar respaldo: {str(e)}"
            self.logger.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)

    def show_search_dialog(self):
        """Muestra un diálogo para buscar personas en la base de datos."""
        try:
            search_dialog = SearchDialog(self.person_database, self)
            search_dialog.exec()
        except Exception as e:
            self.logger.log_message(f"❌ Error al abrir búsqueda: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al abrir búsqueda: {str(e)}")

    def show_delete_person_dialog(self):
        """Muestra un diálogo para eliminar una persona."""
        try:
            people = list(self.person_database.keys())
            if not people:
                QMessageBox.warning(self, "Aviso", 
                    "No hay personas registradas en la base de datos")
                return
                
            # Diálogo más avanzado con búsqueda
            delete_dialog = QDialog(self)
            delete_dialog.setWindowTitle("Eliminar Registro")
            delete_dialog.setMinimumSize(500, 400)
            
            layout = QVBoxLayout()
            
            # Campo de búsqueda
            search_layout = QHBoxLayout()
            search_label = QLabel("Buscar:")
            search_label.setStyleSheet("font-size: 14px; font-weight: bold;")
            search_input = QLineEdit()
            search_input.setMinimumHeight(35)
            
            search_layout.addWidget(search_label)
            search_layout.addWidget(search_input)
            
            # Lista de personas
            people_list = QTableWidget()
            people_list.setColumnCount(2)
            people_list.setHorizontalHeaderLabels(["Nombre", "Facultad"])
            people_list.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            people_list.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            people_list.setStyleSheet("""
                QTableWidget {
                    font-size: 14px;
                }
                QHeaderView::section {
                    background-color: #E0E0E0;
                    padding: 5px;
                    font-size: 14px;
                    font-weight: bold;
                    border: 1px solid #D3D3D3;
                }
            """)
            
            # Llenar la tabla
            people_list.setRowCount(len(people))
            for i, person_name in enumerate(sorted(people)):
                person_data = self.person_database[person_name]['data']
                people_list.setItem(i, 0, QTableWidgetItem(person_name))
                people_list.setItem(i, 1, QTableWidgetItem(person_data.facultad))
            
            # Ajustar columnas
            header = people_list.horizontalHeader()
            header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
            header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
            
            # Filtrar la lista al escribir
            def filter_people_list():
                text = search_input.text().lower()
                for row in range(people_list.rowCount()):
                    name_item = people_list.item(row, 0)
                    faculty_item = people_list.item(row, 1)
                    show = (text in name_item.text().lower() or 
                            text in faculty_item.text().lower())
                    people_list.setRowHidden(row, not show)
            
            search_input.textChanged.connect(filter_people_list)
            
            # Botones
            buttons_layout = QHBoxLayout()
            
            delete_btn = QPushButton("Eliminar")
            delete_btn.setMinimumHeight(40)
            delete_btn.clicked.connect(lambda: self.delete_selected_person(people_list, delete_dialog))
            
            cancel_btn = QPushButton("Cancelar")
            cancel_btn.setMinimumHeight(40)
            cancel_btn.clicked.connect(delete_dialog.reject)
            
            buttons_layout.addWidget(delete_btn)
            buttons_layout.addWidget(cancel_btn)
            
            # Armado del layout
            layout.addLayout(search_layout)
            layout.addWidget(people_list)
            layout.addLayout(buttons_layout)
            
            delete_dialog.setLayout(layout)
            delete_dialog.exec()
                    
        except Exception as e:
            self.logger.log_message(f"❌ Error al mostrar diálogo de eliminación: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error: {str(e)}")

    def delete_selected_person(self, people_list, dialog):
        """
        Elimina la persona seleccionada de la lista.
        
        Args:
            people_list (QTableWidget): Lista de personas
            dialog (QDialog): Diálogo padre
        """
        try:
            selected_items = people_list.selectedItems()
            if not selected_items:
                QMessageBox.warning(dialog, "Advertencia", "Por favor seleccione una persona para eliminar")
                return
                
            # Obtener el nombre de la primera columna
            selected_row = selected_items[0].row()
            person_name = people_list.item(selected_row, 0).text()
            
            # Confirmar eliminación
            confirm = QMessageBox.question(
                dialog, "Confirmar Eliminación",
                f"¿Está seguro de eliminar a {person_name}? Esta acción no se puede deshacer.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm != QMessageBox.StandardButton.Yes:
                return
            
            # Obtener datos de la persona
            person_data = self.person_database[person_name]['data']
            facultad_path = os.path.join(BASE_PATH, person_data.facultad)
            person_path = os.path.join(facultad_path, person_data.nombre)
            
            # Eliminar directorio
            if os.path.exists(person_path):
                shutil.rmtree(person_path)
            
            # Eliminar de la base de datos
            del self.person_database[person_name]
            
            # Actualizar la base de datos en el procesador de frames
            if hasattr(self, 'frame_processor'):
                self.frame_processor.person_database = self.person_database
            
            self.logger.log_message(f"🗑️ Persona eliminada: {person_name}")
            self.update_stats()
            
            dialog.accept()
            QMessageBox.information(dialog, "Éxito", "Registro eliminado correctamente")
            
        except Exception as e:
            self.logger.log_message(f"❌ Error al eliminar persona: {str(e)}")
            QMessageBox.critical(dialog, "Error", f"Error al eliminar: {str(e)}")

    def update_frame(self):
        """Captura un frame y lo envía al procesador en segundo plano."""
        if not self.is_camera_running:
            return
            
        # Omitir algunos frames para mejor rendimiento
        self.frame_count += 1
        if self.frame_count % self.process_every_n_frames != 0:
            return
            
        ret, frame = self.camera.read()
        if ret:
            # Enviar el frame al procesador en segundo plano
            self.frame_processor.add_frame(frame)
    
    def on_frame_processed(self, display_frame, identity, confidence):
        """
        Callback cuando el procesador ha terminado con un frame.
        
        Args:
            display_frame: Frame procesado con anotaciones
            identity: Identidad reconocida (o None)
            confidence: Nivel de confianza del reconocimiento
        """
        # Actualizar la interfaz de usuario con el frame procesado
        rgb_frame = cv2.cvtColor(display_frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(qt_image).scaled(
            self.video_label.size(), Qt.AspectRatioMode.KeepAspectRatio))
            
        # Actualizar información de detección en la UI
        if identity:
            self.update_detection_info(identity, confidence)
            
            # Registrar acceso pero con cooldown para evitar registros duplicados
            current_time = time.time()
            if current_time - self.last_detection_time > self.detection_cooldown:
                self.access_log_manager.log_access(identity, confidence, self.logger)
                self.last_detection_time = current_time
                self.update_stats()
        else:
            # Solo actualizar la UI sin cambiar el cooldown
            self.update_detection_info(None, 0)

    def update_detection_info(self, identity, confidence):
        """
        Actualiza la información de detección en la interfaz.
        
        Args:
            identity: Identidad reconocida (o None)
            confidence: Nivel de confianza del reconocimiento
        """
        if identity:
            # Determinar el color basado en el nivel de confianza
            if confidence > 60:
                confidence_color = "#006633"  # Verde institucional
                confidence_bg = "#E8F5E9"
                confidence_text = "Alta"
            elif confidence > 40:
                confidence_color = "#00802b"  # Verde más claro
                confidence_bg = "#F1F8E9"
                confidence_text = "Media"
            else:
                confidence_color = "#004d25"  # Verde más oscuro
                confidence_bg = "#E8F5E9"
                confidence_text = "Baja"

            info = f"""
                <h3 style='color: {confidence_color}; font-size: 18px;'>👤 Persona Detectada</h3>
                <div style='background-color: {confidence_bg}; padding: 10px; border-radius: 5px; font-size: 16px;'>
                    <p><b>Nombre:</b> {identity.nombre}</p>
                    <p><b>ID/Código:</b> {identity.id}</p>
                    <p><b>Facultad:</b> {identity.facultad}</p>
                    <p><b>Programa:</b> {identity.programa}</p>
                    <p><b>Rol:</b> {identity.rol}</p>
                    <p><b>Sede:</b> {identity.sede or "No especificada"}</p>
                    <p><b>Tipo de Acceso:</b> {identity.tipo}</p>
                    <p><b>Confianza:</b> {confidence:.1f}% ({confidence_text})</p>
                </div>
            """
        else:
            info = """
                <h3 style='color: #CC0000; font-size: 18px;'>⚠️ Persona No Identificada</h3>
                <div style='background-color: #FFEBEE; padding: 10px; border-radius: 5px; font-size: 16px;'>
                    <p>No se encontró coincidencia en la base de datos</p>
                    <p>Se recomienda registrar a esta persona en el sistema</p>
                </div>
            """
        self.detection_info.setText(info)

    def update_stats(self):
        """Actualiza las estadísticas mostradas en la interfaz."""
        try:
            if not hasattr(self, 'person_database') or not hasattr(self, 'access_log_manager'):
                return
                
            # Contar personas por facultad
            facultad_counts = {}
            rol_counts = {}
            sede_counts = {}
            for person_data in self.person_database.values():
                facultad = person_data['data'].facultad
                rol = person_data['data'].rol
                sede = person_data['data'].sede if person_data['data'].sede else "No especificada"
                
                facultad_counts[facultad] = facultad_counts.get(facultad, 0) + 1
                rol_counts[rol] = rol_counts.get(rol, 0) + 1
                sede_counts[sede] = sede_counts.get(sede, 0) + 1

            # Calcular accesos de hoy
            access_logs = self.access_log_manager.access_logs
            today = datetime.now().date()
            today_logs = access_logs[access_logs['Fecha'] == today] if not access_logs.empty else pd.DataFrame()
            accesos_hoy = len(today_logs)
            
            # Calcular estadísticas de reconocimiento
            if not today_logs.empty:
                avg_confidence = today_logs['Confianza'].mean()
                max_confidence = today_logs['Confianza'].max()
            else:
                avg_confidence = 0
                max_confidence = 0
                
            # Calcular FPS si está disponible
            fps_info = ""
            if hasattr(self, 'frame_processor') and self.frame_processor.fps_deque:
                avg_fps = sum(self.frame_processor.fps_deque) / len(self.frame_processor.fps_deque)
                fps_info = f"<p>• FPS Actuales: <b>{avg_fps:.1f}</b></p>"

            # Preparar HTML para el dashboard general
            stats_html = f"""
                <h3 style='color: #006633; font-size: 18px;'>📊 Dashboard del Sistema</h3>
                
                <div style='background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <h4 style='font-size: 16px;'>👥 Información General</h4>
                    <p>• Personas Registradas: <b>{len(self.person_database)}</b></p>
                    <p>• Facultades Activas: <b>{len(facultad_counts)}</b></p>
                    <p>• Sedes Activas: <b>{len(sede_counts)}</b></p>
                    <p>• Accesos Hoy: <b>{accesos_hoy}</b></p>
                    <p>• Estado del Sistema: <b>{'🟢 Activo' if self.is_camera_running else '🔴 Inactivo'}</b></p>
                    <p>• Modo de Procesamiento: <b>{self.device.upper()}</b></p>
                    {fps_info}
                </div>

                <div style='background-color: #E8F5E9; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <h4 style='font-size: 16px;'>📈 Estadísticas del Día</h4>
                    <p>• Confianza Promedio: <b>{avg_confidence:.1f}%</b></p>
                    <p>• Confianza Máxima: <b>{max_confidence:.1f}%</b></p>
                </div>

                <div style='background-color: #F1F8E9; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <h4 style='font-size: 16px;'>👥 Distribución por Facultad</h4>
                    {''.join(f"<p>• {facultad}: <b>{count}</b> personas</p>" for facultad, count in sorted(facultad_counts.items())[:5])}
                    {f"<p>• <i>Y {len(facultad_counts) - 5} más...</i></p>" if len(facultad_counts) > 5 else ""}
                </div>
                
                <div style='background-color: #F1F8E9; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <h4 style='font-size: 16px;'>👥 Distribución por Rol</h4>
                    {''.join(f"<p>• {rol}: <b>{count}</b></p>" for rol, count in sorted(rol_counts.items(), key=lambda x: x[1], reverse=True))}
                </div>
                
                <div style='background-color: #F1F8E9; padding: 10px; border-radius: 5px; margin: 5px 0;'>
                    <h4 style='font-size: 16px;'>⚙️ Información del Sistema</h4>
                    <p>• Versión: <b>{VERSION}</b></p>
                    <p>• Última Actualización: <b>{datetime.now().strftime('%H:%M:%S')}</b></p>
                </div>
            """
            
            self.stats_label.setText(stats_html)
            
            # Actualizar estadísticas por sede
            self.sedes_label.setText(self.generate_sede_stats_html())
            
            # Actualizar status bar con info resumida
            self.status_label.setText(
                f"Sistema v{VERSION} | YoloGuard | "
                f"Personas: {len(self.person_database)} | "
                f"Accesos Hoy: {accesos_hoy} | "
                f"Estado: {'🟢 Activo' if self.is_camera_running else '🔴 Inactivo'}"
            )
            
        except Exception as e:
            print(f"Error al actualizar estadísticas: {str(e)}")
            traceback.print_exc()

    def show_registro_persona(self):
        """Muestra el diálogo de registro de persona."""
        dialog = RegistroPersonaDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Reintentar recargar la base de datos hasta tres veces
            for _ in range(3):
                try:
                    self.reload_database()
                    # Verificar que la persona fue cargada
                    nueva_persona = dialog.person_data.nombre if dialog.person_data else None
                    if nueva_persona and nueva_persona in self.person_database:
                        self.logger.log_message(f"✅ Persona registrada y cargada correctamente: {nueva_persona}")
                        break
                    else:
                        self.logger.log_message("⚠️ La persona registrada no se encontró en la base de datos, reintentando...")
                except Exception as e:
                    self.logger.log_message(f"❌ Error al recargar base de datos: {str(e)}")
            # Actualizar estadísticas
            self.update_stats()

    def generate_report(self):
        """Genera un informe de accesos."""
        try:
            filename, _ = QFileDialog.getSaveFileName(
                self, "Guardar Reporte", "", 
                "Excel Files (*.xlsx);;CSV Files (*.csv)"
            )
            
            if filename:
                success = self.access_log_manager.generate_report(filename, self.logger)
                if success:
                    QMessageBox.information(self, "Éxito", "Reporte generado correctamente")
        except Exception as e:
            error_msg = f"Error al generar reporte: {str(e)}"
            self.logger.log_message(f"❌ {error_msg}")
            QMessageBox.critical(self, "Error", error_msg)

    def search_log(self):
        """Busca texto en el log."""
        search_text = self.search_log_input.text()
        found = self.logger.search_log(search_text)
        
        if not found:
            QMessageBox.information(self, "Búsqueda", f"No se encontró '{search_text}' en el log")

    def clear_log(self):
        """Limpia el log."""
        self.logger.clear_log()

    def save_log(self):
        """Guarda el log en un archivo."""
        self.logger.save_log(self)

    # Busca la función toggle_camera en gui/main_window.py y reemplázala con esta versión:

    def toggle_camera(self):
        """Activa o desactiva la cámara."""
        if not self.is_camera_running:
            try:
                # Obtener el índice de cámara de la configuración
                camera_index = self.camera_settings.get('camera_index', 0)
            
                # Obtener la resolución de la configuración
                resolution_str = self.camera_settings.get('resolution', '1280x720')
                try:
                    width, height = map(int, resolution_str.split('x'))
                    resolution = (width, height)
                except Exception:
                    resolution = (1280, 720)  # Valor predeterminado
            
                # Usar el método optimizado para abrir la cámara
                self.camera = open_fastest_webcam(camera_index, resolution=resolution, target_fps=TARGET_FPS)
            
                if self.camera is not None and self.camera.isOpened():
                    # Iniciar el procesador de frames si no está activo
                    if not self.frame_processor.isRunning():
                        self.frame_processor.start()
                
                    self.timer.start(1000 // TARGET_FPS)  # Actualizar a la frecuencia objetivo
                    self.is_camera_running = True
                    self.start_button.setText("⏹ Detener Monitoreo")
                    self.logger.log_message(f"🎥 Monitoreo iniciado a {TARGET_FPS} FPS con Cámara {camera_index}")
                
                    # Actualizar status bar
                    self.update_stats()
                else:
                    self.logger.log_message(f"❌ Error: No se pudo acceder a la cámara {camera_index}")
                    QMessageBox.warning(self, "Error", f"No se pudo acceder a la cámara {camera_index}. Verifique la conexión o seleccione otra cámara en Configuración.")
            except Exception as e:
                self.logger.log_message(f"❌ Error al iniciar cámara: {str(e)}")
                QMessageBox.critical(self, "Error", f"Error al iniciar cámara: {str(e)}")
                traceback.print_exc()
        else:
            self.timer.stop()
            if self.camera is not None:
                self.camera.release()
                self.camera = None
        
            # No detener el procesador de frames, solo dejamos de enviarle frames
            self.is_camera_running = False
            self.start_button.setText("🎥 Iniciar Monitoreo")
            self.video_label.clear()
            self.detection_info.setText("Esperando detecciones...")
            self.logger.log_message("⏹ Monitoreo detenido")
        
            # Actualizar status bar
            self.update_stats()
        
            # Liberar memoria
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None

    def closeEvent(self, event):
        """Limpia los recursos antes de cerrar la aplicación."""
        try:
            # Detener todos los procesos en segundo plano
            if hasattr(self, 'frame_processor'):
                self.frame_processor.stop()
                
            if self.camera is not None:
                self.camera.release()
                self.camera = None
                
            # Liberar memoria
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            event.accept()
        except Exception as e:
            print(f"Error al cerrar aplicación: {str(e)}")
            traceback.print_exc()
            event.accept()