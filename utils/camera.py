# -*- coding: utf-8 -*-
"""Módulo para la gestión de la cámara."""

import cv2
import platform
import time

def open_fastest_webcam(camera_index=0, resolution=(1280, 720), target_fps=30):
    """
    Función optimizada para abrir la webcam lo más rápido posible y configurarla para alto FPS.
    
    Args:
        camera_index (int): Índice de la cámara a abrir
        resolution (tuple): Resolución deseada (ancho, alto)
        target_fps (int): FPS objetivo
        
    Returns:
        cv2.VideoCapture: Objeto de captura de video o None si falla
    """
    start_time = time.time()
    print("Iniciando apertura ultra rápida de webcam...")
    
    # Usar el backend correcto según sistema operativo
    if platform.system() == 'Windows':
        # En Windows, DirectShow es mucho más rápido
        cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
        print("Usando backend DirectShow para máxima velocidad")
    else:
        # En Linux/Mac
        cap = cv2.VideoCapture(camera_index)
    
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara")
        return None
    
    # Configurar para máxima velocidad
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, resolution[0])
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, resolution[1])
    cap.set(cv2.CAP_PROP_FPS, target_fps)  # Intentar establecer FPS objetivo
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Reducir buffer para menor latencia
    
    # Verificar qué FPS estamos obteniendo
    actual_fps = cap.get(cv2.CAP_PROP_FPS)
    print(f"FPS configurados: {actual_fps}")
    
    print(f"Cámara abierta en {time.time() - start_time:.3f} segundos")
    return cap

def get_available_cameras(max_cameras=10):
    """
    Detecta cámaras disponibles en el sistema.
    
    Args:
        max_cameras (int): Número máximo de cámaras a verificar
        
    Returns:
        list: Lista de tuplas (índice, nombre, estado) de cámaras disponibles
    """
    available_cameras = []
    for i in range(max_cameras):
        try:
            # En Windows, DirectShow es más rápido y proporciona más información
            if platform.system() == 'Windows':
                cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            else:
                cap = cv2.VideoCapture(i)
            
            if cap.isOpened():
                # Intentar obtener información de la cámara
                # La mayoría de cámaras no reportan esta info correctamente,
                # así que ponemos valores alternativos
                ret, frame = cap.read()
                if ret:
                    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                    name = f"Cámara {i} ({width}x{height})"
                else:
                    name = f"Cámara {i}"
                    
                available_cameras.append((i, name, True))
                cap.release()
            else:
                # Algunos sistemas reportan cámaras aunque no se puedan abrir
                # Las incluimos pero marcadas como no disponibles
                available_cameras.append((i, f"Cámara {i} (No disponible)", False))
        except Exception as e:
            print(f"Error al verificar cámara {i}: {str(e)}")
            
    # Filtrar solo las cámaras disponibles
    return [cam for cam in available_cameras if cam[2]]