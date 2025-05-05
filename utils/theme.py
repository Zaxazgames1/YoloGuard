# -*- coding: utf-8 -*-
"""Módulo para gestionar el tema de la aplicación."""

class UCundinamarcaTheme:
    """Clase que define el tema visual de la Universidad de Cundinamarca."""
    
    PRIMARY = "#006633"  # Verde Institucional
    SECONDARY = "#004d25"  # Verde más oscuro
    ACCENT = "#00802b"  # Verde más claro
    BG_DARK = "#263238"
    BG_LIGHT = "#FFFFFF"
    TEXT_LIGHT = "#FFFFFF"
    TEXT_DARK = "#333333"
    SUCCESS = "#009900"  # Verde éxito
    WARNING = "#FFCC00"  # Amarillo advertencia
    DANGER = "#CC0000"  # Rojo error
    
    @staticmethod
    def get_style():
        """Devuelve el estilo CSS para la aplicación."""
        return """
            QMainWindow, QDialog {
                background-color: #f5f5f5;
            }
            QMenuBar {
                background-color: """ + UCundinamarcaTheme.PRIMARY + """;
                color: """ + UCundinamarcaTheme.TEXT_LIGHT + """;
                padding: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 6px 12px;
            }
            QMenuBar::item:selected {
                background-color: """ + UCundinamarcaTheme.SECONDARY + """;
            }
            QPushButton {
                background-color: """ + UCundinamarcaTheme.PRIMARY + """;
                color: """ + UCundinamarcaTheme.TEXT_LIGHT + """;
                border: none;
                padding: 10px 16px;
                border-radius: 4px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: """ + UCundinamarcaTheme.SECONDARY + """;
            }
            QPushButton:pressed {
                background-color: #003519;
            }
            QLabel {
                color: """ + UCundinamarcaTheme.TEXT_DARK + """;
                font-size: 14px;
            }
            QGroupBox {
                border: 2px solid """ + UCundinamarcaTheme.PRIMARY + """;
                border-radius: 6px;
                margin-top: 1em;
                font-size: 14px;
                font-weight: bold;
            }
            QGroupBox::title {
                color: """ + UCundinamarcaTheme.PRIMARY + """;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
                font-size: 14px;
                font-weight: bold;
            }
            QComboBox {
                padding: 8px 12px;
                border: 1px solid #CCC;
                border-radius: 4px;
                min-height: 28px;
                font-size: 14px;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: #CCC;
                border-left-style: solid;
            }
            QComboBox QAbstractItemView {
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #CCC;
                border-radius: 4px;
                font-size: 14px;
            }
            QTextEdit {
                font-size: 14px;
                line-height: 1.5;
            }
            QTabWidget::pane {
                border: 1px solid #CCC;
                border-radius: 4px;
                background-color: #FFF;
            }
            QTabBar::tab {
                background-color: #F0F0F0;
                border: 1px solid #CCC;
                border-bottom-color: #CCC;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                min-width: 8ex;
                padding: 10px 16px;
                font-size: 14px;
                font-weight: bold;
            }
            QTabBar::tab:selected {
                background-color: """ + UCundinamarcaTheme.PRIMARY + """;
                color: """ + UCundinamarcaTheme.TEXT_LIGHT + """;
            }
            QStatusBar {
                background-color: #F5F5F5;
                color: #333;
                font-size: 13px;
            }
            QTableWidget {
                font-size: 14px;
                gridline-color: #DDD;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QTableWidget QHeaderView {
                background-color: #E0E0E0;
                font-size: 14px;
                font-weight: bold;
            }
            QTableWidget QHeaderView::section {
                background-color: #E0E0E0;
                padding: 5px;
                border: 1px solid #DDD;
                font-size: 14px;
                font-weight: bold;
            }
            QScrollBar:vertical {
                border: none;
                background: #F0F0F0;
                width: 12px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #CCC;
                min-height: 20px;
                border-radius: 6px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
        """