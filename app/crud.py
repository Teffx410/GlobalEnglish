# app/crud.py
from typing import Optional
from app.db import get_conn
import oracledb
import secrets
from datetime import date, datetime, timedelta
from typing import Optional, Tuple

# ============================
# INSTITUCION
# ============================
def create_institucion(data: dict):
    """Crea una institución validando que el nombre sea único"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que el nombre no exista
        cur.execute("SELECT COUNT(*) FROM INSTITUCION WHERE LOWER(nombre_inst) = LOWER(:1)", 
                    (data['nombre_inst'],))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe una institución con ese nombre"}
        
        cur.execute("""INSERT INTO INSTITUCION(nombre_inst, jornada, dir_principal)
                       VALUES (:1,:2,:3)""",
                    (data['nombre_inst'], data.get('jornada'), data.get('dir_principal')))
        conn.commit()
        cur.execute("SELECT id_institucion FROM INSTITUCION WHERE nombre_inst = :1", 
                    (data['nombre_inst'],))
        r = cur.fetchone()
        return {"ok": True, "id_institucion": r[0]} if r else {"error": "No se pudo obtener el ID"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def list_instituciones(limit=100):
    """Lista todas las instituciones"""
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
    """Obtiene una institución por ID"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_institucion, nombre_inst, jornada, dir_principal FROM INSTITUCION WHERE id_institucion = :1", 
                    (id_inst,))
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
    """Elimina una institución si no tiene sedes asociadas"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que no tenga sedes
        cur.execute("SELECT COUNT(*) FROM SEDE WHERE id_institucion = :1", (id_inst,))
        if cur.fetchone()[0] > 0:
            return {"error": "No se puede eliminar una institución que tiene sedes asociadas"}
        
        cur.execute("DELETE FROM INSTITUCION WHERE id_institucion = :1", (id_inst,))
        conn.commit()
        return {"ok": True, "msg": "Institución eliminada correctamente"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def update_institucion(id_inst, data: dict):
    """Actualiza una institución validando nombre único"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que el nombre no exista en otra institución
        cur.execute("""SELECT COUNT(*) FROM INSTITUCION 
                       WHERE LOWER(nombre_inst) = LOWER(:1) AND id_institucion != :2""", 
                    (data['nombre_inst'], id_inst))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe otra institución con ese nombre"}
        
        cur.execute("""UPDATE INSTITUCION SET
                          nombre_inst = :1,
                          jornada = :2,
                          dir_principal = :3
                       WHERE id_institucion = :4""",
                    (data['nombre_inst'], data.get('jornada'), data.get('dir_principal'), id_inst))
        conn.commit()
        return {"ok": True, "msg": "Institución actualizada correctamente"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

# ============================
# SEDE
# ============================
def create_sede(data: dict):
    """Crea una sede validando que la dirección sea única"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que la dirección no exista
        cur.execute("SELECT COUNT(*) FROM SEDE WHERE LOWER(direccion) = LOWER(:1)", 
                    (data.get('direccion'),))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe una sede con esa dirección"}
        
        # Obtener el siguiente id_sede para esta institución
        cur.execute("SELECT NVL(MAX(id_sede), 0) + 1 FROM SEDE WHERE id_institucion = :1", 
                    (data['id_institucion'],))
        next_id_sede = cur.fetchone()[0]
        
        # Insertar sede con el siguiente id_sede
        cur.execute("""INSERT INTO SEDE(id_institucion, id_sede, direccion, es_principal)
                       VALUES (:1, :2, :3, :4)""",
                    (data['id_institucion'], next_id_sede, data.get('direccion'), data.get('es_principal', 'N')))
        conn.commit()
        return {"ok": True, "id_sede": next_id_sede}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def list_sedes(limit=100):
    """Lista todas las sedes"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_sede, id_institucion, direccion, es_principal FROM SEDE ORDER BY id_institucion, id_sede")
        rows = cur.fetchmany(numRows=limit)
        return [dict(id_sede=r[0], id_institucion=r[1], direccion=r[2], es_principal=r[3]) for r in rows]
    finally:
        cur.close()
        conn.close()


def get_sede(id_sede):
    """Obtiene una sede por ID"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_sede, id_institucion, direccion, es_principal FROM SEDE WHERE id_sede = :1", 
                    (id_sede,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(id_sede=r[0], id_institucion=r[1], direccion=r[2], es_principal=r[3])
    finally:
        cur.close()
        conn.close()

def delete_sede(id_institucion, id_sede):
    """
    Elimina una sede (PK compuesta) validando que no tenga aulas asociadas.
    Tanto institución como sede son obligatorios para identificar la fila.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Verifica que la sede existe
        cur.execute(
            "SELECT 1 FROM SEDE WHERE id_institucion = :1 AND id_sede = :2",
            (id_institucion, id_sede)
        )
        if not cur.fetchone():
            return {"error": "Sede no encontrada"}

        # Valida que NO existan aulas asociadas
        cur.execute(
            """SELECT COUNT(*) FROM AULA 
               WHERE id_institucion = :1 AND id_sede = :2""",
            (id_institucion, id_sede)
        )
        count_result = cur.fetchone()
        if count_result and count_result[0] > 0:
            return {"error": "No se puede eliminar una sede que tiene aulas asociadas"}

        # Elimina la sede (usando ambos IDs)
        cur.execute(
            "DELETE FROM SEDE WHERE id_institucion = :1 AND id_sede = :2",
            (id_institucion, id_sede)
        )
        conn.commit()
        return {"ok": True, "msg": "Sede eliminada correctamente"}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def update_sede(id_sede, data: dict):
    """Actualiza una sede validando dirección única"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que la dirección no exista en otra sede
        cur.execute("""SELECT COUNT(*) FROM SEDE 
                       WHERE LOWER(direccion) = LOWER(:1) AND id_sede != :2""", 
                    (data.get('direccion'), id_sede))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe otra sede con esa dirección"}
        
        cur.execute("""UPDATE SEDE SET
                          id_institucion = :1,
                          direccion = :2,
                          es_principal = :3
                       WHERE id_sede = :4""",
                    (data['id_institucion'], data.get('direccion'), data.get('es_principal', 'N'), id_sede))
        conn.commit()
        return {"ok": True, "msg": "Sede actualizada correctamente"}
    except Exception as e:
        return {"error": str(e)}
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
        # Validar que num_documento no esté vacío
        if not data.get('num_documento') or not data.get('num_documento').strip():
            return {"error": "El número de documento es requerido"}
        
        # Validar que num_documento sea único
        cur.execute("SELECT COUNT(*) FROM PERSONA WHERE LOWER(num_documento) = LOWER(:1)", 
                    (data.get('num_documento'),))
        count_result = cur.fetchone()
        count = count_result[0] if count_result else 0
        
        if count > 0:
            return {"error": "El número de documento ya está registrado"}
        
        # Validar que correo sea único
        cur.execute("SELECT COUNT(*) FROM PERSONA WHERE LOWER(correo) = LOWER(:1)", 
                    (data.get('correo'),))
        count_result = cur.fetchone()
        count = count_result[0] if count_result else 0
        
        if count > 0:
            return {"error": "El correo ya está registrado"}
        
        cur.execute("""INSERT INTO PERSONA(tipo_doc, num_documento, nombre, telefono, correo, rol) 
                       VALUES (:1,:2,:3,:4,:5,:6)""",
                    (data.get('tipo_doc'), data.get('num_documento'), data['nombre'], 
                     data.get('telefono'), data.get('correo'), data.get('rol')))
        conn.commit()
        
        cur.execute("SELECT id_persona FROM PERSONA WHERE LOWER(num_documento) = LOWER(:1)", 
                    (data.get('num_documento'),))
        result = cur.fetchone()
        id_persona = result[0] if result else None
        
        return id_persona
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def list_personas(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""SELECT id_persona, tipo_doc, num_documento, nombre, telefono, correo, rol 
                       FROM PERSONA ORDER BY id_persona""")
        rows = cur.fetchmany(numRows=limit)
        result = []
        for r in rows:
            result.append({
                "id_persona": r[0],
                "tipo_doc": r[1],
                "num_documento": r[2],
                "nombre": r[3],
                "telefono": r[4],
                "correo": r[5],
                "rol": r[6]
            })
        return result
    except Exception as e:
        print(f"Error en list_personas: {e}")
        return []
    finally:
        cur.close()
        conn.close()

