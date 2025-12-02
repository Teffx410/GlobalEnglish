# app/crud.py
from typing import Optional, Tuple
from app.db import get_conn
import oracledb
import secrets
from datetime import date, datetime, timedelta

# ============================
# INSTITUCION
# ============================

def create_institucion(data: dict):
    """Crea una institución validando que el nombre sea único y usando RETURNING INTO."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que el nombre no exista
        cur.execute("SELECT COUNT(*) FROM INSTITUCION WHERE LOWER(nombre_inst) = LOWER(:1)", 
                    (data['nombre_inst'],))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe una institución con ese nombre"}
        
        # Usar RETURNING INTO para obtener el ID de forma atómica y eficiente
        id_institucion_var = cur.var(oracledb.NUMBER)
        cur.execute("""INSERT INTO INSTITUCION(nombre_inst, jornada, dir_principal)
                        VALUES (:1,:2,:3)
                        RETURNING id_institucion INTO :4""",
                    (data['nombre_inst'], data.get('jornada'), data.get('dir_principal'), id_institucion_var))
        conn.commit()
        
        id_institucion = id_institucion_var.getvalue()[0]
        return {"ok": True, "id_institucion": id_institucion}
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
            INSERT INTO AULA (id_institucion, id_sede, grado)
            VALUES (:1, :2, :3)
        """, (data["id_institucion"], data["id_sede"], data["grado"]))
        conn.commit()

        cur.execute("""
            SELECT id_aula
            FROM AULA
            WHERE id_institucion = :1
              AND id_sede = :2
              AND grado = :3
            ORDER BY id_aula DESC
        """, (data["id_institucion"], data["id_sede"], data["grado"]))
        r = cur.fetchone()
        return r[0] if r else None
    finally:
        cur.close()
        conn.close()


