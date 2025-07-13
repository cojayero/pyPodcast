#!/usr/bin/env python3
"""
Script de prueba para la funcionalidad de análisis de contenido
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
from app.dialogs.content_analysis_dialog import ContentAnalysisDialog
from services.content_analyzer import ContentAnalyzer

class TestAnalysisWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Prueba: Análisis de Contenido")
        self.setGeometry(100, 100, 500, 400)
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Etiqueta
        label = QLabel("Prueba de análisis inteligente de contenido y generación de resúmenes")
        label.setWordWrap(True)
        layout.addWidget(label)
        
        # Botón para crear item de prueba con contenido largo
        self.create_long_btn = QPushButton("Crear Item con Contenido Largo")
        self.create_long_btn.clicked.connect(self.create_long_content_item)
        layout.addWidget(self.create_long_btn)
        
        # Botón para crear item de prueba con contenido técnico
        self.create_tech_btn = QPushButton("Crear Item con Contenido Técnico")
        self.create_tech_btn.clicked.connect(self.create_tech_content_item)
        layout.addWidget(self.create_tech_btn)
        
        # Botón para analizar último item
        self.analyze_btn = QPushButton("Analizar Último Item")
        self.analyze_btn.clicked.connect(self.analyze_last_item)
        self.analyze_btn.setEnabled(False)
        layout.addWidget(self.analyze_btn)
        
        # Botón para prueba de análisis directo
        self.direct_test_btn = QPushButton("Prueba de Análisis Directo")
        self.direct_test_btn.clicked.connect(self.test_direct_analysis)
        layout.addWidget(self.direct_test_btn)
        
        # Estado
        self.status_label = QLabel("Listo para crear items de prueba")
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        self.db_manager = DatabaseManager()
        self.last_item_id = None
        
        # Verificar si hay items existentes
        self.check_existing_items()
    
    def check_existing_items(self):
        """Verifica si hay items existentes para analizar"""
        try:
            items = self.db_manager.get_content_items()
            if items:
                self.last_item_id = items[0]['id']
                self.analyze_btn.setEnabled(True)
                self.status_label.setText(f"Hay {len(items)} items disponibles para analizar")
        except Exception as e:
            self.status_label.setText(f"Error verificando items: {e}")
    
    def create_long_content_item(self):
        """Crea un item con contenido largo para probar el resumen"""
        try:
            long_content = """
            La inteligencia artificial (IA) ha experimentado un crecimiento exponencial en los últimos años, transformando prácticamente todos los aspectos de nuestra sociedad. Desde los asistentes virtuales en nuestros teléfonos hasta los sistemas de recomendación en las plataformas de streaming, la IA se ha integrado de manera invisible pero fundamental en nuestras vidas cotidianas.

            El aprendizaje automático, una rama de la IA, permite a las máquinas aprender y mejorar automáticamente a través de la experiencia sin ser programadas explícitamente. Esta capacidad ha revolucionado campos como el reconocimiento de imágenes, el procesamiento de lenguaje natural y la toma de decisiones automatizada. Los algoritmos de deep learning, inspirados en la estructura del cerebro humano, han demostrado ser especialmente efectivos en tareas complejas que antes se consideraban exclusivamente humanas.

            En el sector de la salud, la IA está siendo utilizada para diagnosticar enfermedades con mayor precisión y rapidez que los métodos tradicionales. Los sistemas de IA pueden analizar millones de imágenes médicas en segundos, identificando patrones que podrían pasar desapercibidos para el ojo humano. Esto no solo mejora la precisión del diagnóstico, sino que también permite un tratamiento más temprano y personalizado.

            El transporte autónomo representa otra frontera emocionante para la IA. Los vehículos autónomos utilizan una combinación de sensores, cámaras y algoritmos de IA para navegar de manera segura por las carreteras. Aunque aún enfrentamos desafíos técnicos y regulatorios, las primeras implementaciones ya están mostrando resultados prometedores en términos de seguridad y eficiencia.

            Sin embargo, el rápido avance de la IA también plantea importantes cuestiones éticas y sociales. La automatización podría desplazar a millones de trabajadores, creando la necesidad de nuevos modelos educativos y económicos. Además, los sistemas de IA pueden perpetuar o amplificar sesgos existentes si no se diseñan e implementan cuidadosamente.

            La privacidad y la seguridad de los datos también son preocupaciones críticas. Los sistemas de IA requieren enormes cantidades de datos para funcionar efectivamente, lo que plantea preguntas sobre cómo se recopilan, almacenan y utilizan estos datos. Es fundamental desarrollar marcos regulatorios robustos que protejan los derechos individuales mientras permiten la innovación.

            El futuro de la IA promete ser aún más transformador. Los investigadores están trabajando en IA general artificial (AGI), que tendría capacidades cognitivas comparables o superiores a las humanas en todas las áreas. Aunque esto aún está lejos, los avances actuales en IA estrecha continúan creando nuevas oportunidades y desafíos.

            Para navegar exitosamente en esta era de la IA, es crucial que individuos, organizaciones y gobiernos trabajen juntos para asegurar que los beneficios de esta tecnología se distribuyan de manera equitativa y que sus riesgos se gestionen adecuadamente. La educación y la alfabetización en IA serán fundamentales para preparar a la sociedad para este futuro digital.
            """
            
            test_item = ContentItem(
                id=None,
                source_id=1,
                title="El Impacto Transformador de la Inteligencia Artificial en la Sociedad Moderna",
                url="https://ejemplo.com/ia-sociedad",
                description="Un análisis completo sobre cómo la IA está transformando diversos sectores",
                content=long_content,
                summary=None,  # Sin resumen previo para probar la generación
                status='nuevo',
                created_at=datetime.datetime.now(),
                source_name="TechAnalysis",
                source_type="article"
            )
            
            item_id = self.db_manager.insert_content_item(test_item)
            self.last_item_id = item_id
            
            self.status_label.setText(f"✅ Item con contenido largo creado (ID: {item_id}) - {len(long_content)} caracteres")
            self.analyze_btn.setEnabled(True)
            
        except Exception as e:
            self.status_label.setText(f"❌ Error creando item: {e}")
    
    def create_tech_content_item(self):
        """Crea un item con contenido técnico"""
        try:
            tech_content = """
            Python es un lenguaje de programación de alto nivel, interpretado y de propósito general. Fue creado por Guido van Rossum y lanzado por primera vez en 1991. Python es conocido por su sintaxis clara y legible, lo que lo hace ideal tanto para principiantes como para desarrolladores experimentados.

            Una de las características más distintivas de Python es su filosofía de diseño, resumida en "El Zen de Python" por Tim Peters. Esta filosofía enfatiza la legibilidad del código, la simplicidad y la elegancia. El principio "Debería haber una, y preferiblemente solo una, manera obvia de hacerlo" refleja el enfoque de Python hacia la claridad y la consistencia.

            Python soporta múltiples paradigmas de programación, incluyendo programación orientada a objetos, programación funcional y programación procedimental. Esta flexibilidad permite a los desarrolladores elegir el enfoque más adecuado para cada problema específico.

            El ecosistema de Python es uno de sus puntos más fuertes. PyPI (Python Package Index) contiene cientos de miles de paquetes de terceros que extienden las capacidades del lenguaje. Bibliotecas como NumPy y Pandas han hecho de Python la elección preferida para ciencia de datos y análisis. Django y Flask son frameworks web populares que facilitan el desarrollo de aplicaciones web robustas.

            En el campo de la inteligencia artificial y el aprendizaje automático, Python se ha establecido como el lenguaje dominante. Bibliotecas como TensorFlow, PyTorch y Scikit-learn proporcionan herramientas poderosas para desarrollar y entrenar modelos de machine learning. La simplicidad sintáctica de Python permite a los investigadores centrarse en la lógica de sus algoritmos en lugar de lidiar con complejidades del lenguaje.

            La interpretación del código Python se realiza a través del intérprete CPython, aunque existen implementaciones alternativas como PyPy, Jython e IronPython. El proceso de ejecución implica la compilación del código fuente a bytecode, que luego es ejecutado por la máquina virtual de Python.

            Python también sobresale en automatización y scripting. Su capacidad para interactuar con el sistema operativo, procesar archivos y comunicarse con APIs lo convierte en una herramienta valiosa para tareas de administración de sistemas y DevOps.
            """
            
            test_item = ContentItem(
                id=None,
                source_id=1,
                title="Python: Lenguaje de Programación Versátil para el Desarrollo Moderno",
                url="https://ejemplo.com/python-programming",
                description="Guía técnica sobre Python y sus aplicaciones en diversos campos",
                content=tech_content,
                summary=None,
                status='nuevo',
                created_at=datetime.datetime.now(),
                source_name="DevDocs",
                source_type="technical"
            )
            
            item_id = self.db_manager.insert_content_item(test_item)
            self.last_item_id = item_id
            
            self.status_label.setText(f"✅ Item técnico creado (ID: {item_id}) - {len(tech_content)} caracteres")
            self.analyze_btn.setEnabled(True)
            
        except Exception as e:
            self.status_label.setText(f"❌ Error creando item técnico: {e}")
    
    def analyze_last_item(self):
        """Analiza el último item creado"""
        if not self.last_item_id:
            self.status_label.setText("No hay item para analizar")
            return
        
        try:
            # Obtener el item de la base de datos
            items = self.db_manager.get_content_items()
            target_item = None
            
            for item_data in items:
                if item_data['id'] == self.last_item_id:
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
            
            # Abrir diálogo de análisis
            dialog = ContentAnalysisDialog(target_item, self)
            dialog.content_updated.connect(self.on_content_updated)
            result = dialog.exec()
            
            if result:
                self.status_label.setText("✅ Análisis completado exitosamente")
            else:
                self.status_label.setText("Análisis cancelado")
                
        except Exception as e:
            self.status_label.setText(f"❌ Error abriendo análisis: {e}")
    
    def test_direct_analysis(self):
        """Prueba directa del analizador sin interfaz"""
        try:
            test_text = """
            El cambio climático representa uno de los desafíos más urgentes de nuestro tiempo. Las emisiones de gases de efecto invernadero han aumentado drásticamente desde la revolución industrial, causando un calentamiento global sin precedentes. 

            Los efectos ya son visibles: temperaturas récord, derretimiento de glaciares, aumento del nivel del mar y eventos climáticos extremos más frecuentes e intensos. La biodiversidad está amenazada, con especies extinguiéndose a un ritmo acelerado.

            Sin embargo, existen soluciones. La transición hacia energías renovables, como la solar y eólica, está avanzando rápidamente. Las tecnologías de almacenamiento de energía mejoran constantemente, haciendo más viable la adopción masiva de energías limpias.

            Los gobiernos, empresas y individuos deben actuar conjuntamente. Las políticas públicas, la innovación tecnológica y los cambios en el comportamiento del consumidor son todos elementos cruciales para combatir el cambio climático.

            El tiempo para actuar es ahora. Cada grado de calentamiento que evitemos, cada tonelada de CO2 que no emitamos, marca la diferencia para las generaciones futuras.
            """
            
            self.status_label.setText("🔍 Ejecutando análisis directo...")
            QApplication.processEvents()  # Actualizar UI
            
            # Analizar contenido
            analyzer = ContentAnalyzer()
            result = analyzer.analyze_content(test_text, "Cambio Climático: Desafío Global")
            
            # Mostrar resultados
            analysis = result.get('analysis', {})
            summary = result.get('summary', '')
            
            results_text = f"""✅ Análisis completado:
            
