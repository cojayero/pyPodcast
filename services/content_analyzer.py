"""
Servicio de análisis y resumen de contenido
"""

import re
import math
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
from utils.config import config_manager
from utils.logger import get_logger
from services.apple_intelligence_summarizer import get_apple_intelligence_service, is_apple_intelligence_available

logger = get_logger(__name__)

class ContentAnalyzer:
    """Analizador y resumidor de contenido usando técnicas de procesamiento de texto"""
    
    def __init__(self):
        self.max_summary_length = config_manager.get('content.max_summary_length', 500)
        self.summary_language = config_manager.get('content.summary_language', 'es')
        self.use_apple_intelligence = config_manager.get('content.use_apple_intelligence', True)
        
        # Palabras vacías en español
        self.spanish_stopwords = {
            'a', 'ante', 'bajo', 'cabe', 'con', 'contra', 'de', 'desde', 'durante', 'en',
            'entre', 'hacia', 'hasta', 'mediante', 'para', 'por', 'según', 'sin', 'so',
            'sobre', 'tras', 'versus', 'vía', 'el', 'la', 'los', 'las', 'un', 'una',
            'unos', 'unas', 'y', 'o', 'pero', 'si', 'no', 'ni', 'que', 'como', 'cuando',
            'donde', 'quien', 'cual', 'este', 'esta', 'estos', 'estas', 'ese', 'esa',
            'esos', 'esas', 'aquel', 'aquella', 'aquellos', 'aquellas', 'su', 'sus',
            'mi', 'mis', 'tu', 'tus', 'nuestro', 'nuestra', 'nuestros', 'nuestras',
            'vuestro', 'vuestra', 'vuestros', 'vuestras', 'del', 'al', 'muy', 'más',
            'menos', 'tanto', 'tan', 'también', 'tampoco', 'ya', 'aún', 'todavía',
            'ser', 'estar', 'tener', 'hacer', 'decir', 'poder', 'ir', 'ver', 'dar',
            'saber', 'querer', 'llegar', 'pasar', 'deber', 'poner', 'parecer', 'quedar',
            'creer', 'hablar', 'llevar', 'dejar', 'seguir', 'encontrar', 'llamar',
            'venir', 'pensar', 'salir', 'volver', 'tomar', 'conocer', 'vivir', 'sentir'
        }
        
        # Palabras vacías en inglés
        self.english_stopwords = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from', 'has',
            'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the', 'to', 'was',
            'were', 'will', 'with', 'the', 'this', 'but', 'they', 'have', 'had',
            'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their', 'if',
            'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some', 'her',
            'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more', 'go',
            'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call', 'who',
            'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get', 'come',
            'made', 'may', 'part'
        }
    
    def analyze_content(self, content: str, title: str = None) -> Dict[str, Any]:
        """Analiza el contenido y genera un resumen inteligente"""
        if not content or not content.strip():
            return {
                'original_content': content,
                'summary': "",
                'analysis': {
                    'word_count': 0,
                    'sentence_count': 0,
                    'paragraph_count': 0,
                    'reading_time_minutes': 0,
                    'key_phrases': [],
                    'language': 'unknown'
                }
            }
        
        try:
            # Análisis básico
            analysis = self._analyze_text_structure(content)
            
            # Detectar idioma predominante
            language = self._detect_language(content)
            analysis['language'] = language
            
            # Extraer frases clave
            key_phrases = self._extract_key_phrases(content, language)
            analysis['key_phrases'] = key_phrases
            
            # Generar resumen inteligente
            summary = self._generate_smart_summary(content, title, language, key_phrases)
            
            return {
                'original_content': content,
                'summary': summary,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error analizando contenido: {e}")
            return {
                'original_content': content,
                'summary': self._simple_summary(content),
                'analysis': {
                    'word_count': len(content.split()),
                    'sentence_count': content.count('.') + content.count('!') + content.count('?'),
                    'paragraph_count': len([p for p in content.split('\n\n') if p.strip()]),
                    'reading_time_minutes': len(content.split()) / 200,  # 200 wpm promedio
                    'key_phrases': [],
                    'language': 'unknown'
                }
            }
    
    def _analyze_text_structure(self, content: str) -> Dict[str, Any]:
        """Analiza la estructura básica del texto"""
        # Contar palabras
        words = content.split()
        word_count = len(words)
        
        # Contar oraciones (aproximado)
        sentence_count = len(re.findall(r'[.!?]+', content))
        
        # Contar párrafos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        paragraph_count = len(paragraphs)
        
        # Estimar tiempo de lectura (200 palabras por minuto promedio)
        reading_time_minutes = word_count / 200
        
        return {
            'word_count': word_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'reading_time_minutes': reading_time_minutes
        }
    
    def _detect_language(self, content: str) -> str:
        """Detecta el idioma predominante del contenido"""
        words = re.findall(r'\b\w+\b', content.lower())
        
        if not words:
            return 'unknown'
        
        # Contar palabras vacías en cada idioma
        spanish_count = sum(1 for word in words if word in self.spanish_stopwords)
        english_count = sum(1 for word in words if word in self.english_stopwords)
        
        total_words = len(words)
        spanish_ratio = spanish_count / total_words if total_words > 0 else 0
        english_ratio = english_count / total_words if total_words > 0 else 0
        
        # Decidir idioma basado en ratio de palabras vacías
        if spanish_ratio > english_ratio and spanish_ratio > 0.05:
            return 'es'
        elif english_ratio > 0.05:
            return 'en'
        else:
            return 'unknown'
    
    def _extract_key_phrases(self, content: str, language: str) -> List[str]:
        """Extrae frases clave del contenido"""
        try:
            # Obtener palabras vacías según el idioma
            stopwords = self.spanish_stopwords if language == 'es' else self.english_stopwords
            
            # Limpiar y dividir en palabras
            words = re.findall(r'\b\w+\b', content.lower())
            words = [word for word in words if len(word) > 3 and word not in stopwords]
            
            # Contar frecuencia de palabras
            word_freq = Counter(words)
            
            # Obtener las palabras más frecuentes
            top_words = [word for word, freq in word_freq.most_common(15) if freq > 1]
            
            # Extraer frases que contengan palabras clave
            sentences = re.split(r'[.!?]+', content)
            key_phrases = []
            
            for sentence in sentences:
                sentence = sentence.strip()
                if len(sentence) > 20 and len(sentence) < 150:
                    sentence_words = re.findall(r'\b\w+\b', sentence.lower())
                    # Si la oración contiene palabras clave, es una frase relevante
                    if any(word in top_words for word in sentence_words):
                        key_phrases.append(sentence)
            
            # Devolver las mejores frases (máximo 5)
            return key_phrases[:5]
            
        except Exception as e:
            logger.error(f"Error extrayendo frases clave: {e}")
            return []
    
    def _generate_smart_summary(self, content: str, title: str, language: str, key_phrases: List[str]) -> str:
        """Genera un resumen inteligente del contenido"""
        try:
            # Intentar usar Apple Intelligence primero si está disponible y habilitado
            if self.use_apple_intelligence and is_apple_intelligence_available():
                return self._generate_apple_intelligence_summary(content, title, language, key_phrases)
            
            # Fallback al método tradicional si Apple Intelligence no está disponible
            return self._generate_traditional_summary(content, title, language, key_phrases)
            
        except Exception as e:
            logger.error(f"Error generando resumen inteligente: {e}")
            return self._simple_summary(content)
    
    def _generate_apple_intelligence_summary(self, content: str, title: str, language: str, key_phrases: List[str]) -> str:
        """Genera resumen usando Apple Intelligence"""
        try:
            # Crear prompt personalizado basado en el análisis
            if language == 'es':
                prompt = f"""Resume el siguiente contenido en español de manera concisa y clara.
Destaca los puntos principales y las conclusiones más importantes.
Mantén un tono objetivo e informativo.
{f'El título del contenido es: {title}' if title else ''}
{f'Frases clave identificadas: {", ".join(key_phrases[:3])}' if key_phrases else ''}
Longitud máxima: {self.max_summary_length} caracteres."""
            else:
                prompt = f"""Summarize the following content concisely and clearly.
Highlight the main points and most important conclusions.
Maintain an objective and informative tone.
{f'The content title is: {title}' if title else ''}
{f'Key phrases identified: {", ".join(key_phrases[:3])}' if key_phrases else ''}
Maximum length: {self.max_summary_length} characters."""
            
            # Generar resumen con Apple Intelligence
            service = get_apple_intelligence_service()
            result = service.summarize(
                text=content,
                custom_prompt=prompt,
                max_words=min(self.max_summary_length // 5, 200)  # Estimación de palabras
            )
            
            if result and result.get('success') and result.get('summary'):
                ai_summary = result['summary']
                # Truncar si es necesario para cumplir con el límite de caracteres
                if len(ai_summary) > self.max_summary_length:
                    ai_summary = ai_summary[:self.max_summary_length]
                    # Cortar en la última oración completa
                    last_sentence = ai_summary.rfind('.')
                    if last_sentence > self.max_summary_length * 0.7:
                        ai_summary = ai_summary[:last_sentence + 1]
                
                logger.info("Resumen generado exitosamente con Apple Intelligence")
                return ai_summary
            else:
                logger.warning("Apple Intelligence no generó resumen válido, usando método tradicional")
                return self._generate_traditional_summary(content, title, language, key_phrases)
                
        except Exception as e:
            logger.error(f"Error usando Apple Intelligence: {e}")
            return self._generate_traditional_summary(content, title, language, key_phrases)
    
    def _generate_traditional_summary(self, content: str, title: str, language: str, key_phrases: List[str]) -> str:
        """Genera resumen usando el método tradicional (algoritmo propio)"""
        try:
            # Dividir en párrafos
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip() and len(p) > 50]
            
            if not paragraphs:
                return self._simple_summary(content)
            
            # Obtener palabras vacías
            stopwords = self.spanish_stopwords if language == 'es' else self.english_stopwords
            
            # Extraer palabras clave del título si existe
            title_words = set()
            if title:
                title_words = set(re.findall(r'\b\w+\b', title.lower()))
                title_words = {word for word in title_words if word not in stopwords and len(word) > 3}
            
            # Extraer palabras frecuentes del contenido
            all_words = re.findall(r'\b\w+\b', content.lower())
            content_words = [word for word in all_words if word not in stopwords and len(word) > 3]
            word_freq = Counter(content_words)
            frequent_words = set([word for word, freq in word_freq.most_common(10)])
            
            # Combinar palabras importantes
            important_words = title_words.union(frequent_words)
            
            # Puntuar párrafos basado en relevancia
            paragraph_scores = []
            
            for i, paragraph in enumerate(paragraphs):
                score = 0
                paragraph_words = set(re.findall(r'\b\w+\b', paragraph.lower()))
                
                # Puntos por palabras importantes
                score += len(paragraph_words.intersection(important_words)) * 2
                
                # Puntos por posición (primeros y últimos párrafos son más importantes)
                if i == 0:  # Primer párrafo
                    score += 3
                elif i == len(paragraphs) - 1:  # Último párrafo
                    score += 2
                elif i < len(paragraphs) * 0.3:  # Primeros 30%
                    score += 1
                
                # Puntos por longitud óptima
                if 100 <= len(paragraph) <= 300:
                    score += 1
                
                # Puntos si contiene frases clave
                if any(phrase.lower() in paragraph.lower() for phrase in key_phrases):
                    score += 2
                
                paragraph_scores.append((paragraph, score))
            
            # Ordenar por puntuación
            paragraph_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Seleccionar los mejores párrafos para el resumen
            summary_paragraphs = []
            summary_length = 0
            
            for paragraph, score in paragraph_scores:
                if summary_length + len(paragraph) <= self.max_summary_length:
                    summary_paragraphs.append(paragraph)
                    summary_length += len(paragraph)
                
                if summary_length >= self.max_summary_length * 0.8:
                    break
            
            # Si no tenemos suficiente contenido, añadir párrafos adicionales
            if len(summary_paragraphs) == 0:
                summary_paragraphs = [paragraphs[0]]  # Al menos el primer párrafo
            elif len(summary_paragraphs) == 1 and len(paragraphs) > 1:
                # Añadir segundo párrafo si hay espacio
                if summary_length + len(paragraphs[1]) <= self.max_summary_length:
                    summary_paragraphs.append(paragraphs[1])
            
            # Crear resumen final
            summary = '\n\n'.join(summary_paragraphs)
            
            # Truncar si es necesario
            if len(summary) > self.max_summary_length:
                summary = summary[:self.max_summary_length]
                # Cortar en la última oración completa
                last_sentence = summary.rfind('.')
                if last_sentence > self.max_summary_length * 0.7:
                    summary = summary[:last_sentence + 1]
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generando resumen tradicional: {e}")
            return self._simple_summary(content)
    
    def _simple_summary(self, content: str) -> str:
        """Genera un resumen simple como fallback"""
        if not content:
            return ""
        
        # Dividir en párrafos
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs:
            # Si no hay párrafos, tomar las primeras oraciones
            sentences = re.split(r'[.!?]+', content)
            sentences = [s.strip() for s in sentences if s.strip() and len(s) > 20]
            
            summary = ""
            for sentence in sentences[:3]:  # Máximo 3 oraciones
                if len(summary + sentence) <= self.max_summary_length:
                    summary += sentence + ". "
                else:
                    break
            
            return summary.strip()
        
        # Tomar los primeros párrafos más sustanciales
        summary_parts = []
        total_length = 0
        
        for paragraph in paragraphs:
            if len(paragraph) > 50 and total_length < self.max_summary_length:
                summary_parts.append(paragraph)
                total_length += len(paragraph)
            
            if total_length >= self.max_summary_length:
                break
        
        summary = '\n\n'.join(summary_parts)
        
        # Truncar si es necesario
        if len(summary) > self.max_summary_length:
            summary = summary[:self.max_summary_length].rsplit('.', 1)[0] + "."
        
        return summary
    
    def get_content_comparison(self, original: str, summary: str) -> Dict[str, Any]:
        """Compara el contenido original con el resumen"""
        try:
            orig_analysis = self._analyze_text_structure(original)
            summ_analysis = self._analyze_text_structure(summary)
            
            compression_ratio = (len(summary) / len(original)) * 100 if original else 0
            
            return {
                'original_stats': orig_analysis,
                'summary_stats': summ_analysis,
                'compression_ratio': compression_ratio,
                'words_reduced': orig_analysis['word_count'] - summ_analysis['word_count'],
                'reading_time_saved': orig_analysis['reading_time_minutes'] - summ_analysis['reading_time_minutes']
            }
            
        except Exception as e:
            logger.error(f"Error comparando contenido: {e}")
            return {}
    
    def get_summarizer_status(self) -> Dict[str, Any]:
        """Obtiene el estado de los resumidores disponibles"""
        service = get_apple_intelligence_service()
        status = {
            'traditional_algorithm': True,  # Siempre disponible
            'apple_intelligence': {
                'enabled': self.use_apple_intelligence,
                'available': is_apple_intelligence_available(),
                'status': service.get_status()
            }
        }
        
        return status
    
    def set_apple_intelligence_enabled(self, enabled: bool):
        """Habilita o deshabilita el uso de Apple Intelligence"""
        self.use_apple_intelligence = enabled
        config_manager.set('content.use_apple_intelligence', enabled)
        logger.info(f"Apple Intelligence {'habilitado' if enabled else 'deshabilitado'} para resúmenes")
