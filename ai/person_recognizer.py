# -*- coding: utf-8 -*-
"""Módulo para el reconocimiento de personas."""

import torch
import numpy as np
from facenet_pytorch import InceptionResnetV1

class PersonRecognizer:
    """Clase para reconocer personas a partir de sus rostros."""
    
    def __init__(self, device=None):
        """
        Inicializa el reconocedor de personas.
        
        Args:
            device: Dispositivo donde ejecutar el modelo ('cpu', 'cuda', etc.)
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.facenet = InceptionResnetV1(
            pretrained='vggface2',
            device=self.device
        ).eval()
        
    def get_embedding(self, face_tensor):
        """
        Obtiene el embedding (vector característico) de un rostro.
        
        Args:
            face_tensor: Tensor del rostro normalizado
            
        Returns:
            numpy.ndarray: Vector embedding del rostro
        """
        try:
            with torch.no_grad():
                embedding = self.facenet(face_tensor)
                return embedding.cpu().numpy().flatten()
        except Exception as e:
            print(f"Error al obtener embedding: {str(e)}")
            return None
            
    def recognize_face(self, face_embedding, person_database, threshold=1.2):
        """
        Reconoce una persona a partir del embedding de su rostro.
        
        Args:
            face_embedding: Vector embedding del rostro
            person_database: Base de datos de personas
            threshold: Umbral de distancia para considerar una coincidencia
            
        Returns:
            tuple: (identidad reconocida, confianza) o (None, 0.0) si no se reconoce
        """
        try:
            min_dist = float('inf')
            identity = None
            confidence = 0.0
            
            if not person_database:
                return None, 0.0
                
            for person, data in person_database.items():
                try:
                    if 'embeddings' not in data:
                        continue
                        
                    dist = np.linalg.norm(face_embedding - data['embeddings'])
                    
                    if dist < min_dist:
                        min_dist = dist
                        identity = data['data']
                        confidence = max(0, (1 - (dist / threshold)) * 100)
                        
                except Exception:
                    continue
            
            if min_dist > threshold:
                return None, 0.0
            
            return identity, confidence
            
        except Exception as e:
            print(f"Error en reconocimiento facial: {str(e)}")
            return None, 0.0