#!/usr/bin/env python3
"""
Script de prueba simple para el diálogo de confirmación de eliminación
"""

import sys
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QDialog
from app.dialogs.delete_confirmation_dialog import DeleteConfirmationDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba Diálogo de Eliminación")
        self.setGeometry(100, 100, 300, 200)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        button = QPushButton("Mostrar Diálogo de Eliminación")
        button.clicked.connect(self.show_dialog)
        layout.addWidget(button)
        
        central_widget.setLayout(layout)
    
    def show_dialog(self):
        # Crear datos de prueba
        deletion_info = {
            'source_name': 'Fuente de Prueba',
            'source_type': 'youtube',
            'source_url': 'https://www.youtube.com/channel/test',
            'total_items': 5,
            'audio_files_count': 3,
            'audio_file_paths': [
                'audio1.wav',
                'audio2.wav', 
                'audio3.wav'
            ],
            'processing_logs': 10
        }
        
        dialog = DeleteConfirmationDialog(deletion_info, self)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            print("✅ Usuario confirmó la eliminación")
        else:
            print("❌ Usuario canceló la eliminación")

def main():
    app = QApplication(sys.argv)
    
    window = TestWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())
