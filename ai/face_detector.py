# -*- coding: utf-8 -*-
"""Módulo para la detección de rostros."""

import torch
import cv2
import numpy as np
from facenet_pytorch import MTCNN

class FaceDetector:
    """Clase para detectar rostros en imágenes."""
    
    def __init__(self, device=None):
        """
        Inicializa el detector de rostros.
        
        Args:
            device: Dispositivo donde ejecutar el modelo ('cpu', 'cuda', etc.)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.mtcnn = MTCNN(
            keep_all=True,
            device=self.device,
            selection_method='probability'
        )
        
    def detect_faces(self, image):
        """
        Detecta rostros en una imagen.
        
        Args:
            image: Imagen en formato BGR (OpenCV)
            
        Returns:
            tensor: Tensor con los rostros detectados
        """
        try:
            # Convertir a RGB si es necesario
            if len(image.shape) == 3 and image.shape[2] == 3:
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image
                
            # Detectar rostros
            faces = self.mtcnn(rgb_image)
            return faces
        except Exception as e:
            print(f"Error en la detección de rostros: {str(e)}")
            return None
            
    def process_face_tensor(self, faces):
        """
        Procesa el tensor de rostros para normalizarlo.
        
        Args:
            faces: Tensor de rostros detectados
            
        Returns:
            tensor: Tensor de rostros normalizado
        """
        if faces is None:
            return None
            
        try:
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
                
                return face_tensor
        except Exception as e:
            print(f"Error al procesar tensor de rostros: {str(e)}")
            
        return None