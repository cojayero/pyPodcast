#!/usr/bin/env python3
"""
Script de prueba mínima para el checkbox y botón
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QDialog, QVBoxLayout, QCheckBox, QPushButton, QLabel
from PySide6.QtCore import Qt

class SimpleTestDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Test Checkbox/Button")
        self.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        
        # Label explicativo
        label = QLabel("Prueba del checkbox y botón:")
        layout.addWidget(label)
        
        # Checkbox
        self.checkbox = QCheckBox("Confirmo que entiendo")
        self.checkbox.stateChanged.connect(self.on_checkbox_changed)
        layout.addWidget(self.checkbox)
        
        # Botón
        self.button = QPushButton("Botón de Acción")
        self.button.setEnabled(False)
        self.button.setStyleSheet("""
            QPushButton:enabled {
                background-color: green;
                color: white;
            }
            QPushButton:disabled {
                background-color: #ccc;
                color: #666;
            }
        """)
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)
        
        # Status label
        self.status_label = QLabel("Estado: Botón deshabilitado")
        layout.addWidget(self.status_label)
        
        self.setLayout(layout)
        
        print("Diálogo creado")
    
    def on_checkbox_changed(self, state):
        print(f"Checkbox cambió: {state}")
        enabled = state == 2  # 2 = checked
        self.button.setEnabled(enabled)
        
        if enabled:
            self.status_label.setText("Estado: Botón habilitado ✅")
        else:
            self.status_label.setText("Estado: Botón deshabilitado ❌")

class TestApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
    
    def run(self):
        dialog = SimpleTestDialog()
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            print("✅ Diálogo aceptado")
        else:
            print("❌ Diálogo cancelado")
        
        return 0

if __name__ == "__main__":
    test_app = TestApp()
    sys.exit(test_app.run())
