# 📡 WhatsApp Instalaciones — Parser & Dashboard

> **Versión:** `v1.0.0`  
> **Estado:** ✅ Listo para producción

---

## ¿Qué hace esta app?

Procesa archivos de chat exportados de WhatsApp con reportes de **instalación**, **enrutamiento** y **relevamiento** de fibra óptica. Extrae automáticamente actividades, las clasifica por tipo y estado, y genera reportes visuales y archivos de descarga.

---

## 🚀 Funcionalidades

### 📊 App Streamlit (2 pestañas)
| Pestaña | Descripción |
|---|---|
| **Actividades** | Vista interactiva de todas las actividades con filtros |
| **Dashboard** | KPIs, Top Clientes, Top Técnicos, Tipos de Actividad, Ciudades |

### 📁 Archivos de descarga
| Archivo | Descripción |
|---|---|
| `Actividades_Instalaciones.xlsx` | Excel formateado con 3 hojas |
| `Actividades_Instalaciones.json` | JSON con todas las actividades |
| `Actividades_Instalaciones.csv` | CSV para análisis externo |

### 📋 Excel — Hojas
| Hoja | Contenido |
|---|---|
| **Actividades** | Todas las actividades con formato profesional, filas coloreadas por estado |
| **Resumen** | Dashboard visual con KPIs y tablas de Top Clientes, Técnicos, Tipos, Ciudades |
| **Chat_WhatsApp** | Mensajes crudos del chat parseados |

### 🏷️ Tipos de Actividad
- **Instalación** — Instalación de fibra óptica
- **Enrutamiento** — Configuración de rutas
- **Relevamiento** — Inspección técnica
- **Visita** — Visitas de coordinación
- **Tendido** — Despliegue de cables
- **Mantenimiento** — Reparaciones

### 🚦 Estados detectados automáticamente
| Estado | Color | Descripción |
|--------|-------|-------------|
| **Completada** | Verde | Actividad finalizada |
| **En Progreso** | Amarillo | Actividad iniciada |
| **Suspendida** | Naranja | Actividad pausada |
| **En Sitio** | Azul claro | Técnico validando permisos |
| **Pendiente Autorización** | Naranja claro | Esperando aprobación |

---

## 🗂️ Estructura del proyecto

```
whatapp-instalaciones/
├── app.py                     # App principal Streamlit
├── parser_actividades.py      # Motor de parseo del chat
├── exportadores.py            # Generación de Excel, JSON, CSV
├── requirements.txt           # Dependencias
└── README.md
```

---

## 📦 Instalación local

```bash
git clone https://github.com/jaguos/Whatapp-instalaciones.git
cd Whatapp-instalaciones
pip install -r requirements.txt
streamlit run app.py
```

---

## 🔧 Uso

1. Exporta el chat de WhatsApp del grupo de instalaciones
2. Sube el archivo `.txt` en la app
3. Visualiza el dashboard interactivo
4. Descarga Excel, JSON o CSV

---

## 📝 Formato esperado del chat

```
CIUDAD: Bucaramanga
ING CARGO: Javier Gutierrez
CLIENTE: fiber group vitelsa
DIRECCIÓN: parque industrial
TIPO DE ACTIVIDA: instalación
AVANCE: se inicia actividad
```

---

> Desarrollado para equipos de instalaciones de fibra óptica. 2026.
