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