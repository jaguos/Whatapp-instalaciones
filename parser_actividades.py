import pandas as pd
import re
from pathlib import Path
from collections import Counter
from datetime import datetime, timedelta


def parse_fecha_whatsapp(fecha_str, hora_str):
    """Convierte DD/MM/YYYY y HH:MM a.m./p.m. a datetime."""
    try:
        d, m, y = map(int, fecha_str.split("/"))
        hora_clean = re.sub(r"\s+", " ", hora_str.strip())
        am_pm = "pm" if "p" in hora_clean.lower() else "am"
        hm = re.search(r"(\d{1,2}):(\d{2})", hora_clean)
        if not hm:
            return None
        h, mi = int(hm.group(1)), int(hm.group(2))
        if am_pm == "pm" and h != 12:
            h += 12
        if am_pm == "am" and h == 12:
            h = 0
        return datetime(y, m, d, h, mi)
    except:
        return None


def parse_fecha_compacta(fecha_raw):
    """Convierte DDMMYYYY a datetime."""
    try:
        return datetime(int(fecha_raw[4:8]), int(fecha_raw[2:4]), int(fecha_raw[0:2]))
    except:
        return None


def normalizar_tipo(tipo):
    t = tipo.lower().strip()
    if "instalaci" in t or "instalacion" in t:
        return "Instalación"
    elif "enrrutamiento" in t or "enrutamiento" in t or "entretenimiento" in t:
        return "Enrutamiento"
    elif "relevamiento" in t:
        return "Relevamiento"
    elif "visita" in t:
        return "Visita"
    elif "tendido" in t:
        return "Tendido"
    elif "mantenimiento" in t or "preventivo" in t:
        return "Mantenimiento"
    elif "habilitaci" in t:
        return "Habilitación"
    elif "sellamiento" in t:
        return "Sellamiento"
    else:
        return tipo.title().strip()


def detectar_estado_final(avances_list):
    """Determina el estado final basado en todos los avances de la sesión."""
    texto = " ".join(avances_list).lower()
    if any(x in texto for x in ["se finaliza", "se finalizo", "finaliza actividad",
                                  "se realiza enrutamiento", "se cierra", "reflejo ok",
                                  "completad", "actividad finalizada"]):
        return "Completada"
    elif any(x in texto for x in ["se suspende", "suspendida", "para el dia de mañana",
                                   "maana se siguen", "queda pendiente"]):
        return "Suspendida"
    else:
        return "En Progreso"


