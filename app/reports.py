# app/reports.py
from app.db import get_conn
from datetime import datetime

def reporte_asistencia_aula(id_aula, id_semana=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        sql = """
        SELECT 
          inst.nombre_inst, 
          au.id_aula,
          aa.id_asist, 
          aa.fecha_clase,
          aa.hora_inicio,                    -- <-- ¡ASEGÚRATE QUE ESTE ESTÉ AQUÍ!
          CASE WHEN f.id_festivo IS NOT NULL THEN 'S' ELSE 'N' END as es_festivo,
          h.dia_semana, h.h_inicio, h.h_final,
          aa.dictada, aa.horas_dictadas, m.descripcion motivo,
          aa.reposicion, aa.fecha_reposicion,
          at.id_persona as id_tutor_persona,
          aa.id_motivo                        -- Si quieres usar id_motivo
        FROM ASISTENCIA_AULA aa
        JOIN AULA au ON aa.id_aula = au.id_aula
        JOIN INSTITUCION inst ON au.id_institucion = inst.id_institucion
        LEFT JOIN FESTIVO f ON TRUNC(aa.fecha_clase)=f.fecha
        LEFT JOIN HORARIO h ON aa.id_horario = h.id_horario
        LEFT JOIN MOTIVO_INASISTENCIA m ON aa.id_motivo = m.id_motivo
        LEFT JOIN ASIGNACION_TUTOR at ON aa.id_tutor_aula = at.id_tutor_aula
        WHERE au.id_aula = :id_aula
        """
        params = [id_aula]
        if id_semana:
            sql += " AND aa.id_semana = :2"
            params.append(id_semana)
        sql += " ORDER BY aa.fecha_clase"
        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [c[0].lower() for c in cur.description]  # mejor lower por robustez
        result = []
        for r in rows:
            d = dict(zip(cols, r))
            # importante: si hora_inicio es datetime/time convierte a string HH:MM
            hi = d.get("hora_inicio")
            if hi is not None:
                if isinstance(hi, str):
                    d["hora_inicio"] = hi[:5]
                else:
                    # Si viene como time
                    d["hora_inicio"] = hi.strftime("%H:%M")
            else:
                d["hora_inicio"] = ""
            result.append(d)
        return result
    finally:
        cur.close()
        conn.close()


def reporte_asistencia_aula_rango(id_aula: int, fecha_inicio: str, fecha_fin: str):
    """
    Reporte de asistencia del aula en un rango de fechas.
    Usa: INSTITUCION, AULA, ASISTENCIA_AULA, SEMANA, ASIGNACION_TUTOR, PERSONA.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        sql = """
        SELECT
            i.nombre_inst                       AS nombre_inst,
            a.id_aula,
            a.grado                             AS grado,
            s.numero_semana                     AS numero_semana,
            aa.id_asist,
            aa.fecha_clase,
            aa.hora_inicio,
            aa.es_festivo,
            h.dia_semana,
            h.h_inicio,
            h.h_final,
            aa.dictada,
            aa.horas_dictadas,
            m.descripcion                        AS motivo,
            aa.reposicion,
            aa.fecha_reposicion,
            t.id_persona                         AS id_tutor_persona,
            p.nombre                             AS tutor,
            aa.id_motivo
        FROM ASISTENCIA_AULA aa
        JOIN AULA a
          ON a.id_aula = aa.id_aula
        JOIN INSTITUCION i
          ON i.id_institucion = a.id_institucion
        LEFT JOIN SEMANA s
          ON s.id_semana = aa.id_semana
        LEFT JOIN HORARIO h
          ON h.id_horario = aa.id_horario
        LEFT JOIN MOTIVO_INASISTENCIA m
          ON m.id_motivo = aa.id_motivo
        LEFT JOIN ASIGNACION_TUTOR t
          ON t.id_tutor_aula = aa.id_tutor_aula
        LEFT JOIN PERSONA p
          ON p.id_persona = t.id_persona
        WHERE aa.id_aula = :1
          AND TRUNC(aa.fecha_clase) BETWEEN :2 AND :3
        ORDER BY aa.fecha_clase, aa.hora_inicio
        """

        cur.execute(sql, [id_aula, f_ini, f_fin])
        cols = [c[0].lower() for c in cur.description]

        data = []
        for row in cur.fetchall():
            d = dict(zip(cols, row))

            # fechas a ISO string si quieres
            fc = d.get("fecha_clase")
            fr = d.get("fecha_reposicion")
            if fc:
                d["fecha_clase"] = fc.isoformat()
            if fr:
                d["fecha_reposicion"] = fr.isoformat()

            data.append({
                "nombre_inst": d.get("nombre_inst"),
                "id_aula": d.get("id_aula"),
                "grado": d.get("grado"),
                "numero_semana": d.get("numero_semana"),
                "id_asist": d.get("id_asist"),
                "fecha_clase": d.get("fecha_clase"),
                "hora_inicio": d.get("hora_inicio"),
                "es_festivo": d.get("es_festivo"),
                "dia_semana": d.get("dia_semana"),
                "h_inicio": d.get("h_inicio"),
                "h_final": d.get("h_final"),
                "dictada": d.get("dictada"),
                "horas_dictadas": d.get("horas_dictadas"),
                "motivo": d.get("motivo"),
                "reposicion": d.get("reposicion"),
                "fecha_reposicion": d.get("fecha_reposicion"),
                "id_tutor_persona": d.get("id_tutor_persona"),
                "tutor": d.get("tutor"),
                "id_motivo": d.get("id_motivo"),
            })

        return data
    finally:
        cur.close()
        conn.close()



def reporte_asistencia_estudiante_rango(id_estudiante: int, fecha_inicio: str, fecha_fin: str):
    """
    Reporte de asistencia de un estudiante en un rango de fechas.
    Solo muestra: fecha, semana, institución, aula, grado, tutor, día,
    hora inicio/fin y si asistió.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
        f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()

        sql = """
        SELECT
            aa.fecha_clase                      AS fecha_clase,
            s.numero_semana                     AS numero_semana,
            i.nombre_inst                       AS nombre_inst,
            a.id_aula                           AS id_aula,
            a.grado                             AS grado,
            p.nombre                            AS tutor,
            h.dia_semana                        AS dia_semana,
            h.h_inicio                          AS h_inicio,
            h.h_final                           AS h_final,
            NVL(ae.asistio, 'N')                AS asistio
        FROM ASISTENCIA_AULA aa
        JOIN AULA a
          ON aa.id_aula = a.id_aula
        JOIN INSTITUCION i
          ON i.id_institucion = a.id_institucion
        LEFT JOIN SEMANA s
          ON s.id_semana = aa.id_semana
        LEFT JOIN HORARIO h
          ON h.id_horario = aa.id_horario
        LEFT JOIN ASIGNACION_TUTOR at
          ON at.id_tutor_aula = aa.id_tutor_aula
        LEFT JOIN PERSONA p
          ON p.id_persona = at.id_persona
        JOIN HISTORICO_AULA_ESTUDIANTE hae
          ON hae.id_aula = aa.id_aula
         AND (hae.fecha_fin IS NULL OR hae.fecha_fin >= aa.fecha_clase)
         AND hae.fecha_inicio <= aa.fecha_clase
        JOIN ESTUDIANTE e
          ON e.id_estudiante = hae.id_estudiante
        LEFT JOIN ASISTENCIA_ESTUDIANTE ae
          ON ae.id_asist = aa.id_asist
         AND ae.id_estudiante = e.id_estudiante
        WHERE e.id_estudiante = :1
          AND aa.fecha_clase BETWEEN :2 AND :3
        ORDER BY aa.fecha_clase, h.h_inicio
        """

        cur.execute(sql, [id_estudiante, f_ini, f_fin])
        cols = [c[0].lower() for c in cur.description]

        data = []
        for row in cur.fetchall():
            d = dict(zip(cols, row))

            fc = d.get("fecha_clase")
            if isinstance(fc, datetime):
                d["fecha_clase"] = fc.date().isoformat()
            elif fc:
                d["fecha_clase"] = fc.isoformat()

            data.append({
                "fecha_clase": d.get("fecha_clase"),
                "numero_semana": d.get("numero_semana"),
                "nombre_inst": d.get("nombre_inst"),
                "id_aula": d.get("id_aula"),
                "grado": d.get("grado"),
                "tutor": d.get("tutor"),
                "dia_semana": d.get("dia_semana"),
                "hora_inicio": d.get("h_inicio"),
                "hora_fin": d.get("h_final"),
                "asistio": d.get("asistio"),
            })

        return data
    finally:
        cur.close()
        conn.close()

def boletin_estudiante_periodo(id_estudiante: int, id_periodo: int):
    """
    Boletín de calificaciones de un estudiante en un periodo:
    institución, grado, programa, periodo, componentes, nota y definitiva.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Datos básicos: institución, grado y programa (INSIDE/OUTSIDE)
        sql_info = """
        SELECT
            i.nombre_inst,
            a.grado,
            c.tipo_programa,
            p.nombre AS nombre_periodo
        FROM HISTORICO_AULA_ESTUDIANTE hae
        JOIN AULA a
          ON a.id_aula = hae.id_aula
        JOIN SEDE s
          ON s.id_institucion = a.id_institucion
         AND s.id_sede = a.id_sede
        JOIN INSTITUCION i
          ON i.id_institucion = s.id_institucion
        JOIN COMPONENTE c
          ON c.id_periodo = :idp
        JOIN PERIODO p
          ON p.id_periodo = c.id_periodo
        WHERE hae.id_estudiante = :ide
          AND (hae.fecha_fin IS NULL OR hae.fecha_fin >= p.fecha_inicio)
          AND hae.fecha_inicio <= p.fecha_fin
        FETCH FIRST 1 ROW ONLY
        """
        cur.execute(sql_info, {"idp": id_periodo, "ide": id_estudiante})
        info = cur.fetchone()
        if not info:
            return {
                "id_estudiante": id_estudiante,
                "id_periodo": id_periodo,
                "institucion": None,
                "grado": None,
                "programa": None,
                "periodo": None,
                "componentes": [],
                "definitiva": None,
            }

        nombre_inst, grado, tipo_programa, nombre_periodo = info

        # Componentes del periodo y sus notas para el estudiante
        sql_comp = """
        SELECT
            c.id_componente,
            c.nombre,
            c.porcentaje,
            c.tipo_programa,
            n.nota
        FROM COMPONENTE c
        LEFT JOIN NOTA_ESTUDIANTE n
          ON n.id_componente = c.id_componente
         AND n.id_estudiante = :ide
        WHERE c.id_periodo = :idp
        ORDER BY c.id_componente
        """
        cur.execute(sql_comp, {"idp": id_periodo, "ide": id_estudiante})
        componentes = []
        suma_ponderada = 0.0
        for idc, nombre, porc, tipoprog, nota in cur.fetchall():
            porc_val = float(porc) if porc is not None else 0.0
            nota_val = float(nota) if nota is not None else None
            if nota_val is not None:
                suma_ponderada += nota_val * (porc_val / 100.0)
            componentes.append(
                {
                    "id_componente": idc,
                    "nombre": nombre,
                    "porcentaje": porc_val,
                    "tipo_programa": tipoprog,
                    "nota": nota_val,
                }
            )

        definitiva = round(suma_ponderada, 2) if componentes else None

        return {
            "id_estudiante": id_estudiante,
            "id_periodo": id_periodo,
            "institucion": nombre_inst,
            "grado": grado,
            "programa": tipo_programa,
            "periodo": nombre_periodo,
            "componentes": componentes,
            "definitiva": definitiva,
        }
    finally:
        cur.close()
        conn.close()