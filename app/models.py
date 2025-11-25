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
    id_sede: int                       # se puede ignorar en el backend si se autogenera
    direccion: Optional[str] = None
    es_principal: Optional[str] = 'N'

class SedeOut(SedeIn):
    pass    # id_sede ya viene de SedeIn


# ============================
# PERSONA
# ============================

class PersonaIn(BaseModel):
    tipo_doc: Optional[str]
    nombre: str
    telefono: Optional[str]
    correo: Optional[str]
    rol: Optional[str]

class PersonaOut(PersonaIn):
    id_persona: int


# ============================
# AULA
# ============================

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


# ============================
# USUARIO
# ============================

class UsuarioIn(BaseModel):
    nombre_user: str
    contrasena: str
    id_persona: int

class UsuarioOut(BaseModel):
    nombre_user: str
    correo: str
    nombre: str
    rol: str
    id_persona: int

class AsignarHorarioAulaIn(BaseModel):
    id_aula: int
    id_horario: int
    fecha_inicio: Optional[str] = None  # formato "YYYY-MM-DD" desde el front

class AsignarTutorAulaIn(BaseModel):
    id_aula: int
    id_persona: int
    fecha_inicio: Optional[str] = None  # "YYYY-MM-DD"
    motivo_cambio: Optional[str] = None