def list_aulas(limit: int = 100):
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
            dict(
                id_aula=r[0],
                id_institucion=r[1],
                id_sede=r[2],
                grado=r[3],
            )
            for r in rows
        ]
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
        return dict(
            id_aula=r[0],
            id_institucion=r[1],
            id_sede=r[2],
            grado=r[3],
        )
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
                id_sede        = :2,
                grado          = :3
            WHERE id_aula      = :4
        """, (data["id_institucion"], data["id_sede"], data["grado"], id_aula))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def delete_aula(id_aula: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # si quieres, aquí primero borrar filas relacionadas en TUTOR_AULA
        cur.execute("DELETE FROM TUTOR_AULA WHERE id_aula = :1", (id_aula,))
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

    # 1. Grado y jornada del aula
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

    # Normalizar grado a int
    try:
        grado_int = int(str(grado).strip())
    except ValueError:
        grado_int = None

    # Normalizar fecha_inicio a date
    fecha_new = datetime.strptime(fecha_inicio[:10], "%Y-%m-%d").date()

    # 2. Datos del horario nuevo
    cur.execute("""
        SELECT dia_semana, h_inicio, h_final, minutos_equiv
        FROM HORARIO
        WHERE id_horario = :1
    """, (id_horario,))
    row = cur.fetchone()
    if not row:
        cur.close()
        conn.close()
        return False, "El horario no existe."
    dia_semana_new, h_inicio_new, h_final_new, min_equiv_new = row
    min_equiv_new = min_equiv_new or 60  # tamaño de la hora equivalente

    # --- utilidades ---
    rango_maniana_inicio = "06:00"
    rango_maniana_fin    = "13:00"
    rango_tarde_inicio   = "13:00"
    rango_tarde_fin      = "18:00"

    dias_primaria   = ("Lunes", "Martes", "Miércoles", "Jueves", "Viernes")
    dias_secundaria = dias_primaria + ("Sábado",)

    def en_rango(h, inicio, fin):
        return inicio <= h <= fin

    def to_mins(hhmm: str) -> int:
        h, m = map(int, hhmm.split(":"))
        return h * 60 + m

    # Duración real de la franja
    duracion_min = to_mins(h_final_new) - to_mins(h_inicio_new)

    # 2.1 Límite de duración de UNA franja
    if grado_int in (4, 5) and duracion_min > 120:
        cur.close()
        conn.close()
        return False, "Para 4° y 5° cada franja no puede exceder 2 horas continuas."
    if grado_int in (9, 10) and duracion_min > 180:
        cur.close()
        conn.close()
        return False, "Para 9° y 10° cada franja no puede exceder 3 horas continuas."

    # 2.2 Reglas de jornada/días
    if grado_int in (4, 5):
        if dia_semana_new not in dias_primaria:
            cur.close()
            conn.close()
            return False, "Solo lunes a viernes para 4° y 5°."
        if jornada == "MAÑANA" and not (
            en_rango(h_inicio_new, rango_maniana_inicio, rango_maniana_fin)
            and en_rango(h_final_new,  rango_maniana_inicio, rango_maniana_fin)
        ):
            cur.close()
            conn.close()
            return False, "En 4°-5° con jornada MAÑANA el horario debe estar entre 06:00 y 13:00."
        if jornada == "TARDE" and not (
            en_rango(h_inicio_new, rango_tarde_inicio, rango_tarde_fin)
            and en_rango(h_final_new,  rango_tarde_inicio, rango_tarde_fin)
        ):
            cur.close()
            conn.close()
            return False, "En 4°-5° con jornada TARDE el horario debe estar entre 13:00 y 18:00."

    elif grado_int in (9, 10):
        if dia_semana_new not in dias_secundaria:
            cur.close()
            conn.close()
            return False, "Solo lunes a sábado para 9° y 10°."
        if jornada == "MAÑANA" and not (
            en_rango(h_inicio_new, rango_tarde_inicio, rango_tarde_fin)
            and en_rango(h_final_new,  rango_tarde_inicio, rango_tarde_fin)
        ):
            cur.close()
            conn.close()
            return False, "En 9°-10° con jornada MAÑANA el horario debe estar en la TARDE (13:00–18:00)."
        if jornada == "TARDE" and not (
            en_rango(h_inicio_new, rango_maniana_inicio, rango_maniana_fin)
            and en_rango(h_final_new,  rango_maniana_inicio, rango_maniana_fin)
        ):
            cur.close()
            conn.close()
            return False, "En 9°-10° con jornada TARDE el horario debe estar en la MAÑANA (06:00–13:00)."
    # MIXTA permite ambas franjas

    # 3. Duplicidad / solapamiento con horarios ACTIVOS
    cur.execute("""
        SELECT ho.dia_semana, ho.h_inicio, ho.h_final, ho.id_horario
        FROM HISTORICO_HORARIO_AULA ha
        JOIN HORARIO ho ON ha.id_horario = ho.id_horario
        WHERE ha.id_aula = :1
          AND ha.fecha_fin IS NULL
    """, (id_aula,))

    ini_new = to_mins(h_inicio_new)
    fin_new = to_mins(h_final_new)

    for dia_exist, h_ini_exist, h_fin_exist, _ in cur.fetchall():
        ini_exist = to_mins(h_ini_exist)
        fin_exist = to_mins(h_fin_exist)

        if dia_exist == dia_semana_new and ini_new == ini_exist and fin_new == fin_exist:
            cur.close()
            conn.close()
            return False, "El horario ya está asignado a esta aula para ese día y franja."

        if dia_exist == dia_semana_new and ini_new < fin_exist and fin_new > ini_exist:
            cur.close()
            conn.close()
            return False, f"Cruce con horario existente: {dia_exist} {h_ini_exist}-{h_fin_exist}."

    # 3.b No reutilizar MISMA franja dentro de un rango de fechas ya usado (históricos finalizados)
    cur.execute("""
        SELECT hha.fecha_inicio, hha.fecha_fin
        FROM HISTORICO_HORARIO_AULA hha
        JOIN HORARIO ho ON hha.id_horario = ho.id_horario
        WHERE hha.id_aula = :1
          AND hha.fecha_fin IS NOT NULL
          AND ho.dia_semana = :2
          AND ho.h_inicio   = :3
          AND ho.h_final    = :4
    """, (id_aula, dia_semana_new, h_inicio_new, h_final_new))

    for f_ini, f_fin in cur.fetchall():
        ini = f_ini.date() if hasattr(f_ini, "date") else f_ini
        fin = f_fin.date() if hasattr(f_fin, "date") else f_fin
        if ini <= fecha_new <= fin:
            cur.close()
            conn.close()
            return False, (
                "Ya existe un historial para este mismo horario entre "
                f"{ini} y {fin}; no puede volver a usarse dentro de ese rango."
            )

    # 4. Tope de horas equivalentes VIGENTES en la fecha de inicio
    cur.execute("""
        SELECT ho.minutos_equiv
        FROM HISTORICO_HORARIO_AULA ha
        JOIN HORARIO ho ON ha.id_horario = ho.id_horario
        WHERE ha.id_aula = :1
          AND ha.fecha_inicio <= TO_DATE(:2, 'YYYY-MM-DD')
          AND (ha.fecha_fin IS NULL OR ha.fecha_fin >= TO_DATE(:3, 'YYYY-MM-DD'))
    """, (id_aula, fecha_inicio[:10], fecha_inicio[:10]))

    total_equiv = sum(r[0] for r in cur.fetchall() if r[0] is not None)

    if grado_int in (4, 5):
        max_equiv = 2 * 60      # 2 horas equivalentes
    elif grado_int in (9, 10):
        max_equiv = 3 * 60      # 3 horas equivalentes
    else:
        max_equiv = 3 * 60

    if total_equiv + min_equiv_new > max_equiv:
        cur.close()
        conn.close()
        return False, f"Supera el máximo de horas equivalentes permitidas ({max_equiv // 60} horas)."

    cur.close()
    conn.close()
    return True, "OK"
# ============================
# HISTÓRICO HORARIO AULA
# ============================

def asignar_horario_aula(data):
    id_aula = data["id_aula"]
    id_horario = data["id_horario"]
    fecha_inicio = data["fecha_inicio"]

    valido, msg = validar_horario_aula(id_aula, id_horario, fecha_inicio)
    if not valido:
        return {"error": msg}

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
                "fecha_fin": r[4],
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

def list_horarios_aula(id_aula: int):
    """
    Historial completo de horarios de un aula (activos e inactivos).
    Usado en la pantalla 'Asignar horario a aula'.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
              hha.id_hist_horario,
              hha.id_horario,
              hha.fecha_inicio,
              hha.fecha_fin,
              ho.dia_semana,
              ho.h_inicio,
              ho.h_final,
              ho.minutos_equiv,
              ho.es_continuo
            FROM HISTORICO_HORARIO_AULA hha
            JOIN HORARIO ho ON hha.id_horario = ho.id_horario
            WHERE hha.id_aula = :1
            ORDER BY hha.fecha_inicio, ho.dia_semana, ho.h_inicio
        """, (id_aula,))
        rows = cur.fetchall()
        return [
            {
                "id_hist_horario": r[0],
                "id_horario":      r[1],
                "fecha_inicio":    r[2].strftime("%Y-%m-%d") if r[2] else None,
                "fecha_fin":       r[3].strftime("%Y-%m-%d") if r[3] else None,
                "dia_semana":      r[4],
                "h_inicio":        r[5].strftime("%H:%M") if hasattr(r[5], "strftime") else str(r[5])[:5],
                "h_final":         r[6].strftime("%H:%M") if hasattr(r[6], "strftime") else str(r[6])[:5],
                "minutos_equiv":   r[7],
                "es_continuo":     r[8],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

# ============================
# ASIGNACIÓN TUTOR AULA
# ============================


def list_tutores_aula(id_aula: int):
    """
    Historial de tutores de un aula usando TUTOR_AULA + ASIGNACION_TUTOR.
    """
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
            FROM TUTOR_AULA ta
            JOIN ASIGNACION_TUTOR at ON ta.id_tutor_aula = at.id_tutor_aula
            JOIN PERSONA p          ON at.id_persona = p.id_persona
            WHERE ta.id_aula = :1
            ORDER BY at.fecha_inicio ASC, at.id_tutor_aula ASC
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

def aula_tiene_tutor_activo_en_fecha(id_aula: int, fecha: str) -> bool:
    """
    ¿Hay alguna asignación en ese aula vigente en la fecha dada (YYYY-MM-DD)?
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM TUTOR_AULA ta
            JOIN ASIGNACION_TUTOR at ON ta.id_tutor_aula = at.id_tutor_aula
            WHERE ta.id_aula = :id_aula
              AND at.fecha_inicio <= TO_DATE(:fecha, 'YYYY-MM-DD')
              AND (at.fecha_fin IS NULL OR at.fecha_fin >= TO_DATE(:fecha, 'YYYY-MM-DD'))
        """, {"id_aula": id_aula, "fecha": fecha[:10]})
        (count,) = cur.fetchone()
        return count > 0
    finally:
        cur.close()
        conn.close()

def aula_tiene_tutor_activo(id_aula: int) -> bool:
    """
    ¿Hay alguna asignación en ese aula con fecha_fin NULL?
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT COUNT(*)
            FROM TUTOR_AULA ta
            JOIN ASIGNACION_TUTOR at ON ta.id_tutor_aula = at.id_tutor_aula
            WHERE ta.id_aula = :1
              AND at.fecha_fin IS NULL
        """, (id_aula,))
        (count,) = cur.fetchone()
        return count > 0
    finally:
        cur.close()
        conn.close()

def obtener_horarios_aula_en_fecha(id_aula: int, fecha: str):
    """
    Devuelve una lista de tuplas (dia_semana, h_inicio, h_final) para el aula
    que estén vigentes en la fecha dada (YYYY-MM-DD).
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT h.dia_semana, h.h_inicio, h.h_final
            FROM HISTORICO_HORARIO_AULA hha
            JOIN HORARIO h ON h.id_horario = hha.id_horario
            WHERE hha.id_aula = :id_aula
              AND hha.fecha_inicio <= TO_DATE(:fecha, 'YYYY-MM-DD')
              AND (hha.fecha_fin IS NULL OR hha.fecha_fin >= TO_DATE(:fecha, 'YYYY-MM-DD'))
        """, {"id_aula": id_aula, "fecha": fecha[:10]})
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def obtener_aulas_activas_tutor(id_persona: int, fecha: str):
    """
    Devuelve los id_aula donde el tutor está activo en la fecha dada.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT ta.id_aula
            FROM ASIGNACION_TUTOR at
            JOIN TUTOR_AULA ta ON ta.id_tutor_aula = at.id_tutor_aula
            WHERE at.id_persona = :id_persona
              AND at.fecha_inicio <= TO_DATE(:fecha, 'YYYY-MM-DD')
              AND (at.fecha_fin IS NULL OR at.fecha_fin >= TO_DATE(:fecha, 'YYYY-MM-DD'))
        """, {"id_persona": id_persona, "fecha": fecha[:10]})
        return [r[0] for r in cur.fetchall()]
    finally:
        cur.close()
        conn.close()



def rangos_se_solapan(h1_ini: str, h1_fin: str, h2_ini: str, h2_fin: str) -> bool:
    """
    Determina si dos rangos horarios [h1_ini, h1_fin) y [h2_ini, h2_fin) se solapan.
    Formato de hora: 'HH24:MI' guardado como VARCHAR2(5).
    """
    return h1_ini < h2_fin and h1_fin > h2_ini


def hay_cruce_horario_tutor(id_persona: int, id_aula_nueva: int, fecha_inicio_nueva: str) -> bool:
    """
    True si el tutor ya tiene alguna otra aula activa en esa fecha
    cuyo horario se cruza con el horario del aula nueva.
    """
    fecha = fecha_inicio_nueva[:10]

    # Horarios de la nueva aula
    horarios_nueva = obtener_horarios_aula_en_fecha(id_aula_nueva, fecha)
    if not horarios_nueva:
        # Si el aula no tiene horarios definidos, no se puede validar cruce
        return False

    # Aulas donde el tutor ya está activo en esa fecha
    aulas_existentes = obtener_aulas_activas_tutor(id_persona, fecha)

    for id_aula_exist in aulas_existentes:
        if id_aula_exist == id_aula_nueva:
            continue  # misma aula, no cuenta como cruce

        horarios_exist = obtener_horarios_aula_en_fecha(id_aula_exist, fecha)
        for dia_n, hi_n, hf_n in horarios_nueva:
            for dia_e, hi_e, hf_e in horarios_exist:
                if dia_n == dia_e and rangos_se_solapan(hi_n, hf_n, hi_e, hf_e):
                    return True

    return False

def asignar_tutor_aula(data: dict):
    id_persona = int(data["id_persona"])
    id_aula = int(data["id_aula"])
    fecha_inicio = str(data["fecha_inicio"])[:10]
    fecha_fin = data.get("fecha_fin")  # puede ser None

    # 1) Validar que el aula no tenga tutor en esa fecha
    if aula_tiene_tutor_activo_en_fecha(id_aula, fecha_inicio):
        return {
            "error": "El aula ya tiene un tutor asignado en esa fecha. Ajuste el historial primero."
        }

    # 2) Validar cruce de horarios con otras aulas del tutor
    if hay_cruce_horario_tutor(id_persona, id_aula, fecha_inicio):
        return {
            "error": "El tutor ya tiene otra aula con horario que se cruza con esta a partir de esa fecha."
        }

    conn = get_conn()
    cur = conn.cursor()
    try:
        new_id = cur.var(oracledb.NUMBER)
        if fecha_fin:
            cur.execute("""
                INSERT INTO ASIGNACION_TUTOR (id_persona, fecha_inicio, fecha_fin, motivo_cambio)
                VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), TO_DATE(:3, 'YYYY-MM-DD'), NULL)
                RETURNING id_tutor_aula INTO :4
            """, (id_persona, fecha_inicio, fecha_fin[:10], new_id))
        else:
            cur.execute("""
                INSERT INTO ASIGNACION_TUTOR (id_persona, fecha_inicio, motivo_cambio)
                VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), NULL)
                RETURNING id_tutor_aula INTO :3
            """, (id_persona, fecha_inicio, new_id))

        id_tutor_aula = int(new_id.getvalue()[0])

        cur.execute("""
            INSERT INTO TUTOR_AULA (id_tutor_aula, id_aula)
            VALUES (:1, :2)
        """, (id_tutor_aula, id_aula))

        conn.commit()
        return {"msg": "Tutor asignado al aula.", "id_tutor_aula": id_tutor_aula}
    finally:
        cur.close()
        conn.close()

def cambiar_tutor_aula(data: dict):
    id_aula = int(data["id_aula"])
    id_persona_nuevo = int(data["id_persona"])
    fecha_inicio_nuevo = str(data["fecha_inicio"])[:10]
    motivo = data["motivo_cambio"]
    id_tutor_aula_actual = int(data["id_tutor_aula_actual"])
    fecha_fin_actual = data.get("fecha_fin_actual")

    # El aula no puede quedar con dos tutores en la misma fecha de inicio
    if aula_tiene_tutor_activo_en_fecha(id_aula, fecha_inicio_nuevo):
        return {
            "error": "El aula ya tiene un tutor asignado en esa fecha. Ajuste la fecha de fin del tutor actual."
        }

    # Validar cruce de horarios para el nuevo tutor
    if hay_cruce_horario_tutor(id_persona_nuevo, id_aula, fecha_inicio_nuevo):
        return {
            "error": "El nuevo tutor ya tiene otra aula con horario que se cruza con esta a partir de esa fecha."
        }

    conn = get_conn()
    cur = conn.cursor()
    try:
        # 1) cerrar asignación actual
        if fecha_fin_actual:
            cur.execute("""
                UPDATE ASIGNACION_TUTOR
                SET fecha_fin = TO_DATE(:1, 'YYYY-MM-DD'),
                    motivo_cambio = :2
                WHERE id_tutor_aula = :3
                  AND fecha_fin IS NULL
            """, (fecha_fin_actual, motivo, id_tutor_aula_actual))
        else:
            cur.execute("""
                UPDATE ASIGNACION_TUTOR
                SET fecha_fin = SYSDATE,
                    motivo_cambio = :1
                WHERE id_tutor_aula = :2
                  AND fecha_fin IS NULL
            """, (motivo, id_tutor_aula_actual))

        # 2) nueva asignación
        new_id = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO ASIGNACION_TUTOR (id_persona, fecha_inicio, motivo_cambio)
            VALUES (:1, TO_DATE(:2, 'YYYY-MM-DD'), NULL)
            RETURNING id_tutor_aula INTO :3
        """, (id_persona_nuevo, fecha_inicio_nuevo, new_id))
        id_tutor_aula_nuevo = int(new_id.getvalue()[0])

        cur.execute("""
            INSERT INTO TUTOR_AULA (id_tutor_aula, id_aula)
            VALUES (:1, :2)
        """, (id_tutor_aula_nuevo, id_aula))

        conn.commit()
        return {
            "msg": "Tutor cambiado correctamente.",
            "id_tutor_aula": id_tutor_aula_nuevo,
        }
    finally:
        cur.close()
        conn.close()

