import oracledb
import os
from hashlib import sha256

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")


def hash_pwd(pwd: str) -> str:
    return sha256(pwd.encode()).hexdigest()


def insertar_datos():
    print("Insertando PERSONA y USUARIO de prueba...")
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()

    # ========== PERSONA (10) ==========
    personas = [
        ("CC", "100000001", "Ana Administradora", "3001111111", "ana.admin@uninorte.edu", "ADMINISTRADOR"),
        ("CC", "100000002", "Luis Administrador", "3001112222", "luis.admin@unal.edu", "ADMINISTRADOR"),
        ("CC", "200000001", "Carla Administrativa", "3002221111", "carla.adm@javeriana.edu", "ADMINISTRATIVO"),
        ("CC", "200000002", "Diego Administrativo", "3002222222", "diego.adm@usp.br", "ADMINISTRATIVO"),
        ("CC", "200000003", "Paula Administrativa", "3002223333", "paula.adm@utoronto.ca", "ADMINISTRATIVO"),
        ("CC", "300000001", "Juan Tutor", "3003331111", "juan.tutor@globalenglish.edu", "TUTOR"),
        ("CC", "300000002", "Laura Tutor", "3003332222", "laura.tutor@globalenglish.edu", "TUTOR"),
        ("CC", "300000003", "Miguel Tutor", "3003333333", "miguel.tutor@globalenglish.edu", "TUTOR"),
        ("CC", "300000004", "Sara Tutor", "3003334444", "sara.tutor@globalenglish.edu", "TUTOR"),
        ("CC", "300000005", "Carlos Tutor", "3003335555", "carlos.tutor@globalenglish.edu", "TUTOR"),
    ]
    cur.executemany(
        """
        INSERT INTO PERSONA (tipo_doc, num_documento, nombre, telefono, correo, rol)
        VALUES (:1, :2, :3, :4, :5, :6)
        """,
        personas,
    )

    # ========== USUARIO (10) ==========
    pwd_hash = hash_pwd("Password123!")
    usuarios = [
        ("ana.admin",   pwd_hash, 1),
        ("luis.admin",  pwd_hash, 2),
        ("carla.adm",   pwd_hash, 3),
        ("diego.adm",   pwd_hash, 4),
        ("paula.adm",   pwd_hash, 5),
        ("juan.tutor",  pwd_hash, 6),
        ("laura.tutor", pwd_hash, 7),
        ("miguel.tutor",pwd_hash, 8),
        ("sara.tutor",  pwd_hash, 9),
        ("carlos.tutor",pwd_hash, 10),
    ]
    cur.executemany(
        """
        INSERT INTO USUARIO (nombre_user, contrasena, id_persona)
        VALUES (:1, :2, :3)
        """,
        usuarios,
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Datos insertados correctamente.")


if __name__ == "__main__":
    insertar_datos()
