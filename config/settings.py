# -*- coding: utf-8 -*-
"""Configuraciones del sistema."""

import os
import json
from config.constants import BASE_PATH, TARGET_FPS

class Settings:
    """Clase para gestionar la configuración del sistema."""
    
    def __init__(self):
        """Inicializa la configuración con valores predeterminados."""
        self.config = {
            'base_path': BASE_PATH,
            'target_fps': TARGET_FPS,
            'process_every_n_frames': 2,
            'detection_cooldown': 3.0,
            'recognition_threshold': 1.2,
            'device': 'auto',  # 'auto', 'cpu', 'cuda'
            'log_level': 'normal',  # 'minimal', 'normal', 'detailed', 'debug'
            'camera_index': 0,
            'resolution': '1280x720',
            'max_log_entries': 1000,
            'memory_limit': 1000  # MB
        }
        
    def save_to_file(self, filepath):
        """
        Guarda la configuración en un archivo.
        
        Args:
            filepath (str): Ruta del archivo
            
        Returns:
            bool: True si se guardó correctamente, False en caso contrario
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {str(e)}")
            return False
            
    def load_from_file(self, filepath):
        """
        Carga la configuración desde un archivo.
        
        Args:
            filepath (str): Ruta del archivo
            
        Returns:
            bool: True si se cargó correctamente, False en caso contrario
        """
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Actualizar solo las claves existentes
                    for key, value in data.items():
                        if key in self.config:
                            self.config[key] = value
                            
                return True
        except Exception as e:
            print(f"Error al cargar configuración: {str(e)}")
        
        return False
        
    def get(self, key, default=None):
        """
        Obtiene un valor de configuración.
        
        Args:
            key (str): Clave de configuración
            default: Valor predeterminado si la clave no existe
            
        Returns:
            Valor de configuración
        """
        return self.config.get(key, default)
        
    def set(self, key, value):
        """
        Establece un valor de configuración.
        
        Args:
            key (str): Clave de configuración
            value: Valor a establecer
        """
        if key in self.config:
            self.config[key] = value
            return True
        return False
        
    def update(self, config_dict):
        """
        Actualiza varios valores de configuración a la vez.
        
        Args:
            config_dict (dict): Diccionario con claves y valores a actualizar
        """
        for key, value in config_dict.items():
            self.set(key, value)