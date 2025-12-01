# app/reports.py
from app.db import get_conn
from datetime import time, datetime, date

def _to_str_time(value):
    """Convierte time/datetime/string a formato 'HH:MM'. Manejo seguro."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value[:5]  # "HH:MM:SS" → "HH:MM"
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    return ""


def _to_str_date(value):
    """Convierte date/datetime a 'YYYY-MM-DD'."""
    if value is None:
        return ""
    if isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    if isinstance(value, datetime):
        return value.date().strftime("%Y-%m-%d")
    return ""


def reporte_asistencia_aula(id_aula: int, id_semana: int | None = None):
    """
    Reporte completo de asistencia de un aula.
    Incluye institución, horario, motivos, festivos y reposiciones.
    """
    conn = get_conn()
    cur = conn.cursor()

    try:
        sql = """
        SELECT 
            inst.nombre_inst, 
            au.id_aula,
            aa.id_asist,
            aa.fecha_clase,
            aa.hora_inicio,
            CASE WHEN f.id_festivo IS NOT NULL THEN 'S' ELSE 'N' END AS es_festivo,
            h.dia_semana,
            h.h_inicio,
            h.h_final,
            aa.dictada,
            aa.horas_dictadas,
            m.descripcion AS motivo,
            aa.reposicion,
            aa.fecha_reposicion,
            at.id_persona AS id_tutor_persona,
            aa.id_motivo
        FROM ASISTENCIA_AULA aa
        JOIN AULA au ON aa.id_aula = au.id_aula
        JOIN INSTITUCION inst ON au.id_institucion = inst.id_institucion

        LEFT JOIN FESTIVO f ON CAST(aa.fecha_clase AS DATE) = CAST(f.fecha AS DATE)

        LEFT JOIN HORARIO h ON aa.id_horario = h.id_horario
        LEFT JOIN MOTIVO_INASISTENCIA m ON aa.id_motivo = m.id_motivo
        LEFT JOIN ASIGNACION_TUTOR at ON aa.id_tutor_aula = at.id_tutor_aula

        WHERE au.id_aula = :id_aula
        """

        params = {"id_aula": id_aula}

        if id_semana:
            sql += " AND aa.id_semana = :id_semana"
            params["id_semana"] = id_semana

        sql += " ORDER BY aa.fecha_clase, aa.hora_inicio"

        cur.execute(sql, params)

        rows = cur.fetchall()
        columns = [col[0].lower() for col in cur.description]

        result = []

        for row in rows:
            d = dict(zip(columns, row))

            # Normalizar fechas y horas
            d["fecha_clase"] = _to_str_date(d.get("fecha_clase"))
            d["fecha_reposicion"] = _to_str_date(d.get("fecha_reposicion"))
            d["hora_inicio"] = _to_str_time(d.get("hora_inicio"))
            d["h_inicio"] = _to_str_time(d.get("h_inicio"))
            d["h_final"] = _to_str_time(d.get("h_final"))

            result.append(d)

        return result

    finally:
        cur.close()
        conn.close()
