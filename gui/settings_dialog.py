# -*- coding: utf-8 -*-
"""Módulo para el diálogo de configuración."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QWidget, QFormLayout,
    QComboBox, QSpinBox, QDoubleSpinBox, QLineEdit,
    QFileDialog, QGroupBox
)
from PyQt6.QtCore import Qt

from config.constants import TARGET_FPS

class SettingsDialog(QDialog):
    """Diálogo para la configuración de la aplicación."""
    
    def __init__(self, parent=None, camera_settings=None):
        """
        Inicializa el diálogo de configuración.
        
        Args:
            parent: Widget padre
            camera_settings (dict, optional): Configuración de la cámara
        """
        super().__init__(parent)
        self.setWindowTitle("Configuración")
        self.setMinimumSize(500, 400)
        self.camera_settings = camera_settings or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout()
        
        tabs = QTabWidget()
        
        # Tab Cámara
        camera_tab = QWidget()
        camera_layout = QFormLayout(camera_tab)
        
        # Selector de cámara
        self.camera_selector = QComboBox()
        self.camera_selector.setMinimumHeight(35)
        self.camera_selector.addItems([f"Cámara {i}" for i in range(5)])
        
        # Selector de resolución
        self.resolution_selector = QComboBox()
        self.resolution_selector.setMinimumHeight(35)
        self.resolution_selector.addItems([
            "640x480", "800x600", "1280x720", "1920x1080"
        ])
        self.resolution_selector.setCurrentText("1280x720")  # Por defecto
        
        # Control de FPS
        self.fps_spinner = QSpinBox()
        self.fps_spinner.setRange(15, 60)
        self.fps_spinner.setValue(TARGET_FPS)
        self.fps_spinner.setSuffix(" FPS")
        self.fps_spinner.setMinimumHeight(35)
        
        # Nivel de confianza mínimo
        self.confidence_spinner = QSpinBox()
        self.confidence_spinner.setRange(10, 95)
        self.confidence_spinner.setValue(20)  # Valor predeterminado
        self.confidence_spinner.setSuffix("%")
        self.confidence_spinner.setMinimumHeight(35)
        
        # Optimización de rendimiento
        self.frame_skip_spinner = QSpinBox()
        self.frame_skip_spinner.setRange(1, 10)
        self.frame_skip_spinner.setValue(self.camera_settings.get('process_every_n_frames', 2))
        self.frame_skip_spinner.setToolTip("Procesar 1 de cada N frames. Mayor número = mejor rendimiento, menor precisión")
        self.frame_skip_spinner.setMinimumHeight(35)
        
        # Tiempo de cooldown
        self.cooldown_spinner = QDoubleSpinBox()
        self.cooldown_spinner.setRange(0.5, 10.0)
        self.cooldown_spinner.setValue(self.camera_settings.get('detection_cooldown', 3.0))
        self.cooldown_spinner.setSingleStep(0.5)
        self.cooldown_spinner.setDecimals(1)
        self.cooldown_spinner.setSuffix(" segundos")
        self.cooldown_spinner.setMinimumHeight(35)
        
        # Etiquetas con estilo
        cam_label = QLabel("Seleccionar cámara:")
        cam_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        res_label = QLabel("Resolución:")
        res_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        fps_label = QLabel("FPS:")
        fps_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        conf_label = QLabel("Confianza mínima:")
        conf_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        skip_label = QLabel("Saltar frames:")
        skip_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        cooldown_label = QLabel("Tiempo entre detecciones:")
        cooldown_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        camera_layout.addRow(cam_label, self.camera_selector)
        camera_layout.addRow(res_label, self.resolution_selector)
        camera_layout.addRow(fps_label, self.fps_spinner)
        camera_layout.addRow(conf_label, self.confidence_spinner)
        camera_layout.addRow(skip_label, self.frame_skip_spinner)
        camera_layout.addRow(cooldown_label, self.cooldown_spinner)
        
        # Tab Sistema
        system_tab = QWidget()
        system_layout = QFormLayout(system_tab)
        
        # Directorio base
        self.base_dir_edit = QLineEdit()
        self.base_dir_edit.setMinimumHeight(35)
        self.base_dir_browse = QPushButton("Examinar...")
        self.base_dir_browse.setMinimumHeight(35)
        self.base_dir_browse.clicked.connect(self.browse_base_dir)
        
        base_dir_layout = QHBoxLayout()
        base_dir_layout.addWidget(self.base_dir_edit)
        base_dir_layout.addWidget(self.base_dir_browse)
        
        # Modo de procesamiento
        self.process_mode = QComboBox()
        self.process_mode.setMinimumHeight(35)
        self.process_mode.addItems(["Auto", "CPU", "CUDA (GPU)"])
        
        # Nivel de logging
        self.log_level = QComboBox()
        self.log_level.setMinimumHeight(35)
        self.log_level.addItems(["Mínimo", "Normal", "Detallado", "Depuración"])
        self.log_level.setCurrentText("Normal")  # Predeterminado
        
        # Etiquetas con estilo
        dir_label = QLabel("Directorio base:")
        dir_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        proc_label = QLabel("Modo de procesamiento:")
        proc_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        log_label = QLabel("Nivel de log:")
        log_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        
        system_layout.addRow(dir_label, base_dir_layout)
        system_layout.addRow(proc_label, self.process_mode)
        system_layout.addRow(log_label, self.log_level)
        
        # Añadir tabs
        tabs.addTab(camera_tab, "Cámara")
        tabs.addTab(system_tab, "Sistema")
        
        layout.addWidget(tabs)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setMinimumHeight(40)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
        self.setLayout(layout)
        
    def browse_base_dir(self):
        """Abre un diálogo para seleccionar el directorio base."""
        dir_path = QFileDialog.getExistingDirectory(
            self, "Seleccionar Directorio Base", 
            self.base_dir_edit.text()
        )
        if dir_path:
            self.base_dir_edit.setText(dir_path)
            
    def get_settings(self):
        """
        Obtiene la configuración establecida en el diálogo.
        
        Returns:
            dict: Configuración de la aplicación
        """
        return {
            'camera_index': self.camera_selector.currentIndex(),
            'resolution': self.resolution_selector.currentText(),
            'target_fps': self.fps_spinner.value(),
            'min_confidence': self.confidence_spinner.value(),
            'process_every_n_frames': self.frame_skip_spinner.value(),
            'detection_cooldown': self.cooldown_spinner.value(),
            'base_path': self.base_dir_edit.text(),
            'process_mode': self.process_mode.currentText(),
            'log_level': self.log_level.currentText()
        }