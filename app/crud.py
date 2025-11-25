# app/crud.py
from app.db import get_conn
import oracledb

def create_institucion(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO INSTITUCION(nombre_inst, jornada, dir_principal)
                       VALUES (:1,:2,:3)""",
                    (data['nombre_inst'], data.get('jornada'), data.get('dir_principal')))
        conn.commit()
        cur.execute("SELECT id_institucion FROM INSTITUCION WHERE nombre_inst = :1", (data['nombre_inst'],))
        r = cur.fetchone()
        return r[0] if r else None
    finally:
        cur.close()
        conn.close()

def list_instituciones(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_institucion, nombre_inst, jornada, dir_principal FROM INSTITUCION ORDER BY id_institucion")
        rows = cur.fetchmany(numRows=limit)
        return [dict(id_institucion=r[0], nombre_inst=r[1], jornada=r[2], dir_principal=r[3]) for r in rows]
    finally:
        cur.close()
        conn.close()

def get_institucion(id_inst):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_institucion, nombre_inst, jornada, dir_principal FROM INSTITUCION WHERE id_institucion = :1", (id_inst,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(id_institucion=r[0], nombre_inst=r[1], jornada=r[2], dir_principal=r[3])
    finally:
        cur.close()
        conn.close()

        # Borrar Institución
def delete_institucion(id_inst):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM INSTITUCION WHERE id_institucion = :1", (id_inst,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# Editar Institución
def update_institucion(id_inst, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""UPDATE INSTITUCION SET
                          nombre_inst = :1,
                          jornada = :2,
                          dir_principal = :3
                       WHERE id_institucion = :4""",
                    (data['nombre_inst'], data.get('jornada'), data.get('dir_principal'), id_inst))
        conn.commit()
    finally:
        cur.close()
        conn.close()

# CRUD Sede

def create_sede(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        # Obtener el siguiente id_sede para esta institución
        cur.execute("SELECT NVL(MAX(id_sede), 0) + 1 FROM SEDE WHERE id_institucion = :1", (data['id_institucion'],))
        next_id_sede = cur.fetchone()[0]
        # Insertar sede con el siguiente id_sede
        cur.execute("""INSERT INTO SEDE(id_institucion, id_sede, direccion, es_principal)
                       VALUES (:1, :2, :3, :4)""",
                    (data['id_institucion'], next_id_sede, data.get('direccion'), data.get('es_principal', 'N')))
        conn.commit()
        return next_id_sede
    finally:
        cur.close()
        conn.close()


def list_sedes(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_sede, id_institucion, direccion, es_principal FROM SEDE ORDER BY id_sede")
        rows = cur.fetchmany(numRows=limit)
        return [dict(id_sede=r[0], id_institucion=r[1], direccion=r[2], es_principal=r[3]) for r in rows]
    finally:
        cur.close()
        conn.close()

def get_sede(id_sede):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_sede, id_institucion, direccion, es_principal FROM SEDE WHERE id_sede = :1", (id_sede,))
        r = cur.fetchone()
        if not r:
            return None
        return dict(id_sede=r[0], id_institucion=r[1], direccion=r[2], es_principal=r[3])
    finally:
        cur.close()
        conn.close()

def delete_sede(id_sede):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM SEDE WHERE id_sede = :1", (id_sede,))
        conn.commit()
    finally:
        cur.close()
        conn.close()

def update_sede(id_sede, data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""UPDATE SEDE SET
                          id_institucion = :1,
                          direccion = :2,
                          es_principal = :3
                       WHERE id_sede = :4""",
                    (data['id_institucion'], data.get('direccion'), data.get('es_principal', 'N'), id_sede))
        conn.commit()
    finally:
        cur.close()
        conn.close()


# Ejemplo para Persona
def create_persona(data: dict):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO PERSONA(tipo_doc, nombre, telefono, correo, rol) VALUES (:1,:2,:3,:4,:5)""",
                    (data.get('tipo_doc'), data['nombre'], data.get('telefono'), data.get('correo'), data.get('rol')))
        conn.commit()
        cur.execute("SELECT id_persona FROM PERSONA WHERE nombre = :1 ORDER BY id_persona DESC", (data['nombre'],))
        r = cur.fetchone()
        return r[0] if r else None
    finally:
        cur.close()
        conn.close()

def list_personas(limit=100):
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute("SELECT id_persona, tipo_doc, nombre, telefono, correo, rol FROM PERSONA ORDER BY id_persona")
        rows = cur.fetchmany(numRows=limit)
        return [dict(id_persona=r[0], tipo_doc=r[1], nombre=r[2], telefono=r[3], correo=r[4], rol=r[5]) for r in rows]
    finally:
        cur.close()
        conn.close()

# Similar wrappers can be added for Aula, Estudiante, Horario, Asignacion_Tutor, etc.
