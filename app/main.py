# app/main.py
from fastapi import FastAPI, HTTPException, Depends, Query, Body
from app.models import InstitucionIn, InstitucionOut, PersonaIn,  UsuarioIn, PersonaOut, AulaIn, AulaOut, EstudianteIn, EstudianteOut, SedeIn, SedeOut, HistoricoAulaEstudianteIn, CambioEstudianteAulaIn, HorarioIn, HorarioOut, AsignarHorarioAulaIn, CambiarTutorAulaIn, AsignarTutorAulaIn, PeriodoIn, ComponenteIn, AsistenciaAulaIn, RegistrarNotaIn, RegistrarAsistenciaEstudianteIn
import app.crud as crud
import app.reports as reports
from app.auth import create_token, require_role
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional


app = FastAPI()

# Permitir llamadas desde el frontend React (por defecto en localhost:3000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Cambia el puerto si tu React usa otro
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================
# INSTITUCION
# ============================
@app.post("/instituciones", response_model=InstitucionOut)
def create_institucion(payload: InstitucionIn):
    result = crud.create_institucion(payload.dict())

    if not result or "error" in result:
        detalle = result.get("error") if isinstance(result, dict) else "No se pudo crear institución"
        raise HTTPException(status_code=400, detail=detalle)

    # Obtener id_institucion
    id_inst = result.get("id_institucion")
    if not id_inst:
        raise HTTPException(status_code=400, detail="No se pudo obtener el ID de la institución creada")

    # Validar que venga la dirección principal en el payload
    if not payload.dir_principal:
        raise HTTPException(status_code=400, detail="La dirección principal (dir_principal) es obligatoria")

    # Crear sede principal automática
    try:
        sede_result = crud.create_sede({
            "id_institucion": id_inst,
            "direccion": payload.dir_principal,
            "es_principal": "S"
        })

        if isinstance(sede_result, dict) and "error" in sede_result:
            raise HTTPException(status_code=400, detail=f"No se pudo crear la sede principal: {sede_result['error']}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail="No se pudo crear la sede principal")

    out = crud.get_institucion(id_inst)
    if not out:
        raise HTTPException(status_code=500, detail="No se pudo recuperar la institución creada")

    return out

@app.get("/instituciones")
def list_instituciones():
    return crud.list_instituciones()

@app.get("/instituciones/{id_inst}")
def get_institucion(id_inst: int):
    inst = crud.get_institucion(id_inst)
    if not inst:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    return inst

@app.delete("/instituciones/{id_inst}")
def delete_institucion(id_inst: int):
    result = crud.delete_institucion(id_inst)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"ok": True, "msg": result.get("msg", "Institución eliminada")}


@app.put("/instituciones/{id_inst}", response_model=InstitucionOut)
def update_institucion(id_inst: int, payload: InstitucionIn):
    # Validar que la institución exista
    inst_existente = crud.get_institucion(id_inst)
    if not inst_existente:
        raise HTTPException(status_code=404, detail="Institución no encontrada")
    
    # Actualizar
    result = crud.update_institucion(id_inst, payload.dict())
    
    # Validar si hay error
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Obtener la institución actualizada
    inst = crud.get_institucion(id_inst)
    if not inst:
        raise HTTPException(status_code=500, detail="No se pudo recuperar institución")
    
    return inst

# ============================
# SEDE
# ============================

@app.post("/sedes")
def create_sede(payload: SedeIn):
    result = crud.create_sede(payload.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    if "id_sede" in result:
        out = crud.get_sede(result["id_sede"])
        if out:
            return out
    
    raise HTTPException(status_code=400, detail="No se pudo crear sede")

@app.get("/sedes")
def list_sedes():
    return crud.list_sedes()

@app.get("/sedes/{id_sede}")
def get_sede(id_sede: int):
    sede = crud.get_sede(id_sede)
    if not sede:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    return sede

@app.delete("/sedes/{id_institucion}/{id_sede}")
def delete_sede(id_institucion: int, id_sede: int):
    result = crud.delete_sede(id_institucion, id_sede)
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"ok": True, "msg": result.get("msg", "Sede eliminada")}

