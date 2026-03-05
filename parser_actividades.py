import pandas as pd
import re
from pathlib import Path
from collections import Counter, defaultdict
from datetime import datetime


def extraer_timestamp(ts_str):
    """Extrae fecha y hora de un timestamp WhatsApp."""
    if not ts_str:
        return None, None
    
    match = re.search(r"(\d{1,2}/\d{1,2}/\d{4}),\s*(\d{1,2}:\d{2}\s*(?:p\.\s*m\.|a\.\s*m\.)?)", ts_str, re.IGNORECASE)
    if match:
        return match.group(1).strip(), match.group(2).strip()
    return None, None


def normalizar_tipo_actividad(tipo):
    """Normaliza tipos de actividad a categorías estándar."""
    tipo_lower = tipo.lower().strip()
    
    if "instalaci" in tipo_lower or "instalacion" in tipo_lower:
        return "Instalación"
    elif "enrrutamiento" in tipo_lower or "enrutamiento" in tipo_lower:
        return "Enrutamiento"
    elif "relevamiento" in tipo_lower:
        return "Relevamiento"
    elif "visita" in tipo_lower:
        return "Visita"
    elif "tendido" in tipo_lower:
        return "Tendido"
    elif "mantenimiento" in tipo_lower:
        return "Mantenimiento"
    elif "habilitaci" in tipo_lower:
        return "Habilitación"
    else:
        return tipo.title()


def detectar_estado(avance):
    """Detecta el estado de la actividad según el texto del avance."""
    avance_lower = avance.lower()
    
    if any(x in avance_lower for x in ["se finaliza", "se realiza", "se cierra", "finalizada", "completada"]):
        return "Completada"
    elif any(x in avance_lower for x in ["se inicia", "se comienza", "iniciando"]):
        return "En Progreso"
    elif any(x in avance_lower for x in ["se suspende", "suspendida", "pendiente", "a la espera", "esperando"]):
        return "Suspendida"
    elif any(x in avance_lower for x in ["en sitio", "validando permisos", "verificando permisos"]):
        return "En Sitio"
    elif any(x in avance_lower for x in ["solicita", "solicitud", "autorización"]):
        return "Pendiente Autorización"
    else:
        return "En Progreso"


def procesar_chat_instalaciones(file_path):
    """Procesa chat de WhatsApp con reportes de instalaciones/enrutamiento."""
    
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    print(f"Archivo cargado: {len(content):,} caracteres")
    
    # Patrón para detectar bloques de reporte
    pattern = r"(\d{1,2}/\d{1,2}/\d{4},\s*\d{1,2}:\d{2}\s*(?:p\.\s*m\.|a\.\s*m\.)?\s*-\s*[^:]+:\s*)?((?:Bueno|Buenos|Buena)\s+(?:días|dias|tardes|noches|día))?\s*(?:Fecha\s*\d{1,2}\d{1,2}\d{4})?\s*CIUDAD[:\s]*([^\n]+)?\s*ING[\s\.]?(?:CARGO)?[:\s]*([^\n]+)?\s*CLIENTE[:\s]*([^\n]+)?\s*DIRECCI[OÓ]N[:\s]*([^\n]+)?\s*TIPO\s+DE\s+ACTIVIDA[D]?[:\s]*([^\n]+)?\s*AVANCE[:\s]*(.+?)(?=\d{1,2}/\d{1,2}/\d{4},\s*\d{1,2}:\d{2}|Bueno|Buenos|Buena|CIUDAD|\Z)"
    
    matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
    print(f"Reportes encontrados: {len(matches)}")
    
    actividades = []
    id_counter = 1
    
    for match in matches:
        timestamp_str = match.group(1) or ""
        ciudad = (match.group(3) or "N/A").strip()
        ing_cargo = (match.group(4) or "N/A").strip()
        cliente = (match.group(5) or "N/A").strip()
        direccion = (match.group(6) or "N/A").strip()
        tipo_actividad = (match.group(7) or "N/A").strip()
        avance = (match.group(8) or "N/A").strip()
        
        # Extraer fecha y hora
        fecha, hora = extraer_timestamp(timestamp_str)
        if not fecha:
            # Buscar fecha en el contenido cercano
            fecha_match = re.search(r"Fecha\s*(\d{1,2}\d{1,2}\d{4})", match.group(0), re.IGNORECASE)
            if fecha_match:
                fecha_raw = fecha_match.group(1)
                try:
                    fecha = f"{fecha_raw[0:2]}/{fecha_raw[2:4]}/{fecha_raw[4:8]}"
                except:
                    fecha = "N/A"
            else:
                fecha = "N/A"
        
        if not hora:
            hora = "N/A"
        
        # Normalizar y detectar estado
        tipo_normalizado = normalizar_tipo_actividad(tipo_actividad)
        estado = detectar_estado(avance)
        
        # Limpiar avance de saltos de línea excesivos
        avance_limpio = re.sub(r"\s+", " ", avance).strip()
        
        actividades.append({
            "ID": f"ACT{id_counter:04d}",
            "FECHA": fecha,
            "HORA": hora,
            "CIUDAD": ciudad,
            "ING_CARGO": ing_cargo,
            "CLIENTE": cliente,
            "DIRECCION": direccion,
            "TIPO_ACTIVIDAD": tipo_normalizado,
            "ESTADO": estado,
            "AVANCE": avance_limpio[:500]  # Limitar a 500 caracteres
        })
        id_counter += 1
    
    # Crear DataFrame
    df_actividades = pd.DataFrame(actividades)
    
    # Estadísticas
    stats = {
        "total_actividades": len(actividades),
        "por_tipo": dict(Counter(df_actividades["TIPO_ACTIVIDAD"].tolist())),
        "por_estado": dict(Counter(df_actividades["ESTADO"].tolist())),
        "por_ciudad": dict(Counter(df_actividades["CIUDAD"].tolist())),
        "top_clientes": dict(Counter(df_actividades["CLIENTE"].tolist()).most_common(10)),
        "top_tecnicos": dict(Counter(df_actividades["ING_CARGO"].tolist()).most_common(10)),
    }
    
    print(f"\nActividades procesadas: {len(df_actividades)}")
    print(f"Por tipo: {stats['por_tipo']}")
    print(f"Por estado: {stats['por_estado']}")
    
    # Chat raw
    lines = content.splitlines()
    df_chat = pd.DataFrame([{"line_id": i, "raw": l.strip()} for i, l in enumerate(lines) if l.strip()])
    
    return df_actividades, df_chat, stats
