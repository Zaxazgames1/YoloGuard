# -*- coding: utf-8 -*-
"""Módulo para gestionar los registros de acceso."""

import pandas as pd
from datetime import datetime

class AccessLogManager:
    """Clase para gestionar los registros de acceso."""
    
    def __init__(self):
        """Inicializa el gestor de registros de acceso."""
        self.access_logs = pd.DataFrame(columns=[
            'Fecha', 'Hora', 'ID', 'Nombre', 'Facultad', 
            'Programa', 'Rol', 'Tipo_Acceso', 'Sede', 'Extension', 'Semestre', 'Confianza'
        ])
        
    def log_access(self, identity, confidence, logger=None):
        """
        Registra un nuevo acceso.
        
        Args:
            identity: Objeto UniversityPersonData con los datos de la persona
            confidence: Nivel de confianza del reconocimiento
            logger: Logger para registrar mensajes
            
        Returns:
            pd.DataFrame: DataFrame actualizado con los registros
        """
        try:
            now = datetime.now()
            new_log = pd.DataFrame([{
                'Fecha': now.date(),
                'Hora': now.strftime("%H:%M:%S"),
                'ID': identity.id,
                'Nombre': identity.nombre,
                'Facultad': identity.facultad,
                'Programa': identity.programa,
                'Rol': identity.rol,
                'Tipo_Acceso': identity.tipo,
                'Sede': identity.sede,
                'Extension': identity.extension,
                'Semestre': identity.semestre,
                'Confianza': confidence
            }])
            
            self.access_logs = pd.concat([self.access_logs, new_log], ignore_index=True)
            
            # Limitar el tamaño de logs para evitar consumo excesivo de memoria
            if len(self.access_logs) > 10000:
                self.access_logs = self.access_logs.iloc[-10000:]
            
            if logger:
                logger.log_message(
                    f"✅ Acceso: {identity.nombre} ({identity.rol}) - Sede: {identity.sede or 'N/A'} - {confidence:.1f}%"
                )
            
            return self.access_logs
        except Exception as e:
            if logger:
                logger.log_message(f"❌ Error al registrar acceso: {str(e)}")
            return self.access_logs
            
    def generate_report(self, filename, logger=None):
        """
        Genera un informe de accesos.
        
        Args:
            filename (str): Ruta del archivo donde guardar el informe
            logger: Logger para registrar mensajes
            
        Returns:
            bool: True si el informe se generó correctamente, False en caso contrario
        """
        try:
            if filename.endswith('.xlsx'):
                # Crear un informe más detallado para Excel
                writer = pd.ExcelWriter(filename, engine='openpyxl')
                
                # Hoja 1: Todos los accesos
                self.access_logs.to_excel(writer, sheet_name='Todos los Accesos', index=False)
                
                # Hoja 2: Accesos de hoy
                today = datetime.now().date()
                today_logs = self.access_logs[self.access_logs['Fecha'] == today]
                if not today_logs.empty:
                    today_logs.to_excel(writer, sheet_name='Accesos de Hoy', index=False)
                
                # Hoja 3: Estadísticas por facultad
                if not self.access_logs.empty:
                    facultad_stats = self.access_logs.groupby('Facultad').agg({
                        'ID': 'count',
                        'Confianza': ['mean', 'min', 'max']
                    })
                    facultad_stats.columns = ['Total Accesos', 'Confianza Media', 'Confianza Mínima', 'Confianza Máxima']
                    facultad_stats.reset_index().to_excel(writer, sheet_name='Estadísticas por Facultad', index=False)
                
                # Hoja 4: Estadísticas por rol
                if not self.access_logs.empty:
                    rol_stats = self.access_logs.groupby('Rol').agg({
                        'ID': 'count',
                        'Confianza': ['mean', 'min', 'max']
                    })
                    rol_stats.columns = ['Total Accesos', 'Confianza Media', 'Confianza Mínima', 'Confianza Máxima']
                    rol_stats.reset_index().to_excel(writer, sheet_name='Estadísticas por Rol', index=False)
                
                # Hoja 5: Estadísticas por sede
                if not self.access_logs.empty and 'Sede' in self.access_logs.columns:
                    self.access_logs['Sede'].fillna("No especificada", inplace=True)
                    sede_stats = self.access_logs.groupby('Sede').agg({
                        'ID': 'count',
                        'Confianza': ['mean', 'min', 'max']
                    })
                    sede_stats.columns = ['Total Accesos', 'Confianza Media', 'Confianza Mínima', 'Confianza Máxima']
                    sede_stats.reset_index().to_excel(writer, sheet_name='Estadísticas por Sede', index=False)
                
                writer.close()
            else:
                # Formato CSV simple
                self.access_logs.to_csv(filename, index=False)
                
            if logger:
                logger.log_message(f"✅ Reporte guardado en: {filename}")
            
            return True
                
        except Exception as e:
            if logger:
                logger.log_message(f"❌ Error al generar reporte: {str(e)}")
            return False

    def export_statistics(self, filename, logger=None):
        """
        Exporta estadísticas de acceso a Excel.
        
        Args:
            filename (str): Ruta del archivo donde guardar las estadísticas
            logger: Logger para registrar mensajes
            
        Returns:
            bool: True si las estadísticas se exportaron correctamente, False en caso contrario
        """
        try:
            writer = pd.ExcelWriter(filename, engine='openpyxl')
            
            # Hoja 1: Estadísticas Generales
            general_stats = pd.DataFrame({
                'Métrica': [
                    'Total Accesos', 'Accesos Hoy',
                    'Confianza Promedio', 'Confianza Máxima', 'Confianza Mínima'
                ],
                'Valor': [
                    len(self.access_logs),
                    len(self.access_logs[self.access_logs['Fecha'] == datetime.now().date()]),
                    self.access_logs['Confianza'].mean() if not self.access_logs.empty else 0,
                    self.access_logs['Confianza'].max() if not self.access_logs.empty else 0,
                    self.access_logs['Confianza'].min() if not self.access_logs.empty else 0
                ]
            })
            general_stats.to_excel(writer, sheet_name='Estadísticas Generales', index=False)
            
            # Hoja 2: Estadísticas por Facultad
            if not self.access_logs.empty:
                facultad_counts = self.access_logs.groupby('Facultad').size().reset_index(name='Cantidad')
                facultad_counts.to_excel(writer, sheet_name='Por Facultad', index=False)
            
            # Hoja 3: Estadísticas por Rol
            if not self.access_logs.empty:
                rol_counts = self.access_logs.groupby('Rol').size().reset_index(name='Cantidad')
                rol_counts.to_excel(writer, sheet_name='Por Rol', index=False)
            
            # Hoja 4: Estadísticas por Sede
            if not self.access_logs.empty and 'Sede' in self.access_logs.columns:
                self.access_logs['Sede'].fillna("No especificada", inplace=True)
                sede_counts = self.access_logs.groupby('Sede').size().reset_index(name='Cantidad')
                sede_counts.to_excel(writer, sheet_name='Por Sede', index=False)
            
            writer.close()
            
            if logger:
                logger.log_message(f"✅ Estadísticas exportadas a: {filename}")
            
            return True
            
        except Exception as e:
            if logger:
                logger.log_message(f"❌ Error al exportar estadísticas: {str(e)}")
            return False