@app.put("/sedes/{id_sede}")
def update_sede(id_sede: int, payload: SedeIn):
    # Validar que la sede exista
    sede_existente = crud.get_sede(id_sede)
    if not sede_existente:
        raise HTTPException(status_code=404, detail="Sede no encontrada")
    
    # Actualizar
    result = crud.update_sede(id_sede, payload.dict())
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # Obtener la sede actualizada
    sede = crud.get_sede(id_sede)
    if not sede:
        raise HTTPException(status_code=500, detail="No se pudo recuperar sede")
    
    return sede

# ============================
# PERSONA
# ============================

@app.post("/personas", response_model=PersonaOut)
def create_persona(payload: PersonaIn):
    result = crud.create_persona(payload.dict())
    
    # Verificar si hubo error
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    # result es el id_persona
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo crear persona")
    
    # Retornar la estructura correcta: PersonaOut (que incluye id_persona + todos los campos de PersonaIn)
    return {
        "id_persona": result,
        "tipo_doc": payload.tipo_doc,
        "num_documento": payload.num_documento,
        "nombre": payload.nombre,
        "telefono": payload.telefono,
        "correo": payload.correo,
        "rol": payload.rol
    }

@app.get("/personas")
def list_personas():
    return crud.list_personas()

@app.put("/personas/{id_persona}")
def update_persona_endpoint(id_persona: int, payload: PersonaIn):
    result = crud.update_persona(id_persona, payload.dict())
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"ok": True, "message": "Persona actualizada correctamente"}

@app.delete("/personas/{id_persona}")
def delete_persona_endpoint(id_persona: int):
    result = crud.delete_persona(id_persona)
    
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    
    return {"ok": True, "message": "Persona eliminada correctamente"}

# ============================
# USUARIO
# ============================

@app.post("/usuarios")
def crear_usuario(payload: UsuarioIn):
    nombre_user, clave, correo = crud.create_usuario(payload.dict())
    return {
        "nombre_user": nombre_user,
        "correo": correo,
        "clave_generada": clave
    }

@app.get("/usuarios")
def listar_usuarios():
    return crud.list_usuarios()

# ============================
# AULAS
# ============================

@app.post("/aulas", response_model=AulaOut)
def create_aula(payload: AulaIn):
    id_aula = crud.create_aula(payload.dict())
    if not id_aula:
        raise HTTPException(status_code=400, detail="No se pudo crear aula")
    out = crud.get_aula(id_aula)
    return out

@app.get("/aulas")
def list_aulas():
    return crud.list_aulas()

@app.get("/aulas/{id_aula}")
def get_aula(id_aula: int):
    aula = crud.get_aula(id_aula)
    if not aula:
        raise HTTPException(status_code=404, detail="No encontrada")
    return aula

@app.delete("/aulas/{id_aula}")
def delete_aula(id_aula: int):
    crud.delete_aula(id_aula)
    return {"ok": True}

@app.put("/aulas/{id_aula}", response_model=AulaOut)
def update_aula(id_aula: int, payload: AulaIn):
    crud.update_aula(id_aula, payload.dict())
    aula = crud.get_aula(id_aula)
    if not aula:
        raise HTTPException(status_code=404, detail="No encontrada")
    return aula

# ============================
# HORARIOS
# ============================

dias_primaria = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
dias_secundaria = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"]
minutos_validos = [40, 45, 50, 55, 60]

# Validación básica para ejemplo, extiéndela según tu flujo
def validar_horario(data, grado="4", jornada_institucion="MAÑANA"):
    if grado in ["4", "5"]:
        if data['dia_semana'] not in dias_primaria:
            raise HTTPException(status_code=400, detail="Solo lunes-viernes para 4º/5º")
        if not ("06:00" <= data['h_inicio'] <= "18:00"):
            raise HTTPException(status_code=400, detail="Fuera de 06:00-18:00")
        if data['minutos_equiv'] not in minutos_validos:
            raise HTTPException(status_code=400, detail="Minutos equivocados")
    elif grado in ["9", "10"]:
        if data['dia_semana'] not in dias_secundaria:
            raise HTTPException(status_code=400, detail="Solo lunes-sábado para 9º/10º")
        if data['minutos_equiv'] not in minutos_validos:
            raise HTTPException(status_code=400, detail="Minutos equivocados")

