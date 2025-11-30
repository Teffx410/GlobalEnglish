# scripts/seed_data.py
import os
import oracledb
from datetime import date
from hashlib import sha256

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1522/XEPDB1")

def hash_pwd(pwd: str) -> str:
    return sha256(pwd.encode()).hexdigest()


def main():
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()

    # ---------- INSTITUCION ----------
    instituciones = [
        ("Harvard University", "Mañana", "Cambridge, MA, USA"),
        ("Stanford University", "Mañana", "Stanford, CA, USA"),
        ("Massachusetts Institute of Technology", "Tarde", "Cambridge, MA, USA"),
        ("University of Oxford", "Mañana", "Oxford, UK"),
        ("University of Cambridge", "Mañana", "Cambridge, UK"),
        ("University of Toronto", "Tarde", "Toronto, Canada"),
        ("University of São Paulo", "Mañana", "São Paulo, Brazil"),
        ("Universidad Nacional de Colombia", "Tarde", "Bogotá, Colombia"),
        ("Pontificia Universidad Javeriana", "Mañana", "Bogotá, Colombia"),
        ("Universidad del Norte", "Tarde", "Barranquilla, Colombia"),
    ]
    cur.executemany(
        """
        INSERT INTO INSTITUCION (nombre_inst, jornada, dir_principal)
        VALUES (:1, :2, :3)
        """,
        instituciones,
    )

    # ---------- SEDE ----------
    sedes = [
        (1, 1, "Harvard Main Campus", "S"),
        (2, 1, "Stanford Main Campus", "S"),
        (3, 1, "MIT Main Campus", "S"),
        (4, 1, "Oxford City Centre", "S"),
        (5, 1, "Cambridge City Centre", "S"),
        (6, 1, "Downtown Toronto Campus", "S"),
        (7, 1, "Cidade Universitária", "S"),
        (8, 1, "Ciudad Universitaria Bogotá", "S"),
        (9, 1, "Sede Bogotá", "S"),
        (10, 1, "Km 5 Vía Puerto Colombia", "S"),
    ]
    cur.executemany(
        """
        INSERT INTO SEDE (id_institucion, id_sede, direccion, es_principal)
        VALUES (:1, :2, :3, :4)
        """,
        sedes,
    )

    # ---------- PERSONA ----------
    personas = [
        # id_persona 1..10 por identidad
        ("CC", "100000001", "Ana Administradora", "3001111111", "ana.admin@uninorte.edu", "ADMINISTRADOR"),
        ("CC", "100000002", "Luis Administrador", "3001112222", "luis.admin@unal.edu", "ADMINISTRADOR"),
        ("CC", "200000001", "Carla Administrativa", "3002221111", "carla.adm@javeriana.edu", "ADMINISTRATIVO"),
        ("CC", "200000002", "Diego Administrativo", "3002222222", "diego.adm@usp.br", "ADMINISTRATIVO"),
        ("CC", "200000003", "Paula Administrativa", "3002223333", "paula.adm@utoronto.ca", "ADMINISTRATIVO"),
        ("CC", "300000001", "Nay Tutor", "3003331111", "nay.tutor@globalenglish.edu", "TUTOR"),
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

    # ---------- USUARIO ----------
    pwd_hash = hash_pwd("Password123!")
    usuarios = [
        ("ana.admin", pwd_hash, 1),
        ("luis.admin", pwd_hash, 2),
        ("carla.adm", pwd_hash, 3),
        ("diego.adm", pwd_hash, 4),
        ("paula.adm", pwd_hash, 5),
        ("nay.tutor", pwd_hash, 6),
        ("laura.tutor", pwd_hash, 7),
        ("miguel.tutor", pwd_hash, 8),
        ("sara.tutor", pwd_hash, 9),
        ("carlos.tutor", pwd_hash, 10),
    ]
    cur.executemany(
        """
        INSERT INTO USUARIO (nombre_user, contrasena, id_persona)
        VALUES (:1, :2, :3)
        """,
        usuarios,
    )

    # ---------- AULA ----------
    aulas = [
        (8, 1, "3"),
        (8, 1, "4"),
        (8, 1, "5"),
        (9, 1, "6"),
        (9, 1, "7"),
        (10, 1, "8"),
        (10, 1, "9"),
        (10, 1, "10"),
        (7, 1, "3"),
        (7, 1, "4"),
    ]
    cur.executemany(
        """
        INSERT INTO AULA (id_institucion, id_sede, grado)
        VALUES (:1, :2, :3)
        """,
        aulas,
    )

    # ---------- HORARIO ----------
    horarios = [
        ("LUNES", "07:00", "08:30", 90, "S"),
        ("LUNES", "08:30", "10:00", 90, "S"),
        ("MARTES", "07:00", "08:30", 90, "S"),
        ("MARTES", "08:30", "10:00", 90, "S"),
        ("MIERCOLES", "07:00", "09:00", 120, "S"),
        ("JUEVES", "09:00", "11:00", 120, "S"),
        ("VIERNES", "07:00", "09:00", 120, "S"),
        ("SABADO", "08:00", "10:00", 120, "S"),
        ("LUNES", "10:00", "12:00", 120, "S"),
        ("MARTES", "10:00", "12:00", 120, "S"),
    ]
    cur.executemany(
        """
        INSERT INTO HORARIO (dia_semana, h_inicio, h_final, minutos_equiv, es_continuo)
        VALUES (:1, :2, :3, :4, :5)
        """,
        horarios,
    )

    # ---------- HISTORICO_HORARIO_AULA ----------
    hha = [
        (1, 1, date(2025, 1, 1), None),
        (1, 2, date(2025, 1, 1), None),
        (2, 3, date(2025, 1, 1), None),
        (2, 4, date(2025, 1, 1), None),
        (3, 5, date(2025, 1, 1), None),
        (4, 6, date(2025, 1, 1), None),
        (5, 7, date(2025, 1, 1), None),
        (6, 8, date(2025, 1, 1), None),
        (7, 9, date(2025, 1, 1), None),
        (8, 10, date(2025, 1, 1), None),
    ]
    cur.executemany(
        """
        INSERT INTO HISTORICO_HORARIO_AULA (id_aula, id_horario, fecha_inicio, fecha_fin)
        VALUES (:1, :2, :3, :4)
        """,
        hha,
    )

    # ---------- MOTIVO_INASISTENCIA ----------
    motivos = [
        ("Enfermedad",),
        ("Cita médica",),
        ("Problemas de transporte",),
        ("Asuntos familiares",),
        ("Evento institucional",),
        ("Condiciones climáticas",),
        ("Paro",),
        ("Licencia",),
        ("Retraso del tutor",),
        ("Otro",),
    ]
    cur.executemany(
        "INSERT INTO MOTIVO_INASISTENCIA (descripcion) VALUES (:1)",
        motivos,
    )

    # ---------- FESTIVO ----------
    festivos = [
        (date(2025, 1, 1), "Año Nuevo"),
        (date(2025, 1, 6), "Reyes"),
        (date(2025, 3, 24), "Festivo Marzo"),
        (date(2025, 4, 18), "Viernes Santo"),
        (date(2025, 5, 1), "Día del Trabajo"),
        (date(2025, 6, 29), "San Pedro y San Pablo"),
        (date(2025, 7, 20), "Independencia de Colombia"),
        (date(2025, 8, 7), "Batalla de Boyacá"),
        (date(2025, 10, 12), "Día de la Raza"),
        (date(2025, 12, 25), "Navidad"),
    ]
    cur.executemany(
        "INSERT INTO FESTIVO (fecha, descripcion) VALUES (:1, :2)",
        festivos,
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Datos de prueba insertados correctamente.")


if __name__ == "__main__":
    main()