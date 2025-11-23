# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from app.models import InstitucionIn, InstitucionOut, PersonaIn, PersonaOut, AulaIn, AulaOut, EstudianteIn, EstudianteOut
import app.crud as crud
import app.reports as reports
from app.auth import create_token, require_role
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Permitir llamadas desde el frontend React (por defecto en localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambia el puerto si tu React usa otro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Instituciones
@app.post("/instituciones", response_model=InstitucionOut)
def create_institucion(payload: InstitucionIn):
    id_inst = crud.create_institucion(payload.dict())
    if not id_inst:
        raise HTTPException(status_code=400, detail="No se pudo crear institución")
    out = crud.get_institucion(id_inst)
    return out

@app.get("/instituciones")
def list_instituciones():
    return crud.list_instituciones()

@app.get("/instituciones/{id_inst}")
def get_institucion(id_inst: int):
    inst = crud.get_institucion(id_inst)
    if not inst:
        raise HTTPException(status_code=404, detail="No encontrada")
    return inst

# Personas (ejemplo)
@app.post("/personas", response_model=PersonaOut)
def create_persona(payload: PersonaIn):
    pid = crud.create_persona(payload.dict())
    if not pid:
        raise HTTPException(status_code=400, detail="No se pudo crear persona")
    return {"id_persona": pid, **payload.dict()}

@app.get("/personas")
def list_personas():
    return crud.list_personas()

# Aulas (ejemplo)
@app.post("/aulas", response_model=AulaOut)
def create_aula(payload: AulaIn):
    # simplified creation
    conn = crud.get_conn = None
    # direct SQL for brevity
    import app.db as dbmod
    conn = dbmod.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO AULA(id_institucion, id_sede, grado) VALUES(:1,:2,:3)", (payload.id_institucion, payload.id_sede, payload.grado))
        conn.commit()
        cur.execute("SELECT id_aula FROM AULA WHERE rownum=1 ORDER BY id_aula DESC")
        r = cur.fetchone()
        return {"id_aula": r[0], **payload.dict()}
    finally:
        cur.close()
        conn.close()

# Estudiantes
@app.post("/estudiantes", response_model=EstudianteOut)
def create_estudiante(payload: EstudianteIn):
    import app.db as dbmod
    conn = dbmod.get_conn(); cur = conn.cursor()
    try:
        cur.execute("""INSERT INTO ESTUDIANTE(tipo_documento, num_documento, nombres, apellidos, telefono, fecha_nacimiento, correo, score_entrada)
                       VALUES(:1,:2,:3,:4,:5,:6,:7,:8)""",
                    (payload.tipo_documento, payload.num_documento, payload.nombres, payload.apellidos, payload.telefono, payload.fecha_nacimiento, payload.correo, payload.score_entrada))
        conn.commit()
        cur.execute("SELECT id_estudiante FROM ESTUDIANTE WHERE num_documento = :1 ORDER BY id_estudiante DESC", (payload.num_documento,))
        r = cur.fetchone()
        return {"id_estudiante": r[0], **payload.dict()}
    finally:
        cur.close(); conn.close()

# Reports
@app.get("/reportes/aula/{id_aula}/asistencia")
def reporte_aula(id_aula: int, id_semana: int = None):
    return reports.reporte_asistencia_aula(id_aula, id_semana)

from pydantic import BaseModel

class LoginIn(BaseModel):
    correo: str
    contrasena: str

@app.post("/login")
def login(payload: LoginIn):
    print("****** LOGIN ENDPOINT CALLED ******")
    print("LOGIN DATA:", payload)
    try:
        conn = crud.get_conn()
        cur = conn.cursor()
        print("Buscando correo:", repr(payload.correo))

        cur.execute("""
            SELECT u.contrasena, p.rol, u.nombre_user
            FROM USUARIO u JOIN PERSONA p ON u.id_persona = p.id_persona
            WHERE TRIM(LOWER(p.correo)) = TRIM(LOWER(:1))
        """, (payload.correo.strip().lower(),))

        result = cur.fetchone()
        print("DB QUERY RESULT:", result)
        if not result:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        db_pass, rol, nombre_user = result
        if db_pass != payload.contrasena:
            raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
        token = create_token({"correo": payload.correo, "rol": rol, "nombre_user": nombre_user})
        
        # 🚩 Devuelve token, rol y nombre_user (opcional para el frontend)
        return {
            "ftoken": token,       # puedes cambiar a "token" si prefieres, igual que antes
            "rol": rol,
            "nombre_user": nombre_user
        }
    except Exception as e:
        print("ERROR EN LOGIN:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        try:
            cur.close()
            conn.close()
        except:
            pass


@app.get("/test-db-status")
def test_db_status():
    import app.db as dbmod
    conn = dbmod.get_conn()
    cur = conn.cursor()
    info = {}

    # Usuario conectado
    cur.execute("SELECT USER FROM DUAL")
    info["usuario_conectado"] = cur.fetchone()[0]

    # Tablas accesibles
    cur.execute("SELECT TABLE_NAME FROM USER_TABLES")
    info["tablas_visibles"] = [row[0] for row in cur.fetchall()]

    # Registros crudos en USUARIO
    cur.execute("SELECT * FROM USUARIO")
    usuarios = cur.fetchall()
    info["registros_usuario"] = usuarios

    cur.close()
    conn.close()
    return info

