# -*- coding: utf-8 -*-
"""Módulo para gestionar la base de datos de personas."""

import os
import json
import numpy as np
import torch
import traceback
import gc
import cv2
from PyQt6.QtWidgets import QProgressDialog
from PyQt6.QtCore import Qt

from data.person import UniversityPersonData
from config.constants import BASE_PATH

class PersonDatabase:
    """Clase para gestionar la base de datos de personas."""
    
    def __init__(self, mtcnn, facenet):
        """
        Inicializa la base de datos de personas.
        
        Args:
            mtcnn: Modelo MTCNN para detección de rostros
            facenet: Modelo FaceNet para extracción de características
        """
        self.mtcnn = mtcnn
        self.facenet = facenet
        self.person_database = {}
        
    def load_database(self, parent_widget=None):
        """
        Carga la base de datos de personas.
        
        Args:
            parent_widget: Widget padre para mostrar el diálogo de progreso
            
        Returns:
            dict: Base de datos de personas
        """
        self.person_database.clear()
        try:
            print("\nCargando base de datos de personas...")
            
            if not os.path.exists(BASE_PATH):
                os.makedirs(BASE_PATH)
                print(f"Directorio base creado: {BASE_PATH}")
                return self.person_database

            # Mostrar diálogo de progreso si hay un widget padre
            progress = None
            if parent_widget:
                progress = QProgressDialog("Cargando base de datos...", "Cancelar", 0, 100, parent_widget)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(0)
            
            # Primero contar cuántas personas hay para actualizar la barra de progreso
            total_people = 0
            for facultad in os.listdir(BASE_PATH):
                facultad_path = os.path.join(BASE_PATH, facultad)
                if os.path.isdir(facultad_path):
                    for person in os.listdir(facultad_path):
                        if os.path.isdir(os.path.join(facultad_path, person)):
                            total_people += 1
            
            if total_people == 0:
                if progress:
                    progress.setValue(100)
                print("No se encontraron personas en la base de datos")
                return self.person_database
            
            # Ahora procesar cada persona
            processed_people = 0
            total_embeddings = 0
            
            for facultad in os.listdir(BASE_PATH):
                facultad_path = os.path.join(BASE_PATH, facultad)
                if not os.path.isdir(facultad_path):
                    continue
                    
                print(f"\nProcesando facultad: {facultad}")
                for person in os.listdir(facultad_path):
                    if progress and progress.wasCanceled():
                        break
                        
                    person_path = os.path.join(facultad_path, person)
                    if not os.path.isdir(person_path):
                        continue
                    
                    print(f"Procesando persona: {person}")
                    
                    # Cargar metadata
                    info_path = os.path.join(person_path, "info.json")
                    if os.path.exists(info_path):
                        with open(info_path, 'r', encoding='utf-8') as f:
                            person_data = UniversityPersonData.from_dict(json.load(f))
                    else:
                        print(f"Archivo info.json no encontrado para {person}")
                        continue

                    # Procesar imágenes
                    embeddings = []
                    image_count = 0
                    
                    # Limitar a procesar máximo 5 imágenes por persona para mejor rendimiento
                    image_files = [f for f in os.listdir(person_path) 
                                  if f.lower().endswith(('.jpg', '.jpeg', '.png'))][:5]
                    
                    for img_file in image_files:
                        img_path = os.path.join(person_path, img_file)
                        try:
                            img = cv2.imread(img_path)
                            if img is None:
                                print(f"No se pudo cargar la imagen: {img_path}")
                                continue
                                
                            # Reducir tamaño de imagen para procesamiento más rápido
                            if img.shape[0] > 640 or img.shape[1] > 640:
                                scale = min(640/img.shape[0], 640/img.shape[1])
                                new_size = (int(img.shape[1] * scale), int(img.shape[0] * scale))
                                img = cv2.resize(img, new_size)
                                
                            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            faces = self.mtcnn(rgb_img)
                            
                            if faces is not None:
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

                                    # Obtener embedding
                                    with torch.no_grad():
                                        embedding = self.facenet(face_tensor)
                                        embedding_np = embedding.cpu().numpy().flatten()
                                        embeddings.append(embedding_np)
                                        image_count += 1
                                        print(f"Procesada imagen {image_count} para {person}")
                                        total_embeddings += 1
                                        
                        except Exception as e:
                            print(f"Error al procesar imagen {img_path}: {str(e)}")
                            continue
                    
                    if embeddings:
                        print(f"Generando embedding promedio para {person}")
                        mean_embedding = np.mean(embeddings, axis=0)
                        self.person_database[person] = {
                            'embeddings': mean_embedding,
                            'data': person_data
                        }
                        print(f"Persona {person} agregada a la base de datos")
                    else:
                        print(f"No se encontraron rostros válidos para {person}")
                    
                    # Actualizar progreso
                    processed_people += 1
                    if progress:
                        progress_value = int((processed_people / total_people) * 100)
                        progress.setValue(progress_value)

            if progress:
                progress.setValue(100)
            
            print(f"\nBase de datos cargada exitosamente")
            print(f"Total de personas registradas: {len(self.person_database)}")
            print(f"Total de embeddings procesados: {total_embeddings}")
            
            # Liberar memoria no utilizada
            gc.collect()
            torch.cuda.empty_cache() if torch.cuda.is_available() else None
            
            return self.person_database
            
        except Exception as e:
            error_msg = f"Error al cargar base de datos: {str(e)}"
            print(error_msg)
            traceback.print_exc()
            return self.person_database

    def verify_images(self, directory, parent_widget=None, logger=None):
        """
        Verifica la integridad de las imágenes en la base de datos.
        
        Args:
            directory (str): Directorio a verificar
            parent_widget: Widget padre para mostrar el diálogo de progreso
            logger: Logger para registrar mensajes
            
        Returns:
            tuple: (total_images, valid_images, invalid_images)
        """
        try:
            total_images = 0
            valid_images = 0
            invalid_images = 0
            
            if logger:
                logger.log_message("🔍 Iniciando verificación de imágenes...")
            
            # Mostrar diálogo de progreso
            progress = None
            if parent_widget:
                progress = QProgressDialog("Verificando imágenes...", "Cancelar", 0, 100, parent_widget)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
                progress.setValue(0)
            
            # Primero contar el total de imágenes
            image_paths = []
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        image_paths.append(os.path.join(root, file))
            
            total_images = len(image_paths)
            if total_images == 0:
                if progress:
                    progress.setValue(100)
                if logger:
                    logger.log_message("ℹ️ No se encontraron imágenes para verificar")
                return 0, 0, 0
                
            # Ahora procesar cada imagen
            for i, img_path in enumerate(image_paths):
                if progress and progress.wasCanceled():
                    break
                    
                try:
                    img = cv2.imread(img_path)
                    
                    if img is None:
                        if logger:
                            logger.log_message(f"❌ Imagen corrupta: {img_path}")
                        invalid_images += 1
                        continue
                    
                    # Reducir tamaño para procesamiento más rápido
                    if img.shape[0] > 640 or img.shape[1] > 640:
                        scale = min(640/img.shape[0], 640/img.shape[1])
                        new_size = (int(img.shape[1] * scale), int(img.shape[0] * scale))
                        img = cv2.resize(img, new_size)
                    
                    rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                    faces = self.mtcnn(rgb_img)
                    
                    if faces is None:
                        if logger:
                            logger.log_message(f"⚠️ No se detectaron rostros en: {img_path}")
                        invalid_images += 1
                    else:
                        valid_images += 1
                        if i % 10 == 0 and logger:  # Reducir registro de log para hacerlo más eficiente
                            logger.log_message(f"✅ Imagen válida: {img_path}")
                except Exception as e:
                    if logger:
                        logger.log_message(f"❌ Error al procesar imagen {img_path}: {str(e)}")
                    invalid_images += 1
                
                # Actualizar progreso
                if progress:
                    progress_value = int((i + 1) / total_images * 100)
                    progress.setValue(progress_value)
            
            if progress:
                progress.setValue(100)
            
            return total_images, valid_images, invalid_images
            
        except Exception as e:
            if logger:
                logger.log_message(f"❌ Error durante la verificación: {str(e)}")
            return 0, 0, 0