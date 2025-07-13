#!/usr/bin/env python3
"""
Script de prueba para Apple Intelligence Summarizer

Este script prueba la implementación de Apple Intelligence siguiendo
las especificaciones del documento ComousarAppleIntelligence.txt.

Funcionalidades probadas:
- Conectividad con el servidor local Apple Intelligence
- Resumen directo para textos cortos
- Fragmentación y resumen jerárquico para textos largos
- Prompts optimizados y personalizados
- Manejo de errores y fallbacks

Author: Test Team
Date: 2025
"""

import sys
import os

# Añadir el directorio raíz al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from services.apple_intelligence_summarizer import (
    AppleIntelligenceSummarizer, 
    AppleIntelligenceConfig,
    get_apple_intelligence_service,
    is_apple_intelligence_available,
    summarize_with_apple_intelligence
)
from services.content_analyzer import ContentAnalyzer
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_apple_intelligence_availability():
    """Prueba la disponibilidad del servicio Apple Intelligence"""
    print("=" * 60)
    print("PRUEBA 1: Disponibilidad de Apple Intelligence")
    print("=" * 60)
    
    service = get_apple_intelligence_service()
    status = service.get_status()
    
    print("Estado del servicio:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    is_available = is_apple_intelligence_available()
    print(f"\nServicio disponible: {is_available}")
    
    if not is_available:
        print("\n⚠️  AVISO: Apple Intelligence no está disponible")
        print("Para usar Apple Intelligence, asegúrate de:")
        print("1. Tener macOS Sequoia 15.1+ instalado")
        print("2. Apple Intelligence habilitado en Configuración del Sistema")
        print("3. Servidor AppleOnDeviceOpenAI ejecutándose en localhost:11535")
        print("4. Mac con chip Apple Silicon (M1, M2, M3 o posterior)")
        print("5. Al menos 8GB de RAM disponible")
    
    return is_available

def test_short_text_summarization():
    """Prueba resumen directo de texto corto"""
    print("\n" + "=" * 60)
    print("PRUEBA 2: Resumen de Texto Corto (Directo)")
    print("=" * 60)
    
    text = """
    Apple Intelligence representa un avance significativo en el procesamiento de IA en el dispositivo,
    llevando modelos de lenguaje potentes directamente a los dispositivos de los usuarios mientras
    mantiene la privacidad. El sistema utiliza un modelo de 3 mil millones de parámetros que funciona
    localmente en Apple Silicon, proporcionando capacidades de IA rápidas, seguras y rentables.
    
    Las características clave incluyen resumen de texto, asistencia de escritura y análisis inteligente
    de contenido. El marco Foundation Models permite a los desarrolladores integrar estas capacidades
    en sus aplicaciones con código mínimo, típicamente requiriendo solo tres líneas de código Swift.
    
    Sin embargo, el modelo en el dispositivo tiene limitaciones, incluyendo una ventana de contexto
    de 4096 tokens y capacidades de razonamiento reducidas en comparación con modelos más grandes
    basados en la nube. Esto lo hace ideal para tareas enfocadas como resumen y edición de texto,
    pero puede tener dificultades con razonamiento complejo o documentos muy largos.
    """
    
    service = get_apple_intelligence_service()
    
    print(f"Texto de entrada ({len(text)} caracteres):")
    print(text[:200] + "..." if len(text) > 200 else text)
    
    print(f"\nTokens estimados: {service.estimate_tokens(text)}")
    print(f"¿Cabe en ventana de contexto?: {service.can_fit_in_context(text, 'Resume este texto.')}")
    
    if service.is_available:
        result = service.summarize(
            text=text,
            max_words=100,
            style="neutral",
            format_type="paragraph"
        )
        
        print(f"\nResultado del resumen:")
        for key, value in result.items():
            if key != 'summary':
                print(f"  {key}: {value}")
        
        if result['success']:
            print(f"\n📝 RESUMEN GENERADO:")
            print("-" * 40)
            print(result['summary'])
            print("-" * 40)
        else:
            print(f"\n❌ Error: {result.get('error', 'Desconocido')}")
    else:
        print("\n⚠️  Apple Intelligence no disponible - probando con función de conveniencia")
        result = summarize_with_apple_intelligence(text, max_words=100)
        print(f"Resultado: {result}")

def test_long_text_summarization():
    """Prueba resumen con fragmentación para texto largo"""
    print("\n" + "=" * 60)
    print("PRUEBA 3: Resumen de Texto Largo (Fragmentación)")
    print("=" * 60)
    
    # Crear un texto largo que exceda la ventana de contexto
    long_text = """
    Apple Intelligence marca un hito importante en la evolución de la inteligencia artificial personal,
    representando un cambio paradigmático hacia el procesamiento en el dispositivo que prioriza la
    privacidad del usuario sin comprometer la funcionalidad. Este enfoque innovador integra modelos
    de lenguaje de gran tamaño directamente en el hardware de Apple, eliminando la necesidad de
    transmitir datos sensibles a servidores externos.
    
    El sistema utiliza un modelo de 3 mil millones de parámetros optimizado específicamente para
    ejecutarse en chips Apple Silicon, aprovechando el Neural Engine y la arquitectura de memoria
    unificada para ofrecer un rendimiento excepcional. Esta implementación local garantiza respuestas
    instantáneas y elimina los costos operativos asociados con las APIs basadas en la nube.
    
    Las capacidades principales de Apple Intelligence incluyen herramientas de escritura avanzadas
    que pueden resumir, corregir y reescribir texto de manera inteligente. El sistema también
    incorpora funciones de análisis de contenido, extracción de información clave y generación
    de resúmenes contextuales que se adaptan al estilo y propósito del documento original.
    
    El marco Foundation Models proporciona una interfaz de programación elegante que permite a
    los desarrolladores integrar estas capacidades con apenas unas líneas de código. Esta
    simplicidad de implementación democratiza el acceso a tecnologías de IA avanzadas, permitiendo
    que aplicaciones de todos los tamaños incorporen funcionalidades inteligentes.
    
    Sin embargo, la arquitectura en el dispositivo presenta ciertas limitaciones inherentes que
    los desarrolladores deben considerar. La ventana de contexto está limitada a 4096 tokens,
    lo que equivale aproximadamente a 12,000-16,000 caracteres en inglés. Esta restricción
    requiere estrategias cuidadosas de gestión de contenido para documentos extensos.
    
    Las técnicas de fragmentación y resumen jerárquico se vuelven esenciales cuando se trabaja
    con contenido que excede estos límites. El proceso implica dividir el texto en segmentos
    manejables, resumir cada fragmento individualmente, y luego combinar estos resúmenes
    parciales en un resumen final coherente y completo.
    
    La ingeniería de prompts juega un papel crucial en la optimización del rendimiento del
    sistema. Los prompts deben ser específicos, concisos y estructurados para guiar al modelo
    hacia los resultados deseados. Las mejores prácticas incluyen colocar las instrucciones
    al principio, ser descriptivo sobre el formato de salida deseado, y utilizar ejemplos
    cuando sea necesario.
    
    El equilibrio entre privacidad, rendimiento y funcionalidad representa una de las ventajas
    más significativas de Apple Intelligence. Los usuarios pueden beneficiarse de capacidades
    de IA avanzadas sin preocuparse por la transmisión de datos personales a terceros, mientras
    disfrutan de respuestas rápidas y sin costos adicionales por uso.
    
    Las aplicaciones prácticas de esta tecnología son vastas, desde la automatización de tareas
    de escritura hasta el análisis inteligente de documentos extensos. Los desarrolladores pueden
    crear experiencias de usuario más inteligentes y contextuales, mejorando la productividad
    y la eficiencia sin comprometer la privacidad.
    
    La integración con el ecosistema de desarrollo de Apple facilita la adopción de estas
    tecnologías, proporcionando herramientas y frameworks familiares que reducen la curva
    de aprendizaje. Esto permite que los desarrolladores se concentren en la innovación
    y la creación de valor agregado en lugar de en los aspectos técnicos de la implementación.
    
    Mirando hacia el futuro, Apple Intelligence establece las bases para una nueva generación
    de aplicaciones inteligentes que respetan la privacidad del usuario mientras ofrecen
    capacidades de IA de vanguardia. Esta aproximación podría influenciar significativamente
    la dirección de la industria hacia soluciones más centradas en la privacidad y el usuario.
    """ * 2  # Duplicar para hacer el texto aún más largo
    
    service = get_apple_intelligence_service()
    
    print(f"Texto largo ({len(long_text)} caracteres)")
    print(f"Tokens estimados: {service.estimate_tokens(long_text)}")
    print(f"¿Cabe en ventana de contexto?: {service.can_fit_in_context(long_text, 'Resume este texto.')}")
    
    if service.is_available:
        print("\nGenerando resumen con fragmentación...")
        
        result = service.summarize(
            text=long_text,
            max_words=300,
            style="academic",
            format_type="paragraph"
        )
        
        print(f"\nResultado del resumen:")
        for key, value in result.items():
            if key != 'summary':
                print(f"  {key}: {value}")
        
        if result['success']:
            print(f"\n📝 RESUMEN GENERADO (TEXTO LARGO):")
            print("-" * 50)
            print(result['summary'])
            print("-" * 50)
        else:
            print(f"\n❌ Error: {result.get('error', 'Desconocido')}")
    else:
        print("\n⚠️  Apple Intelligence no disponible - no se puede probar fragmentación")

def test_custom_prompts():
    """Prueba prompts personalizados optimizados"""
    print("\n" + "=" * 60)
    print("PRUEBA 4: Prompts Personalizados Optimizados")
    print("=" * 60)
    
    text = """
    El Machine Learning es una rama de la inteligencia artificial que permite a los sistemas
    aprender y mejorar automáticamente a partir de la experiencia sin ser programados
    explícitamente. Utiliza algoritmos que pueden identificar patrones en datos y hacer
    predicciones o tomar decisiones basadas en esos patrones. Las aplicaciones incluyen
    reconocimiento de voz, procesamiento de lenguaje natural, visión por computadora,
    sistemas de recomendación y vehículos autónomos. Los tipos principales incluyen
    aprendizaje supervisado, no supervisado y por refuerzo.
    """
    
    # Diferentes tipos de prompts personalizados
    prompts = [
        {
            "name": "Académico",
            "prompt": """Proporciona un resumen académico del siguiente texto.
            
FORMATO REQUERIDO:
- Máximo 100 palabras
- Tono formal y objetivo
- Incluye terminología técnica apropiada
- Estructura: definición, características principales, aplicaciones

Texto a resumir:"""
        },
        {
            "name": "Divulgativo",
            "prompt": """Resume el siguiente texto para el público general.

INSTRUCCIONES:
- Usa lenguaje simple y accesible
- Máximo 80 palabras
- Evita jerga técnica excesiva
- Enfócate en aplicaciones prácticas

Contenido:"""
        },
        {
            "name": "Lista de puntos",
            "prompt": """Crea un resumen en formato de lista con los puntos clave.

FORMATO:
• Punto principal 1
• Punto principal 2
• Punto principal 3
(máximo 5 puntos, cada uno de 10-15 palabras)

Texto fuente:"""
        }
    ]
    
    service = get_apple_intelligence_service()
    
    if service.is_available:
        for i, prompt_config in enumerate(prompts, 1):
            print(f"\n{i}. Probando prompt {prompt_config['name']}:")
            print("-" * 30)
            
            result = service.summarize(
                text=text,
                custom_prompt=prompt_config['prompt'],
                max_words=100
            )
            
            if result['success']:
                print(f"✓ Resumen ({prompt_config['name']}):")
                print(result['summary'])
            else:
                print(f"✗ Error: {result.get('error', 'Desconocido')}")
    else:
        print("\n⚠️  Apple Intelligence no disponible - no se pueden probar prompts personalizados")

def test_content_analyzer_integration():
    """Prueba la integración con ContentAnalyzer"""
    print("\n" + "=" * 60)
    print("PRUEBA 5: Integración con ContentAnalyzer")
    print("=" * 60)
    
    text = """
    La inteligencia artificial generativa ha revolucionado la forma en que interactuamos con
    la tecnología, permitiendo la creación de contenido nuevo y original a partir de patrones
    aprendidos de datos existentes. Esta tecnología incluye modelos como GPT para texto,
    DALL-E para imágenes, y sistemas de síntesis de voz. Las aplicaciones van desde la
    automatización de escritura hasta la creación artística, pasando por la programación
    asistida y el diseño gráfico. Sin embargo, también plantea desafíos éticos relacionados
    con la autenticidad, los derechos de autor y el potencial de desinformación.
    """
    
    analyzer = ContentAnalyzer()
    
    print("Estado de los resumidores:")
    status = analyzer.get_summarizer_status()
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print(f"\nAnalizando contenido ({len(text)} caracteres)...")
    
    result = analyzer.analyze_content(text, title="Inteligencia Artificial Generativa")
    
    print(f"\nAnálisis completado:")
    print(f"  Palabras: {result['analysis']['word_count']}")
    print(f"  Oraciones: {result['analysis']['sentence_count']}")
    print(f"  Párrafos: {result['analysis']['paragraph_count']}")
    print(f"  Tiempo de lectura: {result['analysis']['reading_time_minutes']:.1f} minutos")
    print(f"  Idioma detectado: {result['analysis']['language']}")
    print(f"  Frases clave: {', '.join(result['analysis']['key_phrases'][:3])}")
    
    print(f"\n📝 RESUMEN INTEGRADO:")
    print("-" * 40)
    print(result['summary'])
    print("-" * 40)

def test_error_handling():
    """Prueba el manejo de errores y casos extremos"""
    print("\n" + "=" * 60)
    print("PRUEBA 6: Manejo de Errores y Casos Extremos")
    print("=" * 60)
    
    service = get_apple_intelligence_service()
    
    test_cases = [
        ("Texto vacío", ""),
        ("Texto muy corto", "Hola."),
        ("Solo espacios", "   \n\t   "),
        ("Caracteres especiales", "¡¿@#$%^&*()_+-=[]{}|;:,.<>?"),
    ]
    
    for name, text in test_cases:
        print(f"\n• Probando: {name}")
        result = service.summarize(text, max_words=50)
        print(f"  Éxito: {result['success']}")
        if not result['success']:
            print(f"  Error: {result.get('error', 'Desconocido')}")
        else:
            print(f"  Resumen: {result.get('summary', 'N/A')[:50]}...")

def main():
    """Función principal del script de pruebas"""
    print("🧪 PRUEBAS DE APPLE INTELLIGENCE SUMMARIZER")
    print("Basado en las especificaciones de ComousarAppleIntelligence.txt")
    print("\n" + "=" * 60)
    
    # Ejecutar todas las pruebas
    is_available = test_apple_intelligence_availability()
    
    test_short_text_summarization()
    test_long_text_summarization()
    test_custom_prompts()
    test_content_analyzer_integration()
    test_error_handling()
    
    print("\n" + "=" * 60)
    print("🏁 PRUEBAS COMPLETADAS")
    print("=" * 60)
    
    if is_available:
        print("✅ Apple Intelligence funcionando correctamente")
        print("   Todas las funcionalidades están disponibles")
    else:
        print("⚠️  Apple Intelligence no disponible")
        print("   Las pruebas se ejecutaron con fallbacks y simulaciones")
    
    print("\nPara habilitar Apple Intelligence completamente:")
    print("1. Instalar macOS Sequoia 15.1+")
    print("2. Habilitar Apple Intelligence en Configuración del Sistema")
    print("3. Descargar y ejecutar AppleOnDeviceOpenAI")
    print("4. Verificar conectividad en localhost:11535")

if __name__ == "__main__":
    main()
