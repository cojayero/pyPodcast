#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de edición de contenido
"""

import sys
import os
from pathlib import Path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QLabel
from PySide6.QtCore import Qt
import datetime

from models.database import DatabaseManager
from models.content_item import ContentItem
from app.dialogs.content_edit_dialog import ContentEditDialog

class TestEditWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba: Edición de Contenido")
        self.setGeometry(100, 100, 400, 300)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Etiqueta
        label = QLabel("Prueba de la funcionalidad de edición de contenido de items")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Botón para crear item de prueba
        self.create_btn = QPushButton("Crear Item de Prueba")
        self.create_btn.clicked.connect(self.create_test_item)
        layout.addWidget(self.create_btn)
        
        # Botón para editar último item
        self.edit_btn = QPushButton("Editar Último Item")
        self.edit_btn.clicked.connect(self.edit_last_item)
        self.edit_btn.setEnabled(False)
        layout.addWidget(self.edit_btn)
        
        # Estado
        self.status_label = QLabel("Listo para crear item de prueba")
        layout.addWidget(self.status_label)
        
        self.db_manager = DatabaseManager()
        self.last_item_id = None
        
        # Verificar si hay items existentes
        self.check_existing_items()
    
    def check_existing_items(self):
        """Verifica si hay items existentes para editar"""
        try:
            # Obtener el último item
            items = self.db_manager.get_content_items()
            if items:
                self.last_item_id = items[0]['id']  # Primer item (más reciente)
                self.edit_btn.setEnabled(True)
                self.status_label.setText(f"Hay {len(items)} items disponibles para editar")
        except Exception as e:
            self.status_label.setText(f"Error verificando items: {e}")
    
    def create_test_item(self):
        """Crea un item de prueba para editar"""
        try:
            # Crear item de prueba
            test_content = """
            Este es un contenido de prueba para la funcionalidad de edición.
            
            El sistema de podcasts permite extraer contenido de diversas fuentes como YouTube, 
            feeds RSS y páginas web, y convertirlo automáticamente en podcasts de audio usando 
            síntesis de voz.
            
            Características principales:
            - Extracción automática de contenido
            - Conversión texto a voz con voces naturales
            - Gestión de múltiples fuentes de datos
            - Reproductor embebido para escuchar podcasts
            - Base de datos SQLite para almacenar información
            
            Esta funcionalidad de edición permite personalizar el contenido antes de generar 
            el audio final, dando control total sobre qué se incluye en el podcast.
            """
            
            test_item = ContentItem(
                id=None,
                source_id=1,  # Asumiendo que existe una fuente con ID 1
                title="Item de Prueba - Edición de Contenido",
                url="https://ejemplo.com/test",
                description="Item creado para probar la funcionalidad de edición de contenido",
                content=test_content,
                summary=test_content[:200] + "...",
                status='nuevo',
                created_at=datetime.datetime.now(),
                source_name="Prueba",
                source_type="test"
            )
            
            # Insertar en base de datos
            item_id = self.db_manager.insert_content_item(test_item)
            self.last_item_id = item_id
            
            self.status_label.setText(f"✅ Item de prueba creado con ID: {item_id}")
            self.edit_btn.setEnabled(True)
            
        except Exception as e:
            self.status_label.setText(f"❌ Error creando item: {e}")
    
    def edit_last_item(self):
        """Abre el editor para el último item"""
        if not self.last_item_id:
            self.status_label.setText("No hay item para editar")
            return
        
        try:
            # Obtener el item de la base de datos
            items = self.db_manager.get_content_items()
            target_item = None
            
            for item_data in items:
                if item_data['id'] == self.last_item_id:
                    # Convertir a ContentItem
                    target_item = ContentItem(
                        id=item_data['id'],
                        source_id=item_data['source_id'],
                        title=item_data['title'],
                        url=item_data['url'],
                        description=item_data.get('description'),
                        content=item_data.get('content'),
                        summary=item_data.get('summary'),
                        audio_file=item_data.get('audio_file'),
                        status=item_data.get('status', 'nuevo'),
                        created_at=item_data.get('created_at'),
                        source_name=item_data.get('source_name'),
                        source_type=item_data.get('source_type')
                    )
                    break
            
            if not target_item:
                self.status_label.setText("Item no encontrado")
                return
            
            # Abrir diálogo de edición
            dialog = ContentEditDialog(target_item, self)
            dialog.content_updated.connect(self.on_content_updated)
            result = dialog.exec()
            
            if result:
                self.status_label.setText("✅ Contenido editado exitosamente")
            else:
                self.status_label.setText("Edición cancelada")
                
        except Exception as e:
            self.status_label.setText(f"❌ Error abriendo editor: {e}")
    
    def on_content_updated(self, item_id: int):
        """Se ejecuta cuando se actualiza el contenido"""
        self.status_label.setText(f"✅ Item {item_id} actualizado correctamente")

def main():
    app = QApplication(sys.argv)
    
    window = TestEditWindow()
    window.show()
    
    print("=== PRUEBA DE EDICIÓN DE CONTENIDO ===")
    print("1. Haz clic en 'Crear Item de Prueba' para crear un item de ejemplo")
    print("2. Haz clic en 'Editar Último Item' para abrir el editor")
    print("3. En el editor puedes:")
    print("   - Ver el contenido original (lado izquierdo)")
    print("   - Editar el contenido para audio (lado derecho)")
    print("   - Generar un preview de audio")
    print("   - Guardar cambios y opcionalmente regenerar audio")
    print("4. Prueba las diferentes funciones del editor")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