@app.post("/horarios")
def crear_horario(payload: HorarioIn):
    # Validación básica formato/time, pero NO restringir días/franja por grado aquí
    try:
        h_inicio = payload.h_inicio
        h_final = payload.h_final
        if h_inicio >= h_final:
            raise HTTPException(status_code=400, detail="Hora de inicio debe ser menor que fin")
        id_horario = crud.create_horario(payload.dict())
        return {"id_horario": id_horario}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/horarios")
def listar_horarios():
    return crud.list_horarios()

@app.delete("/horarios/{id_horario}")
def eliminar_horario(id_horario: int):
    crud.delete_horario(id_horario)
    return {"ok": True}


# ============================
# ASIGNAR HORARIO A AULA + HISTÓRICO
# ============================

@app.post("/asignar-horario-aula")
def asignar_horario_aula(payload: AsignarHorarioAulaIn):
    result = crud.asignar_horario_aula(payload.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/historial-horarios-aula/{id_aula}")
def historial_horarios_aula(id_aula: int):
    return crud.list_horarios_aula(id_aula)


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


@app.put("/asignacion-tutor/{id_tutor_aula}/fin")
def finalizar_asignacion_tutor_endpoint(
    id_tutor_aula: int,
    fecha_fin: Optional[str] = Query(None),
    motivo_cambio: Optional[str] = Query(None),
):
    crud.finalizar_asignacion_tutor(id_tutor_aula, fecha_fin, motivo_cambio)
    return {"msg": "Asignación de tutor finalizada"}

@app.delete("/asignacion-tutor/{id_tutor_aula}")
def delete_asignacion_tutor_endpoint(id_tutor_aula: int):
    try:
        crud.delete_asignacion_tutor(id_tutor_aula)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.post("/asignar-tutor-aula")
def asignar_tutor_aula(payload: AsignarTutorAulaIn):
    result = crud.asignar_tutor_aula(payload.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/historial-tutores-aula/{id_aula}")
def historial_tutores_aula(id_aula: int):
    return crud.list_tutores_aula(id_aula)

@app.post("/cambiar-tutor-aula")
def cambiar_tutor_aula_endpoint(payload: CambiarTutorAulaIn):
    result = crud.cambiar_tutor_aula(payload.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# ============================
# HISTÓRICO AULA ESTUDIANTE
# ============================

@app.post("/asignar-estudiante-aula")
def asignar_estudiante_aula_endpoint(payload: HistoricoAulaEstudianteIn):
    result = crud.asignar_estudiante_aula(payload.dict())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/estudiantes-aula/{id_aula}")
def estudiantes_aula(id_aula: int):
    return crud.listar_estudiantes_de_aula(id_aula)

@app.put("/hist-aula-estudiante/{id_hist_aula_est}/fin")
def finalizar_asignacion_estudiante_endpoint(
    id_hist_aula_est: int,
    fecha_fin: Optional[str] = None,
):
    try:
        crud.finalizar_asignacion_estudiante(id_hist_aula_est, fecha_fin)
        return {"msg": "Asignación de estudiante finalizada."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/cambiar-estudiante-aula")
def cambiar_estudiante_aula_endpoint(payload: CambioEstudianteAulaIn):
    result = crud.cambiar_estudiante_aula(payload.dict())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/estudiantes-disponibles/{id_aula}")
def estudiantes_disponibles(id_aula: int):
    # id_aula se recibe por consistencia, aunque la función no lo use
    return crud.listar_estudiantes_disponibles_para_aula(id_aula)

@app.get("/estudiantes-aula/{id_aula}")
def estudiantes_aula(id_aula: int):
    return crud.listar_estudiantes_de_aula(id_aula)

# ============================
# HORARIOS POR TUTOR
# ============================

@app.get("/horarios-tutor/{id_persona}")
def horarios_tutor(id_persona: int):
    return crud.list_horario_tutor(id_persona)

@app.get("/tutores")
def listar_tutores():
    return crud.listar_tutores()

@app.get("/admin/listar-aulas-tutor")
def listar_aulas_tutor(id_persona: int):
    return crud.listar_aulas_tutor(id_persona)

@app.get("/id-tutor-aula/{id_tutor}/{id_aula}")
def get_id_tutor_aula(id_tutor: int, id_aula: int):
    return crud.get_id_tutor_aula(id_tutor, id_aula)

@app.get("/asistencia/encontrar-horario-semana")
def encontrar_horario_y_semana(id_aula: int, fecha_clase: str, hora_inicio: str):
    return crud.encontrar_horario_y_semana(id_aula, fecha_clase, hora_inicio)

# ============================
# ESTUDIANTES
# ============================

@app.post("/estudiantes", response_model=EstudianteOut)
def create_estudiante(payload: EstudianteIn):
    result = crud.create_estudiante(payload.dict())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    if not result:
        raise HTTPException(status_code=400, detail="No se pudo crear estudiante")
    out = crud.get_estudiante(result)
    return out

@app.put("/estudiantes/{id_est}", response_model=EstudianteOut)
def update_estudiante(id_est: int, payload: EstudianteIn):
    result = crud.update_estudiante(id_est, payload.dict())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    estu = crud.get_estudiante(id_est)
    if not estu:
        raise HTTPException(status_code=404, detail="No encontrado")
    return estu

@app.get("/estudiantes")
def list_estudiantes():
    return crud.list_estudiantes()

@app.get("/estudiantes/{id_est}")
def get_estudiante(id_est: int):
    estu = crud.get_estudiante(id_est)
    if not estu:
        raise HTTPException(status_code=404, detail="No encontrado")
    return estu

@app.delete("/estudiantes/{id_est}")
def delete_estudiante(id_est: int):
    crud.delete_estudiante(id_est)
    return {"ok": True}

# ============================
# PERIODOS
# ============================

@app.post("/periodos")
def crear_periodo(payload: PeriodoIn):
    crud.create_periodo(payload.dict())
    return {"msg": "Periodo registrado."}

@app.get("/periodos")
def listar_periodos():
    return crud.list_periodos()

@app.put("/periodos/{id_periodo}")
def actualizar_periodo(id_periodo: int, payload: PeriodoIn):
    crud.update_periodo(id_periodo, payload.dict())
    return {"msg": "Periodo actualizado."}

@app.delete("/periodos/{id_periodo}")
def eliminar_periodo(id_periodo: int):
    try:
        crud.delete_periodo(id_periodo)
        return {"msg": "Periodo eliminado."}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# ============================
# COMPONENTES
# ============================

@app.get("/componentes")
def listar_componentes():
    return crud.list_componentes()

@app.post("/componentes")
def crear_componente_endpoint(payload: ComponenteIn):
    r = crud.crear_componente(**payload.dict())
    if not r["ok"]:
        raise HTTPException(status_code=400, detail=r["msg"])
    return r

@app.put("/componentes/{id_componente}")
def actualizar_componente_endpoint(id_componente: int, payload: ComponenteIn):
    r = crud.actualizar_componente(id_componente, **payload.dict())
    if not r["ok"]:
        raise HTTPException(status_code=400, detail=r["msg"])
    return r

@app.delete("/componentes/{id_componente}")
def eliminar_componente_endpoint(id_componente: int):
    r = crud.eliminar_componente(id_componente)
    if not r["ok"]:
        raise HTTPException(status_code=400, detail=r["msg"])
    return r

# ============================
# ASISTENCIA AULA
# ============================

@app.post("/asistir-aula")
def asistir_aula(payload: AsistenciaAulaIn):
    result = crud.registrar_asistencia_aula(payload.dict())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.put("/asistir-aula/{id_asist}")
def modificar_asistencia(id_asist: int, payload: AsistenciaAulaIn):
    result = crud.modificar_asistencia_aula(id_asist, payload.dict())
    if isinstance(result, dict) and "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return {"msg": "Asistencia modificada correctamente."}

@app.get("/horarios-aula-activos/{id_aula}")
def horarios_aula_activos(id_aula: int):
    return crud.list_horarios_aula_activos(id_aula)

# ============================
# ASISTENCIA ESTUDIANTE
# ============================

@app.get("/admin/listar-clases-tutor")
def listar_clases_tutor(id_persona: int = Query(...)):
    return crud.listar_clases_tutor(id_persona)

@app.post("/admin/registrar-asistencia-estudiante")
def registrar_asistencia_estudiante(payload: RegistrarAsistenciaEstudianteIn):
    """
    Inserta o actualiza la asistencia de un estudiante para una clase específica.
    """
    r = crud.registrar_asistencia_estudiante(payload.dict())
    if isinstance(r, dict) and r.get("error"):
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail=r["error"])
    return r

@app.get("/admin/listar-asistencia-estudiantes")
def listar_asistencia_estudiantes(id_asist: int):
    """
    Devuelve los estudiantes del aula de esa asistencia, con su marca de asistencia (S/N) y observación.
    """
    return crud.listar_asistencia_estudiantes(id_asist)

@app.get("/admin/listar-asistencia-estudiantes-todas")
def listar_asistencia_estudiantes_todas(id_persona: int):
    """
    Historial plano de asistencia por estudiante para todas las clases
    de un tutor (una fila por estudiante x clase).
    """
    return crud.listar_asistencia_estudiantes_todas(id_persona)

# ============================
# NOTA ESTUDIANTE
# ============================

@app.get("/admin/listar-estudiantes-aula")
def listar_estudiantes_aula(id_aula: int = Query(...)):
    return crud.listar_estudiantes_aula(id_aula)

@app.get("/admin/listar-periodos")
def listar_periodos():
    return crud.listar_periodos()

@app.post("/admin/registrar-nota-estudiante")
def registrar_nota_estudiante(payload: RegistrarNotaIn):
    r = crud.registrar_o_actualizar_nota(
        payload.id_estudiante,
        payload.id_componente,
        payload.nota,
    )
    if not r["ok"]:
        raise HTTPException(status_code=400, detail=r.get("msg", "Error"))
    return r

@app.get("/admin/obtener-nota-estudiante")
def obtener_nota_estudiante(id_estudiante: int, id_componente: int):
    return crud.obtener_nota_estudiante(id_estudiante, id_componente)

@app.get("/admin/listar-componentes-periodo-tipo")
def listar_componentes_periodo_tipo(id_periodo: int, tipo_programa: str):
    return crud.listar_componentes_periodo_tipo(id_periodo, tipo_programa)

@app.get("/admin/listar-aulas-tutor")
def listar_aulas_tutor(id_persona: int = Query(...)):
    return crud.listar_aulas_tutor(id_persona)

# ============================
# CALENDARIO SEMANAS
# ============================

@app.post("/admin/generar-calendario-semanas")
def generar_calendario_semanas(anio: int = Query(..., description="Año a generar")):
    """
    Genera todas las semanas del año especificado, de lunes a domingo.
    El administrador debe usar esta función al iniciar el ciclo académico.
    """
    return crud.generar_calendario_semanas(anio)

@app.get("/admin/listar-semanas")
def endpoint_listar_semanas():
    return crud.listar_semanas()

# ============================
# FESTIVOS
# ============================

@app.post("/admin/agregar-festivo")
def endpoint_agregar_festivo(
    fecha: str = Body(..., embed=True),
    descripcion: str = Body(..., embed=True)
):
    return crud.agregar_festivo(fecha, descripcion)

@app.get("/admin/listar-festivos")
def endpoint_listar_festivos(anio: int = Query(...)):
    return crud.listar_festivos(anio)

# ============================
# MOTIVOS DE INASISTENCIA
# ============================

@app.post("/admin/agregar-motivo-inasistencia")
def agregar_motivo_inasistencia(descripcion: str = Body(..., embed=True)):
    return crud.agregar_motivo_inasistencia(descripcion)

@app.get("/admin/listar-motivos-inasistencia")
def listar_motivos_inasistencia():
    return crud.listar_motivos()

@app.delete("/admin/eliminar-motivo-inasistencia")
def eliminar_motivo_inasistencia(id_motivo: int = Query(...)):
    return crud.eliminar_motivo(id_motivo)

@app.put("/admin/modificar-motivo-inasistencia")
def modificar_motivo_inasistencia(payload: dict = Body(...)):
    return crud.modificar_motivo(payload['id_motivo'], payload['descripcion'])

@app.get("/motivos-inasistencia")
def motivos_inasistencia():
    return crud.get_motivos_inasistencia()

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
        print("Rol encontrado en base:", rol)

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

# ============================
# REPORTES
# ============================

@app.get("/reportes/aula/{id_aula}/asistencia")
def reporte_aula(id_aula: int, id_semana: int = None):
    return reports.reporte_asistencia_aula(id_aula, id_semana)