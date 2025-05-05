#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
YoloGuard - Sistema de Control de Acceso Universidad de Cundinamarca
Versión 2.0

Este es el punto de entrada principal de la aplicación.
"""

import sys
import os
import traceback
import gc

import torch
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt

from config.constants import BASE_PATH, VERSION
from ai.model_loader import ModelLoader
from utils.logger import Logger
from utils.theme import UCundinamarcaTheme
from gui.main_window import AccessControlSystem

def main():
    """Función principal que inicia la aplicación."""
    try:
        print("\n====== INICIANDO SISTEMA DE CONTROL DE ACCESO UDEC CON YOLOGUARD ======")
        print(f"Versión: {VERSION}")
        
        app = QApplication(sys.argv)
        app.setStyle("Fusion")
        
        # Verificar y crear directorio base
        if not os.path.exists(BASE_PATH):
            print(f"Creando directorio base: {BASE_PATH}")
            os.makedirs(BASE_PATH)
        
        # Ajustar para pantallas de alta resolución
        if hasattr(Qt.ApplicationAttribute, 'AA_EnableHighDpiScaling'):
            app.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
        if hasattr(Qt.ApplicationAttribute, 'AA_UseHighDpiPixmaps'):
            app.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
        
        # Crear logger
        logger = Logger()
        
        # Cargar modelos de IA
        print("Cargando modelos de IA...")
        model_loader = ModelLoader()
        yolo, mtcnn, facenet, device = model_loader.load_models()
        
        # Iniciar aplicación
        print("Iniciando interfaz gráfica...")
        window = AccessControlSystem(yolo, mtcnn, facenet, device, logger)
        window.show()
        
        # Asignar el widget de log al logger
        logger.set_log_widget(window.log_text)
        logger.log_message("✅ Sistema iniciado correctamente")
        
        print("Sistema iniciado correctamente")
        return app.exec()
        
    except Exception as e:
        print("\n====== ERROR FATAL ======")
        print(f"Error al iniciar el sistema: {str(e)}")
        traceback.print_exc()
        
        if QApplication.instance():
            QMessageBox.critical(
                None, 
                "Error Fatal", 
                f"Error al iniciar la aplicación: {str(e)}\n\nConsulte la consola para más detalles."
            )
        return 1

if __name__ == "__main__":
    sys.exit(main())