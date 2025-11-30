import oracledb
import os
from hashlib import sha256

USER = os.getenv("DB_USER", "GLOBALENGLISH")
PASSWORD = os.getenv("DB_PASS", "oracle")
DSN = os.getenv("DB_DSN", "localhost:1521/XEPDB1")


def hash_pwd(pwd: str) -> str:
    return sha256(pwd.encode()).hexdigest()


def insertar_datos():
    print("Insertando datos de prueba...")
    conn = oracledb.connect(user=USER, password=PASSWORD, dsn=DSN)
    cur = conn.cursor()

    # ========== INSTITUCION ==========
    cur.execute("""
        INSERT INTO INSTITUCION (nombre_inst, jornada, dir_principal)
        VALUES ('IES Ejemplo', 'Mañana', 'Calle 123')
    """)
    cur.execute("SELECT MAX(id_institucion) FROM INSTITUCION")
    id_institucion = cur.fetchone()[0]

    # ========== SEDE ==========
    cur.execute("""
        INSERT INTO SEDE (id_institucion, id_sede, direccion, es_principal)
        VALUES (:1, 1, 'Sede Principal', 'S')
    """, [id_institucion])

    # ========== PERSONAS (TUTOR y ADMIN) ==========
    # Tutor
    cur.execute("""
        INSERT INTO PERSONA (tipo_doc, num_documento, nombre, telefono, correo, rol)
        VALUES ('CC', '300000010', 'Juan Tutor', '3121231111', 'juan@tutor.com', 'TUTOR')
    """)
    cur.execute("SELECT MAX(id_persona) FROM PERSONA")
    id_tutor = cur.fetchone()[0]

    # Admin
    cur.execute("""
        INSERT INTO PERSONA (tipo_doc, num_documento, nombre, telefono, correo, rol)
        VALUES ('CC', '100000010', 'Ana Admin', '3133331111', 'ana@admin.com', 'ADMINISTRADOR')
    """)
    cur.execute("SELECT MAX(id_persona) FROM PERSONA")
    id_admin = cur.fetchone()[0]

    # ========== USUARIO (hash SHA-256) ==========
    pwd_hash = hash_pwd("Password123!")
    cur.execute("""
        INSERT INTO USUARIO (nombre_user, contrasena, id_persona)
        VALUES ('juantutor', :1, :2)
    """, [pwd_hash, id_tutor])

    cur.execute("""
        INSERT INTO USUARIO (nombre_user, contrasena, id_persona)
        VALUES ('ana.admin', :1, :2)
    """, [pwd_hash, id_admin])

    # ========== AULA ==========
    cur.execute("""
        INSERT INTO AULA (id_institucion, id_sede, grado)
        VALUES (:1, 1, '5')
    """, [id_institucion])
    cur.execute("SELECT MAX(id_aula) FROM AULA")
    id_aula = cur.fetchone()[0]

    # ========== HORARIO ==========
    cur.execute("""
        INSERT INTO HORARIO (dia_semana, h_inicio, h_final, minutos_equiv, es_continuo)
        VALUES ('LUNES', '08:00', '10:00', 120, 'S')
    """)
    cur.execute("SELECT MAX(id_horario) FROM HORARIO")
    id_horario = cur.fetchone()[0]

    # ========== HISTORICO_HORARIO_AULA ==========
    cur.execute("""
        INSERT INTO HISTORICO_HORARIO_AULA (id_aula, id_horario, fecha_inicio)
        VALUES (:1, :2, DATE '2025-01-15')
    """, [id_aula, id_horario])

    # ========== ASIGNACION_TUTOR (solo persona) ==========
    cur.execute("""
        INSERT INTO ASIGNACION_TUTOR (id_persona, fecha_inicio)
        VALUES (:1, DATE '2025-01-15')
    """, [id_tutor])
    cur.execute("SELECT MAX(id_tutor_aula) FROM ASIGNACION_TUTOR")
    id_tutor_aula = cur.fetchone()[0]

    # ========== TUTOR_AULA (relación tutor-aula) ==========
    cur.execute("""
        INSERT INTO TUTOR_AULA (id_tutor_aula, id_aula)
        VALUES (:1, :2)
    """, [id_tutor_aula, id_aula])

    # ========== ESTUDIANTE ==========
    cur.execute("""
        INSERT INTO ESTUDIANTE (
            tipo_documento, num_documento, nombres, apellidos,
            telefono, fecha_nacimiento, correo, score_entrada, score_salida
        ) VALUES (
            'TI', '123456', 'Pepe', 'Perez',
            '3211231234', DATE '2013-04-01',
            'pepe@est.com', 70, 80
        )
    """)
    cur.execute("SELECT MAX(id_estudiante) FROM ESTUDIANTE")
    id_estudiante = cur.fetchone()[0]

    # ========== HISTORICO_AULA_ESTUDIANTE ==========
    cur.execute("""
        INSERT INTO HISTORICO_AULA_ESTUDIANTE (id_estudiante, id_aula, fecha_inicio)
        VALUES (:1, :2, DATE '2025-02-01')
    """, [id_estudiante, id_aula])

    # ========== MOTIVO / SEMANA / FESTIVO ==========
    cur.execute("INSERT INTO MOTIVO_INASISTENCIA (descripcion) VALUES ('Enfermedad')")
    cur.execute("SELECT MAX(id_motivo) FROM MOTIVO_INASISTENCIA")
    id_motivo = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO SEMANA (numero_semana, fecha_inicio, fecha_fin)
        VALUES (10, DATE '2025-03-01', DATE '2025-03-07')
    """)
    cur.execute("SELECT MAX(id_semana) FROM SEMANA")
    id_semana = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO FESTIVO (fecha, descripcion)
        VALUES (DATE '2025-03-05', 'Día festivo')
    """)

    # ========== ASISTENCIA_AULA ==========
    cur.execute("""
        INSERT INTO ASISTENCIA_AULA (
            id_aula, id_tutor_aula, id_horario, id_semana, fecha_clase,
            dictada, horas_dictadas, reposicion, fecha_reposicion, id_motivo,
            hora_inicio, hora_fin, corresponde_horario, es_festivo
        ) VALUES (
            :1, :2, :3, :4, DATE '2025-03-03',
            'S', 2, 'N', NULL, :5,
            '08:00', '10:00', 1, 0
        )
    """, [id_aula, id_tutor_aula, id_horario, id_semana, id_motivo])

    # ========== ASISTENCIA_ESTUDIANTE ==========
    cur.execute("SELECT MAX(id_asist) FROM ASISTENCIA_AULA")
    id_asist = cur.fetchone()[0]
    cur.execute("""
        INSERT INTO ASISTENCIA_ESTUDIANTE (id_asist, id_estudiante, asistio, observacion)
        VALUES (:1, :2, 'S', 'Presente')
    """, [id_asist, id_estudiante])

    # ========== PERIODO / COMPONENTE / NOTA_ESTUDIANTE ==========
    cur.execute("""
        INSERT INTO PERIODO (nombre, fecha_inicio, fecha_fin)
        VALUES ('Primer Periodo', DATE '2025-01-15', DATE '2025-06-15')
    """)
    cur.execute("SELECT MAX(id_periodo) FROM PERIODO")
    id_periodo = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO COMPONENTE (nombre, porcentaje, tipo_programa, id_periodo)
        VALUES ('Matemáticas', 50, 'Académico', :1)
    """, [id_periodo])
    cur.execute("SELECT MAX(id_componente) FROM COMPONENTE")
    id_componente = cur.fetchone()[0]

    cur.execute("""
        INSERT INTO NOTA_ESTUDIANTE (id_estudiante, id_componente, nota)
        VALUES (:1, :2, 4.7)
    """, [id_estudiante, id_componente])

    conn.commit()
    cur.close()
    conn.close()
    print("Datos insertados correctamente.")


if __name__ == "__main__":
    insertar_datos()
