# Eliminación Avanzada de Fuentes de Datos

## Descripción

Esta funcionalidad permite eliminar completamente una fuente de datos junto con todos sus contenidos asociados, incluyendo:
- Registros de la fuente en la base de datos
- Todos los items de contenido relacionados
- Archivos de audio generados
- Registros de procesamiento y logs
- Directorios vacíos resultantes

## Características Principales

### 1. Análisis Previo de Eliminación
- **Información detallada**: Muestra exactamente qué se eliminará antes de proceder
- **Cálculo de espacio**: Estima el espacio en disco que se liberará
- **Lista de archivos**: Muestra los archivos específicos que se eliminarán

### 2. Diálogo de Confirmación Avanzada
- **Interfaz intuitiva**: Presenta toda la información de manera clara
- **Confirmación explícita**: Requiere que el usuario confirme entendiendo las consecuencias
- **Prevención de errores**: Desactiva el botón de eliminación hasta confirmar

### 3. Eliminación Segura
- **Orden correcto**: Elimina primero los archivos físicos, luego los registros de BD
- **Manejo de errores**: Continúa la eliminación aunque algunos archivos no existan
- **Limpieza completa**: Elimina directorios vacíos resultantes
- **Logging detallado**: Registra todas las operaciones para auditoría

### 4. Reporte de Resultados
- **Confirmación visual**: Muestra qué se eliminó exitosamente
- **Estadísticas**: Número de items, archivos y espacio liberado
- **Detalles expandibles**: Información completa disponible en un clic

## Flujo de Eliminación

```
1. Usuario selecciona fuente → 2. Análisis de contenido → 3. Diálogo de confirmación
         ↓                              ↓                           ↓
4. Confirmación usuario → 5. Eliminación archivos → 6. Eliminación BD → 7. Reporte
```

## Archivos Involucrados

### Nuevos Archivos

1. **`utils/file_manager.py`**
   - Gestión segura de archivos
   - Eliminación de archivos de audio
   - Limpieza de directorios vacíos
   - Formateo de tamaños de archivo

2. **`app/dialogs/delete_confirmation_dialog.py`**
   - Diálogo de confirmación avanzada
   - Presentación de información de eliminación
   - Interfaz visual intuitiva

3. **`test_advanced_deletion.py`**
   - Script de prueba y demostración
   - Casos de prueba para todas las funcionalidades
   - Creación de datos de prueba

### Archivos Modificados

1. **`models/database.py`**
   - `get_source_deletion_info()`: Obtiene información completa de eliminación
   - `delete_data_source_and_content()`: Elimina fuente y contenido asociado
   - `update_content_item_text()`: Método adicional para edición de texto

2. **`app/widgets/data_source_widget.py`**
   - `remove_selected_source()`: Implementación completa de eliminación
   - `_perform_deletion()`: Lógica de eliminación paso a paso
   - `_show_deletion_report()`: Reporte visual de resultados

## Métodos Principales

### DatabaseManager

```python
def get_source_deletion_info(self, source_id: int) -> Dict[str, Any]:
    """Obtiene información detallada sobre lo que se eliminará"""
    
def delete_data_source_and_content(self, source_id: int) -> bool:
    """Elimina una fuente de datos y todo su contenido asociado"""
```

### FileManager

```python
def delete_audio_files(file_paths: List[str]) -> Dict[str, Any]:
    """Elimina archivos de audio de manera segura"""
    
def clean_empty_directories(directory: Path) -> int:
    """Limpia directorios vacíos de manera recursiva"""
```

### DeleteConfirmationDialog

```python
def __init__(self, deletion_info: Dict[str, Any], parent=None):
    """Crea diálogo con información de eliminación"""
```

## Casos de Uso

### 1. Eliminación de Fuente con Pocos Elementos
- Fuente con 1-5 items de contenido
- Algunos archivos de audio
- Confirmación simple y rápida

### 2. Eliminación de Fuente con Muchos Elementos
- Fuente con decenas de items
- Múltiples archivos de audio
- Vista con scroll para todos los detalles

### 3. Eliminación de Fuente Vacía
- Solo registro de fuente sin contenido
- Confirmación mínima
- Eliminación instantánea

### 4. Manejo de Errores
- Archivos no encontrados (continúa)
- Errores de permisos (registra y continúa)
- Errores de BD (aborta con mensaje)

## Pruebas

### Script de Prueba Automática
```bash
python test_advanced_deletion.py
```

### Funcionalidades Probadas
1. ✅ Obtención de información de eliminación
2. ✅ Diálogo de confirmación visual
3. ✅ Operaciones de archivos seguras
4. ✅ Creación de datos de prueba

### Casos de Prueba Manual
1. **Eliminar fuente con contenido**: Verificar eliminación completa
2. **Cancelar eliminación**: Verificar que nada se elimina
3. **Fuente inexistente**: Manejo graceful de errores
4. **Archivos no encontrados**: Continúa sin fallos

## Configuración

Las rutas y configuraciones relevantes están en `utils/config.py`:

```json
{
  "audio": {
    "output_dir": "podcasts"
  },
  "database": {
    "path": "data/pypodcast.db"
  }
}
```

## Logging

Todas las operaciones se registran con diferentes niveles:

- **INFO**: Operaciones exitosas
- **WARNING**: Archivos no encontrados, pero operación continúa
- **ERROR**: Errores que impiden la operación

Ejemplo de logs:
```
INFO: Archivo eliminado: /ruta/audio.wav (2048 bytes)
WARNING: Archivo no encontrado para eliminar: /ruta/inexistente.wav
INFO: Fuente de datos 123 y todo su contenido eliminado exitosamente
```

## Seguridad

### Prevención de Eliminación Accidental
- Diálogo de confirmación obligatorio
- Checkbox explícito de entendimiento
- Información detallada antes de proceder

### Integridad de Datos
- Eliminación en orden correcto (archivos → BD)
- Transacciones de BD para consistencia
- Manejo de foreign keys

### Recuperación
- Logging completo para auditoría
- Los datos de BD se pueden recuperar de backups
- Los archivos de audio se pueden regenerar desde texto

## Limitaciones Conocidas

1. **Cálculo de Tamaño**: El tamaño estimado es aproximado
2. **Rollback**: No hay rollback automático si falla parcialmente
3. **Archivos Externos**: Solo elimina archivos en directorios gestionados

## Futuras Mejoras

1. **Backup Automático**: Crear backup antes de eliminar
2. **Eliminación Diferida**: Papelera temporal con recuperación
3. **Cálculo Exacto**: Tamaño real de archivos antes de eliminar
4. **Progreso Visual**: Barra de progreso para eliminaciones grandes