def update_persona(id_persona: int, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que num_documento sea único (excluyendo la persona actual)
        if data.get('num_documento'):
            cur.execute("""SELECT COUNT(*) FROM PERSONA 
                           WHERE LOWER(num_documento) = LOWER(:1) AND id_persona != :2""", 
                        (data.get('num_documento'), id_persona))
            count_result = cur.fetchone()
            count = count_result[0] if count_result else 0
            
            if count > 0:
                return {"error": "El número de documento ya está registrado"}
        
        # Validar que correo sea único (excluyendo la persona actual)
        if data.get('correo'):
            cur.execute("""SELECT COUNT(*) FROM PERSONA 
                           WHERE LOWER(correo) = LOWER(:1) AND id_persona != :2""", 
                        (data.get('correo'), id_persona))
            count_result = cur.fetchone()
            count = count_result[0] if count_result else 0
            
            if count > 0:
                return {"error": "El correo ya está registrado"}
        
        cur.execute("""UPDATE PERSONA SET tipo_doc = :1, num_documento = :2, nombre = :3, 
                       telefono = :4, correo = :5, rol = :6 WHERE id_persona = :7""",
                    (data.get('tipo_doc'), data.get('num_documento'), data['nombre'],
                     data.get('telefono'), data.get('correo'), data.get('rol'), id_persona))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def delete_persona(id_persona: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Verificar si la persona está asociada a USUARIO
        cur.execute("SELECT COUNT(*) FROM USUARIO WHERE id_persona = :1", (id_persona,))
        count_usuario_result = cur.fetchone()
        count_usuario = count_usuario_result[0] if count_usuario_result else 0
        
        if count_usuario > 0:
            return {"error": "No se puede eliminar una persona que está registrada como usuario"}
        
        # Intentar eliminar la persona
        cur.execute("DELETE FROM PERSONA WHERE id_persona = :1", (id_persona,))
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        error_msg = str(e)
        # Si es un error de constraint, mostrar un mensaje más amigable
        if "CONSTRAINT" in error_msg or "constraint" in error_msg:
            return {"error": "No se puede eliminar esta persona porque tiene registros asociados"}
        return {"error": error_msg}
    finally:
        cur.close()
        conn.close()

# ============================
# USUARIO
# ============================

def create_usuario(data: dict):
    from hashlib import sha256
    conn = get_conn()
    cur = conn.cursor()
    clave = data.get("contrasena") or secrets.token_urlsafe(8)
    clave_hash = sha256(clave.encode()).hexdigest()
    try:
        cur.execute("""INSERT INTO USUARIO(nombre_user, contrasena, id_persona) VALUES (:1,:2,:3)""",
                    (data["nombre_user"], clave_hash, data["id_persona"]))
        conn.commit()
        cur.execute("SELECT correo FROM PERSONA WHERE id_persona = :1", (data["id_persona"],))
        correo = cur.fetchone()[0]
        return data["nombre_user"], clave, correo
    finally:
        cur.close()
        conn.close()

def list_usuarios(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT u.nombre_user, p.correo, p.nombre, p.rol
            FROM USUARIO u JOIN PERSONA p ON u.id_persona = p.id_persona
            ORDER BY u.nombre_user
        """)
        rows = cur.fetchmany(numRows=limit)
        return [dict(nombre_user=r[0], correo=r[1], nombre=r[2], rol=r[3]) for r in rows]
    finally:
        cur.close()
        conn.close()

# ============================
# AULAS
# ============================

def create_aula(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO AULA (id_institucion, id_sede, grado, id_tutor_aula)
            VALUES (:1, :2, :3, NULL)
        """, (data['id_institucion'], data['id_sede'], data['grado']))
        conn.commit()

        cur.execute("""
            SELECT id_aula FROM AULA
            WHERE id_institucion=:1 AND id_sede=:2 AND grado=:3
            ORDER BY id_aula DESC
        """, (data['id_institucion'], data['id_sede'], data['grado']))
        r = cur.fetchone()
        return r[0] if r else None
    finally:
        cur.close()
        conn.close()


def list_aulas(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_aula, id_institucion, id_sede, grado, id_tutor_aula
            FROM AULA
            ORDER BY id_aula
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            dict(
                id_aula=r[0],
                id_institucion=r[1],
                id_sede=r[2],
                grado=r[3],
                id_tutor_aula=r[4]
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()


def get_aula(id_aula):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_aula, id_institucion, id_sede, grado, id_tutor_aula
            FROM AULA
            WHERE id_aula = :1
        """, (id_aula,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(
            id_aula=r[0],
            id_institucion=r[1],
            id_sede=r[2],
            grado=r[3],
            id_tutor_aula=r[4]
        )
    finally:
        cur.close()
        conn.close()


def update_aula(id_aula, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE AULA SET
                id_institucion = :1,
                id_sede        = :2,
                grado          = :3
            WHERE id_aula = :4
        """, (data['id_institucion'], data['id_sede'], data['grado'], id_aula))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def delete_aula(id_aula):
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

def create_horario(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO HORARIO (dia_semana, h_inicio, h_final, minutos_equiv, es_continuo)
            VALUES (:1, :2, :3, :4, :5)
        """, (
            data['dia_semana'], data['h_inicio'], data['h_final'],
            data['minutos_equiv'], data.get('es_continuo', 'S')
        ))
        conn.commit()
        cur.execute("SELECT id_horario FROM HORARIO ORDER BY id_horario DESC")
        r = cur.fetchone()
        return r[0] if r else None
    finally:
        cur.close()
        conn.close()

def list_horarios(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_horario, dia_semana, h_inicio, h_final, minutos_equiv, es_continuo
            FROM HORARIO ORDER BY id_horario DESC
        """)
        rows = cur.fetchmany(numRows=limit)
        return [
            dict(
                id_horario=r[0],
                dia_semana=r[1],
                h_inicio=r[2],
                h_final=r[3],
                minutos_equiv=r[4],
                es_continuo=r[5]
            ) for r in rows
        ]
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
        
def validar_horario_aula(id_aula, id_horario, fecha_inicio):
    conn = get_conn()
    cur = conn.cursor()

    # Obtener grado y jornada del aula/sede/institución
    cur.execute("""
        SELECT a.grado, i.jornada
        FROM AULA a
        JOIN INSTITUCION i ON a.id_institucion = i.id_institucion
        WHERE a.id_aula = :1
    """, (id_aula,))

    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return False, "Aula o sede no encontrada."
    grado, jornada = row

    # Obtener datos del horario nuevo
    cur.execute("SELECT dia_semana, h_inicio, h_final, minutos_equiv FROM HORARIO WHERE id_horario = :1", (id_horario,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return False, "El horario no existe."
    dia_semana_new, h_inicio_new, h_final_new, min_equiv_new = row

    # Definición de rangos de jornada
    rango_maniana_inicio = "06:00"
    rango_maniana_fin = "13:00"
    rango_tarde_inicio = "13:00"
    rango_tarde_fin = "18:00"

    dias_primaria = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
    dias_secundaria = dias_primaria + ["Sábado"]

    def en_rango(h, inicio, fin):
        return inicio <= h < fin

    # Validaciones por grado/jornada
    if grado in ("4", "5"):
        if dia_semana_new not in dias_primaria:
            cur.close()
            conn.close()
            return False, "Solo lunes a viernes para 4º/5º."
        if jornada == "MAÑANA" and not (en_rango(h_inicio_new, rango_maniana_inicio, rango_maniana_fin) and en_rango(h_final_new, rango_maniana_inicio, rango_maniana_fin)):
            cur.close()
            conn.close()
            return False, "En 4º/5º con jornada MAÑANA: horario debe estar entre 06:00 y 13:00."
        elif jornada == "TARDE" and not (en_rango(h_inicio_new, rango_tarde_inicio, rango_tarde_fin) and en_rango(h_final_new, rango_tarde_inicio, rango_tarde_fin)):
            cur.close()
            conn.close()
            return False, "En 4º/5º con jornada TARDE: horario debe estar entre 13:00 y 18:00."
        # MIXTA permite ambos rangos
    elif grado in ("9", "10"):
        if dia_semana_new not in dias_secundaria:
            cur.close()
            conn.close()
            return False, "Solo lunes a sábado para 9º/10º."
        if jornada == "MAÑANA" and not (en_rango(h_inicio_new, rango_tarde_inicio, rango_tarde_fin) and en_rango(h_final_new, rango_tarde_inicio, rango_tarde_fin)):
            cur.close()
            conn.close()
            return False, "En 9º/10º con jornada MAÑANA: horario debe estar en la TARDE."
        elif jornada == "TARDE" and not (en_rango(h_inicio_new, rango_maniana_inicio, rango_maniana_fin) and en_rango(h_final_new, rango_maniana_inicio, rango_maniana_fin)):
            cur.close()
            conn.close()
            return False, "En 9º/10º con jornada TARDE: horario debe estar en la MAÑANA."
        # MIXTA permite ambas

    # Validar cruce y duplicidad EXACTA de horario
    cur.execute("""
        SELECT ho.dia_semana, ho.h_inicio, ho.h_final, ho.id_horario
        FROM HISTORICO_HORARIO_AULA ha
        JOIN HORARIO ho ON ha.id_horario = ho.id_horario
        WHERE ha.id_aula = :1 AND ha.fecha_fin IS NULL
    """, (id_aula,))
    def to_mins(h): return int(h[:2]) * 60 + int(h[3:])
    ini_new = to_mins(h_inicio_new)
    fin_new = to_mins(h_final_new)
    for dia_exist, h_ini_exist, h_fin_exist, id_horario_exist in cur.fetchall():
        ini_exist = to_mins(h_ini_exist)
        fin_exist = to_mins(h_fin_exist)
        # Duplicidad exacta
        if dia_exist == dia_semana_new and ini_new == ini_exist and fin_new == fin_exist:
            cur.close()
            conn.close()
            return False, "El horario ya está asignado a esta aula para ese día y franja."
        # Solapamiento parcial
        if dia_exist == dia_semana_new and ini_new < fin_exist and fin_new > ini_exist:
            cur.close()
            conn.close()
            return False, f"Cruce con horario existente ({dia_exist} {h_ini_exist}-{h_fin_exist})."

    # Valida suma máxima de horas equivalentes
    cur.execute("""
        SELECT ho.minutos_equiv
        FROM HISTORICO_HORARIO_AULA ha
        JOIN HORARIO ho ON ha.id_horario = ho.id_horario
        WHERE ha.id_aula = :1 AND ha.fecha_fin IS NULL
    """, (id_aula,))
    total_equiv = sum((r[0] if r[0] else 45) for r in cur.fetchall()) + (min_equiv_new if min_equiv_new else 45)
    if grado in ("4", "5"):
        max_equiv = 2 * 45   # dos horas equivalentes
    elif grado in ("9", "10"):
        max_equiv = 3 * 45   # tres horas equivalentes
    else:
        max_equiv = 3 * 45
    if total_equiv > max_equiv:
        cur.close()
        conn.close()
        return False, f"Supera el máximo de horas equivalentes permitidas ({max_equiv // 45} horas)"

    cur.close()
    conn.close()
    return True, "OK"

# ============================
# HISTÓRICO HORARIO AULA
# ============================

def asignar_horario_aula(data):
    id_aula = data['id_aula']
    id_horario = data['id_horario']
    fecha_inicio = data['fecha_inicio']

    valido, msg = validar_horario_aula(id_aula, id_horario, fecha_inicio)
    if not valido:
        return {"error": msg}
    
    # Realiza insert como antes
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO HISTORICO_HORARIO_AULA (id_aula, id_horario, fecha_inicio)
        VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
    """, (id_aula, id_horario, fecha_inicio))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Horario asignado correctamente."}

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

def list_horarios_aula(id_aula):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.id_hist_horario, h.id_horario, h.fecha_inicio, h.fecha_fin,
            ho.dia_semana, ho.h_inicio, ho.h_final, ho.minutos_equiv, ho.es_continuo
        FROM HISTORICO_HORARIO_AULA h
        JOIN HORARIO ho ON h.id_horario = ho.id_horario
        WHERE h.id_aula = :1
        ORDER BY h.fecha_inicio DESC
    """, (id_aula,))
    rows = cur.fetchall()
    result = [
        dict(
            id_hist_horario=r[0], id_horario=r[1], fecha_inicio=str(r[2]),
            fecha_fin=str(r[3]) if r[3] else None,
            dia_semana=r[4], h_inicio=r[5], h_final=r[6],
            minutos_equiv=r[7], es_continuo=r[8]
        ) for r in rows
    ]
    cur.close()
    conn.close()
    return result

# ============================
# ASIGNACIÓN TUTOR AULA
# ============================

def cerrar_tutor_actual(id_aula: int):
    """Cierra la asignación activa del tutor actual del aula"""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE ASIGNACION_TUTOR at
            SET fecha_fin = SYSDATE
            WHERE at.id_tutor_aula = (
                SELECT id_tutor_aula 
                FROM AULA 
                WHERE id_aula = :1
            )
            AND at.fecha_fin IS NULL
        """, (id_aula,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def list_tutores_aula(id_aula: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                at.id_tutor_aula,
                at.id_persona,
                at.fecha_inicio,
                at.fecha_fin,
                at.motivo_cambio,
                p.nombre,
                p.correo
            FROM ASIGNACION_TUTOR at
            JOIN PERSONA p ON at.id_persona = p.id_persona
            JOIN AULA a ON a.id_tutor_aula = at.id_tutor_aula
            WHERE a.id_aula = :1
            ORDER BY at.fecha_inicio DESC
        """, (id_aula,))
        rows = cur.fetchall()
        return [
            {
                "id_tutor_aula": r[0],
                "id_persona": r[1],
                "fecha_inicio": r[2].strftime("%Y-%m-%d") if r[2] else None,
                "fecha_fin": r[3].strftime("%Y-%m-%d") if r[3] else None,
                "motivo_cambio": r[4],
                "nombre_tutor": r[5],
                "correo_tutor": r[6],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

# --- VALIDACIÓN CRUCE TUTOR ---

def validar_cruce_tutor(id_persona: int, id_aula: int, fecha_inicio: str) -> tuple[bool, str]:
    id_persona = int(id_persona)
    id_aula = int(id_aula)

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM ASIGNACION_TUTOR at
                 JOIN AULA a ON a.id_tutor_aula = at.id_tutor_aula
            WHERE at.id_persona = :1
              AND at.fecha_fin IS NULL
              AND a.id_aula <> :2
        """, (id_persona, id_aula))
        (count,) = cur.fetchone()
        if count > 0:
            return False, "El tutor ya tiene una asignación activa en otra aula."
        return True, ""
    finally:
        cur.close()
        conn.close()

# ---------- ASIGNAR TUTOR ----------

def asignar_tutor_aula(data: dict):
    id_persona = int(data["id_persona"])
    id_aula = int(data["id_aula"])
    fecha_inicio = str(data["fecha_inicio"])[:10]   # 'YYYY-MM-DD'
    motivo = data.get("motivo_cambio")

    valido, msg = validar_cruce_tutor(id_persona, id_aula, fecha_inicio)
    if not valido:
        return {"error": msg}

    conn = get_conn()
    cur = conn.cursor()
    try:
        # Cerrar tutor actual del aula (si lo hay)
        cur.execute("""
            UPDATE ASIGNACION_TUTOR at
            SET fecha_fin = SYSDATE
            WHERE at.id_tutor_aula = (
                SELECT id_tutor_aula FROM AULA WHERE id_aula = :1
            )
              AND at.fecha_fin IS NULL
        """, (id_aula,))

        # Insertar nueva asignación
        new_id = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO ASIGNACION_TUTOR (id_persona, fecha_inicio, motivo_cambio)
            VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), :3)
            RETURNING id_tutor_aula INTO :4
        """, (id_persona, fecha_inicio, motivo, new_id))

        id_tutor_aula = int(new_id.getvalue()[0])

        # Actualizar AULA con el nuevo tutor
        cur.execute("""
            UPDATE AULA
            SET id_tutor_aula = :1
            WHERE id_aula = :2
        """, (id_tutor_aula, id_aula))

        conn.commit()
        return {
            "msg": "Tutor asignado al aula. Se conserva el historial.",
            "id_tutor_aula": id_tutor_aula
        }
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

# ============================
# HISTÓRICO AULA ESTUDIANTE
# ============================

def asignar_estudiante_aula(data):
    conn = get_conn()
    cur = conn.cursor()
    # Verificar si ya tiene una asignación activa
    cur.execute("""
        SELECT COUNT(*) FROM HISTORICO_AULA_ESTUDIANTE
        WHERE id_estudiante = :1 AND fecha_fin IS NULL
    """, (data['id_estudiante'],))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return {"error": "El estudiante ya pertenece a un aula activa."}
    # Si no, inserta la nueva asignación
    from datetime import date
    fecha = data.get('fecha_inicio') or date.today().isoformat()
    cur.execute("""
        INSERT INTO HISTORICO_AULA_ESTUDIANTE (id_estudiante, id_aula, fecha_inicio)
        VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
    """, (data['id_estudiante'], data['id_aula'], fecha))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Estudiante asignado correctamente"}


def listar_asignaciones_por_estudiante(id_estudiante):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT h.id_hist_aula_est, h.id_estudiante, h.id_aula, 
                   a.id_institucion, a.id_sede, a.grado,
                   h.fecha_inicio, h.fecha_fin
            FROM HISTORICO_AULA_ESTUDIANTE h
            JOIN AULA a ON h.id_aula = a.id_aula
            WHERE h.id_estudiante = :1
        """, (id_estudiante,))
        rows = cur.fetchall()
        return [
            dict(id_hist_aula_est=r[0], id_estudiante=r[1], id_aula=r[2],
                 id_institucion=r[3], id_sede=r[4], grado=r[5], 
                 fecha_inicio=str(r[6]), fecha_fin=str(r[7]) if r[7] else None) for r in rows
        ]
    finally:
        cur.close()
        conn.close()

# ============================
# HORARIOS POR TUTOR
# ============================

def list_horario_tutor(id_persona):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT at.id_tutor_aula, a.id_aula, a.grado, h.dia_semana, h.h_inicio, h.h_final, h.minutos_equiv, h.es_continuo, hha.fecha_inicio
        FROM ASIGNACION_TUTOR at
        JOIN AULA a ON at.id_aula = a.id_aula
        JOIN HISTORICO_HORARIO_AULA hha ON a.id_aula = hha.id_aula AND hha.fecha_fin IS NULL
        JOIN HORARIO h ON hha.id_horario = h.id_horario
        WHERE at.id_persona = :1 AND at.fecha_fin IS NULL
        ORDER BY h.dia_semana, h.h_inicio
    """, (id_persona,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        dict(
            id_tutor_aula=r[0],
            id_aula=r[1],
            grado=r[2],
            dia_semana=r[3],
            h_inicio=r[4],
            h_final=r[5],
            minutos_equiv=r[6],
            es_continuo=r[7],
            fecha_inicio=str(r[8]) if r[8] else None  # Convierte a string (ISO) para React
        ) for r in rows
    ]

def listar_tutores():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "SELECT id_persona, nombre, correo FROM persona WHERE rol = 'TUTOR'"
    )
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_persona": r[0], "nombre": r[1], "correo": r[2]} for r in rows]
#crud estudiantes

def create_estudiante(data):
    conn = get_conn()
    cur = conn.cursor()
    # Verificar num_documento único
    cur.execute("SELECT COUNT(*) FROM ESTUDIANTE WHERE num_documento = :1", (data['num_documento'],))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return {"error": "Ya existe un estudiante con ese número de documento."}
    # Verificar correo único (si se envía)
    correo = data.get('correo')
    if correo:
        cur.execute("SELECT COUNT(*) FROM ESTUDIANTE WHERE lower(correo) = lower(:1)", (correo,))
        if cur.fetchone()[0] > 0:
            cur.close()
            conn.close()
            return {"error": "Ya existe un estudiante con ese correo."}

    # Insertar registro
    cur.execute("""INSERT INTO ESTUDIANTE
        (tipo_documento, num_documento, nombres, apellidos, telefono, fecha_nacimiento, correo)
        VALUES (:1, :2, :3, :4, :5, TO_DATE(:6, 'YYYY-MM-DD'), :7)
    """, (
        data.get('tipo_documento'), data['num_documento'], data['nombres'], data.get('apellidos'),
        data.get('telefono'), data.get('fecha_nacimiento'), data.get('correo')
    ))
    conn.commit()
    cur.execute("SELECT id_estudiante FROM ESTUDIANTE WHERE num_documento = :1", (data['num_documento'],))
    r = cur.fetchone()
    cur.close()
    conn.close()
    return r[0] if r else None

def update_estudiante(id_est, data):
    conn = get_conn()
    cur = conn.cursor()
    # Prohibir duplicidad de documento (en otro estudiante)
    cur.execute("SELECT COUNT(*) FROM ESTUDIANTE WHERE num_documento = :1 AND id_estudiante != :2", (data['num_documento'], id_est))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return {"error": "Ya existe otro estudiante con ese número de documento."}
    # Prohibir duplicidad de correo (en otro estudiante)
    correo = data.get('correo')
    if correo:
        cur.execute("SELECT COUNT(*) FROM ESTUDIANTE WHERE lower(correo) = lower(:1) AND id_estudiante != :2", (correo, id_est))
        if cur.fetchone()[0] > 0:
            cur.close()
            conn.close()
            return {"error": "Ya existe otro estudiante con ese correo."}
    # Update
    cur.execute("""
        UPDATE ESTUDIANTE SET tipo_documento=:1, num_documento=:2, nombres=:3, apellidos=:4,
            telefono=:5, fecha_nacimiento=TO_DATE(:6, 'YYYY-MM-DD'), correo=:7
        WHERE id_estudiante=:8
    """, (
        data.get('tipo_documento'), data['num_documento'], data['nombres'], data.get('apellidos'),
        data.get('telefono'), data.get('fecha_nacimiento'), data.get('correo'), id_est
    ))
    conn.commit()
    cur.close()
    conn.close()
    return True


def list_estudiantes(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_estudiante, tipo_documento, num_documento, nombres, apellidos, telefono, fecha_nacimiento, correo FROM ESTUDIANTE ORDER BY id_estudiante")
        rows = cur.fetchmany(numRows=limit)
        return [
            dict(
                id_estudiante=r[0],
                tipo_documento=r[1],
                num_documento=r[2],
                nombres=r[3],
                apellidos=r[4],
                telefono=r[5],
                fecha_nacimiento=str(r[6]) if r[6] else None,
                correo=r[7]
            ) for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def get_estudiante(id_est):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_estudiante, tipo_documento, num_documento, nombres, apellidos, telefono, fecha_nacimiento, correo FROM ESTUDIANTE WHERE id_estudiante = :1", (id_est,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(
            id_estudiante=r[0],
            tipo_documento=r[1],
            num_documento=r[2],
            nombres=r[3],
            apellidos=r[4],
            telefono=r[5],
            fecha_nacimiento=str(r[6]) if r[6] else None,
            correo=r[7]
        )
    finally:
        cur.close()
        conn.close()

def delete_estudiante(id_est):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM ESTUDIANTE WHERE id_estudiante = :1", (id_est,))
        conn.commit()
    finally:
        cur.close()
        conn.close()









# Similar wrappers can be added for Aula, Estudiante, Horario, Asignacion_Tutor, etc.





def create_periodo(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    # Conversión robusta de fechas
    fecha_inicio = datetime.strptime(data['fecha_inicio'], "%Y-%m-%d").date() if data['fecha_inicio'] else date.today()
    fecha_fin = datetime.strptime(data['fecha_fin'], "%Y-%m-%d").date() if data['fecha_fin'] else date.today()
    cur.execute(
        "INSERT INTO PERIODO (nombre, fecha_inicio, fecha_fin) VALUES (:1, :2, :3)",
        (data['nombre'], fecha_inicio, fecha_fin)
    )
    conn.commit()
    cur.close()
    conn.close()

def list_periodos():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_periodo, nombre, fecha_inicio, fecha_fin FROM PERIODO ORDER BY id_periodo DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        dict(id_periodo=r[0], nombre=r[1], fecha_inicio=str(r[2]), fecha_fin=str(r[3]))
        for r in rows
    ]

def crear_componente(nombre: str, porcentaje: float, tipo_programa: str, id_periodo: int):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO COMPONENTE (nombre, porcentaje, tipo_programa, id_periodo)
        VALUES (:1, :2, :3, :4)
    """, [nombre, porcentaje, tipo_programa, id_periodo])
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "msg": "Componente registrado exitosamente"}


def list_componentes():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_componente, nombre, porcentaje FROM COMPONENTE ORDER BY id_componente DESC")
        rows = cur.fetchall()
        return [
            dict(id_componente=r[0], nombre=r[1], porcentaje=r[2])
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()



# --- Aulas por tutor ---
def get_aulas_por_tutor(id_tutor):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id_aula, a.grado
        FROM asignacion_tutor at
        JOIN aula a ON at.id_aula = a.id_aula
        WHERE at.id_persona = :1 AND at.fecha_fin IS NULL
    """, (id_tutor,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_aula": r[0], "grado": r[1]} for r in rows]

def obtener_id_semana(fecha_clase):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_semana FROM semana
        WHERE fecha_inicio <= TO_DATE(:1,'YYYY-MM-DD') 
          AND fecha_fin >= TO_DATE(:1,'YYYY-MM-DD')
        """, [fecha_clase])
    r = cur.fetchone()
    cur.close()
    conn.close()
    return r[0] if r else None

def obtener_id_horario_para_asistencia(id_aula, fecha_clase, hora_inicio):
    fecha = datetime.strptime(fecha_clase, "%Y-%m-%d")
    dia = fecha.strftime('%A').capitalize()
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT h.id_horario FROM horario h
        JOIN historico_horario_aula ha ON ha.id_horario = h.id_horario
        WHERE ha.id_aula = :1 AND h.dia_semana = :2
        AND (ha.fecha_fin IS NULL OR ha.fecha_fin >= TO_DATE(:3,'YYYY-MM-DD'))
        AND ha.fecha_inicio <= TO_DATE(:3,'YYYY-MM-DD')
        AND h.h_inicio <= :4 AND h.h_final >= :4
    """, (id_aula, dia, fecha_clase, hora_inicio))
    r = cur.fetchone()
    cur.close()
    conn.close()
    return r[0] if r else None

def es_festivo(fecha_clase):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM festivo WHERE fecha = TO_DATE(:1,'YYYY-MM-DD')", [fecha_clase])
    is_fest = cur.fetchone()[0] > 0
    cur.close()
    conn.close()
    return 1 if is_fest else 0

def registrar_asistencia_aula(data):
    conn = get_conn()
    cur = conn.cursor()
    # Validaciones previas
    obligatorios = ["id_aula", "id_tutor_aula", "id_horario", "id_semana", "fecha_clase", "hora_inicio", "dictada", "horas_dictadas", "corresponde_horario", "es_festivo"]
    for key in obligatorios:
        if data.get(key) in (None, ""):
            cur.close()
            conn.close()
            return {"error": f"Falta el campo obligatorio: {key}"}
    if data['dictada'] == "N" and not data.get('id_motivo'):
        cur.close()
        conn.close()
        return {"error": "Debe registrar el motivo de inasistencia"}
    if data.get('reposicion') == "S" and not data.get('fecha_reposicion'):
        cur.close()
        conn.close()
        return {"error": "Indique la fecha de reposición"}

    # Insert
    cur.execute("""
        INSERT INTO ASISTENCIA_AULA (
            id_aula, id_tutor_aula, id_horario, id_semana, fecha_clase,
            hora_inicio, hora_fin, dictada, horas_dictadas, reposicion,
            fecha_reposicion, id_motivo, corresponde_horario, es_festivo)
        VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), :6, :7, :8, :9, :10, TO_DATE(:11, 'YYYY-MM-DD'), :12, :13, :14)
    """, (
        data['id_aula'], data['id_tutor_aula'], data['id_horario'], data['id_semana'], data['fecha_clase'],
        data['hora_inicio'], data.get('hora_fin'), data['dictada'], data['horas_dictadas'], data.get('reposicion','N'),
        data.get('fecha_reposicion'), data.get('id_motivo'), data['corresponde_horario'], data['es_festivo']
    ))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Asistencia registrada correctamente."}

def modificar_asistencia_aula(id_asist, data):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Define solamente los campos que realmente vas a actualizar
        fields = [
            ("id_aula", data.get("id_aula")),
            ("id_tutor_aula", data.get("id_tutor_aula")),
            ("id_horario", data.get("id_horario")),
            ("id_semana", data.get("id_semana")),
            ("fecha_clase", data.get("fecha_clase")),        # -> YYYY-MM-DD
            ("hora_inicio", data.get("hora_inicio")),
            ("hora_fin", data.get("hora_fin")),
            ("dictada", data.get("dictada")),
            ("horas_dictadas", data.get("horas_dictadas")),
            ("reposicion", data.get("reposicion")),
            ("fecha_reposicion", data.get("fecha_reposicion")),
            ("id_motivo", data.get("id_motivo")),
            ("corresponde_horario", data.get("corresponde_horario")),
            ("es_festivo", data.get("es_festivo")),
        ]
        set_stmt = []
        valores = []
        for f, v in fields:
            if v is not None:
                if f == "fecha_clase":
                    set_stmt.append(f"{f}=TO_DATE(:{len(valores)+1}, 'YYYY-MM-DD')")
                    valores.append(str(v)[:10] if v else None)
                else:
                    set_stmt.append(f"{f}=:{len(valores)+1}")
                    valores.append(v)
        if not set_stmt:
            return {"error": "No hay campos para modificar."}
        sql = f"UPDATE ASISTENCIA_AULA SET {', '.join(set_stmt)} WHERE id_asist=:{len(valores)+1}"
        valores.append(id_asist)
        cur.execute(sql, valores)
        conn.commit()
        return True
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


# --- Ingresar nota (ejemplo simple, ajusta según tus tablas) ---
def ingresar_nota(data):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO nota_estudiante (id_aula, id_estudiante, nota) VALUES (:1, :2, :3)",
        (data['id_aula'], data['id_estudiante'], data['nota'])
    )
    conn.commit()
    cur.close()
    conn.close()


    from .db import get_conn
from datetime import datetime

def listar_tutores():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_persona, nombre FROM persona WHERE rol = 'TUTOR'")
    datos = [dict(id_persona=r[0], nombre=r[1]) for r in cur]
    cur.close()
    conn.close()
    return datos

def get_aulas_por_tutor(id_tutor):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id_aula, a.grado
        FROM asignacion_tutor at
        JOIN aula a ON at.id_aula = a.id_aula
        WHERE at.id_persona = :1 AND (at.fecha_fin IS NULL OR at.fecha_fin > SYSDATE)
    """, [id_tutor])
    datos = [dict(id_aula=r[0], grado=r[1]) for r in cur]
    cur.close()
    conn.close()
    return datos

def hora_a_minutos(h_str):
    h, m = map(int, h_str.split(":"))
    return h * 60 + m

def get_horarios_aula(id_aula):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT ho.dia_semana, ho.h_inicio, ho.h_final, hha.fecha_inicio
        FROM HISTORICO_HORARIO_AULA hha
        JOIN HORARIO ho ON hha.id_horario = ho.id_horario
        WHERE hha.id_aula = :1 AND hha.fecha_fin IS NULL

    """, (id_aula,))
    horarios = []
    for r in cur.fetchall():
        horarios.append({
            "dia_semana": r[0],
            "h_inicio": r[1],
            "h_final": r[2],
            "fechainicio": r[3].strftime("%Y-%m-%d") if r[3] else None
        })
    cur.close()
    conn.close()
    return horarios





def get_motivos_inasistencia():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_motivo, descripcion FROM motivo_inasistencia")
    datos = [dict(id_motivo=r[0], descripcion=r[1]) for r in cur]
    cur.close()
    conn.close()
    return datos

def get_id_tutor_aula(id_tutor, id_aula):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_tutor_aula FROM asignacion_tutor
        WHERE id_persona = :1 AND id_aula = :2
        AND (fecha_fin IS NULL OR fecha_fin > SYSDATE)
        ORDER BY fecha_inicio DESC FETCH FIRST 1 ROWS ONLY
    """, [id_tutor, id_aula])
    r = cur.fetchone()
    cur.close()
    conn.close()
    return {"id_tutor_aula": r[0] if r else None}

def encontrar_horario_y_semana(id_aula, fecha_clase, hora_inicio):
    from datetime import datetime
    conn = get_conn()
    cur = conn.cursor()

    fecha = datetime.strptime(fecha_clase, "%Y-%m-%d")
    dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
    dia_semana = dias[fecha.weekday()]

    # Normaliza hora a HH:MM
    if len(hora_inicio) > 5:
        hora_inicio = hora_inicio[:5]

    cur.execute("""
        SELECT h.id_horario, h.h_inicio, h.h_final
        FROM HISTORICO_HORARIO_AULA ha
        JOIN HORARIO h ON ha.id_horario = h.id_horario
        WHERE ha.id_aula = :1 AND h.dia_semana = :2 AND ha.fecha_fin IS NULL
    """, (id_aula, dia_semana))
    horarios = cur.fetchall()

    id_horario = None
    corresponde_horario = 0

    def to_mins(h): return int(h[:2]) * 60 + int(h[3:5])

    mins_input = to_mins(hora_inicio)
    for h in horarios:
        mins_ini, mins_fin = to_mins(h[1]), to_mins(h[2])
        if mins_ini <= mins_input < mins_fin:
            id_horario = h[0]
            corresponde_horario = 1
            break

    cur.execute("""
        SELECT ID_SEMANA FROM SEMANA
        WHERE FECHA_INICIO <= TO_DATE(:1, 'YYYY-MM-DD') AND FECHA_FIN >= TO_DATE(:2, 'YYYY-MM-DD')
    """, (fecha_clase, fecha_clase))
    r = cur.fetchone()
    id_semana = r[0] if r else None

    cur.execute("SELECT COUNT(*) FROM FESTIVO WHERE FECHA = TO_DATE(:1, 'YYYY-MM-DD')", (fecha_clase,))
    es_festivo = 1 if cur.fetchone()[0] > 0 else 0

    print("DEBUG >>>> Día:", dia_semana, "Horarios:", horarios, "hora_inicio:", hora_inicio, "id_horario:", id_horario, "id_semana:", id_semana)

    cur.close()
    conn.close()
    return {
        "id_horario": id_horario,
        "id_semana": id_semana,
        "corresponde_horario": corresponde_horario,
        "es_festivo": es_festivo
    }

def generar_calendario_semanas(anio: int):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    # Valida duplicidad
    cur.execute("SELECT COUNT(*) FROM SEMANA WHERE EXTRACT(YEAR FROM fecha_inicio) = :1", [anio])
    si_existe = cur.fetchone()[0]
    if si_existe > 0:
        cur.close()
        conn.close()
        return {"ok": False, "msg": f"El calendario del año {anio} ya existe. No se puede volver a crear."}
    # Genera calendario semana por semana (lunes-domingo)
    fecha_ini = date(anio, 1, 1)
    fecha_fin = date(anio, 12, 31)
    semana_ini = fecha_ini
    numero_semana = 1
    # Ajusta para que siempre empiece en lunes
    while semana_ini.weekday() != 0:
        semana_ini += timedelta(days=1)
    while semana_ini <= fecha_fin:
        semana_fin = semana_ini + timedelta(days=6)
        if semana_fin > fecha_fin:
            semana_fin = fecha_fin
        # El orden correcto es: INICIO (menor), FIN (mayor)
        cur.execute("""
            INSERT INTO SEMANA (NUMERO_SEMANA, FECHA_INICIO, FECHA_FIN)
            VALUES (:1, TO_DATE(:2,'YYYY-MM-DD'), TO_DATE(:3,'YYYY-MM-DD'))
        """, [numero_semana, semana_ini.strftime('%Y-%m-%d'), semana_fin.strftime('%Y-%m-%d')])
        semana_ini += timedelta(days=7)
        numero_semana += 1
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "msg": f"Semanas para el año {anio} generadas exitosamente."}

def listar_semanas():
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT numero_semana, fecha_inicio, fecha_fin FROM SEMANA ORDER BY fecha_inicio")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    # Fechas a string
    return [
        {
            "numero_semana": r[0],
            "fecha_inicio": r[1].strftime('%Y-%m-%d'),
            "fecha_fin": r[2].strftime('%Y-%m-%d')
        } for r in rows
    ]

def agregar_festivo(fecha: str, descripcion: str):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    # Valida duplicado (no mete el mismo día dos veces)
    cur.execute("SELECT COUNT(*) FROM FESTIVO WHERE fecha = TO_DATE(:1,'YYYY-MM-DD')", [fecha])
    existe = cur.fetchone()[0]
    if existe > 0:
        cur.close()
        conn.close()
        return {"ok": False, "msg": "Ese festivo ya existe."}
    cur.execute(
        "INSERT INTO FESTIVO (fecha, descripcion) VALUES (TO_DATE(:1,'YYYY-MM-DD'), :2)",
        [fecha, descripcion]
    )
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "msg": f"Festivo registrado: {descripcion} - {fecha}"}

def listar_festivos(anio: int):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_festivo, fecha, descripcion 
        FROM FESTIVO 
        WHERE EXTRACT(YEAR FROM fecha) = :1
        ORDER BY fecha
    """, [anio])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {"id_festivo": r[0], "fecha": r[1].strftime('%Y-%m-%d'), "descripcion": r[2]}
        for r in rows
    ]

