# -*- coding: utf-8 -*-
"""Módulo para el diálogo de búsqueda de personas."""

import traceback
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QScrollArea, QFormLayout, QGroupBox, QMessageBox, QProgressDialog
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QImage

class SearchDialog(QDialog):
    """Diálogo para buscar personas en la base de datos."""
    
    def __init__(self, person_database, parent=None):
        """
        Inicializa el diálogo de búsqueda.
        
        Args:
            person_database (dict): Base de datos de personas
            parent: Widget padre
        """
        super().__init__(parent)
        self.setWindowTitle("Buscar Persona")
        self.setMinimumSize(700, 500)
        self.person_database = person_database
        self.setup_ui()
        
    def setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout()
        
        # Campo de búsqueda
        search_layout = QHBoxLayout()
        search_label = QLabel("Buscar:")
        search_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        self.search_input = QLineEdit()
        self.search_input.setMinimumHeight(35)
        self.search_input.setPlaceholderText("Nombre, ID, Facultad, Programa, etc...")
        self.search_input.returnPressed.connect(self.perform_search)
        
        search_button = QPushButton("🔍 Buscar")
        search_button.setMinimumHeight(35)
        search_button.clicked.connect(self.perform_search)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(search_button)
        
        # Tabla de resultados
        self.search_results = QTableWidget()
        self.search_results.setColumnCount(7)
        self.search_results.setHorizontalHeaderLabels([
            "Nombre", "ID", "Facultad", "Programa", "Rol", "Sede", "Tipo"
        ])
        self.search_results.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.search_results.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.search_results.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #E0E0E0;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                border: 1px solid #D3D3D3;
            }
        """)
        self.search_results.doubleClicked.connect(self.show_person_details)
        
        # Ajustar columnas
        header = self.search_results.horizontalHeader()
        for i in range(7):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
        
        # Botones
        button_layout = QHBoxLayout()
        
        details_button = QPushButton("Ver Detalles")
        details_button.setMinimumHeight(40)
        details_button.clicked.connect(self.show_person_details)
        
        edit_button = QPushButton("Editar")
        edit_button.setMinimumHeight(40)
        edit_button.clicked.connect(self.edit_person)
        
        delete_button = QPushButton("Eliminar")
        delete_button.setMinimumHeight(40)
        delete_button.clicked.connect(self.delete_person)
        
        close_button = QPushButton("Cerrar")
        close_button.setMinimumHeight(40)
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(details_button)
        button_layout.addWidget(edit_button)
        button_layout.addWidget(delete_button)
        button_layout.addWidget(close_button)
        
        # Armado del layout
        layout.addLayout(search_layout)
        layout.addWidget(self.search_results)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Inicialización con todos los registros
        self.search_input.setText("")
        self.perform_search()
        
    def perform_search(self):
        """Realiza la búsqueda en la base de datos."""
        try:
            search_text = self.search_input.text().lower()
            
            # Limpiar tabla
            self.search_results.setRowCount(0)
            
            # Mostrar diálogo de progreso si hay muchas personas
            if len(self.person_database) > 100:
                progress = QProgressDialog("Buscando personas...", "Cancelar", 0, len(self.person_database), self)
                progress.setWindowModality(Qt.WindowModality.WindowModal)
                progress.setMinimumDuration(0)
            else:
                progress = None
            
            row = 0
            for i, (person_name, data) in enumerate(self.person_database.items()):
                if progress:
                    progress.setValue(i)
                    if progress.wasCanceled():
                        break
                        
                person = data['data']
                
                # Si hay texto de búsqueda, filtrar
                if search_text:
                    # Buscar en todos los campos
                    if not (search_text in person.nombre.lower() or
                            search_text in person.id.lower() or
                            search_text in person.facultad.lower() or
                            search_text in person.programa.lower() or
                            search_text in person.rol.lower() or
                            search_text in (person.sede or "").lower() or
                            search_text in person.tipo.lower()):
                        continue
                
                # Agregar a la tabla
                self.search_results.insertRow(row)
                self.search_results.setItem(row, 0, QTableWidgetItem(person.nombre))
                self.search_results.setItem(row, 1, QTableWidgetItem(person.id))
                self.search_results.setItem(row, 2, QTableWidgetItem(person.facultad))
                self.search_results.setItem(row, 3, QTableWidgetItem(person.programa))
                self.search_results.setItem(row, 4, QTableWidgetItem(person.rol))
                self.search_results.setItem(row, 5, QTableWidgetItem(person.sede or ""))
                self.search_results.setItem(row, 6, QTableWidgetItem(person.tipo))
                
                row += 1
            
            if progress:
                progress.setValue(len(self.person_database))
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al realizar búsqueda: {str(e)}")
            traceback.print_exc()
    
    def show_person_details(self):
        """Muestra detalles de la persona seleccionada."""
        try:
            selected_rows = self.search_results.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Advertencia", "Por favor seleccione una persona para ver detalles")
                return
                
            # Obtener el nombre de la primera columna
            selected_row = selected_rows[0].row()
            person_name = self.search_results.item(selected_row, 0).text()
            
            # Buscar en la base de datos
            if person_name in self.person_database:
                person = self.person_database[person_name]['data']
                
                # Crear diálogo de detalles
                details_dialog = QDialog(self)
                details_dialog.setWindowTitle(f"Detalles: {person.nombre}")
                details_dialog.setMinimumSize(600, 400)
                
                layout = QVBoxLayout()
                
                # Información personal
                info_group = QGroupBox("Información Personal")
                info_layout = QFormLayout()
                
                # Crear etiquetas con la información
                info_layout.addRow("<b>Nombre:</b>", QLabel(person.nombre))
                info_layout.addRow("<b>ID/Código:</b>", QLabel(person.id))
                info_layout.addRow("<b>Rol:</b>", QLabel(person.rol))
                info_layout.addRow("<b>Tipo de Acceso:</b>", QLabel(person.tipo))
                info_layout.addRow("<b>Facultad:</b>", QLabel(person.facultad))
                info_layout.addRow("<b>Programa:</b>", QLabel(person.programa))
                info_layout.addRow("<b>Sede:</b>", QLabel(person.sede or "No especificada"))
                info_layout.addRow("<b>Extensión:</b>", QLabel(person.extension or "No especificada"))
                if person.semestre:
                    info_layout.addRow("<b>Semestre:</b>", QLabel(person.semestre))
                info_layout.addRow("<b>Fecha de Registro:</b>", QLabel(person.fecha_registro))
                
                # Estilo para las etiquetas
                for i in range(info_layout.rowCount()):
                    label_item = info_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
                    if label_item:
                        label_widget = label_item.widget()
                        if label_widget:
                            label_widget.setStyleSheet("font-size: 14px;")
                    
                    field_item = info_layout.itemAt(i, QFormLayout.ItemRole.FieldRole)
                    if field_item:
                        field_widget = field_item.widget()
                        if field_widget:
                            field_widget.setStyleSheet("font-size: 14px; font-weight: bold;")
                
                info_group.setLayout(info_layout)
                layout.addWidget(info_group)
                
                # Botones
                button_layout = QHBoxLayout()
                
                edit_btn = QPushButton("Editar")
                edit_btn.setMinimumHeight(40)
                edit_btn.clicked.connect(lambda: self.edit_person(person_name))
                edit_btn.clicked.connect(details_dialog.accept)
                
                delete_btn = QPushButton("Eliminar")
                delete_btn.setMinimumHeight(40)
                delete_btn.clicked.connect(lambda: self.delete_person(person_name))
                delete_btn.clicked.connect(details_dialog.accept)
                
                close_btn = QPushButton("Cerrar")
                close_btn.setMinimumHeight(40)
                close_btn.clicked.connect(details_dialog.accept)
                
                button_layout.addWidget(edit_btn)
                button_layout.addWidget(delete_btn)
                button_layout.addWidget(close_btn)
                
                layout.addLayout(button_layout)
                
                details_dialog.setLayout(layout)
                details_dialog.exec()
            else:
                QMessageBox.warning(self, "Error", "Persona no encontrada en la base de datos")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al mostrar detalles: {str(e)}")
            traceback.print_exc()
    
    def edit_person(self, person_name=None):
        """
        Abre el diálogo de registro para editar a una persona existente.
        
        Args:
            person_name (str, optional): Nombre de la persona a editar
        """
        # Si no se proporciona un nombre, usar el seleccionado en la tabla
        if person_name is None:
            selected_rows = self.search_results.selectedItems()
            if not selected_rows:
                QMessageBox.warning(self, "Advertencia", "Por favor seleccione una persona para editar")
                return
                
            selected_row = selected_rows[0].row()
            person_name = self.search_results.item(selected_row, 0).text()
        
        # Verificar que existe en la base de datos
        if person_name not in self.person_database:
            QMessageBox.warning(self, "Error", "Persona no encontrada en la base de datos")
            return
        
        # Hacer lógica para editar (implementación pendiente)
        QMessageBox.information(
            self, "Información",
            "La funcionalidad de edición será implementada en una próxima actualización"
        )
    
    def delete_person(self, person_name=None):
        """
        Elimina una persona de la base de datos.
        
        Args:
            person_name (str, optional): Nombre de la persona a eliminar
        """
        # Esta función se delega al padre (la ventana principal)
        if self.parent():
            self.parent().delete_person(person_name)
            self.perform_search()  # Actualizar la tabla después de eliminar
        else:
            QMessageBox.warning(self, "Error", "No se puede eliminar: sin acceso a la ventana principal")