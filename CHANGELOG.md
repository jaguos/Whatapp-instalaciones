# Changelog

## [v1.0.0] - 2026-03-05

### ✅ Features Iniciales
- Parser especializado para reportes de instalaciones/enrutamiento/relevamiento
- Detección automática de tipos de actividad (Instalación, Enrutamiento, Relevamiento, etc.)
- Detección automática de estados (Completada, En Progreso, Suspendida, En Sitio, Pendiente)
- Dashboard Streamlit interactivo con:
  - Vista tabla de todas las actividades
  - KPIs: Total, Completadas, En Progreso, Suspendidas
  - Top Clientes más atendidos
  - Top Técnicos más productivos
  - Distribución por tipo de actividad
  - Distribución por ciudad
- Excel formateado con:
  - Hoja "Actividades" con filas coloreadas según estado
  - Hoja "Resumen" con dashboard visual (KPIs + tablas)
  - Hoja "Chat_WhatsApp" con mensajes crudos
  - Filtros automáticos, anchos dinámicos, formato profesional
- Exportación a JSON y CSV

### 📄 Estructura de datos
- Campos extraídos: ID, FECHA, HORA, CIUDAD, ING_CARGO, CLIENTE, DIRECCIÓN, TIPO_ACTIVIDAD, ESTADO, AVANCE
- Normalización de tipos de actividad
- Limpieza de avances (500 caracteres máximo)

### 🎨 Colores por estado
| Estado | Color |
|--------|-------|
| Completada | Verde |
| En Progreso | Amarillo |
| Suspendida | Naranja |
| En Sitio | Azul claro |
| Pendiente Autorización | Naranja claro |

---

## Roadmap v1.1
- [ ] Filtros por fecha en la app
- [ ] Agrupación por cliente con historial completo
- [ ] Timeline visual de actividades
- [ ] Métricas de días promedio por tipo de actividad
- [ ] Detección de actividades sin finalizar (más de X días)
