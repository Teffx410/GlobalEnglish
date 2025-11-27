# app/reports.py
from app.db import get_conn

def reporte_asistencia_aula(id_aula, id_semana=None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        sql = """
        SELECT inst.nombre_inst, s.id_sede, au.id_aula,
               aa.id_asist, aa.fecha_clase, 
               CASE WHEN f.id_festivo IS NOT NULL THEN 'S' ELSE 'N' END as es_festivo,
               h.dia_semana, h.h_inicio, h.h_final,
               aa.dictada, aa.horas_dictadas, m.descripcion motivo,
               aa.reposicion, aa.fecha_reposicion,
               at.id_persona as id_tutor_persona
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
        cols = [c[0] for c in cur.description]
        result = [dict(zip(cols, r)) for r in rows]
        return result
    finally:
        cur.close()
        conn.close()