def agregar_motivo_inasistencia(descripcion: str):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    # Valida duplicado por descripción exacta (puedes poner lower para evitar mayúsculas/minúsculas)
    cur.execute("SELECT COUNT(*) FROM MOTIVO_INASISTENCIA WHERE lower(descripcion) = lower(:1)", [descripcion])
    existe = cur.fetchone()[0]
    if existe > 0:
        cur.close()
        conn.close()
        return {"ok": False, "msg": "Ese motivo ya existe."}
    cur.execute("INSERT INTO MOTIVO_INASISTENCIA (descripcion) VALUES (:1)", [descripcion])
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "msg": f"Motivo registrado: {descripcion}"}

def listar_motivos():
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_motivo, descripcion FROM MOTIVO_INASISTENCIA ORDER BY descripcion")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_motivo": r[0], "descripcion": r[1]} for r in rows]

def eliminar_motivo(id_motivo: int):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM MOTIVO_INASISTENCIA WHERE id_motivo = :1", [id_motivo])
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "msg": "Motivo eliminado."}

def modificar_motivo(id_motivo, descripcion):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE MOTIVO_INASISTENCIA SET descripcion=:1 WHERE id_motivo=:2",
                (descripcion, id_motivo))
    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Motivo actualizado."}

def listar_clases_tutor(id_persona: int):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT aa.id_asist, aa.fecha_clase, aa.id_aula, aa.id_horario, aa.id_semana
        FROM ASISTENCIA_AULA aa
        JOIN ASIGNACION_TUTOR at ON aa.id_tutor_aula = at.id_tutor_aula
        WHERE at.id_persona = :1
        ORDER BY aa.fecha_clase DESC
    """, [id_persona])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id_asist": r[0],
            "fecha_clase": r[1].strftime('%Y-%m-%d'),
            "id_aula": r[2],
            "id_horario": r[3],
            "id_semana": r[4]
        } for r in rows
    ]

def listar_aulas_tutor(id_persona: int):
    """Lista aulas asignadas a un tutor"""
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT a.id_aula, a.grado
        FROM AULA a
        JOIN ASIGNACION_TUTOR at ON a.id_aula = at.id_aula
        WHERE at.id_persona = :1 AND at.fecha_fin IS NULL
        ORDER BY a.grado
    """, [id_persona])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_aula": r[0], "grado": r[1]} for r in rows]


