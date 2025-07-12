#!/usr/bin/env python3
"""
Script para ejecutar pruebas específicas y actualizar documentación
"""

import sys
import os
import argparse
from update_test_docs import update_test_documentation

def run_specific_test(test_name):
    """Ejecuta una prueba específica"""
    
    test_files = {
        'components': 'test_components.py',
        'youtube': 'test_youtube_improved.py',
        'youtube-extensive': 'test_youtube_extensive.py', 
        'demo': 'demo_youtube_fixes.py',
        'all': None  # Ejecutar todas
    }
    
    if test_name not in test_files:
        print(f"❌ Prueba '{test_name}' no reconocida.")
        print(f"Pruebas disponibles: {', '.join(test_files.keys())}")
        return False
    
    if test_name == 'all':
        print("🧪 Ejecutando todas las pruebas...")
        return update_test_documentation()
    
    test_file = test_files[test_name]
    
    if not os.path.exists(test_file):
        print(f"❌ Archivo de prueba {test_file} no encontrado.")
        return False
    
    print(f"🧪 Ejecutando prueba: {test_name} ({test_file})")
    print("=" * 50)
    
    # Ejecutar la prueba
    import subprocess
    try:
        result = subprocess.run([sys.executable, test_file], cwd=os.getcwd())
        success = result.returncode == 0
        
        print("=" * 50)
        if success:
            print("✅ Prueba completada exitosamente")
        else:
            print("❌ Prueba falló")
        
        # Actualizar documentación
        print("\n🔄 Actualizando documentación...")
        update_test_documentation()
        
        return success
        
    except Exception as e:
        print(f"❌ Error ejecutando prueba: {e}")
        return False

def main():
    """Función principal"""
    parser = argparse.ArgumentParser(description='Ejecutor de pruebas con actualización automática de documentación')
    parser.add_argument('test', nargs='?', default='all', 
                       help='Prueba a ejecutar: components, youtube, youtube-extensive, demo, all (default: all)')
    parser.add_argument('--update-only', action='store_true',
                       help='Solo actualizar documentación sin ejecutar pruebas')
    
    args = parser.parse_args()
    
    print("🧪 PyPodcast - Ejecutor de Pruebas")
    print("=" * 40)
    
    if args.update_only:
        print("📝 Solo actualizando documentación...")
        success = update_test_documentation()
    else:
        success = run_specific_test(args.test)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