📊 Estadísticas:
• Palabras originales: {analysis.get('word_count', 0)}
• Palabras en resumen: {len(summary.split()) if summary else 0}
• Idioma detectado: {analysis.get('language', 'unknown').upper()}
• Frases clave encontradas: {len(analysis.get('key_phrases', []))}

📝 Resumen generado: {len(summary)} caracteres
            
El análisis inteligente está funcionando correctamente."""
            
            self.status_label.setText(results_text)
            
        except Exception as e:
            self.status_label.setText(f"❌ Error en análisis directo: {e}")
    
    def on_content_updated(self, item_id: int):
        """Se ejecuta cuando se actualiza el contenido"""
        self.status_label.setText(f"✅ Item {item_id} actualizado con nuevo resumen")

def main():
    app = QApplication(sys.argv)
    
    window = TestAnalysisWindow()
    window.show()
    
    print("=== PRUEBA DE ANÁLISIS DE CONTENIDO ===")
    print("1. Crea items de prueba con diferentes tipos de contenido")
    print("2. Usa 'Analizar Último Item' para abrir el diálogo completo")
    print("3. Usa 'Prueba de Análisis Directo' para ver el analizador en acción")
    print("4. En el diálogo de análisis puedes:")
    print("   - Ver estadísticas detalladas del contenido")
    print("   - Revisar el resumen inteligente generado")
    print("   - Comparar original vs resumen")
    print("   - Editar el resumen manualmente")
    print("   - Generar preview de audio")
    print("   - Guardar el resumen mejorado")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
