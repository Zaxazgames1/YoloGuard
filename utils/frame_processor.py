# -*- coding: utf-8 -*-
"""Módulo para el procesamiento de frames."""

import cv2
import torch
import numpy as np
import time
import traceback
from collections import deque
from queue import Queue
from PyQt6.QtCore import QThread, pyqtSignal

class FrameProcessor(QThread):
    """Clase para procesar frames en un hilo separado y evitar bloquear la UI."""
    
    frame_processed = pyqtSignal(object, object, float)
    
    def __init__(self, yolo, mtcnn, facenet, device, person_database, parent=None):
        """
        Inicializa el procesador de frames.
        
        Args:
            yolo: Modelo YOLO para detección de personas
            mtcnn: Modelo MTCNN para detección de rostros
            facenet: Modelo FaceNet para reconocimiento facial
            device: Dispositivo de procesamiento (CPU/GPU)
            person_database: Base de datos de personas registradas
            parent: Objeto padre para la jerarquía de Qt
        """
        super().__init__(parent)
        self.yolo = yolo
        self.mtcnn = mtcnn
        self.facenet = facenet
        self.device = device
        self.person_database = person_database
        self.frame_queue = Queue(maxsize=2)  # Solo mantenemos 2 frames en cola
        self.running = False
        self.fps_deque = deque(maxlen=30)  # Para calcular FPS promedio
        self.process_every_n_frames = 2  # Procesar solo cada n frames para mejor rendimiento
        self.frame_count = 0
        
    def add_frame(self, frame):
        """
        Añade un frame a la cola de procesamiento.
        
        Args:
            frame: Frame a procesar
        """
        # Omitir algunos frames para mejor rendimiento
        self.frame_count += 1
        if self.frame_count % self.process_every_n_frames == 0:
            if not self.frame_queue.full():
                self.frame_queue.put(frame.copy())  # Usar .copy() para evitar problemas de referencias
    
    def run(self):
        """Método principal que se ejecuta en el hilo."""
        self.running = True
        while self.running:
            if not self.frame_queue.empty():
                try:
                    start_time = time.time()
                    frame = self.frame_queue.get()
                    
                    # Detección de personas con YOLO - reducir resolución para mayor velocidad
                    frame_small = cv2.resize(frame, (640, 480))
                    results = self.yolo(frame_small, classes=[0])  # clase 0 = persona
                    
                    # Escalar resultados de vuelta a la resolución original
                    scale_x = frame.shape[1] / frame_small.shape[1]
                    scale_y = frame.shape[0] / frame_small.shape[0]
                    
                    display_frame = frame.copy()
                    detected_identity = None
                    detected_confidence = 0
                    
                    for result in results:
                        boxes = result.boxes
                        for box in boxes:
                            # Obtener coordenadas y escalarlas
                            x1, y1, x2, y2 = map(int, box.xyxy[0])
                            x1, x2 = int(x1 * scale_x), int(x2 * scale_x)
                            y1, y2 = int(y1 * scale_y), int(y2 * scale_y)
                            
                            # Asegurar que las coordenadas sean válidas
                            x1, x2 = max(0, x1), min(frame.shape[1], x2)
                            y1, y2 = max(0, y1), min(frame.shape[0], y2)
                            
                            # Extraer y procesar rostro
                            if (x2 - x1) <= 0 or (y2 - y1) <= 0:
                                continue
                                
                            face_img = frame[y1:y2, x1:x2]
                            if face_img.size == 0:
                                continue
                                
                            # Procesar cara sólo si es lo suficientemente grande
                            if (x2 - x1) < 60 or (y2 - y1) < 60:
                                continue
                            
                            rgb_face = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
                            
                            # Usar el detector MTCNN
                            try:
                                faces = self.mtcnn(rgb_face)
                                
                                if faces is not None:
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

                                        # Verificar que el tensor tiene la forma correcta
                                        if face_tensor.size(0) == 1:
                                            # Obtener embedding y reconocer
                                            with torch.no_grad():
                                                embedding = self.facenet(face_tensor)
                                                face_embedding = embedding.cpu().numpy().flatten()
                                                
                                                identity, confidence = self.recognize_face(face_embedding)
                                                
                                                # Si encontramos una identidad con buena confianza
                                                if identity and confidence > 20:
                                                    detected_identity = identity
                                                    detected_confidence = confidence
                                                    
                                                    # Ajustar el color basado en el nivel de confianza
                                                    if confidence > 60:
                                                        color = (0, 128, 0)  # Verde Institucional
                                                    elif confidence > 40:
                                                        color = (0, 100, 0)  # Verde más oscuro
                                                    else:
                                                        color = (0, 80, 0)  # Verde aún más oscuro
                                                    
                                                    label = f"{identity.nombre} - {identity.rol} ({confidence:.1f}%)"
                                                    
                                                    # Dibujar recuadro y etiqueta
                                                    cv2.rectangle(display_frame, (x1-10, y1-10), (x2+10, y2+10), color, 3)
                                                    
                                                    # Fondo semi-transparente para el texto
                                                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
                                                    cv2.rectangle(display_frame, 
                                                                (x1-10, y1-40),
                                                                (x1 + text_size[0], y1-10),
                                                                color, -1)
                                                    
                                                    # Texto en blanco
                                                    cv2.putText(display_frame, label,
                                                            (x1-10, y1-15),
                                                            cv2.FONT_HERSHEY_DUPLEX, 0.8,
                                                            (255, 255, 255), 2)
                                                else:
                                                    color = (0, 0, 255)  # Rojo para desconocidos
                                                    label = "No encontrado en la base de datos"
                                                    
                                                    # Dibujar recuadro rojo y etiqueta
                                                    cv2.rectangle(display_frame, (x1-10, y1-10), (x2+10, y2+10), color, 2)
                                                    
                                                    text_size = cv2.getTextSize(label, cv2.FONT_HERSHEY_DUPLEX, 0.8, 2)[0]
                                                    cv2.rectangle(display_frame,
                                                                (x1-10, y1-40),
                                                                (x1 + text_size[0], y1-10),
                                                                color, -1)
                                                    cv2.putText(display_frame, label,
                                                              (x1-10, y1-15),
                                                              cv2.FONT_HERSHEY_DUPLEX, 0.8,
                                                              (255, 255, 255), 2)
                            except Exception as e:
                                print(f"Error al procesar rostro: {e}")
                                continue
                    
                    # Calcular FPS
                    end_time = time.time()
                    processing_time = end_time - start_time
                    fps = 1.0 / processing_time if processing_time > 0 else 0
                    self.fps_deque.append(fps)
                    avg_fps = sum(self.fps_deque) / len(self.fps_deque)
                    
                    # Mostrar FPS en la esquina superior izquierda (fuente más grande)
                    cv2.putText(display_frame, f"FPS: {avg_fps:.1f}", (10, 30), 
                              cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 128, 0), 3)
                    
                    # Logo YoloGuard en la esquina superior derecha (fuente más grande)
                    logo_text = "YoloGuard"
                    logo_size = cv2.getTextSize(logo_text, cv2.FONT_HERSHEY_SIMPLEX, 1.0, 2)[0]
                    cv2.putText(display_frame, logo_text, 
                             (display_frame.shape[1] - logo_size[0] - 10, 30),
                             cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 128, 0), 3)
                    
                    # Emitir señal con el frame procesado
                    self.frame_processed.emit(display_frame, detected_identity, detected_confidence)
                    
                except Exception as e:
                    print(f"Error en procesamiento de frame: {e}")
                    traceback.print_exc()
            else:
                # Dormir un poco si no hay frames para procesar
                time.sleep(0.01)
    
    def recognize_face(self, face_embedding, threshold=1.2):
        """
        Reconoce un rostro comparándolo con la base de datos.
        
        Args:
            face_embedding: Embedding facial a comparar
            threshold: Umbral de distancia para considerar una coincidencia
            
        Returns:
            tuple: (identidad reconocida, confianza) o (None, 0.0) si no se reconoce
        """
        try:
            min_dist = float('inf')
            identity = None
            confidence = 0.0
            
            if not self.person_database:
                return None, 0.0
                
            for person, data in self.person_database.items():
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
    
    def stop(self):
        """Detiene el procesamiento de frames."""
        self.running = False
        self.wait()