def procesar_chat_instalaciones(file_path):
    """
    Procesa chat de WhatsApp de instalaciones.
    Agrupa reportes por cliente+ciudad en sesiones (corte si gap > 3 dias).
    Retorna FECHA_INICIO, HORA_INICIO, FECHA_FIN, HORA_FIN, DURACION_DIAS por sesion.
    """
    content = Path(file_path).read_text(encoding="utf-8", errors="ignore")
    print(f"Archivo cargado: {len(content):,} caracteres")

    pattern = (
        r"(\d{1,2}/\d{1,2}/\d{4},\s*\d{1,2}:\d{2}\s*(?:p\.?\s*m\.|a\.?\s*m\.)?)\s*-\s*[^:\n]+:\s*"
        r"(?:(?:Bueno|Buenos|Buena)\s+(?:días|dias|tardes|noches|día)[^\n]*)?\s*"
        r"(?:Fecha\s*(\d{8}))?\s*"
        r"CIUDAD[:\s]*([^\n]+)\s*"
        r"ING[\s\.]*(?:CARGO)?[:\s]*([^\n]+)\s*"
        r"CLIENTE[:\s]*([^\n]+)\s*"
        r"DIRECCI[OÓ]N[:\s]*([^\n]+)\s*"
        r"TIPO\s+DE\s+ACTIVIDA[D]?[:\s]*([^\n]+)\s*"
        r"AVANCE[:\s]*(.+?)(?=\d{1,2}/\d{1,2}/\d{4},\s*\d{1,2}:\d{2}|\Z)"
    )

    matches = list(re.finditer(pattern, content, re.DOTALL | re.IGNORECASE))
    print(f"Reportes crudos encontrados: {len(matches)}")

    # Extraer reportes individuales
    reportes = []
    for m in matches:
        ts_str     = m.group(1) or ""
        fecha_comp = m.group(2)
        ciudad     = (m.group(3) or "N/A").strip()
        ing_cargo  = (m.group(4) or "N/A").strip()
        cliente    = (m.group(5) or "N/A").strip().lower()
        direccion  = (m.group(6) or "N/A").strip()
        tipo_raw   = (m.group(7) or "N/A").strip()
        avance     = re.sub(r"\s+", " ", (m.group(8) or "N/A")).strip()

        ts_m = re.search(
            r"(\d{1,2}/\d{1,2}/\d{4}),\s*(\d{1,2}:\d{2}\s*(?:p\.?\s*m\.|a\.?\s*m\.)?)",
            ts_str, re.IGNORECASE
        )
        if ts_m:
            dt = parse_fecha_whatsapp(ts_m.group(1), ts_m.group(2))
        elif fecha_comp:
            dt = parse_fecha_compacta(fecha_comp)
        else:
            dt = None

        if dt is None:
            continue

        reportes.append({
            "dt":        dt,
            "ciudad":    ciudad,
            "ing_cargo": ing_cargo,
            "cliente":   cliente,
            "direccion": direccion,
            "tipo":      normalizar_tipo(tipo_raw),
            "avance":    avance[:300],
        })

    # Ordenar cronologicamente
    reportes.sort(key=lambda r: r["dt"])

    # Agrupar en sesiones: mismo cliente+ciudad, gap max 3 dias = sede diferente
    MAX_GAP = timedelta(days=3)
    ultimo_dt = {}
    sesion_idx = {}
    sesiones = {}

    for r in reportes:
        key = (r["cliente"], r["ciudad"].lower())
        if key not in ultimo_dt:
            sesion_idx[key] = 1
        else:
            if r["dt"] - ultimo_dt[key] > MAX_GAP:
                sesion_idx[key] += 1
        ultimo_dt[key] = r["dt"]
        fk = (r["cliente"], r["ciudad"].lower(), sesion_idx[key])
        sesiones.setdefault(fk, []).append(r)

    print(f"Sesiones unicas: {len(sesiones)}")

    # Construir DataFrame final
    rows = []
    for i, ((cliente, ciudad, _), reps) in enumerate(sesiones.items(), 1):
        dts     = [r["dt"] for r in reps]
        dt_i    = min(dts)
        dt_f    = max(dts)
        tipos   = list(dict.fromkeys([r["tipo"] for r in reps]))
        avances = [r["avance"] for r in reps]

        rows.append({
            "ID":             f"SES{i:04d}",
            "CLIENTE":        reps[0]["cliente"].title(),
            "CIUDAD":         reps[0]["ciudad"],
            "ING_CARGO":      reps[0]["ing_cargo"],
            "DIRECCION":      reps[0]["direccion"],
            "FECHA_INICIO":   dt_i.strftime("%d/%m/%Y"),
            "HORA_INICIO":    dt_i.strftime("%I:%M %p"),
            "FECHA_FIN":      dt_f.strftime("%d/%m/%Y"),
            "HORA_FIN":       dt_f.strftime("%I:%M %p"),
            "DURACION_DIAS":  (dt_f.date() - dt_i.date()).days,
            "TIPO_ACTIVIDAD": " / ".join(tipos),
            "TOTAL_REPORTES": len(reps),
            "ESTADO":         detectar_estado_final(avances),
            "AVANCE_FINAL":   avances[-1] if avances else "N/A",
        })

    df_actividades = pd.DataFrame(rows)

    stats = {
        "total_sesiones":  len(rows),
        "total_reportes":  len(reportes),
        "por_tipo":        dict(Counter([t for r in rows for t in r["TIPO_ACTIVIDAD"].split(" / ")]).most_common()),
        "por_estado":      dict(Counter(df_actividades["ESTADO"].tolist())),
        "por_ciudad":      dict(Counter(df_actividades["CIUDAD"].tolist())),
        "top_clientes":    dict(Counter(df_actividades["CLIENTE"].tolist()).most_common(10)),
        "top_tecnicos":    dict(Counter(df_actividades["ING_CARGO"].tolist()).most_common(10)),
    }

    lines = content.splitlines()
    df_chat = pd.DataFrame([{"line_id": i, "raw": l.strip()} for i, l in enumerate(lines) if l.strip()])

    print(f"Sesiones procesadas: {len(df_actividades)} | Reportes crudos: {len(reportes)}")
    return df_actividades, df_chat, stats
