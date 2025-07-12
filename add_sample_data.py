#!/usr/bin/env python3
"""
Script para añadir datos de ejemplo a PyPodcast
"""

import sys
from pathlib import Path

# Añadir directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from models.database import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger()

def add_sample_data():
    """Añade datos de ejemplo a la base de datos"""
    print("📝 Añadiendo datos de ejemplo...")
    
    try:
        db = DatabaseManager()
        db.initialize_database()
        
        # Fuentes de ejemplo
        sample_sources = [
            {
                'name': 'BBC News en Español',
                'type': 'rss',
                'url': 'https://feeds.bbci.co.uk/mundo/rss.xml',
                'description': 'Noticias internacionales en español'
            },
            {
                'name': 'Canal de YouTube - TED Talks',
                'type': 'youtube',
                'url': 'https://www.youtube.com/channel/UCAuUUnT6oDeKwE6v1NGQxug',
                'description': 'Conferencias TED inspiradoras'
            },
            {
                'name': 'Xataka - Tecnología',
                'type': 'rss',
                'url': 'https://www.xataka.com/index.xml',
                'description': 'Blog de tecnología en español'
            }
        ]
        
        added_count = 0
        
        for source in sample_sources:
            try:
                source_id = db.add_data_source(
                    name=source['name'],
                    source_type=source['type'],
                    url=source['url'],
                    description=source['description']
                )
                print(f"✅ Añadida fuente: {source['name']}")
                added_count += 1
                
            except ValueError:
                print(f"⚠️ Fuente ya existe: {source['name']}")
            except Exception as e:
                print(f"❌ Error añadiendo {source['name']}: {e}")
        
        print(f"\n📊 Resultado: {added_count} fuentes añadidas")
        
        if added_count > 0:
            print("\n🎉 Datos de ejemplo añadidos correctamente!")
            print("💡 Ahora puedes:")
            print("   1. Ejecutar la aplicación: python main.py")
            print("   2. Actualizar feeds desde el menú Archivo > Actualizar Feeds")
            print("   3. Procesar contenido haciendo clic derecho en los elementos")
        else:
            print("\n📋 No se añadieron nuevas fuentes (ya existían)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error añadiendo datos de ejemplo: {e}")
        return False

def main():
    """Función principal"""
    print("🚀 PyPodcast - Datos de Ejemplo")
    print("=" * 40)
    
    success = add_sample_data()
    
    print("\n" + "=" * 40)
    
    if success:
        print("✅ Proceso completado exitosamente")
    else:
        print("❌ Hubo errores en el proceso")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
