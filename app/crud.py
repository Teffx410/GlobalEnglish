# app/crud.py
from typing import Optional, Tuple
from app.db import get_conn
import oracledb
import secrets
from datetime import date, datetime, timedelta
# Nota: La importación de hashlib se moverá a create_usuario para mantener la limpieza.

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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    """
    Crea una sede validando que la dirección sea única.
    **MODIFICADO:** Usa una secuencia de Oracle (SEDE_SEQ) o campo IDENTITY
    para generar el id_sede de forma segura y concurrente.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que la dirección no exista
        cur.execute("SELECT COUNT(*) FROM SEDE WHERE LOWER(direccion) = LOWER(:1)", 
                    (data.get('direccion'),))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe una sede con esa dirección"}
        
        # Usar RETURNING INTO para obtener el ID de forma atómica y eficiente.
        # Asumimos que id_sede es generado por una secuencia (SEDE_SEQ.NEXTVAL) o es IDENTITY.
        id_sede_var = cur.var(oracledb.NUMBER)
        cur.execute("""INSERT INTO SEDE(id_institucion, id_sede, direccion, es_principal)
                        VALUES (:1, SEDE_SEQ.NEXTVAL, :2, :3)
                        RETURNING id_sede INTO :4""",
                    (data['id_institucion'], data.get('direccion'), data.get('es_principal', 'N'), id_sede_var))
        
        conn.commit()
        next_id_sede = id_sede_var.getvalue()[0]
        return {"ok": True, "id_sede": next_id_sede}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def list_sedes(limit=100):
    """Lista todas las sedes"""
    # ... (Sin cambios en esta función)
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_sede, id_institucion, direccion, es_principal FROM SEDE ORDER BY id_institucion, id_sede")
        rows = cur.fetchmany(numRows=limit)
        return [dict(id_sede=r[0], id_institucion=r[1], direccion=r[2], es_principal=r[3]) for r in rows]
    finally:
        cur.close()
        conn.close()

def get_sede(id_institucion, id_sede):
    """
    Obtiene una sede por su clave primaria compuesta.
    **MODIFICADO:** Ahora requiere id_institucion e id_sede.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_sede, id_institucion, direccion, es_principal FROM SEDE WHERE id_institucion = :1 AND id_sede = :2", 
                    (id_institucion, id_sede))
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
    # ... (Sin cambios en esta función)
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

