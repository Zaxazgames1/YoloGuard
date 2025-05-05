# -*- coding: utf-8 -*-
"""Módulo para la detección de personas con YOLO."""

import cv2
from ultralytics import YOLO

class YoloDetector:
    """Clase para detectar personas en imágenes usando YOLO."""
    
    def __init__(self, model_path='yolov8n.pt'):
        """
        Inicializa el detector YOLO.
        
        Args:
            model_path (str): Ruta al modelo YOLO
        """
        self.model = YOLO(model_path)
        
    def detect_persons(self, image, conf=0.25):
        """
        Detecta personas en una imagen.
        
        Args:
            image: Imagen en formato BGR (OpenCV)
            conf (float): Umbral de confianza para detecciones
            
        Returns:
            results: Resultados de la detección
        """
        try:
            # Reducir resolución para mayor velocidad
            image_small = cv2.resize(image, (640, 480))
            results = self.model(image_small, classes=[0], conf=conf)  # clase 0 = persona
            return results
        except Exception as e:
            print(f"Error en la detección YOLO: {str(e)}")
            return None
            
    def scale_detections(self, results, orig_shape, small_shape=(640, 480)):
        """
        Escala las detecciones a la resolución original.
        
        Args:
            results: Resultados de la detección
            orig_shape: Forma de la imagen original (alto, ancho)
            small_shape: Forma de la imagen reducida usada para detección
            
        Returns:
            list: Lista de cajas redimensionadas [(x1, y1, x2, y2), ...]
        """
        if results is None or len(results) == 0:
            return []
            
        try:
            scale_x = orig_shape[1] / small_shape[0]
            scale_y = orig_shape[0] / small_shape[1]
            
            scaled_boxes = []
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                    y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                    
                    # Asegurar que las coordenadas sean válidas
                    x1, x2 = max(0, x1), min(orig_shape[1], x2)
                    y1, y2 = max(0, y1), min(orig_shape[0], y2)
                    
                    if (x2 - x1) > 0 and (y2 - y1) > 0:
                        scaled_boxes.append((x1, y1, x2, y2))
                        
            return scaled_boxes
        except Exception as e:
            print(f"Error al escalar detecciones: {str(e)}")
            return []