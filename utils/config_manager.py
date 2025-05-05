# -*- coding: utf-8 -*-
"""Módulo para gestionar la configuración de la aplicación."""

import os
import json
from config.constants import BASE_PATH, TARGET_FPS

class ConfigManager:
    """Clase para gestionar la configuración de la aplicación."""
    
    def __init__(self, config_path="config.json"):
        """
        Inicializa el gestor de configuración.
        
        Args:
            config_path (str): Ruta del archivo de configuración
        """
        self.config_path = config_path
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
        self.load_config()
        
    def load_config(self):
        """Carga la configuración desde el archivo."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # Actualizar solo las claves existentes
                    for key, value in loaded_config.items():
                        if key in self.config:
                            self.config[key] = value
                print(f"Configuración cargada desde {self.config_path}")
            else:
                print(f"No se encontró archivo de configuración en {self.config_path}, usando valores predeterminados")
                # Guardar configuración predeterminada
                self.save_config()
        except Exception as e:
            print(f"Error al cargar configuración: {str(e)}")
            # En caso de error, guardar la configuración predeterminada
            self.save_config()
            
    def save_config(self):
        """Guarda la configuración en el archivo."""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"Configuración guardada en {self.config_path}")
            return True
        except Exception as e:
            print(f"Error al guardar configuración: {str(e)}")
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
            
        Returns:
            bool: True si se pudo establecer, False en caso contrario
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
            
        Returns:
            bool: True si se pudo actualizar, False en caso contrario
        """
        try:
            for key, value in config_dict.items():
                if key in self.config:
                    self.config[key] = value
            return True
        except Exception:
            return False
        
    def get_resolution(self):
        """
        Obtiene la resolución como tupla (ancho, alto).
        
        Returns:
            tuple: (ancho, alto)
        """
        resolution_str = self.config.get('resolution', '1280x720')
        try:
            width, height = map(int, resolution_str.split('x'))
            return (width, height)
        except Exception:
            return (1280, 720)  # Valor predeterminado