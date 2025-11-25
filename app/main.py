# app/main.py
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models import (
    InstitucionIn, InstitucionOut,
    PersonaIn, PersonaOut,
    AulaIn, AulaOut,
    EstudianteIn, EstudianteOut,
    SedeIn, SedeOut,
    UsuarioIn, UsuarioOut,
    HorarioIn, HorarioOut,
    AsignarHorarioAulaIn,
    AsignarTutorAulaIn
)
import app.crud as crud
import app.reports as reports
from app.auth import create_token, require_role
from pydantic import BaseModel

app = FastAPI()

# CORS para React
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# INSTITUCIONES
# ============================

@app.post("/instituciones", response_model=InstitucionOut)
def create_institucion(payload: InstitucionIn):
    id_inst = crud.create_institucion(payload.dict())
    if not id_inst:
        raise HTTPException(status_code=400, detail="No se pudo crear institución")

    # Crear sede principal automática
    try:
        crud.create_sede({
            "id_institucion": id_inst,
            "direccion": payload.dir_principal,
            "es_principal": "S"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"No se pudo crear la sede inicial: {e}")

    return crud.get_institucion(id_inst)


@app.get("/instituciones")
def list_instituciones():
    return crud.list_instituciones()


@app.get("/instituciones/{id_inst}")
def get_institucion(id_inst: int):
    inst = crud.get_institucion(id_inst)
    if not inst:
        raise HTTPException(status_code=404, detail="No encontrada")
    return inst


@app.delete("/instituciones/{id_inst}")
def delete_institucion(id_inst: int):
    crud.delete_institucion(id_inst)
    return {"ok": True}


@app.put("/instituciones/{id_inst}", response_model=InstitucionOut)
def update_institucion(id_inst: int, payload: InstitucionIn):
    crud.update_institucion(id_inst, payload.dict())
    inst = crud.get_institucion(id_inst)
    if not inst:
        raise HTTPException(status_code=404, detail="No encontrada")
    return inst


# ============================
# SEDES
# ============================

@app.post("/sedes", response_model=SedeOut)
def create_sede(payload: SedeIn):
    id_sede = crud.create_sede(payload.dict())
    if not id_sede:
        raise HTTPException(status_code=400, detail="No se pudo crear sede")
    out = crud.get_sede(payload.id_institucion, id_sede)
    return out


@app.get("/sedes")
def list_sedes():
    return crud.list_sedes()


@app.get("/sedes/{id_institucion}/{id_sede}")
def get_sede(id_institucion: int, id_sede: int):
    sede = crud.get_sede(id_institucion, id_sede)
    if not sede:
        raise HTTPException(status_code=404, detail="No encontrada")
    return sede


@app.delete("/sedes/{id_institucion}/{id_sede}")
def delete_sede(id_institucion: int, id_sede: int):
    crud.delete_sede(id_institucion, id_sede)
    return {"ok": True}


@app.put("/sedes/{id_institucion}/{id_sede}", response_model=SedeOut)
def update_sede(id_institucion: int, id_sede: int, payload: SedeIn):
    crud.update_sede(id_institucion, id_sede, payload.dict())
    sede = crud.get_sede(id_institucion, id_sede)
    if not sede:
        raise HTTPException(status_code=404, detail="No encontrada")
    return sede


# ============================
# PERSONAS
# ============================

@app.post("/personas", response_model=PersonaOut)
def create_persona(payload: PersonaIn):
    pid = crud.create_persona(payload.dict())
    if not pid:
        raise HTTPException(status_code=400, detail="No se pudo crear persona")
    return {"id_persona": pid, **payload.dict()}


@app.get("/personas")
def list_personas():
    return crud.list_personas()


# ============================
# USUARIOS
# ============================

@app.post("/usuarios")
def create_usuario(payload: UsuarioIn):
    try:
        crud.create_usuario(payload.dict())
        return {
            "nombre_user": payload.nombre_user,
            "clave_generada": payload.contrasena,
            "id_persona": payload.id_persona
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/usuarios")
def list_usuarios():
    return crud.list_usuarios()


# ============================
# AULAS
# ============================

@app.get("/aulas")
def list_aulas():
    return crud.list_aulas()


@app.post("/aulas", response_model=AulaOut)
def create_aula(payload: AulaIn):
    id_aula = crud.create_aula(payload.dict())
    return {"id_aula": id_aula, **payload.dict()}


@app.put("/aulas/{id_aula}", response_model=AulaOut)
def update_aula(id_aula: int, payload: AulaIn):
    crud.update_aula(id_aula, payload.dict())
    aula = crud.get_aula(id_aula)
    if not aula:
        raise HTTPException(status_code=404, detail="Aula no encontrada")
    return aula


@app.delete("/aulas/{id_aula}")
def delete_aula(id_aula: int):
    crud.delete_aula(id_aula)
    return {"ok": True}


# ============================
# ESTUDIANTES
# ============================

@app.post("/estudiantes", response_model=EstudianteOut)
def create_estudiante(payload: EstudianteIn):
    import app.db as dbmod
    conn = dbmod.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO ESTUDIANTE(
                tipo_documento, num_documento, nombres, apellidos,
                telefono, fecha_nacimiento, correo, score_entrada
            )
            VALUES(:1,:2,:3,:4,:5,:6,:7,:8)
        """, (
            payload.tipo_documento,
            payload.num_documento,
            payload.nombres,
            payload.apellidos,
            payload.telefono,
            payload.fecha_nacimiento,
            payload.correo,
            payload.score_entrada
        ))
        conn.commit()
        cur.execute("""
            SELECT id_estudiante
            FROM ESTUDIANTE
            WHERE num_documento = :1
            ORDER BY id_estudiante DESC
        """, (payload.num_documento,))
        r = cur.fetchone()
        return {"id_estudiante": r[0], **payload.dict()}
    finally:
        cur.close()
        conn.close()


# ============================
# REPORTES
# ============================

@app.get("/reportes/aula/{id_aula}/asistencia")
def reporte_aula(id_aula: int, id_semana: int = None):
    return reports.reporte_asistencia_aula(id_aula, id_semana)


# ============================
# LOGIN
# ============================

class LoginIn(BaseModel):
    correo: str
    contrasena: str

@app.post("/login")
def login(payload: LoginIn):
    print("****** LOGIN ENDPOINT CALLED ******")
    print("LOGIN DATA:", payload)
    try:
        conn = crud.get_conn()  # OJO: aquí podrías cambiar a app.db.get_conn()
        cur = conn.cursor()
        print("Buscando correo:", repr(payload.correo))

        cur.execute("""
            SELECT u.contrasena, p.rol, u.nombre_user
            FROM USUARIO u
            JOIN PERSONA p ON u.id_persona = p.id_persona
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
        print("Rol encontrado en base:", rol)

        return {
            "ftoken": token,
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


# ============================
# TEST DB
# ============================

@app.get("/test-db-status")
def test_db_status():
    import app.db as dbmod
    conn = dbmod.get_conn()
    cur = conn.cursor()
    info = {}

    cur.execute("SELECT USER FROM DUAL")
    info["usuario_conectado"] = cur.fetchone()[0]

    cur.execute("SELECT TABLE_NAME FROM USER_TABLES")
    info["tablas_visibles"] = [row[0] for row in cur.fetchall()]

    cur.execute("SELECT * FROM USUARIO")
    usuarios = cur.fetchall()
    info["registros_usuario"] = usuarios

    cur.close()
    conn.close()
    return info


# ============================
# HORARIOS
# ============================

@app.get("/horarios")
def list_horarios():
    return crud.list_horarios()


@app.post("/horarios", response_model=HorarioOut)
def create_horario(payload: HorarioIn):
    data = payload.dict()
    id_horario = crud.create_horario(data)
    return {
        "id_horario": id_horario,
        **payload.dict()
    }


@app.delete("/horarios/{id_horario}")
def delete_horario(id_horario: int):
    try:
        crud.delete_horario(id_horario)
        return {"ok": True}
    except Exception as e:
        # Esto lo verá el frontend si intenta borrar uno aún activo
        raise HTTPException(status_code=400, detail=str(e))


# ============================
# ASIGNAR HORARIO A AULA + HISTÓRICO
# ============================

@app.post("/asignar-horario-aula")
def asignar_horario_aula(payload: AsignarHorarioAulaIn):
    """
    Body: { "id_aula": int, "id_horario": int, "fecha_inicio": "YYYY-MM-DD" (opcional) }
    """
    try:
        new_id = crud.asignar_horario_a_aula(payload.dict())
        return {"msg": f"Horario asignado correctamente (historial #{new_id})"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/historial-horarios-aula/{id_aula}")
def historial_horarios_aula(id_aula: int):
    return crud.get_historial_horarios_aula(id_aula)

@app.put("/historial-horarios-aula/{id_hist_horario}/fin")
def finalizar_historial(id_hist_horario: int, fecha_fin: Optional[str] = Query(None)):
    """
    Marca un registro del historial como finalizado.
    Si no se pasa fecha_fin, se usa la fecha actual (SYSDATE).
    """
    try:
        crud.finalizar_historial_horario(id_hist_horario, fecha_fin)
        return {"msg": "Horario marcado como finalizado"}
    except Exception as e:
        # Si por ejemplo no había un histórico activo con ese ID, se verá aquí
        raise HTTPException(status_code=400, detail=str(e))
    
# ============================
# ASIGNAR TUTOR A AULA + HISTÓRICO
# ============================

@app.post("/asignar-tutor-aula")
def asignar_tutor_aula(payload: AsignarTutorAulaIn):
    try:
        new_id = crud.asignar_tutor_a_aula(payload.dict())
        return {"msg": f"Tutor asignado correctamente (registro #{new_id})"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/historial-tutores-aula/{id_aula}")
def historial_tutores_aula(id_aula: int):
    return crud.get_historial_tutores_aula(id_aula)

@app.put("/asignacion-tutor/{id_tutor_aula}/fin")
def finalizar_asignacion_tutor_endpoint(
    id_tutor_aula: int,
    fecha_fin: Optional[str] = Query(None)
):
    """
    Finaliza una asignación (pone FECHA_FIN).
    Si no se pasa fecha_fin, usa la fecha actual.
    """
    try:
        crud.finalizar_asignacion_tutor(id_tutor_aula, fecha_fin)
        return {"msg": "Asignación de tutor finalizada"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/asignacion-tutor/{id_tutor_aula}")
def delete_asignacion_tutor_endpoint(id_tutor_aula: int):
    try:
        crud.delete_asignacion_tutor(id_tutor_aula)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))