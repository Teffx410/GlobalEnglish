import oracledb

USER = "GLOBALENGLISH"
PASSWORD = "oracle"
<<<<<<< HEAD
DSN = "localhost:1521/XEPDB1"
=======
DSN = "localhost:1522/XEPDB1"
>>>>>>> main

conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
cur = conn.cursor()

# Usuarios y personas a insertar
<<<<<<< HEAD
# tipo_doc, num_documento, nombre, telefono, correo, rol, nombre_user, contrasena
personas = [
    ('CC', '1234567890', 'Admin Principal',   '3001112222', 'admin@globalenglish.com',    'ADMINISTRADOR',  'admin',     '123456'),
    ('CC', '1234567891', 'Admin Operativo',   '3002223333', 'operativo@globalenglish.com','ADMINISTRATIVO', 'operativo', '654321'),
    ('CC', '1234567892', 'Tutor Bilingüe',    '3003334444', 'tutor@globalenglish.com',    'TUTOR',          'tutor',     'abcdef'),
    ('CC', '1234567893', 'Tutor Inglés',      '3004445555', 'tutor2@globalenglish.com',   'TUTOR',          'tutor2',    'xyz789'),
    ('CC', '1234567894', 'Estudiante Juan',   '3005556666', 'juan@globalenglish.com',     'ESTUDIANTE',     'juan.est',  'pass123'),
    ('CC', '1234567895', 'Estudiante María',  '3006667777', 'maria@globalenglish.com',    'ESTUDIANTE',     'maria.est', 'pass456'),
]

try:
    for tipo_doc, num_documento, nombre, telefono, correo, rol, nombre_user, contrasena in personas:
        print(f"\n--- Procesando: {correo} ---")
        
        # Eliminar USUARIO si existe
        cur.execute(
            "DELETE FROM USUARIO WHERE id_persona IN (SELECT id_persona FROM PERSONA WHERE correo = :1)",
            (correo,))
        print("✓ Borrado USUARIO (si existía)")
        
        # Eliminar PERSONA si existe
        cur.execute(
            "DELETE FROM PERSONA WHERE correo = :1",
            (correo,))
        print("✓ Borrado PERSONA (si existía)")
        
        # Insertar PERSONA con num_documento
        cur.execute("""
            INSERT INTO PERSONA (tipo_doc, num_documento, nombre, telefono, correo, rol)
            VALUES (:1, :2, :3, :4, :5, :6)
        """, (tipo_doc, num_documento, nombre, telefono, correo, rol))
        print(f"✓ Insertada PERSONA (ID: {num_documento})")
        
        # Obtener id_persona
        cur.execute("SELECT id_persona FROM PERSONA WHERE correo = :1", (correo,))
        id_persona = cur.fetchone()[0]
        print(f"✓ id_persona asignada: {id_persona}")
        
        # Insertar USUARIO
=======
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
>>>>>>> main
        cur.execute("""
            INSERT INTO USUARIO (nombre_user, contrasena, id_persona)
            VALUES (:1, :2, :3)
        """, (nombre_user, contrasena, id_persona))
<<<<<<< HEAD
        print(f"✓ Insertado USUARIO: {nombre_user}")

    conn.commit()
    print("\n" + "="*50)
    print("✓ Todos los usuarios y personas creados exitosamente.")
    print("="*50)
    
except Exception as e:
    conn.rollback()
    print("\n" + "="*50)
    print(f"❌ Error al insertar datos: {e}")
    print("="*50)
    
=======
        print("Insertado USUARIO")


    conn.commit()
    print("\nTodos los usuarios y personas creados exitosamente.")
except Exception as e:
    print("\nError al insertar datos:", e)
>>>>>>> main
finally:
    cur.close()
    conn.close()