def update_sede(id_institucion, id_sede, data: dict):
    """
    Actualiza una sede validando dirección única.
    **MODIFICADO:** Ahora requiere id_institucion e id_sede para identificar la fila a actualizar.
    """
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que la dirección no exista en otra sede de la MISMA INSTITUCION (mejor práctica)
        # O en cualquier sede (como estaba originalmente, que es más estricto)
        cur.execute("""SELECT COUNT(*) FROM SEDE 
                       WHERE LOWER(direccion) = LOWER(:1) 
                         AND NOT (id_institucion = :2 AND id_sede = :3)""", 
                    (data.get('direccion'), id_institucion, id_sede))
        if cur.fetchone()[0] > 0:
            return {"error": "Ya existe otra sede con esa dirección"}
        
        # El id_institucion debería venir en data, o tomarse del argumento, pero id_sede no se actualiza
        cur.execute("""UPDATE SEDE SET
                          id_institucion = :1, -- Debería ser el mismo, a menos que se quiera mover la sede
                          direccion = :2,
                          es_principal = :3
                        WHERE id_institucion = :4 AND id_sede = :5""",
                    (data.get('id_institucion', id_institucion), data.get('direccion'), 
                     data.get('es_principal', 'N'), id_institucion, id_sede))
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
    """Crea una persona validando unicidad y usando RETURNING INTO."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que num_documento no esté vacío
        if not data.get('num_documento') or not data.get('num_documento').strip():
            return {"error": "El número de documento es requerido"}
        
        # Validar que num_documento sea único
        cur.execute("SELECT COUNT(*) FROM PERSONA WHERE LOWER(num_documento) = LOWER(:1)", 
                    (data.get('num_documento'),))
        if cur.fetchone()[0] > 0:
            return {"error": "El número de documento ya está registrado"}
        
        # Validar que correo sea único
        if data.get('correo'):
             cur.execute("SELECT COUNT(*) FROM PERSONA WHERE LOWER(correo) = LOWER(:1)", 
                         (data.get('correo'),))
             if cur.fetchone()[0] > 0:
                 return {"error": "El correo ya está registrado"}
        
        id_persona_var = cur.var(oracledb.NUMBER)
        cur.execute("""INSERT INTO PERSONA(tipo_doc, num_documento, nombre, telefono, correo, rol) 
                        VALUES (:1,:2,:3,:4,:5,:6)
                        RETURNING id_persona INTO :7""",
                    (data.get('tipo_doc'), data.get('num_documento'), data['nombre'], 
                     data.get('telefono'), data.get('correo'), data.get('rol'), id_persona_var))
        conn.commit()
        
        id_persona = id_persona_var.getvalue()[0]
        return {"ok": True, "id_persona": id_persona}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()

def list_personas(limit=100):
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Validar que num_documento sea único (excluyendo la persona actual)
        if data.get('num_documento'):
            cur.execute("""SELECT COUNT(*) FROM PERSONA 
                          WHERE LOWER(num_documento) = LOWER(:1) AND id_persona != :2""", 
                        (data.get('num_documento'), id_persona))
            if cur.fetchone()[0] > 0:
                return {"error": "El número de documento ya está registrado"}
        
        # Validar que correo sea único (excluyendo la persona actual)
        if data.get('correo'):
            cur.execute("""SELECT COUNT(*) FROM PERSONA 
                          WHERE LOWER(correo) = LOWER(:1) AND id_persona != :2""", 
                        (data.get('correo'), id_persona))
            if cur.fetchone()[0] > 0:
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
    # ... (Sin cambios en esta función)
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Verificar si la persona está asociada a USUARIO
        cur.execute("SELECT COUNT(*) FROM USUARIO WHERE id_persona = :1", (id_persona,))
        count_usuario = cur.fetchone()[0]
        
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
        if "CONSTRAINT" in error_msg.upper():
            return {"error": "No se puede eliminar esta persona porque tiene registros asociados (ej. es tutor o está en otras tablas)."}
        return {"error": error_msg}
    finally:
        cur.close()
        conn.close()

# ============================
# USUARIO
# ============================

def create_usuario(data: dict):
    from hashlib import sha256 # Movida aquí
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
    # ... (Sin cambios en esta función)
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
    """Crea un aula y usa RETURNING INTO para obtener id_aula."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_aula_var = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO AULA (id_institucion, id_sede, grado)
            VALUES (:1, :2, :3)
            RETURNING id_aula INTO :4
        """, (data["id_institucion"], data["id_sede"], data["grado"], id_aula_var))
        conn.commit()

        id_aula = id_aula_var.getvalue()[0]
        return id_aula
    finally:
        cur.close()
        conn.close()


def list_aulas(limit: int = 100):
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    """Crea un horario y usa RETURNING INTO para obtener id_horario."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        id_horario_var = cur.var(oracledb.NUMBER)
        cur.execute("""
            INSERT INTO HORARIO (dia_semana, h_inicio, h_final, minutos_equiv, es_continuo)
            VALUES (:1, :2, :3, :4, :5)
            RETURNING id_horario INTO :6
        """, (
            data['dia_semana'], data['h_inicio'], data['h_final'],
            data['minutos_equiv'], data.get('es_continuo', 'S'), id_horario_var
        ))
        conn.commit()
        
        id_horario = id_horario_var.getvalue()[0]
        return id_horario
    finally:
        cur.close()
        conn.close()

def list_horarios(limit=100):
    # ... (Sin cambios en esta función)
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

def get_horario(id_horario: int):
    """Obtiene un horario por ID."""
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            SELECT id_horario, dia_semana, h_inicio, h_final, minutos_equiv, es_continuo
            FROM HORARIO
            WHERE id_horario = :1
        """, (id_horario,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(
            id_horario=r[0],
            dia_semana=r[1],
            h_inicio=r[2],
            h_final=r[3],
            minutos_equiv=r[4],
            es_continuo=r[5]
        )
    finally:
        cur.close()
        conn.close()

def delete_horario(id_horario: int):
    """
    Borra de HORARIO solo si NO hay registros ACTIVOS en el histórico
    (es decir, si no hay filas con fecha_fin IS NULL para ese id_horario).
    """
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
    id_aula = data['id_aula']
    id_horario = data['id_horario']
    fecha_inicio = data['fecha_inicio']

    valido, msg = validar_horario_aula(id_aula, id_horario, fecha_inicio)
    if not valido:
        return {"error": msg}
    
    # Realiza insert como antes
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO HISTORICO_HORARIO_AULA (id_aula, id_horario, fecha_inicio)
            VALUES (:1, :2, TO_DATE(:3, 'YYYY-MM-DD'))
        """, (id_aula, id_horario, fecha_inicio))
        conn.commit()
        return {"msg": "Horario asignado correctamente."}
    except Exception as e:
        return {"error": str(e)}
    finally:
        cur.close()
        conn.close()


def get_historial_horarios_aula(id_aula: int, limit=200):
    # ... (Sin cambios en esta función)
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
                TO_CHAR(hha.fecha_fin, 'YYYY-MM-DD')    AS fecha_fin,
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
    # ... (Sin cambios en esta función)
    """
    Marca un registro de HISTORICO_HORARIO_AULA como finalizado.
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
    # ... (Sin cambios en esta función)
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
    # ... (Sin cambios en esta función)
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
            JOIN PERSONA p           ON at.id_persona = p.id_persona
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


def aula_tiene_tutor_activo(id_aula: int) -> bool:
    # ... (Sin cambios en esta función)
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
