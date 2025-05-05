# -*- coding: utf-8 -*-
"""Constantes globales para el sistema YoloGuard."""

import os

# Rutas y configuraciones globales
BASE_PATH = "dataset_ucundinamarca"
VERSION = "2.0"
TARGET_FPS = 30
MAX_LOG_ENTRIES = 1000
BATCH_SIZE = 4

# Definir sedes de la Universidad de Cundinamarca
SEDES = [
    "Fusagasugá", "Girardot", "Ubaté", "Facatativá", "Chía", "Chocontá", 
    "Zipaquirá", "Soacha"
]

# Definir extensiones y sus carreras asociadas
EXTENSIONES_CARRERAS = {
    "Fusagasugá": [
        "Administración de Empresas", "Contaduría Pública", "Licenciatura en Educación Física",
        "Ingeniería Agronómica", "Ingeniería de Sistemas", "Ingeniería Electrónica",
        "Zootecnia", "Licenciatura en Matemáticas", "Licenciatura en Ciencias Sociales",
        "Licenciatura en Educación Básica", "Psicología", "Música"
    ],
    "Girardot": [
        "Administración de Empresas", "Enfermería", "Ingeniería de Sistemas",
        "Licenciatura en Educación Básica", "Tecnología en Gestión Turística y Hotelera"
    ],
    "Ubaté": [
        "Administración de Empresas", "Contaduría Pública", "Ingeniería de Sistemas",
        "Zootecnia"
    ],
    "Facatativá": [
        "Administración de Empresas", "Contaduría Pública", "Ingeniería Agronómica",
        "Ingeniería de Sistemas", "Ingeniería Ambiental", "Psicología"
    ],
    "Chía": [
        "Administración de Empresas", "Ingeniería de Sistemas"
    ],
    "Chocontá": [
        "Administración de Empresas", "Zootecnia"
    ],
    "Zipaquirá": [
        "Música", "Ingeniería de Sistemas"
    ],
    "Soacha": [
        "Ingeniería Industrial", "Tecnología en Desarrollo de Software"
    ]
}