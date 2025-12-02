from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app import models
from app.auth import (
    create_token,
    get_current_user,
    requires_role,
    get_person_id_to_act_on
)
from app import crud

app = FastAPI(
    title="Sistema Programa Niños y Jóvenes Globales",
    description="Backend oficial del proyecto académico basado en FastAPI",
    version="1.0"
)

# =====================================================
# CORS CONFIG (IMPORTANTE PARA QUE EL FRONT SE CONECTE)
# =====================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
#   ENDPOINTS DE AUTENTICACIÓN
# =====================================================

@app.post("/login")
def login(data: models.UsuarioLogin):
    usuario = crud.login(data.nombre_user, data.contrasena)

    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos.")

    token = create_token({
        "id_usuario": usuario["id_usuario"],
        "id_persona": usuario["id_persona"],
        "rol": usuario["rol"]
    })

    return {"token": token, "rol": usuario["rol"]}


# =====================================================
#   ENDPOINTS ROLES (solo ADMINISTRADOR)
# =====================================================

@app.post("/roles", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def crear_rol(data: models.RolBase):
    return crud.crear_rol(data)


@app.get("/roles", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def listar_roles():
    return crud.listar_roles()


# =====================================================
#   TIPOS DE DOCUMENTO (ADMINISTRADOR)
# =====================================================

@app.post("/tipo-documento", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def crear_tipo_doc(data: models.TipoDocumentoBase):
    return crud.crear_tipo_documento(data)


@app.get("/tipo-documento", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def listar_tipo_doc():
    return crud.listar_tipo_documento()


# =====================================================
#    PERSONA — Crear/Actualizar (ADMINISTRATIVO + ADMIN)
# =====================================================

@app.post("/persona", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def crear_persona(data: models.PersonaCreate):
    return crud.crear_persona(data)


@app.put("/persona/{id_persona}", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def actualizar_persona(id_persona: int, data: models.PersonaUpdate):
    return crud.actualizar_persona(id_persona, data)


@app.get("/persona/{id_persona}")
def obtener_persona(id_persona: int):
    return crud.obtener_persona(id_persona)


# =====================================================
#    USUARIOS (ADMINISTRADOR)
# =====================================================

@app.post("/usuario", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def crear_usuario(data: models.UsuarioCreate):
    return crud.crear_usuario(data)


@app.get("/usuario/{id_usuario}", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def obtener_usuario(id_usuario: int):
    return crud.obtener_usuario(id_usuario)


# =====================================================
#    INSTITUCIONES (ADMINISTRATIVO + ADMINISTRADOR)
# =====================================================

@app.post("/institucion", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def crear_institucion(data: models.InstitucionCreate):
    return crud.crear_institucion(data)


@app.get("/institucion", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def listar_instituciones():
    return crud.listar_instituciones()


# =====================================================
#   SEDE (ADMINISTRATIVO + ADMIN)
# =====================================================

@app.post("/sede", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def crear_sede(data: models.SedeCreate):
    return crud.crear_sede(data)


@app.put("/sede/{id_sede}/{id_institucion}", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def actualizar_sede(id_sede: int, id_institucion: int, data: models.SedeUpdate):
    return crud.actualizar_sede(id_sede, id_institucion, data)


@app.get("/sede/{id_institucion}")
def listar_sedes(id_institucion: int):
    return crud.listar_sedes(id_institucion)


# =====================================================
#   AULA (ADMINISTRATIVO + ADMIN)
# =====================================================

@app.post("/aula", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def crear_aula(data: models.AulaCreate):
    return crud.crear_aula(data)


@app.get("/aula/{id_institucion}")
def listar_aulas(id_institucion: int):
    return crud.listar_aulas(id_institucion)


# =====================================================
#   HORARIOS (ADMINISTRATIVO + ADMIN)
# =====================================================

@app.post("/horario", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def crear_horario(data: models.HorarioCreate):
    return crud.crear_horario(data)


@app.post("/horario/asignar", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def asignar_horario(data: models.AsignarHorarioAula):
    return crud.asignar_horario(data)


# =====================================================
#   ASIGNAR TUTOR A AULA (ADMINISTRATIVO + ADMIN)
# =====================================================

@app.post("/tutor/asignar", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def asignar_tutor(data: models.TutorAulaAssign):
    return crud.asignar_tutor_aula(data)


@app.post("/tutor/desasignar", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def remover_tutor(data: models.TutorAulaUnassign):
    return crud.remover_tutor_de_aula(data)


# =====================================================
#   ESTUDIANTES (ADMINISTRATIVO + ADMIN)
# =====================================================

@app.post("/estudiante", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def crear_estudiante(data: models.EstudianteIn):
    return crud.crear_estudiante(data)


@app.post("/estudiante/ingresar", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def ingresar_estudiante_aula(data: models.HistoricoAulaEstudianteIn):
    return crud.ingresar_estudiante_aula(data)


@app.post("/estudiante/mover", dependencies=[Depends(requires_role(["ADMINISTRATIVO"]))])
def mover_estudiante(data: models.CambioEstudianteAulaIn):
    return crud.mover_estudiante(data)


# =====================================================
#   ASISTENCIA DEL TUTOR (TUTOR o ADMINISTRATIVO con delegación)
# =====================================================

@app.post("/asistencia/registrar")
def registrar_asistencia(
    data: models.AsistenciaAulaBase,
    user=Depends(requires_role(["TUTOR"])),
    id_actor=Depends(get_person_id_to_act_on)
):
    return crud.registrar_asistencia(data, id_actor)


# =====================================================
#   REGISTRO DE NOTAS (TUTOR o ADMINISTRATIVO con delegación)
# =====================================================

@app.post("/notas/registrar")
def registrar_nota(
    data: models.RegistrarNotaIn,
    user=Depends(requires_role(["TUTOR"])),
    id_actor=Depends(get_person_id_to_act_on)
):
    return crud.registrar_nota(data, id_actor)


# =====================================================
#   REPORTES (TUTOR o ADMINISTRATIVO con delegación)
# =====================================================

@app.get("/reportes/asistencia")
def reporte_asistencia(
    fecha_inicio: str,
    fecha_fin: str,
    user=Depends(requires_role(["TUTOR"])),
    id_actor=Depends(get_person_id_to_act_on)
):
    return crud.reporte_asistencia(id_actor, fecha_inicio, fecha_fin)


@app.get("/reportes/notas")
def reporte_notas(
    user=Depends(requires_role(["TUTOR"])),
    id_actor=Depends(get_person_id_to_act_on)
):
    return crud.reporte_notas(id_actor)


# =====================================================
#   CALENDARIO DE SEMANAS (ADMINISTRADOR)
# =====================================================

@app.post("/semanas", dependencies=[Depends(requires_role(["ADMINISTRADOR"]))])
def crear_semana(data: models.SemanaCreate):
    return crud.crear_semana(data) este es el main 
