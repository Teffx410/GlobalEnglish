# app/main.py
from fastapi import FastAPI, HTTPException, Depends
from app.models import InstitucionIn, InstitucionOut, PersonaIn, PersonaOut, AulaIn, AulaOut, EstudianteIn, EstudianteOut
import app.crud as crud
import app.reports as reports
from app.auth import create_token, require_role

app = FastAPI(title="GlobalEnglish API")

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
