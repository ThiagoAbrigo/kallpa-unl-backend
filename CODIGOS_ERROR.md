# Códigos de Error del Controlador de Asistencia

## Resumen de Actualización
Se agregaron códigos de error HTTP consistentes al `AttendanceController` siguiendo el patrón del `AssessmentController`.

## Códigos de Error Implementados

### 400 - Bad Request (Errores de Validación)
Usados cuando el cliente envía datos inválidos o incompletos:

- ✅ **Campos faltantes**: Cuando faltan campos requeridos
- ✅ **Estados inválidos**: Cuando el status no es `present` o `absent`
- ✅ **Formato de fecha inválido**: Cuando la fecha no está en formato YYYY-MM-DD
- ✅ **Asistencia duplicada**: Cuando ya existe registro para el participante/horario/fecha
- ✅ **Cupos llenos**: Cuando la sesión no tiene cupos disponibles
- ✅ **Programa inválido**: Cuando el programa no es INICIACION o FUNCIONAL
- ✅ **Formato de hora inválido**: Cuando la hora no está en formato HH:MM
- ✅ **Hora inicio >= hora fin**: Cuando la hora de inicio es igual o mayor a la de fin
- ✅ **Día inválido**: Cuando el día de la semana no es válido
- ✅ **Cupos negativos**: Cuando el número de cupos es <= 0
- ✅ **Fecha pasada**: Cuando se intenta crear sesión con fecha anterior a hoy
- ✅ **Solapamiento de horarios**: Cuando el horario se solapa con otro existente

### 404 - Not Found
Usados cuando no se encuentra el recurso solicitado:

- ✅ **Participante no encontrado**: El external_id del participante no existe
- ✅ **Horario no encontrado**: El external_id del schedule no existe
- ✅ **Asistencia no encontrada**: El external_id de la asistencia no existe

### 500 - Internal Server Error
Usados para errores inesperados del servidor:

- ✅ **Excepciones generales**: Cualquier error no controlado en try/catch
- ✅ **Errores de base de datos**: Rollback automático con código 500

## Métodos Actualizados

### Registro de Asistencia
- `register_attendance()` - ✅
- `register_bulk_attendance()` - ✅

### Obtener Asistencias
- `get_attendances()` - ✅
- `get_attendance_by_id()` - ✅
- `get_participant_summary()` - ✅

### Actualizar/Eliminar Asistencias
- `update_attendance()` - ✅
- `delete_attendance()` - ✅

### Gestión de Horarios
- `create_schedule()` - ✅
- `update_schedule()` - ✅
- `delete_schedule()` - ✅
- `get_schedules()` - ✅

### Métodos Públicos
- `get_participants()` - ✅
- `get_today_sessions()` - ✅
- `get_history()` - ✅
- `get_programs()` - ✅
- `get_session_detail()` - ✅
- `delete_session_attendance()` - ✅

## Ejemplos de Respuestas

### Error 400 - Validación
```json
{
  "code": 400,
  "status": "error",
  "msg": "Falta el campo requerido: participant_external_id",
  "data": null
}
```

### Error 404 - No Encontrado
```json
{
  "code": 404,
  "status": "error",
  "msg": "Participante no encontrado",
  "data": null
}
```

### Error 500 - Error Interno
```json
{
  "code": 500,
  "status": "error",
  "msg": "Error interno: [descripción del error]",
  "data": null
}
```

## Consistencia con AssessmentController

El `AttendanceController` ahora sigue el mismo patrón de códigos de error que el `AssessmentController`:

| Situación | AssessmentController | AttendanceController |
|-----------|---------------------|---------------------|
| Campos inválidos | 400 | 400 ✅ |
| Recurso no existe | 404 | 404 ✅ |
| Error del servidor | 500 | 500 ✅ |
| Validación múltiple | Diccionario de errores | Mensaje directo |

## Testing

- ✅ **33/33 pruebas** de asistencia pasando
- ✅ **3/3 pruebas** de evaluación pasando
- ✅ Todos los códigos de error verificados con tests unitarios

## Autor
- Actualización: Elías Poma
- Fecha: 7 de enero de 2026
- Patrón base: Santiago (AssessmentController)
