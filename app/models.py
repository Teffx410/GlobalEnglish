# app/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

# ============================
# INSTITUCION
# ============================

class InstitucionIn(BaseModel):
    nombre_inst: str
    jornada: Optional[str] = None
    dir_principal: Optional[str] = None

class InstitucionOut(InstitucionIn):
    id_institucion: int


# ============================
# SEDE
# ============================

class SedeIn(BaseModel):
    id_institucion: int
<<<<<<< HEAD
=======
    id_sede: int                       # se puede ignorar en el backend si se autogenera
>>>>>>> main
    direccion: Optional[str] = None
    es_principal: Optional[str] = 'N'

class SedeOut(SedeIn):
    id_sede: int


class PersonaIn(BaseModel):
    tipo_doc: str
    num_documento: str
    nombre: str
    telefono: Optional[str] = None
    correo: str
    rol: str


class PersonaOut(PersonaIn):
    id_persona: int

class UsuarioIn(BaseModel):
    nombre_user: str
    id_persona: int
    contrasena: Optional[str] = None

class AulaIn(BaseModel):
    id_institucion: int
    id_sede: int
    grado: str

class AulaOut(AulaIn):
    id_aula: int


# ============================
# HORARIO
# ============================

# ============================
# HORARIO
# ============================

class HorarioIn(BaseModel):
    dia_semana: str
    h_inicio: str       # "HH:MM"
    h_final: str
    minutos_equiv: int = 60
    es_continuo: str = "S"   # "S" o "N"

class HorarioOut(HorarioIn):
    id_horario: int

# ============================
# ESTUDIANTE
# ============================

class EstudianteIn(BaseModel):
    tipo_documento: Optional[str]
    num_documento: str
    nombres: str
    apellidos: Optional[str]
    telefono: Optional[str]
    fecha_nacimiento: Optional[date]
    correo: Optional[str]
    score_entrada: Optional[float] = None
    score_salida: Optional[float] = None

class EstudianteOut(EstudianteIn):
    id_estudiante: int

class HistoricoAulaEstudianteIn(BaseModel):
    id_estudiante: int
    id_aula: int
    fecha_inicio: Optional[date] = None  # Puede usar date.today() en el frontend si lo quieres automático

class HorarioIn(BaseModel):
    dia_semana: str
    h_inicio: str
    h_final: str
    minutos_equiv: Optional[int] = 60
    es_continuo: Optional[str] = "S"

class HorarioOut(HorarioIn):
    id_horario: int

class AsignarHorarioAulaIn(BaseModel):
    id_aula: int
    id_horario: int
    fecha_inicio: str  # formato "YYYY-MM-DD"

class AsignarTutorAulaIn(BaseModel):
    id_persona: int        # id del tutor (de PERSONA)
    id_aula: int
    fecha_inicio: Optional[str] = None
    motivo_cambio: Optional[str] = None

class PeriodoIn(BaseModel):
    nombre: str
    fecha_inicio: str   # formato 'YYYY-MM-DD'
    fecha_fin: str      # formato 'YYYY-MM-DD'

class ComponenteIn(BaseModel):
    nombre: str
    porcentaje: float
    tipo_programa: Optional[str] = None  


class AsistenciaAulaIn(BaseModel):
    id_aula: int
    id_tutor_aula: int
    id_horario: int
    id_semana: int
    fecha_clase: str
    hora_inicio: str
    hora_fin: str = None
    dictada: str
    horas_dictadas: int
    reposicion: str = "N"
    fecha_reposicion: str = None
    id_motivo: int = None
    corresponde_horario: int
    es_festivo: int


class IngresarNotaIn(BaseModel):
    id_aula: int
    id_estudiante: int
    nota: float

class GenerarSemanasRequest(BaseModel):
    anio: int
