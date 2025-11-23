# scripts/seed_data.py
import os
import oracledb
from datetime import date

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")

def seed():
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()
    try:
        # Instituciones
        cur.execute("INSERT INTO INSTITUCION(nombre_inst, jornada, dir_principal) VALUES (:1,:2,:3)",
                    ("IED San Jose", "UNICA_MAÑANA", "Calle 1"))
        cur.execute("INSERT INTO INSTITUCION(nombre_inst, jornada, dir_principal) VALUES (:1,:2,:3)",
                    ("IED Norte", "MIXTA", "Av. Siempre Viva 100"))
        # obtener ids
        conn.commit()
        # Sede
        cur.execute("SELECT id_institucion FROM INSTITUCION WHERE nombre_inst = :1", ("IED San Jose",))
        id_inst = cur.fetchone()[0]
        cur.execute("INSERT INTO SEDE(id_institucion, id_sede, direccion, es_principal) VALUES (:1,:2,:3,:4)",
                    (id_inst, 1, "Calle 1 #1", 'S'))
        # Persona (tutores/administrativos)
        cur.execute("INSERT INTO PERSONA(tipo_doc, nombre, telefono, correo, rol) VALUES (:1,:2,:3,:4,:5)",
                    ("CC", "Ana Pérez", "3001112222", "ana@ejemplo.com", "TUTOR"))
        cur.execute("INSERT INTO PERSONA(tipo_doc, nombre, telefono, correo, rol) VALUES (:1,:2,:3,:4,:5)",
                    ("CC", "Luis Gomez", "3003334444", "luis@ejemplo.com", "ADMINISTRATIVO"))
        conn.commit()
        # Aula
        cur.execute("INSERT INTO AULA(id_institucion, id_sede, grado) VALUES (:1,:2,:3)",
                    (id_inst, 1, '4'))
        conn.commit()
        # Estudiante
        cur.execute("INSERT INTO ESTUDIANTE(tipo_documento, num_documento, nombres, apellidos, telefono, fecha_nacimiento, correo, score_entrada) VALUES (:1,:2,:3,:4,:5,:6,:7,:8)",
                    ("CC","12345","Juan","Perez","3005556666", date(2012,5,1), "juan@test.com", 45))
        conn.commit()
        print("Seed completed.")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    seed()
