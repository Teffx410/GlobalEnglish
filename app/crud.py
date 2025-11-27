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
# ESTUDIANTES
# ============================

def list_estudiantes(limit=500):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_estudiante,
                   tipo_documento,
                   num_documento,
                   nombres,
                   apellidos,
                   telefono,
                   fecha_nacimiento,
                   correo,
                   score_entrada,
                   score_salida
            FROM ESTUDIANTE
            ORDER BY id_estudiante
        """)
        rows = cur.fetchmany(numRows=limit)
        result = []
        for r in rows:
            result.append({
                "id_estudiante": r[0],
                "tipo_documento": r[1],
                "num_documento": r[2],
                "nombres": r[3],
                "apellidos": r[4],
                "telefono": r[5],
                "fecha_nacimiento": r[6],
                "correo": r[7],
                "score_entrada": r[8],
                "score_salida": r[9],
            })
        return result
    finally:
        cur.close()
        conn.close()


def get_estudiante(id_estudiante: int) -> Optional[dict]:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_estudiante,
                   tipo_documento,
                   num_documento,
                   nombres,
                   apellidos,
                   telefono,
                   fecha_nacimiento,
                   correo,
                   score_entrada,
                   score_salida
            FROM ESTUDIANTE
            WHERE id_estudiante = :1
        """, (id_estudiante,))
        r = cur.fetchone()
        if not r:
            return None
        return {
            "id_estudiante": r[0],
            "tipo_documento": r[1],
            "num_documento": r[2],
            "nombres": r[3],
            "apellidos": r[4],
            "telefono": r[5],
            "fecha_nacimiento": r[6],
            "correo": r[7],
            "score_entrada": r[8],
            "score_salida": r[9],
        }
    finally:
        cur.close()
        conn.close()


def update_estudiante(id_estudiante: int, data: dict) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE ESTUDIANTE
            SET tipo_documento = :1,
                num_documento   = :2,
                nombres         = :3,
                apellidos       = :4,
                telefono        = :5,
                fecha_nacimiento= :6,
                correo          = :7,
                score_entrada   = :8,
                score_salida    = :9
            WHERE id_estudiante = :10
        """, (
            data.get("tipo_documento"),
            data["num_documento"],
            data["nombres"],
            data.get("apellidos"),
            data.get("telefono"),
            data.get("fecha_nacimiento"),
            data.get("correo"),
            data.get("score_entrada"),
            data.get("score_salida"),
            id_estudiante
        ))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


def delete_estudiante(id_estudiante: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM ESTUDIANTE WHERE id_estudiante = :1", (id_estudiante,))
        conn.commit()
        return cur.rowcount > 0
    finally:
        cur.close()
        conn.close()


# ============================
# PERIODOS
# ============================

def list_periodos():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_periodo, nombre, fecha_inicio, fecha_fin
            FROM PERIODO
            ORDER BY fecha_inicio DESC
        """)
        rows = cur.fetchall()
        return [
            {
                "id_periodo": r[0],
                "nombre": r[1],
                "fecha_inicio": r[2],
                "fecha_fin": r[3],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def create_periodo(data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_var = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO PERIODO(nombre, fecha_inicio, fecha_fin)
            VALUES (:nombre, :fecha_inicio, :fecha_fin)
            RETURNING id_periodo INTO :idp
        """, {
            "nombre": data["nombre"],
            "fecha_inicio": data["fecha_inicio"],
            "fecha_fin": data["fecha_fin"],
            "idp": id_var
        })
        conn.commit()
        val = id_var.getvalue()
        if isinstance(val, list):
            val = val[0]
        return int(val)
    finally:
        cur.close()
        conn.close()


# ============================
# COMPONENTES
# ============================

def list_componentes():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_componente, nombre, porcentaje
            FROM COMPONENTE
            ORDER BY id_componente
        """)
        rows = cur.fetchall()
        return [
            {
                "id_componente": r[0],
                "nombre": r[1],
                "porcentaje": r[2],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def create_componente(data: dict) -> int:
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_var = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO COMPONENTE(nombre, porcentaje)
            VALUES (:nombre, :porcentaje)
            RETURNING id_componente INTO :idc
        """, {
            "nombre": data["nombre"],
            "porcentaje": data["porcentaje"],
            "idc": id_var
        })
        conn.commit()
        val = id_var.getvalue()
        if isinstance(val, list):
            val = val[0]
        return int(val)
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


from datetime import date


# ============================
# HISTÓRICO AULA ESTUDIANTE
# ============================

def asignar_estudiante_a_aula(data: dict) -> int:
    """
    Cierra cualquier asignación previa del estudiante (fecha_fin NULL)
    y crea una nueva fila en HISTORICO_AULA_ESTUDIANTE.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        fecha_inicio = data.get("fecha_inicio") or date.today()

        # 1) Cerrar asignaciones anteriores activas del estudiante
        cur.execute("""
            UPDATE HISTORICO_AULA_ESTUDIANTE
            SET fecha_fin = :fecha_fin
            WHERE id_estudiante = :id_estudiante
              AND fecha_fin IS NULL
        """, {
            "fecha_fin": fecha_inicio,
            "id_estudiante": data["id_estudiante"],
        })

        # 2) Crear nueva asignación
        id_var = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO HISTORICO_AULA_ESTUDIANTE(
                id_estudiante, id_aula, fecha_inicio
            )
            VALUES (:id_estudiante, :id_aula, :fecha_inicio)
            RETURNING id_hist_aula_est INTO :id_hist
        """, {
            "id_estudiante": data["id_estudiante"],
            "id_aula": data["id_aula"],
            "fecha_inicio": fecha_inicio,
            "id_hist": id_var
        })

        conn.commit()

        val = id_var.getvalue()
        # oracledb a veces devuelve [valor] en lugar de valor directo
        if isinstance(val, list):
            val = val[0]
        return int(val)
    finally:
        cur.close()
        conn.close()


# ============================
# HORARIOS POR TUTOR
# ============================

def list_horarios_tutor(id_persona: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                a.id_aula,
                a.grado,
                h.dia_semana,
                h.h_inicio,
                h.h_final,
                h.es_continuo,
                h.minutos_equiv
            FROM ASIGNACION_TUTOR at
            JOIN AULA a ON at.id_aula = a.id_aula
            JOIN HISTORICO_HORARIO_AULA hha ON hha.id_aula = a.id_aula
            JOIN HORARIO h ON hha.id_horario = h.id_horario
            WHERE at.id_persona = :1
        """, (id_persona,))
        rows = cur.fetchall()
        return [
            {
                "id_aula": r[0],
                "grado": r[1],
                "dia_semana": r[2],
                "h_inicio": r[3],
                "h_final": r[4],
                "es_continuo": r[5],
                "minutos_equiv": r[6],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()
