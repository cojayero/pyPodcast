#!/usr/bin/env python3
"""
Demo completo de la funcionalidad de eliminación avanzada de fuentes de datos
"""

import sys
import os
from pathlib import Path

# Añadir el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import Qt

from models.database import DatabaseManager
from app.widgets.data_source_widget import DataSourceWidget
from utils.logger import get_logger

logger = get_logger(__name__)

class DemoMainWindow(QMainWindow):
    """Ventana principal de demostración"""
    
    def __init__(self):
        super().__init__()
        self.db_manager = DatabaseManager()
        self.setup_ui()
        self.init_database()
    
    def setup_ui(self):
        """Configura la interfaz principal"""
        self.setWindowTitle("Demo - Eliminación Avanzada de Fuentes de Datos")
        self.setGeometry(100, 100, 900, 700)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("🗑️ Demo: Eliminación Avanzada de Fuentes de Datos")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px; color: #d32f2f;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Instrucciones
        instructions = QLabel("""
📝 Instrucciones:
1. Use el botón "Crear Datos de Prueba" para añadir fuentes con contenido simulado
2. Seleccione una fuente de la lista
3. Haga clic en "Eliminar" para probar la funcionalidad de eliminación avanzada
4. Observe cómo el diálogo muestra toda la información detallada
5. Confirme con el checkbox para activar el botón de eliminación

✨ Características demostradas:
• Análisis previo de contenido a eliminar
• Diálogo de confirmación detallado con scroll
• Estimación de espacio liberado
• Lista de archivos específicos
• Eliminación segura con manejo de errores
• Reporte final de lo eliminado
        """)
        instructions.setStyleSheet("padding: 15px; background-color: #f0f7ff; border: 1px solid #0078d4; border-radius: 8px; margin: 10px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Botón para crear datos de prueba
        self.create_data_button = QPushButton("🔧 Crear Datos de Prueba")
        self.create_data_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.create_data_button.clicked.connect(self.create_test_data)
        layout.addWidget(self.create_data_button)
        
        # Widget de fuentes de datos
        self.data_source_widget = DataSourceWidget()
        layout.addWidget(self.data_source_widget)
        
        central_widget.setLayout(layout)
    
    def init_database(self):
        """Inicializa la base de datos"""
        try:
            self.db_manager.initialize_database()
            logger.info("Base de datos inicializada para demo")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error inicializando base de datos: {e}")
    
    def create_test_data(self):
        """Crea datos de prueba para la demostración"""
        try:
            # Crear múltiples fuentes de prueba con diferentes características
            test_sources = [
                {
                    'name': 'Canal YouTube de Prueba',
                    'type': 'youtube',
                    'url': 'https://www.youtube.com/channel/UC_test_channel',
                    'description': 'Canal de YouTube para demostrar eliminación con muchos contenidos'
                },
                {
                    'name': 'Feed RSS de Noticias',
                    'type': 'rss',
                    'url': 'https://feeds.example.com/news.xml',
                    'description': 'RSS con pocos elementos para probar eliminación simple'
                },
                {
                    'name': 'Página Web Corporativa',
                    'type': 'web',
                    'url': 'https://empresa.ejemplo.com/blog',
                    'description': 'Fuente web con contenido variado y archivos de audio'
                }
            ]
            
            created_sources = []
            
            for i, source_data in enumerate(test_sources):
                # Crear fuente
                source_id = self.db_manager.add_data_source(
                    name=source_data['name'],
                    source_type=source_data['type'],
                    url=source_data['url'],
                    description=source_data['description']
                )
                
                created_sources.append(source_id)
                
                # Crear diferentes cantidades de contenido según la fuente
                content_counts = [8, 3, 12]  # YouTube, RSS, Web
                content_count = content_counts[i]
                
                for j in range(content_count):
                    content_title = f"Contenido {j+1} de {source_data['name']}"
                    content_url = f"{source_data['url']}/item{j+1}"
                    
                    # Crear contenido variado
                    content_text = f"""Este es el contenido {j+1} de la fuente {source_data['name']}.
                    
Este contenido simula un artículo real con múltiples párrafos para demostrar
cómo la funcionalidad de eliminación maneja diferentes tipos de contenido.

El contenido incluye texto extraído, resúmenes generados automáticamente,
y archivos de audio sintetizados a partir del texto.

Párrafo adicional para hacer el contenido más sustancial y realista.
Este tipo de contenido es típico en un sistema de podcasts automatizado."""
                    
                    item_id = self.db_manager.add_content_item(
                        source_id=source_id,
                        title=content_title,
                        url=content_url,
                        description=f"Descripción del {content_title}",
                        content=content_text
                    )
                    
                    if item_id:
                        # Simular archivos de audio (algunos items)
                        if j % 2 == 0:  # Solo la mitad tienen audio
                            audio_file = f"podcasts/source_{source_id}/audio_{item_id}.wav"
                            summary = f"Resumen automático del {content_title}..."
                            self.db_manager.update_content_item_files(item_id, summary=summary, audio_file=audio_file)
                        
                        # Simular logs de procesamiento
                        self.db_manager.log_processing_action(
                            item_id, "text_extraction", "success", "Texto extraído exitosamente"
                        )
                        
                        if j % 2 == 0:
                            self.db_manager.log_processing_action(
                                item_id, "tts_generation", "success", "Audio generado con TTS"
                            )
                            self.db_manager.log_processing_action(
                                item_id, "audio_optimization", "success", "Audio optimizado"
                            )
                        else:
                            self.db_manager.log_processing_action(
                                item_id, "tts_generation", "skipped", "Audio no requerido"
                            )
            
            # Recargar la lista de fuentes
            self.data_source_widget.load_data_sources()
            
            # Mostrar resumen
            total_items = sum([8, 3, 12])
            total_audio = sum([4, 2, 6])  # La mitad de cada fuente
            
            QMessageBox.information(self, "Datos de Prueba Creados", 
                f"""✅ Datos de prueba creados exitosamente:

📝 Fuentes creadas: {len(test_sources)}
📄 Items de contenido: {total_items}
🎵 Archivos de audio simulados: {total_audio}
📊 Registros de procesamiento: {total_items * 2}

Ahora puede seleccionar cualquier fuente y probar la eliminación avanzada.

💡 Tip: Pruebe eliminar fuentes con diferentes cantidades de contenido
para ver cómo cambia la información en el diálogo.""")
            
            logger.info(f"Datos de prueba creados: {len(created_sources)} fuentes")
            
        except ValueError as e:
            QMessageBox.warning(self, "Advertencia", 
                f"Algunos datos ya existen: {e}\n\nPuede proceder con las fuentes existentes.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creando datos de prueba: {e}")
            logger.error(f"Error en create_test_data: {e}")

def main():
    """Función principal de la demo"""
    app = QApplication(sys.argv)
    
    # Configurar logging básico
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Mostrar ventana principal
    window = DemoMainWindow()
    window.show()
    
    return app.exec()

if __name__ == "__main__":
    print("🚀 Iniciando demo de eliminación avanzada de fuentes de datos...")
    print("📱 La ventana de la aplicación se abrirá en un momento...")
    sys.exit(main())
