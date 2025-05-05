# -*- coding: utf-8 -*-
"""Módulo para el diálogo de estadísticas."""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTabWidget, QWidget, QScrollArea
)
from PyQt6.QtCore import Qt
from datetime import datetime

class StatisticsDialog(QDialog):
    """Diálogo para mostrar estadísticas del sistema."""
    
    def __init__(self, person_database, access_logs, parent=None):
        """
        Inicializa el diálogo de estadísticas.
        
        Args:
            person_database (dict): Base de datos de personas
            access_logs (pd.DataFrame): Registros de acceso
            parent: Widget padre
        """
        super().__init__(parent)
        self.setWindowTitle("Estadísticas del Sistema")
        self.setMinimumSize(800, 600)
        self.person_database = person_database
        self.access_logs = access_logs
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout()
        
        # Agregar tabs para diferentes categorías de estadísticas
        tabs = QTabWidget()
        
        # Tab 1: Estadísticas Generales
        general_tab = QWidget()
        general_layout = QVBoxLayout(general_tab)
        
        general_stats = QLabel(self.generate_general_stats_html())
        general_stats.setTextFormat(Qt.TextFormat.RichText)
        general_stats.setWordWrap(True)
        general_stats.setStyleSheet("font-size: 14px; line-height: 1.5;")
        
        general_scroll = QScrollArea()
        general_scroll.setWidgetResizable(True)
        general_scroll.setWidget(general_stats)
        
        general_layout.addWidget(general_scroll)
        
        # Tab 2: Estadísticas por Facultad
        facultad_tab = QWidget()
        facultad_layout = QVBoxLayout(facultad_tab)
        
        facultad_stats = QLabel(self.generate_facultad_stats_html())
        facultad_stats.setTextFormat(Qt.TextFormat.RichText)
        facultad_stats.setWordWrap(True)
        facultad_stats.setStyleSheet("font-size: 14px; line-height: 1.5;")
        
        facultad_scroll = QScrollArea()
        facultad_scroll.setWidgetResizable(True)
        facultad_scroll.setWidget(facultad_stats)
        
        facultad_layout.addWidget(facultad_scroll)
        
        # Tab 3: Estadísticas por Rol
        rol_tab = QWidget()
        rol_layout = QVBoxLayout(rol_tab)
        
        rol_stats = QLabel(self.generate_rol_stats_html())
        rol_stats.setTextFormat(Qt.TextFormat.RichText)
        rol_stats.setWordWrap(True)
        rol_stats.setStyleSheet("font-size: 14px; line-height: 1.5;")
        
        rol_scroll = QScrollArea()
        rol_scroll.setWidgetResizable(True)
        rol_scroll.setWidget(rol_stats)
        
        rol_layout.addWidget(rol_scroll)
        
        # Tab 4: Estadísticas por Sede
        sede_tab = QWidget()
        sede_layout = QVBoxLayout(sede_tab)
        
        sede_stats = QLabel(self.generate_sede_stats_html())
        sede_stats.setTextFormat(Qt.TextFormat.RichText)
        sede_stats.setWordWrap(True)
        sede_stats.setStyleSheet("font-size: 14px; line-height: 1.5;")
        
        sede_scroll = QScrollArea()
        sede_scroll.setWidgetResizable(True)
        sede_scroll.setWidget(sede_stats)
        
        sede_layout.addWidget(sede_scroll)
        
        # Agregar todos los tabs
        tabs.addTab(general_tab, "General")
        tabs.addTab(facultad_tab, "Por Facultad")
        tabs.addTab(rol_tab, "Por Rol")
        tabs.addTab(sede_tab, "Por Sede")
        
        # Agregar tabs al layout principal
        layout.addWidget(tabs)
        
        # Botón para cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setMinimumHeight(40)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def generate_general_stats_html(self):
        """
        Genera el HTML para las estadísticas generales.
        
        Returns:
            str: HTML con las estadísticas generales
        """
        # Contar total de personas
        total_personas = len(self.person_database)
        
        # Contar accesos totales
        total_accesos = len(self.access_logs)
        
        # Accesos de hoy
        today = datetime.now().date()
        today_logs = self.access_logs[self.access_logs['Fecha'] == today] if not self.access_logs.empty else []
        accesos_hoy = len(today_logs)
        
        # Calcular confianza promedio
        if not self.access_logs.empty:
            avg_confidence = self.access_logs['Confianza'].mean()
            max_confidence = self.access_logs['Confianza'].max()
            min_confidence = self.access_logs['Confianza'].min()
        else:
            avg_confidence = max_confidence = min_confidence = 0
            
        # HTML para mostrar estadísticas
        return f"""
            <h2 style='color: #006633; text-align: center;'>Estadísticas Generales del Sistema</h2>
            
            <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                <h3>📊 Resumen General</h3>
                <p>• Total de Personas Registradas: <b>{total_personas}</b></p>
                <p>• Total de Accesos Registrados: <b>{total_accesos}</b></p>
                <p>• Accesos del Día de Hoy: <b>{accesos_hoy}</b></p>
            </div>
            
            <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                <h3>🔍 Métricas de Confianza</h3>
                <p>• Confianza Promedio: <b>{avg_confidence:.2f}%</b></p>
                <p>• Confianza Máxima: <b>{max_confidence:.2f}%</b></p>
                <p>• Confianza Mínima: <b>{min_confidence:.2f}%</b></p>
            </div>
            
            <div style='background-color: #F1F8E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                <h3>⚙️ Información del Sistema</h3>
                <p>• Fecha y Hora: <b>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</b></p>
            </div>
        """
    
    def generate_facultad_stats_html(self):
        """
        Genera el HTML para las estadísticas por facultad.
        
        Returns:
            str: HTML con las estadísticas por facultad
        """
        try:
            # Contar personas por facultad
            facultad_counts = {}
            for person_data in self.person_database.values():
                facultad = person_data['data'].facultad
                facultad_counts[facultad] = facultad_counts.get(facultad, 0) + 1
            
            # Calcular accesos por facultad
            facultad_accesos = {}
            if not self.access_logs.empty:
                facultad_accesos = self.access_logs.groupby('Facultad').size().to_dict()
            
            # HTML para mostrar estadísticas
            facultad_html = "<h2 style='color: #006633; text-align: center;'>Estadísticas por Facultad</h2>"
            
            if facultad_counts:
                facultad_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>📚 Distribución de Personas por Facultad</h3>
                        <ul>
                """
                
                for facultad, count in sorted(facultad_counts.items(), key=lambda x: x[1], reverse=True):
                    facultad_html += f"<li><b>{facultad}:</b> {count} personas</li>"
                    
                facultad_html += """
                        </ul>
                    </div>
                """
            
            if facultad_accesos:
                facultad_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>🚪 Distribución de Accesos por Facultad</h3>
                        <ul>
                """
                
                for facultad, count in sorted(facultad_accesos.items(), key=lambda x: x[1], reverse=True):
                    facultad_html += f"<li><b>{facultad}:</b> {count} accesos</li>"
                    
                facultad_html += """
                        </ul>
                    </div>
                """
                
            return facultad_html
        except Exception as e:
            print(f"Error al generar estadísticas de facultad: {str(e)}")
            return "<h3>Error al generar estadísticas</h3>"
    
    def generate_rol_stats_html(self):
        """
        Genera el HTML para las estadísticas por rol.
        
        Returns:
            str: HTML con las estadísticas por rol
        """
        try:
            # Contar personas por rol
            rol_counts = {}
            for person_data in self.person_database.values():
                rol = person_data['data'].rol
                rol_counts[rol] = rol_counts.get(rol, 0) + 1
            
            # Calcular accesos por rol
            rol_accesos = {}
            if not self.access_logs.empty:
                rol_accesos = self.access_logs.groupby('Rol').size().to_dict()
            
            # HTML para mostrar estadísticas
            rol_html = "<h2 style='color: #006633; text-align: center;'>Estadísticas por Rol</h2>"
            
            if rol_counts:
                rol_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>👥 Distribución de Personas por Rol</h3>
                        <ul>
                """
                
                for rol, count in sorted(rol_counts.items(), key=lambda x: x[1], reverse=True):
                    rol_html += f"<li><b>{rol}:</b> {count} personas</li>"
                    
                rol_html += """
                        </ul>
                    </div>
                """
            
            if rol_accesos:
                rol_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>🚪 Distribución de Accesos por Rol</h3>
                        <ul>
                """
                
                for rol, count in sorted(rol_accesos.items(), key=lambda x: x[1], reverse=True):
                    rol_html += f"<li><b>{rol}:</b> {count} accesos</li>"
                    
                rol_html += """
                        </ul>
                    </div>
                """
                
            return rol_html
        except Exception as e:
            print(f"Error al generar estadísticas de rol: {str(e)}")
            return "<h3>Error al generar estadísticas</h3>"
    
    def generate_sede_stats_html(self):
        """
        Genera el HTML para las estadísticas por sede.
        
        Returns:
            str: HTML con las estadísticas por sede
        """
        try:
            # Contar personas por sede
            sede_counts = {}
            for person_data in self.person_database.values():
                sede = person_data['data'].sede if person_data['data'].sede else "No especificada"
                sede_counts[sede] = sede_counts.get(sede, 0) + 1
            
            # Calcular accesos por sede
            sede_accesos = {}
            if not self.access_logs.empty and 'Sede' in self.access_logs.columns:
                # Manejar valores nulos en Sede
                self.access_logs['Sede'].fillna("No especificada", inplace=True)
                sede_accesos = self.access_logs.groupby('Sede').size().to_dict()
            
            # HTML para mostrar estadísticas
            sede_html = "<h2 style='color: #006633; text-align: center;'>Estadísticas por Sede</h2>"
            
            if sede_counts:
                sede_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>🏢 Distribución de Personas por Sede</h3>
                        <ul>
                """
                
                for sede, count in sorted(sede_counts.items(), key=lambda x: x[1], reverse=True):
                    sede_html += f"<li><b>{sede}:</b> {count} personas</li>"
                    
                sede_html += """
                        </ul>
                    </div>
                """
            
            if sede_accesos:
                sede_html += """
                    <div style='background-color: #E8F5E9; padding: 15px; border-radius: 8px; margin: 10px 0;'>
                        <h3>🚪 Distribución de Accesos por Sede</h3>
                        <ul>
                """
                
                for sede, count in sorted(sede_accesos.items(), key=lambda x: x[1], reverse=True):
                    sede_html += f"<li><b>{sede}:</b> {count} accesos</li>"
                    
                sede_html += """
                        </ul>
                    </div>
                """
                
            return sede_html
        except Exception as e:
            print(f"Error al generar estadísticas de sede: {str(e)}")
            return "<h3>Error al generar estadísticas</h3>"