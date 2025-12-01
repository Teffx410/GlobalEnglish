# app/models.py

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, time, datetime

# ============================
# INSTITUCION
# ============================

class InstitucionCreate(BaseModel):
    nombre_inst: str
    # Jornadas limitadas a 3 opciones
    jornada: Optional[Literal['MAÑANA', 'TARDE', 'MIXTA']] = 'MIXTA'
    dir_principal: Optional[str] = None

class InstitucionOut(InstitucionCreate):
    id_institucion: int


# ============================
# SEDE
# ============================

class SedeCreate(BaseModel):
    id_institucion: int
    direccion: str
    # 'S' (Principal) o 'N' (No Principal)
    es_principal: Literal['S', 'N'] = 'N'

class SedeUpdate(BaseModel):
    direccion: Optional[str] = None
    es_principal: Optional[Literal['S', 'N']] = None

class SedeOut(SedeCreate):
    id_sede: int


# ============================
# PERSONA / USUARIO
# ============================

class PersonaBase(BaseModel):
    # Tipos de roles restringidos para validación estricta
    rol: Literal['ADMINISTRADOR', 'ADMINISTRATIVO', 'TUTOR']

class PersonaCreate(PersonaBase):
    tipo_doc: Optional[str] = 'CC'
    num_documento: str
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None

class PersonaUpdate(BaseModel):
    tipo_doc: Optional[str] = None
    num_documento: Optional[str] = None
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    rol: Optional[Literal['ADMINISTRADOR', 'ADMINISTRATIVO', 'TUTOR']] = None

class PersonaOut(PersonaCreate):
    id_persona: int


class UsuarioCreate(BaseModel):
    nombre_user: str
    id_persona: int
    contrasena: Optional[str] = None


# ============================
# AULA
# ============================

class AulaCreate(BaseModel):
    id_institucion: int
    id_sede: int
    grado: str # Podrías restringir a Literal('4', '5', '9', '10') si solo manejas esos grados

class AulaOut(AulaCreate):
    id_aula: int


# ============================
# HORARIO
# ============================

class HorarioCreate(BaseModel):
    # Días de la semana restringidos
    dia_semana: Literal['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    # Usar el tipo time para validar formato HH:MM
    h_inicio: time
    h_final: time
    minutos_equiv: int = 45 # Usando 45 minutos como hora equivalente
    # 'S' o 'N'
    es_continuo: Literal['S', 'N'] = "S"

class HorarioOut(HorarioCreate):
    id_horario: int

class AsignarHorarioAula(BaseModel):
    id_aula: int
    id_horario: int
    fecha_inicio: date

# ============================
# ASIGNACIÓN DE TUTOR A AULA
# ============================

class TutorAulaAssign(BaseModel):
    id_aula: int
    id_persona: int  # ID del tutor
    fecha_inicio: date
    motivo_cambio: Optional[str] = None

class TutorAulaUnassign(BaseModel):
    id_aula: int
    fecha_fin: date


# ============================
# HISTORICO_AULA_ESTUDIANTE
# (Modelos relacionados con estudiantes y su histórico de aulas)
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
    fecha_inicio: Optional[date] = None

class CambioEstudianteAulaIn(BaseModel):
    id_hist_aula_est: int
    id_aula_origen: int
    id_aula_destino: int
    id_estudiante: int
    fecha_fin_actual: Optional[date] = None 
    fecha_inicio_nueva: date


# ============================
# PERIODO / COMPONENTE
# ============================

class PeriodoIn(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date

class ComponenteIn(BaseModel):
    nombre: str
    porcentaje: float
    tipo_programa: str
    id_periodo: int


# ============================
# ASISTENCIA Y NOTAS
# ============================

class AsistenciaAulaIn(BaseModel):
    id_aula: int
    id_tutor_aula: int
    id_horario: int
    id_semana: int
    fecha_clase: date
    hora_inicio: time
    hora_fin: Optional[time] = None
    dictada: Literal['S', 'N']
    horas_dictadas: int
    reposicion: Literal['S', 'N'] = "N"
    fecha_reposicion: Optional[date] = None
    id_motivo: Optional[int] = None
    corresponde_horario: int
    es_festivo: int


class RegistrarNotaIn(BaseModel):
    id_estudiante: int
    id_componente: int
    nota: float

class RegistrarAsistenciaEstudianteIn(BaseModel):
    id_asist: int
    id_estudiante: int
    asistio: Literal['S', 'N']
    observacion: Optional[str] = None

class GenerarSemanasRequest(BaseModel):
    anio: int
