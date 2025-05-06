# YoloGuard - Sistema de Control de Acceso Universidad de Cundinamarca

<div align="center">
  <img src="resources/images/yologuard_logo.png" alt="YoloGuard Logo" width="200">
  <h3>Control de Acceso Inteligente basado en Reconocimiento Facial</h3>
  <p>Desarrollado por Johan Sebastian Rojas Ramirez</p>
</div>

## 📋 Descripción

YoloGuard es un sistema de control de acceso avanzado basado en reconocimiento facial, desarrollado específicamente para la Universidad de Cundinamarca. Utiliza tecnología de inteligencia artificial de última generación (YOLO v8 y FaceNet) para detectar y reconocer personas en tiempo real, facilitando el control de acceso a las instalaciones universitarias con alta precisión y velocidad.

El sistema está diseñado con una arquitectura modular orientada a objetos, lo que permite una fácil escalabilidad y mantenimiento. Además, cuenta con una interfaz gráfica intuitiva desarrollada con PyQt6 que facilita su uso para operadores con diferentes niveles de experiencia técnica.

## ✨ Características Principales

- **Reconocimiento facial en tiempo real**: Detecta y reconoce personas con alta precisión usando modelos de IA avanzados
- **Interfaz gráfica moderna e intuitiva**: Diseñada con PyQt6 para una experiencia de usuario óptima
- **Registro de personas**: Sistema completo para añadir nuevas personas a la base de datos
- **Seguimiento detallado de accesos**: Control y registro de todos los accesos con fecha, hora y nivel de confianza
- **Estadísticas e informes**: Generación de informes detallados y visualización de estadísticas
- **Multi-sede**: Soporte completo para todas las sedes y extensiones de la Universidad de Cundinamarca
- **Optimizado para rendimiento**: Procesamiento eficiente que funciona incluso en equipos con recursos limitados
- **Respaldo y restauración**: Sistema de copias de seguridad para proteger la base de datos

## 🛠️ Tecnologías Utilizadas

- **Python 3.10+**: Lenguaje de programación principal
- **PyQt6**: Framework para la interfaz gráfica de usuario
- **OpenCV**: Procesamiento de imágenes y manejo de cámara
- **PyTorch**: Framework de aprendizaje profundo para modelos de IA
- **YOLO v8**: Detección de personas en tiempo real
- **FaceNet**: Reconocimiento facial de alta precisión
- **Pandas**: Análisis y gestión de datos
- **Ultralytics**: Implementación optimizada de YOLO
- **NumPy**: Procesamiento numérico eficiente
- **Programación Orientada a Objetos**: Arquitectura modular y mantenible

## 📦 Requisitos

- Python 3.8 o superior
- Tarjeta gráfica NVIDIA con soporte CUDA (recomendado para mejor rendimiento)
- Cámara web de resolución 720p o superior
- Mínimo 4GB de RAM (8GB recomendado)
- Espacio en disco: 2GB para la aplicación y modelos
- Sistemas Operativos soportados:
  - Windows 10/11
  - Ubuntu 20.04 LTS o superior
  - macOS 11 (Big Sur) o superior

## 📥 Instalación

1. Clone el repositorio:
   ```bash
   git clone https://github.com/Zaxazgames1/YoloGuard.git
   cd yologuard
   ```

2. Instale las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecute la aplicación:
   ```bash
   python main.py
   ```

## 🏗️ Estructura del Proyecto

```
yologuard/
├── __init__.py
├── main.py
├── README.md
├── requirements.txt
├── ai/                 # Módulos de inteligencia artificial
│   ├── __init__.py
│   ├── face_detector.py
│   ├── model_loader.py
│   ├── person_recognizer.py
│   └── yolo_detector.py
├── config/             # Configuración global
│   ├── __init__.py
│   ├── constants.py
│   └── settings.py
├── data/               # Gestión de datos
│   ├── __init__.py
│   ├── access_log.py
│   ├── database.py
│   └── person.py
├── gui/                # Interfaces gráficas
│   ├── __init__.py
│   ├── main_window.py
│   ├── registration_dialog.py
│   ├── search_dialog.py
│   ├── settings_dialog.py
│   └── stats_dialog.py
├── logs/               # Logs del sistema
├── resources/          # Recursos estáticos
│   ├── images/
│   └── styles/
├── tests/              # Tests unitarios
└── utils/              # Utilidades
    ├── __init__.py
    ├── camera.py
    ├── config_manager.py
    ├── frame_processor.py
    ├── logger.py
    └── theme.py
```

## 📝 Guía de Uso

### Registro de Personas

1. Inicie la aplicación
2. Haga clic en "Nuevo Registro"
3. Complete la información requerida en las pestañas "Información Personal" y "Información Académica"
4. Capture al menos 5 fotos desde diferentes ángulos
5. Guarde el registro y la persona quedará registrada en la base de datos

### Monitoreo en Tiempo Real

1. Inicie la aplicación
2. Haga clic en "Iniciar Monitoreo"
3. El sistema comenzará a detectar y reconocer personas automáticamente
4. Los accesos reconocidos se registrarán con su nivel de confianza

### Generación de Informes

1. Inicie la aplicación
2. Haga clic en "Generar Informe" o vaya a "Sistema" > "Exportar Registros"
3. Seleccione el formato de salida (Excel o CSV)
4. El sistema generará automáticamente un informe completo con estadísticas

### Búsqueda de Personas

1. Haga clic en "Buscar Persona"
2. Utilice los filtros de búsqueda para encontrar registros específicos
3. Seleccione una persona para ver sus detalles completos

## 🔧 Configuración Avanzada

La configuración del sistema se puede ajustar desde la interfaz gráfica:

1. Vaya a "Configuración" > "Configuración Avanzada"
2. Ajuste los parámetros según sus necesidades:
   - FPS objetivo para el procesamiento de video
   - Resolución de la cámara
   - Umbral de confianza para reconocimiento facial
   - Modo de procesamiento (CPU/GPU)
   - Directorio base para almacenamiento de datos
   - Nivel de detalle de los logs

## 🌐 Soporte para Sedes

YoloGuard está diseñado para funcionar en todas las sedes de la Universidad de Cundinamarca:

- Fusagasugá (Sede Principal)
- Girardot
- Ubaté
- Facatativá
- Chía
- Chocontá
- Zipaquirá
- Soacha

## 🔒 Seguridad

- Todos los datos se almacenan localmente para mayor seguridad
- No se requiere conexión a internet para el funcionamiento básico
- Los embeddings faciales están protegidos y no pueden ser usados fuera del sistema
- Sistema de respaldo integrado para prevenir pérdida de datos

## 👨‍💻 Autor

**Johan Sebastian Rojas Ramirez**

- Correo Electrónico: johansebastianrojasramirez7@gmail.com
- Teléfono: +573214360157
- GitHub: [github.com/Zaxazgames1](https://github.com/Zaxazgames1)

## 📄 Licencia

© 2025 Universidad de Cundinamarca. Todos los derechos reservados.

## 🤝 Contribuciones

Las contribuciones, problemas y solicitudes de funciones son bienvenidas. Póngase en contacto con el autor para más información.

## 🐛 Reporte de Errores

Si encuentra algún error o problema, por favor repórtelo a través de:

1. GitHub Issues
2. Correo electrónico: johansebastianrojasramirez7@gmail.com
3. Teléfono: +573214360157

## 📱 Contacto

Para soporte técnico o consultas:
- Email: johansebastianrojasramirez7@gmail.com
- Teléfono: +573214360157