def finalizar_asignacion_tutor(
    id_tutor_aula: int,
    fecha_fin: Optional[str] = None,
    motivo: Optional[str] = None
):
    """
    Marca una asignación de tutor como finalizada (pone FECHA_FIN y opcionalmente motivo).
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        if fecha_fin:
            cur.execute("""
                UPDATE ASIGNACION_TUTOR
                SET fecha_fin = TO_DATE(:1, 'YYYY-MM-DD'),
                    motivo_cambio = COALESCE(:2, motivo_cambio)
                WHERE id_tutor_aula = :3
                  AND fecha_fin IS NULL
            """, (fecha_fin, motivo, id_tutor_aula))
        else:
            cur.execute("""
                UPDATE ASIGNACION_TUTOR
                SET fecha_fin = SYSDATE,
                    motivo_cambio = COALESCE(:1, motivo_cambio)
                WHERE id_tutor_aula = :2
                  AND fecha_fin IS NULL
            """, (motivo, id_tutor_aula))

        if cur.rowcount == 0:
            raise Exception("No se encontró una asignación activa con ese ID")

        conn.commit()
    finally:
        cur.close()
        conn.close()



# ============================
# HISTÓRICO AULA ESTUDIANTE
# ============================
def get_grado_aula(id_aula: int) -> int:
    """
    Devuelve el grado numérico del aula (asumiendo que AULA.grado almacena un número o un texto convertible a int).
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT grado FROM AULA WHERE id_aula = :1", (id_aula,))
        r = cur.fetchone()
        if not r or r[0] is None:
            raise Exception("No se encontró el aula especificada.")
        return int(r[0])
    finally:
        cur.close()
        conn.close()


def validar_cambio_grado(id_aula_origen: int, id_aula_destino: int) -> tuple[bool, str]:
    """
    Valida la regla:
      - Un estudiante solo se puede mover entre aulas 4º y/o 5º, o entre 9º y/o 10º.
      - No se puede mezclar primaria con secundaria u otros grados.
    """
    grado_origen = get_grado_aula(id_aula_origen)
    grado_destino = get_grado_aula(id_aula_destino)

    grupo_primaria = {4, 5}
    grupo_secundaria = {9, 10}

    if grado_origen in grupo_primaria and grado_destino in grupo_primaria:
        return True, ""
    if grado_origen in grupo_secundaria and grado_destino in grupo_secundaria:
        return True, ""

    return False, "El estudiante solo puede moverse entre aulas 4°-5° o entre 9°-10°. No se permiten cruces entre otros grados."

