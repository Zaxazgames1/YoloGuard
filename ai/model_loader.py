# -*- coding: utf-8 -*-
"""Módulo para cargar modelos de IA."""

import torch
from ultralytics import YOLO
from facenet_pytorch import MTCNN, InceptionResnetV1

class ModelLoader:
    """Clase para cargar y gestionar modelos de IA."""
    
    def __init__(self):
        """Inicializa el cargador de modelos."""
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.yolo = None
        self.mtcnn = None
        self.facenet = None
        
    def load_models(self):
        """
        Carga todos los modelos necesarios.
        
        Returns:
            tuple: (yolo, mtcnn, facenet, device)
        """
        print("\nCargando modelos de IA...")
        print(f"Usando dispositivo: {self.device}")
        
        try:
            print("Cargando YOLO...")
            self.yolo = YOLO('yolov8n.pt')
            
            print("Cargando MTCNN...")
            self.mtcnn = MTCNN(
                keep_all=True,
                device=self.device,
                selection_method='probability'
            )
            
            print("Cargando FaceNet...")
            self.facenet = InceptionResnetV1(
                pretrained='vggface2',
                device=self.device
            ).eval()
            
            print("Modelos cargados correctamente")
            return self.yolo, self.mtcnn, self.facenet, self.device
            
        except Exception as e:
            print(f"Error al cargar modelos: {e}")
            raise