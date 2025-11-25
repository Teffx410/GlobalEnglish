import oracledb

USER = "GLOBALENGLISH"
PASSWORD = "oracle"
DSN = "localhost:1521/XEPDB1"

conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
cur = conn.cursor()

# Usuarios y personas a insertar
personas = [
    # tipo_doc, nombre, telefono, correo, rol, nombre_user, contrasena
    ('CC', 'Admin Principal',   '3001112222', 'admin@globalenglish.com',    'ADMINISTRADOR',  'admin',     '123456'),
    ('CC', 'Admin Operativo',   '3002223333', 'operativo@globalenglish.com','ADMINISTRATIVO', 'operativo', '654321'),
    ('CC', 'Tutor Bilingüe',    '3003334444', 'tutor@globalenglish.com',    'TUTOR',          'tutor',     'abcdef'),
]

try:
    for tipo_doc, nombre, telefono, correo, rol, nombre_user, contrasena in personas:
        print(f"\n--- Procesando: {correo} ---")
        cur.execute(
            "DELETE FROM USUARIO WHERE id_persona IN (SELECT id_persona FROM PERSONA WHERE correo = :1)",
            (correo,))
        print("Borrado USUARIO")
        cur.execute(
            "DELETE FROM PERSONA WHERE correo = :1",
            (correo,))
        print("Borrado PERSONA")
        cur.execute("""
            INSERT INTO PERSONA (tipo_doc, nombre, telefono, correo, rol)
            VALUES (:1, :2, :3, :4, :5)
        """, (tipo_doc, nombre, telefono, correo, rol))
        print("Insertada PERSONA")
        cur.execute("SELECT id_persona FROM PERSONA WHERE correo = :1", (correo,))
        id_persona = cur.fetchone()[0]
        print("id_persona asignada:", id_persona)
        cur.execute("""
            INSERT INTO USUARIO (nombre_user, contrasena, id_persona)
            VALUES (:1, :2, :3)
        """, (nombre_user, contrasena, id_persona))
        print("Insertado USUARIO")


    conn.commit()
    print("\nTodos los usuarios y personas creados exitosamente.")
except Exception as e:
    print("\nError al insertar datos:", e)
finally:
    cur.close()
    conn.close()
