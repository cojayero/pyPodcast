# 🧪 Guía de Pruebas - pyPodcast

Esta guía explica cómo ejecutar y mantener las pruebas del proyecto pyPodcast.

## 🚀 Ejecución Rápida

```bash
# Ejecutar todas las pruebas y actualizar documentación
python run_tests.py

# Ejecutar solo prueba de componentes
python run_tests.py components

# Ejecutar solo pruebas de YouTube
python run_tests.py youtube

# Ejecutar pruebas extensas de YouTube
python run_tests.py youtube-extensive

# Ejecutar demostración de mejoras
python run_tests.py demo

# Solo actualizar documentación sin ejecutar pruebas
python run_tests.py --update-only
```

## 📁 Archivos de Prueba

| Archivo | Comando | Descripción |
|---------|---------|-------------|
| `test_components.py` | `python run_tests.py components` | Prueba todos los componentes principales |
| `test_youtube_improved.py` | `python run_tests.py youtube` | Prueba URLs problemáticas de YouTube |
| `test_youtube_extensive.py` | `python run_tests.py youtube-extensive` | Prueba exhaustiva con 22+ URLs |
| `demo_youtube_fixes.py` | `python run_tests.py demo` | Demostración de mejoras implementadas |

## 📝 Documentación Automática

El archivo `test.md` se actualiza automáticamente cada vez que ejecutas pruebas con:

- ✅ Resultados de cada prueba
- 📊 Estadísticas de éxito
- 📅 Timestamp de última ejecución
- 🔄 Estado general del sistema

## 🛠️ Scripts Utilitarios

- `update_test_docs.py` - Actualizador automático de documentación
- `run_tests.py` - Ejecutor inteligente de pruebas
- `add_sample_data.py` - Datos de ejemplo para pruebas

## 📋 Checklist de Pruebas

Antes de hacer un release, ejecuta:

1. ✅ `python run_tests.py components` - Componentes principales
2. ✅ `python run_tests.py youtube-extensive` - Robustez de YouTube
3. ✅ `python run_tests.py all` - Todas las pruebas
4. ✅ Verificar que `test.md` esté actualizado

## 🎯 Añadir Nuevas Pruebas

1. Crea tu archivo de prueba (ej: `test_nueva_funcionalidad.py`)
2. Añádelo a `test_files` en `update_test_docs.py`
3. Añade comando en `run_tests.py`
4. Ejecuta `python run_tests.py --update-only` para actualizar docs

## 🔍 Debugging

Si una prueba falla:

1. Ejecuta la prueba individual: `python test_archivo.py`
2. Revisa los logs en `logs/pypodcast_YYYYMMDD.log`
3. Verifica `test.md` para detalles del error
4. Usa el debug mode si está disponible

---

**¡Mantén las pruebas actualizadas para un código robusto! 🚀**
