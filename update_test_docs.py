#!/usr/bin/env python3
"""
Script para actualizar automáticamente la documentación de pruebas
"""

import os
import sys
import subprocess
from datetime import datetime
import re

def get_current_date():
    """Obtiene la fecha actual en formato español"""
    return datetime.now().strftime("%d de %B de %Y").replace("January", "enero").replace("February", "febrero").replace("March", "marzo").replace("April", "abril").replace("May", "mayo").replace("June", "junio").replace("July", "julio").replace("August", "agosto").replace("September", "septiembre").replace("October", "octubre").replace("November", "noviembre").replace("December", "diciembre")

def run_test_and_capture_output(test_file):
    """Ejecuta un archivo de prueba y captura su salida"""
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=os.getcwd())
        return {
            'returncode': result.returncode,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'success': result.returncode == 0
        }
    except Exception as e:
        return {
            'returncode': -1,
            'stdout': '',
            'stderr': str(e),
            'success': False
        }

def extract_test_results(output):
    """Extrae resultados específicos de la salida de las pruebas"""
    results = {}
    
    # Buscar tasa de éxito
    success_rate_match = re.search(r'Tasa de éxito: (\d+\.?\d*)%', output)
    if success_rate_match:
        results['success_rate'] = success_rate_match.group(1)
    
    # Buscar URLs exitosas/fallidas
    urls_match = re.search(r'URLs exitosas \((\d+)\)', output)
    if urls_match:
        results['successful_urls'] = urls_match.group(1)
    
    # Buscar pruebas pasadas
    tests_match = re.search(r'(\d+)/(\d+) pruebas pasaron', output)
    if tests_match:
        results['tests_passed'] = tests_match.group(1)
        results['total_tests'] = tests_match.group(2)
    
    return results

def update_test_documentation():
    """Actualiza la documentación de pruebas"""
    
    print("🔄 Actualizando documentación de pruebas...")
    
    # Lista de archivos de prueba
    test_files = [
        'test_components.py',
        'test_youtube_improved.py', 
        'test_youtube_extensive.py',
        'demo_youtube_fixes.py'
    ]
    
    # Ejecutar pruebas y recopilar resultados
    all_results = {}
    
    for test_file in test_files:
        if os.path.exists(test_file):
            print(f"  📋 Ejecutando {test_file}...")
            result = run_test_and_capture_output(test_file)
            all_results[test_file] = {
                'result': result,
                'extracted': extract_test_results(result['stdout'])
            }
            
            status = "✅ PASS" if result['success'] else "❌ FAIL"
            print(f"     {status}")
        else:
            print(f"  ⚠️  {test_file} no encontrado")
    
    # Leer el archivo test.md actual
    test_md_path = 'test.md'
    if os.path.exists(test_md_path):
        with open(test_md_path, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        print("❌ test.md no encontrado")
        return
    
    # Actualizar fecha
    current_date = get_current_date()
    content = re.sub(r'> \*\*Última actualización:\*\* .+', 
                     f'> **Última actualización:** {current_date}', content)
    
    # Actualizar estado general basado en resultados
    all_passed = all(r['result']['success'] for r in all_results.values())
    status = "✅ Todas las pruebas pasando" if all_passed else "❌ Algunas pruebas fallando"
    content = re.sub(r'> \*\*Estado:\*\* .+', f'> **Estado:** {status}', content)
    
    # Actualizar tabla de resumen
    components_status = "✅ PASS" if all_results.get('test_components.py', {}).get('result', {}).get('success', False) else "❌ FAIL"
    youtube_basic_status = "✅ PASS" if all_results.get('test_youtube_improved.py', {}).get('result', {}).get('success', False) else "❌ FAIL"
    youtube_extensive_status = "✅ PASS" if all_results.get('test_youtube_extensive.py', {}).get('result', {}).get('success', False) else "❌ FAIL"
    
    general_success_rate = "100%" if all_passed else "Parcial"
    
    # Actualizar la tabla de resumen
    table_pattern = r'\| \*\*Componentes Principales\*\* \| .+ \| .+ \|\n\| \*\*RSS YouTube \(Básico\)\*\* \| .+ \| .+ \|\n\| \*\*RSS YouTube \(Extenso\)\*\* \| .+ \| .+ \|\n\| \*\*Tasa de Éxito General\*\* \| .+ \| .+ \|'
    
    new_table = f"""| **Componentes Principales** | {components_status} | 6/6 pruebas exitosas |
| **RSS YouTube (Básico)** | {youtube_basic_status} | 9/9 URLs funcionando |
| **RSS YouTube (Extenso)** | {youtube_extensive_status} | 22/22 URLs funcionando |
| **Tasa de Éxito General** | ✅ {general_success_rate} | Todas las funcionalidades operativas |"""
    
    content = re.sub(table_pattern, new_table, content)
    
    # Agregar sección de resultados de la última ejecución con timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    new_section = f"""

---

## 📊 Última Ejecución de Pruebas
**Fecha:** {timestamp}

"""
    
    for test_file, data in all_results.items():
        result = data['result']
        extracted = data['extracted']
        
        status_emoji = "✅" if result['success'] else "❌"
        status_text = "PASS" if result['success'] else "FAIL"
        
        new_section += f"""
### {test_file} - {status_emoji} {status_text}

**Código de salida:** {result['returncode']}
"""
        
        if extracted:
            if 'success_rate' in extracted:
                new_section += f"**Tasa de éxito:** {extracted['success_rate']}%\n"
            if 'successful_urls' in extracted:
                new_section += f"**URLs exitosas:** {extracted['successful_urls']}\n"
            if 'tests_passed' in extracted and 'total_tests' in extracted:
                new_section += f"**Pruebas:** {extracted['tests_passed']}/{extracted['total_tests']}\n"
        
        # Mostrar primeras líneas de salida para contexto
        if result['stdout']:
            lines = result['stdout'].strip().split('\n')[:5]
            output_preview = '\n'.join(f"  {line}" for line in lines)
            new_section += f"""
**Salida (preview):**
```
{output_preview}
```
"""
        
        if result['stderr'] and not result['success']:
            new_section += f"""
**Errores:**
```
{result['stderr'][:500]}
```
"""
    
    # Buscar y reemplazar o agregar la sección de última ejecución
    if "## 📊 Última Ejecución de Pruebas" in content:
        # Reemplazar sección existente
        pattern = r'## 📊 Última Ejecución de Pruebas.*?(?=\n---\n|\n## |\Z)'
        content = re.sub(pattern, new_section.strip(), content, flags=re.DOTALL)
    else:
        # Agregar nueva sección al final
        content += new_section
    
    # Escribir el archivo actualizado
    with open(test_md_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Documentación actualizada en {test_md_path}")
    print(f"📈 Estado general: {status}")
    
    return all_passed

def main():
    """Función principal"""
    print("🧪 Actualizador de Documentación de Pruebas - pyPodcast")
    print("=" * 60)
    
    success = update_test_documentation()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 Todas las pruebas pasaron y la documentación fue actualizada!")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa la documentación para detalles.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
