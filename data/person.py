# -*- coding: utf-8 -*-
"""Módulo para la gestión de datos de personas."""

from datetime import datetime

class UniversityPersonData:
    """Clase que representa los datos de una persona en la universidad."""
    
    def __init__(self, nombre="", id="", facultad="", programa="", rol="", tipo="", sede="", extension="", semestre=""):
        """
        Inicializa un objeto UniversityPersonData.
        
        Args:
            nombre (str): Nombre completo de la persona
            id (str): ID o código de la persona
            facultad (str): Facultad a la que pertenece
            programa (str): Programa académico
            rol (str): Rol en la universidad (Estudiante, Docente, Administrativo)
            tipo (str): Tipo de acceso
            sede (str): Sede principal
            extension (str): Extensión/sede donde estudia
            semestre (str): Semestre actual (para estudiantes)
        """
        self.nombre = nombre
        self.id = id
        self.facultad = facultad
        self.programa = programa
        self.rol = rol
        self.tipo = tipo
        self.sede = sede
        self.extension = extension
        self.semestre = semestre
        self.fecha_registro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """Convierte el objeto a un diccionario."""
        return {
            "nombre": self.nombre,
            "id": self.id,
            "facultad": self.facultad,
            "programa": self.programa,
            "rol": self.rol,
            "tipo": self.tipo,
            "sede": self.sede,
            "extension": self.extension,
            "semestre": self.semestre,
            "fecha_registro": self.fecha_registro
        }

    @staticmethod
    def from_dict(data):
        """
        Crea un objeto UniversityPersonData a partir de un diccionario.
        
        Args:
            data (dict): Diccionario con los datos de la persona
            
        Returns:
            UniversityPersonData: Objeto creado con los datos proporcionados
        """
        person = UniversityPersonData()
        person.nombre = data.get("nombre", "")
        person.id = data.get("id", "")
        person.facultad = data.get("facultad", "")
        person.programa = data.get("programa", "")
        person.rol = data.get("rol", "")
        person.tipo = data.get("tipo", "")
        person.sede = data.get("sede", "")
        person.extension = data.get("extension", "")
        person.semestre = data.get("semestre", "")
        person.fecha_registro = data.get("fecha_registro", "")
        return person