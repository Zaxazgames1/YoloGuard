# -*- coding: utf-8 -*-
"""Módulo para la gestión de logs."""

from datetime import datetime
from PyQt6.QtWidgets import QTextEdit, QFileDialog
from PyQt6.QtGui import QTextCharFormat, QColor, QTextCursor
from config.constants import MAX_LOG_ENTRIES

class Logger:
    """Clase para gestionar logs de la aplicación."""
    
    def __init__(self, log_widget=None):
        """
        Inicializa el logger.
        
        Args:
            log_widget (QTextEdit): Widget donde mostrar los logs
        """
        self.log_widget = log_widget
        
    def set_log_widget(self, log_widget):
        """
        Establece el widget de log.
        
        Args:
            log_widget (QTextEdit): Widget donde mostrar los logs
        """
        self.log_widget = log_widget
        
    def log_message(self, message):
        """
        Registra un mensaje en el log.
        
        Args:
            message (str): Mensaje a registrar
        """
        try:
            if not self.log_widget:
                print(message)
                return
                
            timestamp = datetime.now().strftime("%H:%M:%S")
            self.log_widget.append(f"[{timestamp}] {message}")
            
            # Mantener el tamaño del log limitado
            log_content = self.log_widget.toPlainText()
            lines = log_content.split('\n')
            if len(lines) > MAX_LOG_ENTRIES:
                # Mantener solo las últimas MAX_LOG_ENTRIES líneas
                truncated_log = '\n'.join(lines[-MAX_LOG_ENTRIES:])
                self.log_widget.setPlainText(truncated_log)
            
            # Desplazar al final
            scrollbar = self.log_widget.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
        except Exception as e:
            print(f"Error al registrar mensaje en log: {str(e)}")
            
    def clear_log(self):
        """Limpia el log."""
        if self.log_widget:
            self.log_widget.clear()
            self.log_message("Log limpiado")
            
    def save_log(self, parent_widget=None):
        """
        Guarda el log en un archivo de texto.
        
        Args:
            parent_widget: Widget padre para mostrar el diálogo de guardar
            
        Returns:
            bool: True si el log se guardó correctamente, False en caso contrario
        """
        try:
            if not self.log_widget:
                return False
                
            filename, _ = QFileDialog.getSaveFileName(
                parent_widget, "Guardar Log", "", 
                "Archivos de texto (*.txt);;Todos los archivos (*.*)"
            )
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(self.log_widget.toPlainText())
                self.log_message(f"✅ Log guardado en {filename}")
                return True
            return False
        except Exception as e:
            error_msg = f"Error al guardar log: {str(e)}"
            self.log_message(f"❌ {error_msg}")
            return False
            
    def search_log(self, search_text, search_input=None):
        """
        Busca texto en el log.
        
        Args:
            search_text (str): Texto a buscar
            search_input: Entrada de texto para mostrar el texto buscado
            
        Returns:
            bool: True si se encontró el texto, False en caso contrario
        """
        try:
            if not self.log_widget or not search_text:
                return False
                
            search_text = search_text.lower()
            log_content = self.log_widget.toPlainText()
            cursor = self.log_widget.textCursor()
            
            # Formato para resaltar resultados
            format = QTextCharFormat()
            format.setBackground(QColor(255, 255, 0))  # Amarillo
            
            # Reiniciar formato
            cursor.select(QTextCursor.SelectionType.Document)
            cursor.setCharFormat(QTextCharFormat())
            cursor.clearSelection()
            
            # Buscar y resaltar
            found = False
            pos = 0
            while True:
                pos = log_content.lower().find(search_text, pos)
                if pos < 0:
                    break
                    
                cursor.setPosition(pos)
                cursor.setPosition(pos + len(search_text), QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(format)
                cursor.clearSelection()
                
                pos += len(search_text)
                found = True
                
            return found
        except Exception as e:
            print(f"Error al buscar en el log: {str(e)}")
            return False