def existe_asignacion_en_rango(id_estudiante: int, id_aula: int, fecha_ini: str, fecha_fin: Optional[str]) -> bool:
    """
    True si ya existe en HISTORICO_AULA_ESTUDIANTE una fila para ese estudiante y aula
    cuyo rango [fecha_inicio, fecha_fin] se solape con [fecha_ini, fecha_fin_nueva].
    Si fecha_fin_nueva es None, se toma como 'abierta' hacia el futuro.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        if fecha_fin:
            cur.execute("""
                SELECT COUNT(*)
                FROM HISTORICO_AULA_ESTUDIANTE
                WHERE id_estudiante = :id_est
                  AND id_aula = :id_aula
                  AND (
                        (fecha_fin IS NULL AND fecha_inicio <= TO_DATE(:f_fin, 'YYYY-MM-DD'))
                        OR
                        (fecha_fin IS NOT NULL AND fecha_inicio <= TO_DATE(:f_fin, 'YYYY-MM-DD')
                         AND fecha_fin >= TO_DATE(:f_ini, 'YYYY-MM-DD'))
                      )
            """, {
                "id_est": id_estudiante,
                "id_aula": id_aula,
                "f_ini": fecha_ini[:10],
                "f_fin": fecha_fin[:10],
            })
        else:
            # nueva asignación abierta: solapa con cualquier rango que termine después de fecha_ini
            cur.execute("""
                SELECT COUNT(*)
                FROM HISTORICO_AULA_ESTUDIANTE
                WHERE id_estudiante = :id_est
                  AND id_aula = :id_aula
                  AND (
                        fecha_fin IS NULL
                        OR fecha_fin >= TO_DATE(:f_ini, 'YYYY-MM-DD')
                      )
                  AND fecha_inicio <= TO_DATE(:f_fin, 'YYYY-MM-DD')
            """, {
                "id_est": id_estudiante,
                "id_aula": id_aula,
                "f_ini": fecha_ini[:10],
                "f_fin": fecha_ini[:10],
            })
        (count,) = cur.fetchone()
        return count > 0
    finally:
        cur.close()
        conn.close()


def asignar_estudiante_aula(data):
    conn = get_conn()
    cur = conn.cursor()

    id_est = int(data["id_estudiante"])
    id_aula = int(data["id_aula"])
    fecha_ini = str(data.get("fecha_inicio") or date.today().isoformat())[:10]
    fecha_fin = data.get("fecha_fin")  # opcional

    # No puede tener otra asignación activa en CUALQUIER aula
    cur.execute("""
        SELECT COUNT(*)
        FROM HISTORICO_AULA_ESTUDIANTE
        WHERE id_estudiante = :1 AND fecha_fin IS NULL
    """, (id_est,))
    if cur.fetchone()[0] > 0:
        cur.close()
        conn.close()
        return {"error": "El estudiante ya pertenece a un aula activa."}

    # No puede estar ya asignado a ESTA aula en un rango que se solape
    if existe_asignacion_en_rango(id_est, id_aula, fecha_ini, fecha_fin):
        cur.close()
        conn.close()
        return {"error": "El estudiante ya tiene historial en esta aula que se cruza con el rango indicado."}

    # Insert con fecha_fin opcional
    if fecha_fin:
        cur.execute("""
            INSERT INTO HISTORICO_AULA_ESTUDIANTE (id_estudiante, id_aula, fecha_inicio, fecha_fin)
            VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), TO_DATE(:4, 'YYYY-MM-DD'))
        """, (id_est, id_aula, fecha_ini, fecha_fin[:10]))
    else:
        cur.execute("""
            INSERT INTO HISTORICO_AULA_ESTUDIANTE (id_estudiante, id_aula, fecha_inicio)
            VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
        """, (id_est, id_aula, fecha_ini))

    conn.commit()
    cur.close()
    conn.close()
    return {"msg": "Estudiante asignado correctamente"}


def cambiar_estudiante_aula(data: dict):
    """
    Cierra la asignación actual y crea una nueva en otra aula,
    validando reglas de grado y que no haya solape en el aula destino.
    """
    id_hist = int(data["id_hist_aula_est"])
    id_aula_origen = int(data["id_aula_origen"])
    id_aula_destino = int(data["id_aula_destino"])
    id_estudiante = int(data["id_estudiante"])
    fecha_fin_actual = data.get("fecha_fin_actual")
    fecha_inicio_nueva = data.get("fecha_inicio_nueva")
    fecha_fin_nueva = data.get("fecha_fin_nueva")  # opcional, nuevo campo

    if not fecha_inicio_nueva:
        return {"error": "Debe indicar la fecha de inicio en el aula de destino."}

    es_valido, msg = validar_cambio_grado(id_aula_origen, id_aula_destino)
    if not es_valido:
        return {"error": msg}

    # Validar que no haya solape en el aula destino
    if existe_asignacion_en_rango(id_estudiante, id_aula_destino, fecha_inicio_nueva, fecha_fin_nueva):
        return {"error": "El estudiante ya tiene un historial en el aula destino que se cruza con el rango indicado."}

    conn = get_conn()
    cur = conn.cursor()
    try:
        # cerrar asignación actual
        if fecha_fin_actual:
            cur.execute("""
                UPDATE HISTORICO_AULA_ESTUDIANTE
                SET fecha_fin = TO_DATE(:1, 'YYYY-MM-DD')
                WHERE id_hist_aula_est = :2
                  AND fecha_fin IS NULL
            """, (fecha_fin_actual, id_hist))
        else:
            cur.execute("""
                UPDATE HISTORICO_AULA_ESTUDIANTE
                SET fecha_fin = SYSDATE
                WHERE id_hist_aula_est = :1
                  AND fecha_fin IS NULL
            """, (id_hist,))

        if cur.rowcount == 0:
            raise Exception("No se encontró una asignación activa para ese estudiante en esa aula.")

        # insertar nueva asignación en aula destino
        if fecha_fin_nueva:
            cur.execute("""
                INSERT INTO HISTORICO_AULA_ESTUDIANTE (id_estudiante, id_aula, fecha_inicio, fecha_fin)
                VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'), TO_DATE(:4, 'YYYY-MM-DD'))
            """, (id_estudiante, id_aula_destino, fecha_inicio_nueva, fecha_fin_nueva[:10]))
        else:
            cur.execute("""
                INSERT INTO HISTORICO_AULA_ESTUDIANTE (id_estudiante, id_aula, fecha_inicio)
                VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
            """, (id_estudiante, id_aula_destino, fecha_inicio_nueva))

        conn.commit()
        return {"msg": "Estudiante movido de aula respetando el historial."}
    finally:
        cur.close()
        conn.close()

def listar_estudiantes_de_aula(id_aula: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                h.id_hist_aula_est,
                e.id_estudiante,
                e.nombres,
                e.apellidos,
                TO_CHAR(h.fecha_inicio, 'YYYY-MM-DD') AS fecha_inicio,
                TO_CHAR(h.fecha_fin,    'YYYY-MM-DD') AS fecha_fin
            FROM HISTORICO_AULA_ESTUDIANTE h
            JOIN ESTUDIANTE e ON h.id_estudiante = e.id_estudiante
            WHERE h.id_aula = :1
            ORDER BY e.nombres, e.apellidos
        """, (id_aula,))
        rows = cur.fetchall()
        return [
            dict(
                id_hist_aula_est=r[0],
                id_estudiante=r[1],
                nombres=r[2],
                apellidos=r[3],
                fecha_inicio=r[4],
                fecha_fin=r[5],
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()
        
def finalizar_asignacion_estudiante(id_hist_aula_est: int, fecha_fin: str | None = None):
    """
    Marca una fila de HISTORICO_AULA_ESTUDIANTE como finalizada (fecha_fin).
    Solo si fecha_fin está NULL.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        if fecha_fin:
            cur.execute("""
                UPDATE HISTORICO_AULA_ESTUDIANTE
                SET fecha_fin = TO_DATE(:1, 'YYYY-MM-DD')
                WHERE id_hist_aula_est = :2
                  AND fecha_fin IS NULL
            """, (fecha_fin, id_hist_aula_est))
        else:
            cur.execute("""
                UPDATE HISTORICO_AULA_ESTUDIANTE
                SET fecha_fin = SYSDATE
                WHERE id_hist_aula_est = :1
                  AND fecha_fin IS NULL
            """, (id_hist_aula_est,))

        if cur.rowcount == 0:
            raise Exception("No se encontró una asignación activa para ese estudiante en esa aula.")
        conn.commit()
    finally:
        cur.close()
        conn.close()



# ============================
# HORARIOS POR TUTOR
# ============================
def list_horario_tutor(id_persona: int):
    """
    Historial de horarios por tutor con el esquema:
    ASIGNACION_TUTOR, TUTOR_AULA, AULA, HISTORICO_HORARIO_AULA, HORARIO.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                at.id_tutor_aula,
                a.id_aula,
                a.grado,
                h.dia_semana,
                h.h_inicio,
                h.h_final,
                h.minutos_equiv,
                h.es_continuo,
                at.fecha_inicio    AS fecha_ini_tutor,
                at.fecha_fin       AS fecha_fin_tutor,
                hha.fecha_inicio   AS fecha_ini_horario,
                hha.fecha_fin      AS fecha_fin_horario
            FROM ASIGNACION_TUTOR at
            JOIN TUTOR_AULA ta
                  ON ta.id_tutor_aula = at.id_tutor_aula
            JOIN AULA a
                  ON a.id_aula = ta.id_aula
            JOIN HISTORICO_HORARIO_AULA hha
                  ON hha.id_aula = a.id_aula
            JOIN HORARIO h
                  ON hha.id_horario = h.id_horario
            WHERE at.id_persona = :idp
            ORDER BY a.id_aula, h.dia_semana, h.h_inicio, at.fecha_inicio
        """, {"idp": id_persona})
        rows = cur.fetchall()

        def fmt(d):
            return d.strftime("%Y-%m-%d") if d else None

        result = []
        for r in rows:
            id_tutor_aula, id_aula, grado, dia_sem, h_ini, h_fin, min_equiv, es_cont, \
            f_ini_tutor, f_fin_tutor, f_ini_hor, f_fin_hor = r

            h_ini_str = h_ini if isinstance(h_ini, str) else h_ini.strftime("%H:%M")
            h_fin_str = h_fin if isinstance(h_fin, str) else h_fin.strftime("%H:%M")

            result.append({
                "id_tutor_aula": id_tutor_aula,
                "id_aula": id_aula,
                "grado": grado,
                "dia_semana": dia_sem,
                "h_inicio": h_ini_str,
                "h_final": h_fin_str,
                "minutos_equiv": min_equiv,
                "es_continuo": es_cont,
                "fecha_ini_tutor": fmt(f_ini_tutor),
                "fecha_fin_tutor": fmt(f_fin_tutor),
                "fecha_ini_horario": fmt(f_ini_hor),
                "fecha_fin_horario": fmt(f_fin_hor),
            })
        return result
    finally:
        cur.close()
        conn.close()

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

def get_id_tutor_aula(id_tutor, id_aula):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT at.id_tutor_aula
            FROM ASIGNACION_TUTOR at
            JOIN TUTOR_AULA ta ON ta.id_tutor_aula = at.id_tutor_aula
            WHERE at.id_persona = :1
              AND ta.id_aula   = :2
              AND (at.fecha_fin IS NULL OR at.fecha_fin > SYSDATE)
            ORDER BY at.fecha_inicio DESC
            FETCH FIRST 1 ROWS ONLY
        """, [id_tutor, id_aula])
        r = cur.fetchone()
        return {"id_tutor_aula": r[0] if r else None}
    finally:
        cur.close()
        conn.close()

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

# ============================
# ESTUDIANTES
# ============================

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

# ============================
# PERIODOS
# ============================

def create_periodo(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        fecha_inicio = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date() if data["fecha_inicio"] else date.today()
        fecha_fin    = datetime.strptime(data["fecha_fin"], "%Y-%m-%d").date() if data["fecha_fin"] else date.today()

        cur.execute("""
            INSERT INTO PERIODO (nombre, fecha_inicio, fecha_fin)
            VALUES (:1, :2, :3)
        """, (data["nombre"], fecha_inicio, fecha_fin))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def list_periodos():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_periodo, nombre, fecha_inicio, fecha_fin
            FROM PERIODO
            ORDER BY id_periodo DESC
        """)
        rows = cur.fetchall()
        return [
            dict(
                id_periodo=r[0],
                nombre=r[1],
                fecha_inicio=r[2].strftime("%Y-%m-%d") if r[2] else None,
                fecha_fin=r[3].strftime("%Y-%m-%d") if r[3] else None,
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def update_periodo(id_periodo: int, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        fecha_inicio = datetime.strptime(data["fecha_inicio"], "%Y-%m-%d").date()
        fecha_fin    = datetime.strptime(data["fecha_fin"], "%Y-%m-%d").date()

        cur.execute("""
            UPDATE PERIODO
            SET nombre = :1,
                fecha_inicio = :2,
                fecha_fin = :3
            WHERE id_periodo = :4
        """, (data["nombre"], fecha_inicio, fecha_fin, id_periodo))
        conn.commit()
    finally:
        cur.close()
        conn.close()


def delete_periodo(id_periodo: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # ¿tiene componentes asociados?
        cur.execute("""
            SELECT COUNT(*)
            FROM COMPONENTE
            WHERE id_periodo = :1
        """, (id_periodo,))
        (count,) = cur.fetchone()
        if count > 0:
            raise Exception("No se puede eliminar el período porque tiene componentes asignados.")

        cur.execute("DELETE FROM PERIODO WHERE id_periodo = :1", (id_periodo,))
        if cur.rowcount == 0:
            raise Exception("Periodo no encontrado")
        conn.commit()
    finally:
        cur.close()
        conn.close()

def get_suma_porcentajes_periodo_tipo(id_periodo: int, tipo_programa: str) -> float:
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT NVL(SUM(porcentaje), 0)
            FROM COMPONENTE
            WHERE id_periodo = :1
              AND tipo_programa = :2
        """, (id_periodo, tipo_programa))
        (total,) = cur.fetchone()
        return float(total)
    finally:
        cur.close()
        conn.close()

# ============================
# COMPONENTES
# ============================

def crear_componente(nombre: str,
                     porcentaje: float,
                     tipo_programa: str,
                     id_periodo: int):
    if not tipo_programa:
        return {"ok": False, "msg": "El tipo de programa es obligatorio."}

    tipo_programa = tipo_programa.upper()
    if tipo_programa not in ("INSIDECLASSROOM", "OUTSIDECLASSROOM"):
        return {"ok": False, "msg": "Tipo de programa inválido."}

    total_actual = get_suma_porcentajes_periodo_tipo(id_periodo, tipo_programa)
    if total_actual + porcentaje > 100:
        return {
            "ok": False,
            "msg": f"La suma de porcentajes para el período y tipo '{tipo_programa}' excede 100 (actual: {total_actual}%)."
        }

    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO COMPONENTE (nombre, porcentaje, tipo_programa, id_periodo)
            VALUES (:1, :2, :3, :4)
        """, (nombre, porcentaje, tipo_programa, id_periodo))
        conn.commit()
        return {"ok": True, "msg": "Componente registrado exitosamente"}
    finally:
        cur.close()
        conn.close()

def list_componentes():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT 
                c.id_componente,
                c.nombre,
                c.porcentaje,
                c.tipo_programa,
                p.nombre AS periodo_nombre,
                c.id_periodo
            FROM COMPONENTE c
            LEFT JOIN PERIODO p ON c.id_periodo = p.id_periodo
            ORDER BY c.id_componente DESC
        """)
        rows = cur.fetchall()
        return [
            dict(
                id_componente=r[0],
                nombre=r[1],
                porcentaje=r[2],
                tipo_programa=r[3],
                periodo_nombre=r[4],
                id_periodo=r[5],
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def actualizar_componente(id_componente: int,
                          nombre: str,
                          porcentaje: float,
                          tipo_programa: str,
                          id_periodo: int):
    if not tipo_programa:
        return {"ok": False, "msg": "El tipo de programa es obligatorio."}

    tipo_programa = tipo_programa.upper()
    if tipo_programa not in ("INSIDECLASSROOM", "OUTSIDECLASSROOM"):
        return {"ok": False, "msg": "Tipo de programa inválido."}

    conn = get_conn()
    cur = conn.cursor()
    try:
        # Obtener porcentaje actual del componente (para ese id)
        cur.execute("""
            SELECT porcentaje
            FROM COMPONENTE
            WHERE id_componente = :1
        """, (id_componente,))
        r = cur.fetchone()
        if not r:
            return {"ok": False, "msg": "Componente no encontrado."}
        porcentaje_actual = float(r[0])

        # Suma actual de ese periodo+tipo (incluyendo este componente)
        total_actual = get_suma_porcentajes_periodo_tipo(id_periodo, tipo_programa)

        # Suma sin este componente
        total_sin_actual = total_actual - porcentaje_actual

        # Validar nuevo total
        if total_sin_actual + porcentaje > 100:
            return {
                "ok": False,
                "msg": (
                    f"La suma de porcentajes para el período y tipo '{tipo_programa}' "
                    f"excede 100 (actual sin este componente: {total_sin_actual}%)."
                )
            }

        # Actualizar
        cur.execute("""
            UPDATE COMPONENTE
            SET nombre        = :1,
                porcentaje    = :2,
                tipo_programa = :3,
                id_periodo    = :4
            WHERE id_componente = :5
        """, (nombre, porcentaje, tipo_programa, id_periodo, id_componente))
        conn.commit()
        return {"ok": True, "msg": "Componente actualizado correctamente"}
    finally:
        cur.close()
        conn.close()

def eliminar_componente(id_componente: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM COMPONENTE WHERE id_componente = :1", (id_componente,))
        if cur.rowcount == 0:
            return {"ok": False, "msg": "Componente no encontrado"}
        conn.commit()
        return {"ok": True, "msg": "Componente eliminado correctamente"}
    finally:
        cur.close()
        conn.close()

def get_componente(id_componente: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_componente, nombre, porcentaje, tipo_programa, id_periodo
            FROM COMPONENTE
            WHERE id_componente = :1
        """, (id_componente,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(
            id_componente=r[0],
            nombre=r[1],
            porcentaje=r[2],
            tipo_programa=r[3],
            id_periodo=r[4],
        )
    finally:
        cur.close()
        conn.close()

# ============================
# ASISTENCIA AULA
# ============================
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

def list_horarios_aula_activos(id_aula: int):
    """
    Solo los horarios activos (HISTORICO_HORARIO_AULA.fecha_fin IS NULL)
    para generar las fechas posibles de asistencia.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
              ho.dia_semana,
              ho.h_inicio,
              ho.h_final,
              hha.fecha_inicio
            FROM HISTORICO_HORARIO_AULA hha
            JOIN HORARIO ho ON hha.id_horario = ho.id_horario
            WHERE hha.id_aula = :1
              AND hha.fecha_fin IS NULL
        """, (id_aula,))
        rows = cur.fetchall()
        return [
            {
                "dia_semana":  r[0],
                "h_inicio":    r[1].strftime("%H:%M") if hasattr(r[1], "strftime") else str(r[1])[:5],
                "h_final":     r[2].strftime("%H:%M") if hasattr(r[2], "strftime") else str(r[2])[:5],
                "fechainicio": r[3].strftime("%Y-%m-%d") if r[3] else None,
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

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

# ============================
# ASISTENCIA ESTUDIANTE
# ============================
def listar_clases_tutor(id_persona: int):
    """
    Usa ASISTENCIA_AULA + ASIGNACION_TUTOR para obtener las clases donde ese tutor pasó asistencia.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT aa.id_asist,
                   aa.fecha_clase,
                   aa.id_aula
            FROM ASISTENCIA_AULA aa
            JOIN ASIGNACION_TUTOR at
              ON aa.id_tutor_aula = at.id_tutor_aula
            WHERE at.id_persona = :1
            ORDER BY aa.fecha_clase DESC, aa.id_asist DESC
        """, [id_persona])
        rows = cur.fetchall()
        return [
            {
                "id_asist": r[0],
                "fecha_clase": r[1].strftime("%Y-%m-%d") if r[1] else None,
                "id_aula": r[2],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def registrar_asistencia_estudiante(data: dict):
    """
    Inserta o actualiza ASISTENCIA_ESTUDIANTE (id_asist, id_estudiante).
    Si ya existe el registro, hace UPDATE; si no, INSERT sin usar secuencia.
    """
    id_asist = data["id_asist"]
    id_estudiante = data["id_estudiante"]
    asistio = (data.get("asistio") or "N").upper()
    observacion = data.get("observacion")

    if asistio not in ("S", "N"):
        return {"error": "Valor de 'asistio' inválido. Debe ser 'S' o 'N'."}

    conn = get_conn()
    cur = conn.cursor()
    try:
        # ¿ya existe esa fila?
        cur.execute("""
            SELECT id_asist_est
            FROM ASISTENCIA_ESTUDIANTE
            WHERE id_asist = :1 AND id_estudiante = :2
        """, [id_asist, id_estudiante])
        r = cur.fetchone()

        if r:
            # UPDATE
            cur.execute("""
                UPDATE ASISTENCIA_ESTUDIANTE
                SET asistio = :1,
                    observacion = :2
                WHERE id_asist_est = :3
            """, [asistio, observacion, r[0]])
        else:
            # INSERT sin secuencia explícita (usa IDENTITY de la tabla)
            cur.execute("""
                INSERT INTO ASISTENCIA_ESTUDIANTE
                    (id_asist, id_estudiante, asistio, observacion)
                VALUES (:1, :2, :3, :4)
            """, [id_asist, id_estudiante, asistio, observacion])

        conn.commit()
        return {"ok": True, "msg": "Asistencia de estudiante registrada."}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def listar_asistencia_estudiantes(id_asist: int):
    """
    Lista estudiantes del aula correspondiente a la asistencia,
    junto con su asistencia de ese día (ASISTENCIA_ESTUDIANTE).
    NO falla si la tabla de histórico no existe o no hay registros.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # 1) Obtener aula de la asistencia
        cur.execute("""
            SELECT id_aula
            FROM ASISTENCIA_AULA
            WHERE id_asist = :1
        """, [id_asist])
        r = cur.fetchone()
        if not r:
            return []
        id_aula = r[0]

        estudiantes = {}

        # 2) Intentar leer estudiantes desde el histórico de aula-estudiante
        try:
            cur.execute("""
                SELECT e.id_estudiante,
                       e.nombres,
                       e.apellidos
                FROM ESTUDIANTE e
                JOIN HISTORICO_AULA_ESTUDIANTE hae
                  ON hae.id_estudiante = e.id_estudiante
                WHERE hae.id_aula = :1
                  AND (hae.fecha_fin IS NULL OR hae.fecha_fin >= TRUNC(SYSDATE))
            """, [id_aula])
            rows = cur.fetchall()
        except oracledb.DatabaseError as ex:  # si la tabla no existe o nombre distinto
            # como respaldo: todos los estudiantes actuales del aula
            cur.execute("""
                SELECT e.id_estudiante,
                       e.nombres,
                       e.apellidos
                FROM ESTUDIANTE e
                JOIN AULA_ESTUDIANTE ae
                  ON ae.id_estudiante = e.id_estudiante
                WHERE ae.id_aula = :1
            """, [id_aula])
            rows = cur.fetchall()

        for r in rows:
            estudiantes[r[0]] = {
                "id_estudiante": r[0],
                "nombres": r[1],
                "apellidos": r[2],
                "asistio": "N",
                "observacion": "",
            }

        if not estudiantes:
            return []

        # 3) Cargar marcas de asistencia de ASISTENCIA_ESTUDIANTE
        cur.execute("""
            SELECT id_estudiante, asistio, observacion
            FROM ASISTENCIA_ESTUDIANTE
            WHERE id_asist = :1
        """, [id_asist])
        for est_id, asistio, obs in cur.fetchall():
            if est_id in estudiantes:
                estudiantes[est_id]["asistio"] = asistio or "N"
                estudiantes[est_id]["observacion"] = obs or ""

        return list(estudiantes.values())
    finally:
        cur.close()
        conn.close()

def listar_asistencia_estudiantes_todas(id_persona: int):
    """
    Devuelve todas las asistencias de un tutor, por estudiante y clase:
    columnas: fecha_clase, id_aula, id_asist, id_estudiante, nombres, apellidos, asistio.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                aa.fecha_clase,
                aa.id_aula,
                aa.id_asist,
                e.id_estudiante,
                e.nombres,
                e.apellidos,
                NVL(ae.asistio, 'N') AS asistio
            FROM ASISTENCIA_AULA aa
            JOIN ASIGNACION_TUTOR at
              ON aa.id_tutor_aula = at.id_tutor_aula
            JOIN HISTORICO_AULA_ESTUDIANTE hae
              ON hae.id_aula = aa.id_aula
             AND (hae.fecha_fin IS NULL OR hae.fecha_fin >= aa.fecha_clase)
            JOIN ESTUDIANTE e
              ON e.id_estudiante = hae.id_estudiante
            LEFT JOIN ASISTENCIA_ESTUDIANTE ae
              ON ae.id_asist = aa.id_asist
             AND ae.id_estudiante = e.id_estudiante
            WHERE at.id_persona = :1
            ORDER BY aa.fecha_clase DESC, aa.id_aula, e.apellidos, e.nombres
        """, [id_persona])
        rows = cur.fetchall()
        return [
            {
                "fecha_clase": r[0].strftime("%Y-%m-%d") if r[0] else None,
                "id_aula": r[1],
                "id_asist": r[2],
                "id_estudiante": r[3],
                "nombres": r[4],
                "apellidos": r[5],
                "asistio": r[6],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()
        
# ============================
# NOTA ESTUDIANTE
# ============================

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

def registrar_o_actualizar_nota(id_estudiante: int, id_componente: int, nota: float):
    """
    Inserta o actualiza la nota de un estudiante para un componente.
    La tabla NOTA_ESTUDIANTE tiene: id_nota, id_estudiante, id_componente, nota.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # ¿ya existe?
        cur.execute("""
            SELECT id_nota
            FROM NOTA_ESTUDIANTE
            WHERE id_estudiante = :1
              AND id_componente = :2
        """, (id_estudiante, id_componente))
        fila = cur.fetchone()

        if fila:
            cur.execute("""
                UPDATE NOTA_ESTUDIANTE
                SET nota = :1
                WHERE id_nota = :2
            """, (nota, fila[0]))
            msg = "Nota actualizada correctamente."
        else:
            cur.execute("""
                INSERT INTO NOTA_ESTUDIANTE (id_estudiante, id_componente, nota)
                VALUES (:1, :2, :3)
            """, (id_estudiante, id_componente, nota))
            msg = "Nota registrada correctamente."

        conn.commit()
        return {"ok": True, "msg": msg}
    finally:
        cur.close()
        conn.close()

def obtener_nota_estudiante(id_estudiante: int, id_componente: int):
    """
    Obtiene la nota (o None) de un estudiante para un componente.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT nota
            FROM NOTA_ESTUDIANTE
            WHERE id_estudiante = :1
              AND id_componente = :2
        """, (id_estudiante, id_componente))
        r = cur.fetchone()
        return {"nota": float(r[0]) if r and r[0] is not None else None}
    finally:
        cur.close()
        conn.close()

def listar_componentes_periodo_tipo(id_periodo: int, tipo_programa: str):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_componente, nombre, porcentaje, tipo_programa
            FROM COMPONENTE
            WHERE id_periodo = :1
              AND tipo_programa = :2
            ORDER BY id_componente
        """, (id_periodo, tipo_programa))
        rows = cur.fetchall()
        return [
            dict(
                id_componente=r[0],
                nombre=r[1],
                porcentaje=r[2],
                tipo_programa=r[3]
            )
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def listar_aulas_tutor(id_persona: int):
    """
    Lista las aulas donde el tutor tiene asignación activa.
    Usa la tabla intermedia TUTOR_AULA.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT DISTINCT a.id_aula, a.grado
            FROM ASIGNACION_TUTOR at
            JOIN TUTOR_AULA ta ON ta.id_tutor_aula = at.id_tutor_aula
            JOIN AULA a        ON a.id_aula        = ta.id_aula
            WHERE at.id_persona = :1
              AND at.fecha_fin IS NULL
            ORDER BY a.grado
        """, (id_persona,))
        rows = cur.fetchall()
        return [
            {
                "id_aula": r[0],
                "grado":   r[1],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

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

# ============================
# CALENDARIO SEMANAS
# ============================
def generar_calendario_semanas(anio: int):
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()

    # Valida duplicidad por año en cualquier parte del rango
    cur.execute(
        "SELECT COUNT(*) FROM SEMANA WHERE EXTRACT(YEAR FROM fecha_inicio) = :1",
        [anio]
    )
    si_existe = cur.fetchone()[0]
    if si_existe > 0:
        cur.close()
        conn.close()
        return {
            "ok": False,
            "msg": f"El calendario del año {anio} ya existe. No se puede volver a crear."
        }

    fecha_ini_anio = date(anio, 1, 1)
    fecha_fin_anio = date(anio, 12, 31)

    numero_semana = 1

    # -------- Semana 1: desde el 1 de enero hasta el domingo siguiente --------
    # weekday(): 0 = lunes, 6 = domingo
    # buscamos el próximo domingo (día 6) incluyendo el propio día si ya es domingo
    dias_hasta_domingo = (6 - fecha_ini_anio.weekday()) % 7
    fecha_fin_sem1 = fecha_ini_anio + timedelta(days=dias_hasta_domingo)

    cur.execute("""
        INSERT INTO SEMANA (NUMERO_SEMANA, FECHA_INICIO, FECHA_FIN)
        VALUES (:1, TO_DATE(:2,'YYYY-MM-DD'), TO_DATE(:3,'YYYY-MM-DD'))
    """, [
        numero_semana,
        fecha_ini_anio.strftime('%Y-%m-%d'),
        fecha_fin_sem1.strftime('%Y-%m-%d')
    ])

    numero_semana += 1

    # Siguiente semana empieza el lunes inmediatamente después de ese domingo
    semana_ini = fecha_fin_sem1 + timedelta(days=1)

    # -------- Resto de semanas: siempre lunes–domingo --------
    while semana_ini <= fecha_fin_anio:
        semana_fin = semana_ini + timedelta(days=6)
        if semana_fin > fecha_fin_anio:
            semana_fin = fecha_fin_anio

        cur.execute("""
            INSERT INTO SEMANA (NUMERO_SEMANA, FECHA_INICIO, FECHA_FIN)
            VALUES (:1, TO_DATE(:2,'YYYY-MM-DD'), TO_DATE(:3,'YYYY-MM-DD'))
        """, [
            numero_semana,
            semana_ini.strftime('%Y-%m-%d'),
            semana_fin.strftime('%Y-%m-%d')
        ])

        numero_semana += 1
        semana_ini = semana_fin + timedelta(days=1)

    conn.commit()
    cur.close()
    conn.close()
    return {
        "ok": True,
        "msg": f"Semanas para el año {anio} generadas exitosamente."
    }


def listar_semanas():
    from .db import get_conn
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT numero_semana, fecha_inicio, fecha_fin
        FROM SEMANA
        ORDER BY fecha_inicio
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "numero_semana": r[0],
            "fecha_inicio": r[1].strftime('%Y-%m-%d'),
            "fecha_fin": r[2].strftime('%Y-%m-%d')
        }
        for r in rows
    ]

# ============================
# FESTIVOS
# ============================

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

# ============================
# MOTIVOS DE INASISTENCIA
# ============================

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

def get_motivos_inasistencia():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id_motivo, descripcion FROM motivo_inasistencia")
    datos = [dict(id_motivo=r[0], descripcion=r[1]) for r in cur]
    cur.close()
    conn.close()
    return datos

# ============================
# REPORTES
# ============================

def reporte_asistencia_tutor(id_persona: int, fecha_inicio: str, fecha_fin: str):
    """
    Reporte de asistencia de un tutor entre dos fechas.
    Usa ASISTENCIA_AULA + ASIGNACION_TUTOR + AULA + HORARIO.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                aa.fecha_clase,
                a.id_aula,
                a.grado,
                h.dia_semana,
                aa.hora_inicio,
                aa.hora_fin,
                aa.dictada,
                aa.horas_dictadas,
                aa.reposicion,
                aa.fecha_reposicion
            FROM ASISTENCIA_AULA aa
            JOIN ASIGNACION_TUTOR at
              ON aa.id_tutor_aula = at.id_tutor_aula
            JOIN AULA a
              ON aa.id_aula = a.id_aula
            JOIN HORARIO h
              ON aa.id_horario = h.id_horario
            WHERE at.id_persona = :1
              AND aa.fecha_clase BETWEEN TO_DATE(:2, 'YYYY-MM-DD')
                                      AND TO_DATE(:3, 'YYYY-MM-DD')
            ORDER BY aa.fecha_clase, aa.hora_inicio
        """, [id_persona, fecha_inicio, fecha_fin])

        rows = cur.fetchall()
        return [
            {
                "fecha_clase": r[0].strftime("%Y-%m-%d") if r[0] else None,
                "id_aula": r[1],
                "grado": r[2],
                "dia_semana": r[3],
                "hora_inicio": str(r[4]) if r[4] else None,
                "hora_fin": str(r[5]) if r[5] else None,
                "dictada": r[6],
                "horas_dictadas": r[7],
                "reposicion": r[8],
                "fecha_reposicion": r[9].strftime("%Y-%m-%d") if r[9] else None,
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def actualizar_score_estudiante(id_estudiante: int,
                                score_entrada: float | None,
                                score_salida: float | None):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE ESTUDIANTE
               SET score_entrada = :1,
                   score_salida  = :2
             WHERE id_estudiante = :3
        """, [score_entrada, score_salida, id_estudiante])
        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def obtener_score_estudiante(id_estudiante: int):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT score_entrada, score_salida
              FROM ESTUDIANTE
             WHERE id_estudiante = :1
        """, [id_estudiante])
        r = cur.fetchone()
        if not r:
            return {}
        return {
            "score_entrada": r[0],
            "score_salida": r[1],
        }
    finally:
        cur.close()
        conn.close()

def listar_estudiantes_admin():
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT
                id_estudiante,
                nombres,
                apellidos,
                score_entrada,
                score_salida
            FROM ESTUDIANTE
            ORDER BY apellidos, nombres
        """)
        rows = cur.fetchall()
        return [
            {
                "id_estudiante": r[0],
                "nombres": r[1],
                "apellidos": r[2],
                "score_entrada": r[3],
                "score_salida": r[4],
            }
            for r in rows
        ]
    finally:
        cur.close()
        conn.close()

def reporte_autogestion_tutor(id_persona: int, fecha_inicio: str, fecha_fin: str):
    """
    Reporte de autogestión del tutor: asistencia por clase en un rango de fechas.
    La parte de notas se maneja en otra pestaña.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # 1) Resumen de asistencia por día/clase
        cur.execute("""
            SELECT
                aa.fecha_clase,
                a.id_aula,
                a.grado,
                aa.hora_inicio,
                aa.hora_fin,
                aa.dictada,
                aa.horas_dictadas,
                NVL(ROUND(
                    (SELECT COUNT(*)
                       FROM ASISTENCIA_ESTUDIANTE ae
                      WHERE ae.id_asist = aa.id_asist
                        AND ae.asistio = 'S')
                    /
                    NULLIF( (SELECT COUNT(*)
                               FROM ASISTENCIA_ESTUDIANTE ae2
                              WHERE ae2.id_asist = aa.id_asist), 0)
                    * 100, 1
                ), 0) AS pct_asistencia
            FROM ASISTENCIA_AULA aa
            JOIN ASIGNACION_TUTOR at
              ON aa.id_tutor_aula = at.id_tutor_aula
            JOIN AULA a
              ON aa.id_aula = a.id_aula
            WHERE at.id_persona = :1
              AND aa.fecha_clase BETWEEN TO_DATE(:2,'YYYY-MM-DD')
                                      AND TO_DATE(:3,'YYYY-MM-DD')
            ORDER BY aa.fecha_clase, aa.hora_inicio
        """, [id_persona, fecha_inicio, fecha_fin])

        asis_rows = cur.fetchall()
        asistencia = [
            {
                "fecha_clase": r[0].strftime("%Y-%m-%d") if r[0] else None,
                "id_aula": r[1],
                "grado": r[2],
                "hora_inicio": str(r[3]) if r[3] else None,
                "hora_fin": str(r[4]) if r[4] else None,
                "dictada": r[5],
                "horas_dictadas": r[6],
                "pct_asistencia": float(r[7]) if r[7] is not None else 0.0,
            }
            for r in asis_rows
        ]

        # Notas no se devuelven aquí (se manejan en otra pestaña)
        return {"asistencia": asistencia, "notas": []}
    finally:
        cur.close()
        conn.close()

def resolver_tipo_programa_por_grado(grado: str) -> str:
    """
    Dado el grado del aula, devuelve INSIDECLASSROOM u OUTSIDECLASSROOM.
    AJUSTA LOS CONDICIONALES A CÓMO NOMBRAS TUS GRADOS.
    """
    if not grado:
        return ""

    g = grado.upper()

    # Ejemplos: si el texto del grado contiene estas palabras
    if "OUTSIDE" in g:
        return "OUTSIDECLASSROOM"
    # Por defecto, considerar que es INSIDECLASSROOM
    return "INSIDECLASSROOM"


def reporte_notas_tutor_periodo(id_persona: int, id_periodo: int, id_aula: int):
    """
    Reporte de notas por periodo para un tutor, un aula y un periodo específicos.

    - Solo lectura.
    - Determina tipo_programa (INSIDECLASSROOM/OUTSIDECLASSROOM) a partir del grado del aula.
    - Solo incluye componentes del periodo cuyo tipo_programa coincide con el del aula.
    - Calcula la definitiva por estudiante como sumatoria de (nota * porcentaje/100).
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # 0) Obtener grado del aula y tipo_programa asociado
        cur.execute("""
            SELECT grado
            FROM AULA
            WHERE id_aula = :1
        """, [id_aula])
        r_aula = cur.fetchone()
        if not r_aula:
            return []

        grado_aula = r_aula[0]
        tipo_prog_aula = resolver_tipo_programa_por_grado(grado_aula)

        # 1) Componentes del periodo que aplican al tipo de programa del aula
        cur.execute("""
            SELECT id_componente, nombre, porcentaje
            FROM COMPONENTE
            WHERE id_periodo = :1
              AND tipo_programa = :2
            ORDER BY id_componente
        """, [id_periodo, tipo_prog_aula])
        comp_rows = cur.fetchall()
        if not comp_rows:
            return []

        componentes = [
            {
                "id_componente": r[0],
                "nombre": r[1],
                "porcentaje": float(r[2]) if r[2] is not None else 0.0,
            }
            for r in comp_rows
        ]

        # 2) Estudiantes del aula (histórico vigente)
        cur.execute("""
            SELECT DISTINCT
                   e.id_estudiante,
                   e.nombres,
                   e.apellidos
            FROM HISTORICO_AULA_ESTUDIANTE hae
            JOIN ESTUDIANTE e
              ON hae.id_estudiante = e.id_estudiante
            WHERE hae.id_aula = :1
              AND (hae.fecha_fin IS NULL OR hae.fecha_fin >= SYSDATE)
        """, [id_aula])
        est_rows = cur.fetchall()
        if not est_rows:
            return []

        estudiantes = {}
        for r in est_rows:
            id_est = r[0]
            estudiantes[id_est] = {
                "id_estudiante": id_est,
                "nombres": r[1],
                "apellidos": r[2],
                "componentes": [
                    {
                        "id_componente": c["id_componente"],
                        "nombre_componente": c["nombre"],
                        "porcentaje": c["porcentaje"],
                        "nota": None,
                    }
                    for c in componentes
                ],
                "definitiva": None,
            }

        # 3) Notas existentes para esos estudiantes y estos componentes
        cur.execute("""
            SELECT
                n.id_estudiante,
                n.id_componente,
                n.nota
            FROM NOTA_ESTUDIANTE n
            JOIN COMPONENTE c
              ON n.id_componente = c.id_componente
            WHERE c.id_periodo = :1
              AND c.tipo_programa = :2
              AND n.id_estudiante IN (
                    SELECT DISTINCT e2.id_estudiante
                    FROM HISTORICO_AULA_ESTUDIANTE hae2
                    JOIN ESTUDIANTE e2
                      ON hae2.id_estudiante = e2.id_estudiante
                    WHERE hae2.id_aula = :3
                      AND (hae2.fecha_fin IS NULL OR hae2.fecha_fin >= SYSDATE)
              )
        """, [id_periodo, tipo_prog_aula, id_aula])
        nota_rows = cur.fetchall()

        for est_id, id_comp, nota in nota_rows:
            est = estudiantes.get(est_id)
            if not est:
                continue
            for comp in est["componentes"]:
                if comp["id_componente"] == id_comp:
                    comp["nota"] = float(nota) if nota is not None else None
                    break

        # 4) Calcular definitiva por estudiante: sum(nota * porcentaje/100)
        for est in estudiantes.values():
            suma = 0.0
            for comp in est["componentes"]:
                if comp["nota"] is not None:
                    suma += comp["nota"] * (comp["porcentaje"] / 100.0)
            est["definitiva"] = round(suma, 2) if suma > 0 else None

        return list(estudiantes.values())
    finally:
        cur.close()
        conn.close()



def guardar_notas_tutor_periodo(id_persona: int, id_periodo: int, notas: list[dict]):
    """
    Guarda notas recibidas desde el front.
    notas: [{id_estudiante, id_componente, nota}]
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        for item in notas:
            id_est = item["id_estudiante"]
            id_comp = item["id_componente"]
            nota = item["nota"]

            cur.execute("""
                SELECT id_nota
                  FROM NOTA_ESTUDIANTE
                 WHERE id_estudiante = :1
                   AND id_componente = :2
            """, [id_est, id_comp])
            r = cur.fetchone()

            if r:
                cur.execute("""
                    UPDATE NOTA_ESTUDIANTE
                       SET nota = :1
                     WHERE id_nota = :2
                """, [nota, r[0]])
            else:
                cur.execute("""
                    INSERT INTO NOTA_ESTUDIANTE (id_estudiante, id_componente, nota)
                    VALUES (:1, :2, :3)
                """, [id_est, id_comp, nota])

        conn.commit()
        return {"ok": True}
    except Exception as e:
        conn.rollback()
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def reporte_asistencia_aula(id_aula: int,
                            fecha_inicio: str | None = None,
                            fecha_fin: str | None = None):
    """
    Reporte de asistencia general del aula, opcionalmente filtrado por rango de fechas.
    """

    conn = get_conn()
    cur = conn.cursor()
    try:
        sql = """
        SELECT 
          inst.nombre_inst, 
          au.id_aula,
          au.grado,
          aa.id_asist, 
          aa.fecha_clase,
          aa.hora_inicio,
          CASE WHEN f.id_festivo IS NOT NULL THEN 'S' ELSE 'N' END as es_festivo,
          h.dia_semana,
          h.h_inicio,
          h.h_final,
          aa.dictada,
          aa.horas_dictadas,
          (NVL(h.minutos_equiv,0)/60) - NVL(aa.horas_dictadas,0) AS horas_no_dictadas,
          m.descripcion AS motivo_inasistencia,
          aa.reposicion,
          aa.fecha_reposicion,
          s.numero_semana
        FROM ASISTENCIA_AULA aa
        JOIN AULA au               ON aa.id_aula = au.id_aula
        JOIN INSTITUCION inst      ON au.id_institucion = inst.id_institucion
        LEFT JOIN FESTIVO f        ON TRUNC(aa.fecha_clase) = f.fecha
        LEFT JOIN HORARIO h        ON aa.id_horario = h.id_horario
        LEFT JOIN MOTIVO_INASISTENCIA m 
                                   ON aa.id_motivo = m.id_motivo
        LEFT JOIN SEMANA s         ON s.id_semana = aa.id_semana
        WHERE au.id_aula = :1
        """

        params = [id_aula]

        # Rango de fechas opcional
        if fecha_inicio and fecha_fin:
            # convertir a date de Python
            f_ini = datetime.strptime(fecha_inicio, "%Y-%m-%d").date()
            f_fin = datetime.strptime(fecha_fin, "%Y-%m-%d").date()
            sql += " AND aa.fecha_clase BETWEEN :2 AND :3"
            params.extend([f_ini, f_fin])

        sql += " ORDER BY aa.fecha_clase, aa.hora_inicio"

        cur.execute(sql, params)
        rows = cur.fetchall()
        cols = [c[0].lower() for c in cur.description]

        resultado = []
        for r in rows:
            d = dict(zip(cols, r))

            # fecha_clase como string
            fc = d.get("fecha_clase")
            d["fecha_clase"] = fc.strftime("%Y-%m-%d") if fc else None

            # normalizar hora_inicio y h_inicio / h_final
            for key in ("hora_inicio", "h_inicio", "h_final"):
                val = d.get(key)
                if val is None:
                    d[key] = ""
                elif isinstance(val, str):
                    d[key] = val[:5]
                else:
                    d[key] = val.strftime("%H:%M")

            # renombrar/ajustar claves para que coincidan con el front
            resultado.append({
                "institucion": d.get("nombre_inst"),
                "id_aula": d.get("id_aula"),
                "grado": d.get("grado"),
                "numero_semana": d.get("numero_semana"),
                "fecha_clase": d.get("fecha_clase"),
                "es_festivo": d.get("es_festivo"),
                "dia_semana": d.get("dia_semana"),
                "hora_inicio": d.get("hora_inicio"),
                "hora_fin": d.get("h_final"),
                "tutor": None,  # si luego quieres agregarlo, se añade al SELECT
                "dictada": d.get("dictada"),
                "horas_dictadas": float(d.get("horas_dictadas") or 0),
                "horas_no_dictadas": float(d.get("horas_no_dictadas") or 0),
                "motivo_inasistencia": d.get("motivo_inasistencia"),
                "reposicion": d.get("reposicion"),
                "fecha_reposicion": (
                    d.get("fecha_reposicion").strftime("%Y-%m-%d")
                    if d.get("fecha_reposicion") else None
                ),
            })

        return resultado
    finally:
        cur.close()
        conn.close()