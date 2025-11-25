# app/crud.py
from typing import Optional
from app.db import get_conn
import oracledb

# ============================
# INSTITUCION
# ============================

def create_institucion(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_inst = cur.var(oracledb.NUMBER)

        cur.execute("""
            INSERT INTO INSTITUCION(nombre_inst, jornada, dir_principal)
            VALUES (:1, :2, :3)
            RETURNING id_institucion INTO :4
        """, (
            data['nombre_inst'],
            data.get('jornada'),
            data.get('dir_principal'),
            id_inst
        ))

        conn.commit()
        return int(id_inst.getvalue()[0])
    finally:
        cur.close()
        conn.close()


def list_instituciones(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_institucion, nombre_inst, jornada, dir_principal
            FROM INSTITUCION
            ORDER BY id_institucion
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            dict(
                id_institucion=r[0],
                nombre_inst=r[1],
                jornada=r[2],
                dir_principal=r[3]
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def get_institucion(id_inst):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_institucion, nombre_inst, jornada, dir_principal
            FROM INSTITUCION
            WHERE id_institucion = :1
        """, (id_inst,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(
            id_institucion=r[0],
            nombre_inst=r[1],
            jornada=r[2],
            dir_principal=r[3]
        )
    finally:
        cur.close()
        conn.close()


def delete_institucion(id_inst):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM INSTITUCION WHERE id_institucion = :1", (id_inst,))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_institucion(id_inst, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE INSTITUCION SET
                nombre_inst = :1,
                jornada = :2,
                dir_principal = :3
            WHERE id_institucion = :4
        """, (
            data['nombre_inst'],
            data.get('jornada'),
            data.get('dir_principal'),
            id_inst
        ))
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ============================
# SEDE
# ============================

def create_sede(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT NVL(MAX(id_sede), 0) + 1
            FROM SEDE
            WHERE id_institucion = :1
        """, (data['id_institucion'],))
        next_id_sede = cur.fetchone()[0]

        cur.execute("""
            INSERT INTO SEDE(id_institucion, id_sede, direccion, es_principal)
            VALUES (:1, :2, :3, :4)
        """, (
            data['id_institucion'],
            next_id_sede,
            data.get('direccion'),
            data.get('es_principal', 'N')
        ))
        conn.commit()
        return next_id_sede
    finally:
        cur.close()
        conn.close()


def list_sedes(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_sede, id_institucion, direccion, es_principal
            FROM SEDE
            ORDER BY id_sede
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            dict(
                id_sede=r[0],
                id_institucion=r[1],
                direccion=r[2],
                es_principal=r[3]
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def get_sede(id_institucion, id_sede):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_sede, id_institucion, direccion, es_principal
            FROM SEDE
            WHERE id_institucion = :1 AND id_sede = :2
        """, (id_institucion, id_sede))
        r = cur.fetchone()
        if not r:
            return None
        return dict(
            id_sede=r[0],
            id_institucion=r[1],
            direccion=r[2],
            es_principal=r[3]
        )
    finally:
        cur.close()
        conn.close()


def delete_sede(id_institucion, id_sede):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            DELETE FROM SEDE
            WHERE id_institucion = :1 AND id_sede = :2
        """, (id_institucion, id_sede))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def update_sede(id_institucion, id_sede, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE SEDE SET
                direccion = :1,
                es_principal = :2
            WHERE id_institucion = :3 AND id_sede = :4
        """, (
            data.get('direccion'),
            data.get('es_principal', 'N'),
            id_institucion,
            id_sede
        ))
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ============================
# PERSONA
# ============================

def create_persona(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO PERSONA(tipo_doc, nombre, telefono, correo, rol)
            VALUES (:1,:2,:3,:4,:5)
        """, (
            data.get('tipo_doc'),
            data['nombre'],
            data.get('telefono'),
            data.get('correo'),
            data.get('rol')
        ))
        conn.commit()
        cur.execute("""
            SELECT id_persona
            FROM PERSONA
            WHERE nombre = :1
            ORDER BY id_persona DESC
        """, (data['nombre'],))
        r = cur.fetchone()
        return r[0] if r else None
    finally:
        cur.close()
        conn.close()


def list_personas(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_persona, tipo_doc, nombre, telefono, correo, rol
            FROM PERSONA
            ORDER BY id_persona
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            dict(
                id_persona=r[0],
                tipo_doc=r[1],
                nombre=r[2],
                telefono=r[3],
                correo=r[4],
                rol=r[5]
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


# ============================
# USUARIO
# ============================

def create_usuario(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO USUARIO(nombre_user, contrasena, id_persona)
            VALUES (:1, :2, :3)
        """, (
            data["nombre_user"],
            data["contrasena"],
            data["id_persona"]
        ))
        conn.commit()
        return data["nombre_user"]
    finally:
        cur.close()
        conn.close()


def list_usuarios(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT u.nombre_user,
                   p.correo,
                   p.nombre,
                   p.rol,
                   u.id_persona
            FROM USUARIO u
            JOIN PERSONA p ON u.id_persona = p.id_persona
            ORDER BY u.nombre_user
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            {
                "nombre_user": r[0],
                "correo": r[1],
                "nombre": r[2],
                "rol": r[3],
                "id_persona": r[4]
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


# ============================
# AULAS
# ============================

def list_aulas(limit=200):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_aula, id_institucion, id_sede, grado
            FROM AULA
            ORDER BY id_aula
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            {
                "id_aula": r[0],
                "id_institucion": r[1],
                "id_sede": r[2],
                "grado": r[3]
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def create_aula(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_aula = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO AULA(id_institucion, id_sede, grado)
            VALUES (:1, :2, :3)
            RETURNING id_aula INTO :4
        """, (
            data["id_institucion"],
            data["id_sede"],
            data["grado"],
            id_aula
        ))
        conn.commit()
        return int(id_aula.getvalue()[0])
    finally:
        cur.close()
        conn.close()


def get_aula(id_aula: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_aula, id_institucion, id_sede, grado
            FROM AULA
            WHERE id_aula = :1
        """, (id_aula,))
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id_aula": r[0],
            "id_institucion": r[1],
            "id_sede": r[2],
            "grado": r[3]
        }
    finally:
        cur.close()
        conn.close()


def update_aula(id_aula: int, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE AULA
            SET id_institucion = :1,
                id_sede = :2,
                grado = :3
            WHERE id_aula = :4
        """, (
            data["id_institucion"],
            data["id_sede"],
            data["grado"],
            id_aula
        ))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_aula(id_aula: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM AULA WHERE id_aula = :1", (id_aula,))
        conn.commit()
    finally:
        cur.close()
        conn.close()


# ============================
# HORARIOS
# ============================

def list_horarios(limit=200):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_horario,
                   dia_semana,
                   h_inicio,
                   h_final,
                   minutos_equiv,
                   es_continuo
            FROM HORARIO
            ORDER BY id_horario
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            {
                "id_horario": r[0],
                "dia_semana": r[1],
                "h_inicio": r[2],
                "h_final": r[3],
                "minutos_equiv": r[4],
                "es_continuo": r[5],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def create_horario(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_horario = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO HORARIO(
                dia_semana,
                h_inicio,
                h_final,
                minutos_equiv,
                es_continuo
            )
            VALUES (:1, :2, :3, :4, :5)
            RETURNING id_horario INTO :6
        """, (
            data["dia_semana"],
            data["h_inicio"],
            data["h_final"],
            data["minutos_equiv"],
            data["es_continuo"],
            id_horario
        ))
        conn.commit()
        return int(id_horario.getvalue()[0])
    finally:
        cur.close()
        conn.close()


def delete_horario(id_horario: int):
    """
    Borra de HORARIO solo si NO hay registros ACTIVOS en el histórico
    (es decir, si no hay filas con fecha_fin IS NULL para ese id_horario).
    El histórico NO se borra.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Verificar si existe algún uso ACTIVO en el histórico
        cur.execute("""
            SELECT COUNT(*)
            FROM HISTORICO_HORARIO_AULA
            WHERE id_horario = :1
              AND fecha_fin IS NULL
        """, (id_horario,))
        activos = cur.fetchone()[0]

        if activos > 0:
            raise Exception("No se puede eliminar el horario porque está activo en el histórico")

        # Si no hay usos activos, se puede borrar el horario
        cur.execute("DELETE FROM HORARIO WHERE id_horario = :1", (id_horario,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# ============================
# HISTÓRICO HORARIO AULA
# ============================

def asignar_horario_a_aula(data: dict):
    """
    Cierra cualquier horario activo previo de esa aula (fecha_fin IS NULL)
    y crea un nuevo registro en HISTORICO_HORARIO_AULA.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_aula = data["id_aula"]
        id_horario = data["id_horario"]
        fecha_inicio = data.get("fecha_inicio")  # "YYYY-MM-DD" o None

        # 1) Cerrar cualquier horario activo previo de esa aula
        cur.execute("""
            UPDATE HISTORICO_HORARIO_AULA
            SET fecha_fin = SYSDATE
            WHERE id_aula = :1
              AND fecha_fin IS NULL
        """, (id_aula,))

        # 2) Obtener siguiente ID_HIST_HORARIO
        cur.execute("SELECT NVL(MAX(id_hist_horario), 0) + 1 FROM HISTORICO_HORARIO_AULA")
        next_id = cur.fetchone()[0]

        # 3) Insertar nuevo histórico
        if fecha_inicio:
            cur.execute("""
                INSERT INTO HISTORICO_HORARIO_AULA(
                    id_hist_horario, id_aula, id_horario, fecha_inicio, fecha_fin
                )
                VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), NULL)
            """, (next_id, id_aula, id_horario, fecha_inicio))
        else:
            cur.execute("""
                INSERT INTO HISTORICO_HORARIO_AULA(
                    id_hist_horario, id_aula, id_horario, fecha_inicio, fecha_fin
                )
                VALUES (:1, :2, :3, SYSDATE, NULL)
            """, (next_id, id_aula, id_horario))

        conn.commit()
        return next_id
    finally:
        cur.close()
        conn.close()


def get_historial_horarios_aula(id_aula: int, limit=200):
    """
    Devuelve el historial de horarios de un aula con datos del horario.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                hha.id_hist_horario,
                hha.id_aula,
                hha.id_horario,
                TO_CHAR(hha.fecha_inicio, 'YYYY-MM-DD') AS fecha_inicio,
                TO_CHAR(hha.fecha_fin, 'YYYY-MM-DD')   AS fecha_fin,
                h.dia_semana,
                h.h_inicio,
                h.h_final,
                h.minutos_equiv,
                h.es_continuo
            FROM HISTORICO_HORARIO_AULA hha
            JOIN HORARIO h ON hha.id_horario = h.id_horario
            WHERE hha.id_aula = :1
            ORDER BY hha.fecha_inicio DESC, hha.id_hist_horario DESC
        """, (id_aula,))
        rows = cur.fetchmany(numRows=limit)

        return [
            {
                "id_hist_horario": r[0],
                "id_aula": r[1],
                "id_horario": r[2],
                "fecha_inicio": r[3],
                "fecha_fin": r[4],           # puede ser None
                "dia_semana": r[5],
                "h_inicio": r[6],
                "h_final": r[7],
                "minutos_equiv": r[8],
                "es_continuo": r[9],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def finalizar_historial_horario(id_hist_horario: int, fecha_fin: Optional[str] = None):
    """
    Marca un registro de HISTORICO_HORARIO_AULA como finalizado.
    - Solo afecta registros con fecha_fin IS NULL (activos).
    - Si fecha_fin es None -> SYSDATE
    - Si viene 'YYYY-MM-DD', usa esa fecha.
    Lanza Exception si no se actualizó ninguna fila.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        if fecha_fin:
            cur.execute("""
                UPDATE HISTORICO_HORARIO_AULA
                SET fecha_fin = TO_DATE(:1, 'YYYY-MM-DD')
                WHERE id_hist_horario = :2
                  AND fecha_fin IS NULL
            """, (fecha_fin, id_hist_horario))
        else:
            cur.execute("""
                UPDATE HISTORICO_HORARIO_AULA
                SET fecha_fin = SYSDATE
                WHERE id_hist_horario = :1
                  AND fecha_fin IS NULL
            """, (id_hist_horario,))

        if cur.rowcount == 0:
            # No se actualizó nada: o el id no existe, o ya estaba finalizado
            raise Exception("No se encontró un historial activo con ese ID")

        conn.commit()
    finally:
        cur.close()
        conn.close()

# ============================
# ASIGNACIÓN TUTOR AULA
# ============================

def asignar_tutor_a_aula(data: dict):
    """
    Cierra al tutor activo (si lo hay) de esa aula y crea un nuevo
    registro en ASIGNACION_TUTOR.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_aula = data["id_aula"]
        id_persona = data["id_persona"]
        fecha_inicio = data.get("fecha_inicio")  # "YYYY-MM-DD" o None
        motivo_cambio = data.get("motivo_cambio")

        # 1) Cerrar tutor previo activo de esa aula (fecha_fin IS NULL)
        cur.execute("""
            UPDATE ASIGNACION_TUTOR
            SET fecha_fin = SYSDATE
            WHERE id_aula = :1
              AND fecha_fin IS NULL
        """, (id_aula,))

        # 2) Obtener siguiente ID_TUTOR_AULA
        cur.execute("SELECT NVL(MAX(id_tutor_aula), 0) + 1 FROM ASIGNACION_TUTOR")
        next_id = cur.fetchone()[0]

        # 3) Insertar nuevo registro
        if fecha_inicio:
            cur.execute("""
                INSERT INTO ASIGNACION_TUTOR(
                    id_tutor_aula, id_persona, id_aula, fecha_inicio, fecha_fin, motivo_cambio
                )
                VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), NULL, :5)
            """, (next_id, id_persona, id_aula, fecha_inicio, motivo_cambio))
        else:
            cur.execute("""
                INSERT INTO ASIGNACION_TUTOR(
                    id_tutor_aula, id_persona, id_aula, fecha_inicio, fecha_fin, motivo_cambio
                )
                VALUES (:1, :2, :3, SYSDATE, NULL, :4)
            """, (next_id, id_persona, id_aula, motivo_cambio))

        conn.commit()
        return next_id
    finally:
        cur.close()
        conn.close()

def get_historial_tutores_aula(id_aula: int, limit=200):
    """
    Devuelve el historial de tutores de un aula,
    uniendo ASIGNACION_TUTOR con PERSONA y AULA.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                at.id_tutor_aula,
                at.id_aula,
                at.id_persona,
                TO_CHAR(at.fecha_inicio, 'YYYY-MM-DD') AS fecha_inicio,
                TO_CHAR(at.fecha_fin, 'YYYY-MM-DD')   AS fecha_fin,
                at.motivo_cambio,
                p.nombre,
                p.correo,
                a.id_institucion,
                a.id_sede,
                a.grado
            FROM ASIGNACION_TUTOR at
            JOIN PERSONA p ON at.id_persona = p.id_persona
            JOIN AULA a    ON at.id_aula    = a.id_aula
            WHERE at.id_aula = :1
            ORDER BY at.fecha_inicio DESC, at.id_tutor_aula DESC
        """, (id_aula,))
        rows = cur.fetchmany(numRows=limit)

        return [
            {
                "id_tutor_aula": r[0],
                "id_aula": r[1],
                "id_persona": r[2],
                "fecha_inicio": r[3],
                "fecha_fin": r[4],
                "motivo_cambio": r[5],
                "nombre_tutor": r[6],
                "correo_tutor": r[7],
                "id_institucion": r[8],
                "id_sede": r[9],
                "grado": r[10],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def finalizar_asignacion_tutor(id_tutor_aula: int, fecha_fin: Optional[str] = None):
    """
    Marca una asignación de tutor como finalizada (pone FECHA_FIN).
    Solo actúa si FECHA_FIN es NULL.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        if fecha_fin:
            cur.execute("""
                UPDATE ASIGNACION_TUTOR
                SET fecha_fin = TO_DATE(:1, 'YYYY-MM-DD')
                WHERE id_tutor_aula = :2
                  AND fecha_fin IS NULL
            """, (fecha_fin, id_tutor_aula))
        else:
            cur.execute("""
                UPDATE ASIGNACION_TUTOR
                SET fecha_fin = SYSDATE
                WHERE id_tutor_aula = :1
                  AND fecha_fin IS NULL
            """, (id_tutor_aula,))

        if cur.rowcount == 0:
            # No se actualizó nada: o no existe o ya estaba finalizada
            raise Exception("No se encontró una asignación activa con ese ID")

        conn.commit()
    finally:
        cur.close()
        conn.close()

def delete_asignacion_tutor(id_tutor_aula: int):
    """
    Elimina una fila de ASIGNACION_TUTOR por ID_TUTOR_AULA.
    (Solo afecta histórico de tutores, no PERSONA ni AULA).
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM ASIGNACION_TUTOR WHERE id_tutor_aula = :1",
                    (id_tutor_aula,))
        if cur.rowcount == 0:
            raise Exception("No se encontró una asignación con ese ID")
        conn.commit()
    finally:
        cur.close()
        conn.close()