def listar_estudiantes_aula(id_aula: int):
    """Lista estudiantes matriculados en un aula"""
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT e.id_estudiante, e.nombres, e.apellidos
        FROM ESTUDIANTE e
        JOIN HISTORICO_AULA_ESTUDIANTE hae ON e.id_estudiante = hae.id_estudiante
        WHERE hae.id_aula = :1 AND hae.fecha_fin IS NULL
        ORDER BY e.apellidos, e.nombres
    """, [id_aula])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_estudiante": r[0], "nombres": r[1], "apellidos": r[2]} for r in rows]


def listar_periodos():
    """Lista todos los períodos"""
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_periodo, nombre FROM PERIODO ORDER BY fecha_inicio DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_periodo": r[0], "nombre": r[1]} for r in rows]


def listar_componentes_periodo(id_periodo: int):
    """Lista componentes de un período"""
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_componente, nombre, porcentaje
        FROM COMPONENTE
        WHERE id_periodo = :1
        ORDER BY nombre
    """, [id_periodo])
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id_componente": r[0], "nombre": r[1], "porcentaje": r[2]} for r in rows]


def obtener_nota_estudiante(id_estudiante: int, id_periodo: int, id_componente: int):
    """Obtiene nota existente de un estudiante"""
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_nota, nota
        FROM NOTA_ESTUDIANTE
        WHERE id_estudiante = :1 AND id_periodo = :2 AND id_componente = :3
    """, [id_estudiante, id_periodo, id_componente])
    row = cur.fetchone()
    cur.close()
    conn.close()
    if row:
        return {"id_nota": row[0], "nota": row[1]}
    return {"id_nota": None, "nota": None}


def registrar_nota_estudiante(id_estudiante: int, id_periodo: int, id_componente: int, nota: float):
    """Registra o actualiza nota de un estudiante"""
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    # Valida que nota esté entre 0 y 5 (o el rango que uses)
    if nota < 0 or nota > 5:
        return {"ok": False, "msg": "La nota debe estar entre 0 y 5"}
    # Verifica si existe
    cur.execute("""
        SELECT id_nota FROM NOTA_ESTUDIANTE
        WHERE id_estudiante = :1 AND id_periodo = :2 AND id_componente = :3
    """, [id_estudiante, id_periodo, id_componente])
    existe = cur.fetchone()
    if existe:
        cur.execute("""
            UPDATE NOTA_ESTUDIANTE
            SET nota = :4
            WHERE id_estudiante = :1 AND id_periodo = :2 AND id_componente = :3
        """, [id_estudiante, id_periodo, id_componente, nota])
        msg = "Nota actualizada"
    else:
        cur.execute("""
            INSERT INTO NOTA_ESTUDIANTE (id_estudiante, id_periodo, id_componente, nota)
            VALUES (:1, :2, :3, :4)
        """, [id_estudiante, id_periodo, id_componente, nota])
        msg = "Nota registrada"
    conn.commit()
    cur.close()
    conn.close()
    return {"ok": True, "msg": msg}

