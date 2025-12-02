# app/models.py

from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, time


# ============================
# ROLES Y CONFIGURACIÓN
# ============================

class RolBase(BaseModel):
    nombre: Literal['ADMINISTRADOR', 'ADMINISTRATIVO', 'TUTOR']
    descripcion: Optional[str] = None

class RolOut(RolBase):
    id_rol: int


class TipoDocumentoBase(BaseModel):
    nombre_tipo: str
    sigla: str

class TipoDocumentoOut(TipoDocumentoBase):
    id_tipo_doc: int


class SemanaBase(BaseModel):
    nombre_semana: str
    fecha_inicio: date
    fecha_fin: date
    anio: int

class SemanaCreate(SemanaBase):
    pass

class SemanaOut(SemanaBase):
    id_semana: int


# ============================
# INSTITUCIÓN / SEDE
# ============================

class InstitucionCreate(BaseModel):
    nombre_inst: str
    jornada: Optional[Literal['MAÑANA', 'TARDE', 'MIXTA']] = 'MIXTA'
    dir_principal: Optional[str] = None

class InstitucionOut(InstitucionCreate):
    id_institucion: int


class SedeCreate(BaseModel):
    id_institucion: int
    direccion: str
    es_principal: Literal['S', 'N'] = 'N'


# >>>>>>> ESTA ES LA CORRECCIÓN QUE TE FALTABA <<<<<<<<<
class SedeUpdate(BaseModel):
    direccion: Optional[str] = None
    es_principal: Optional[Literal['S', 'N']] = None
# >>>>>>> FIN DE LA CORRECCIÓN <<<<<<<<<


class SedeOut(SedeCreate):
    id_sede: int


# ============================
# PERSONA Y USUARIO
# ============================

class PersonaCreate(BaseModel):
    id_tipo_doc: int
    num_documento: str
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    contratado: Literal['S', 'N'] = "S"
    perfil_tecnico: Optional[Literal['S', 'N']] = "N"  # Para ADMINISTRADOR

class PersonaOut(PersonaCreate):
    id_persona: int


class PersonaUpdate(BaseModel):
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    perfil_tecnico: Optional[Literal['S', 'N']] = None


class UsuarioCreate(BaseModel):
    id_persona: int
    id_rol: int
    nombre_user: str
    contrasena: str
    enviar_correo: bool = True

class UsuarioLogin(BaseModel):
    nombre_user: str
    contrasena: str

class UsuarioOut(BaseModel):
    id_usuario: int
    nombre_user: str
    id_persona: int
    rol: Literal['ADMINISTRADOR', 'ADMINISTRATIVO', 'TUTOR']


# ============================
# AULA
# ============================

class AulaCreate(BaseModel):
    id_institucion: int
    id_sede: int
    grado: str

class AulaOut(AulaCreate):
    id_aula: int


# ============================
# HORARIO
# ============================

class HorarioCreate(BaseModel):
    dia_semana: Literal[
        'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo'
    ]
    h_inicio: time
    h_final: time
    minutos_equiv: int = 45
    es_continuo: Literal['S', 'N'] = "S"

class HorarioOut(HorarioCreate):
    id_horario: int


class AsignarHorarioAula(BaseModel):
    id_aula: int
    id_horario: int
    fecha_inicio: date


# ============================
# TUTOR – AULA
# ============================

class TutorAulaAssign(BaseModel):
    id_aula: int
    id_persona: int
    fecha_inicio: date
    motivo_cambio: Optional[str] = None

class TutorAulaOut(TutorAulaAssign):
    id_tutor_aula: int


class TutorAulaUnassign(BaseModel):
    id_aula: int
    fecha_fin: date


# ============================
# ESTUDIANTES / HISTÓRICO
# ============================

class EstudianteIn(BaseModel):
    id_tipo_doc: int
    num_documento: str
    nombres: str
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    correo: Optional[str] = None
    score_entrada: Optional[float] = None
    score_salida: Optional[float] = None

class EstudianteOut(EstudianteIn):
    id_estudiante: int


class EstudianteUpdate(BaseModel):
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    score_entrada: Optional[float] = None
    score_salida: Optional[float] = None


class HistoricoAulaEstudianteIn(BaseModel):
    id_estudiante: int
    id_aula: int
    fecha_inicio: Optional[date] = None


class CambioEstudianteAulaIn(BaseModel):
    id_estudiante: int
    id_aula_origen: int
    id_aula_destino: int
    fecha_fin_origen: date
    fecha_inicio_destino: date


# ============================
# ASISTENCIA AULA Y ESTUDIANTES
# ============================

class AsistenciaAulaBase(BaseModel):
    id_aula: int
    id_tutor_aula: int          # tutor real asignado al aula
    id_tutor_que_registra: int  # tutor o administrativo que registra la asistencia
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
    corresponde_horario: Literal['S', 'N']
    es_festivo: Literal['S', 'N']

class AsistenciaAulaOut(AsistenciaAulaBase):
    id_asist: int


class RegistrarAsistenciaEstudianteIn(BaseModel):
    id_asist: int
    id_estudiante: int
    asistio: Literal['S', 'N']
    observacion: Optional[str] = None


class RegistrarAsistenciaTutor(BaseModel):
    id_tutor: int
    fecha: date
    asistio: Literal['S', 'N']
    observacion: Optional[str] = None


# ============================
# NOTAS / PERIODO / COMPONENTES
# ============================

class RegistrarNotaIn(BaseModel):
    id_estudiante: int
    id_componente: int
    nota: float = Field(ge=0, le=5)

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
# MOTIVOS / FESTIVOS
# ============================

class MotivoNoAsistenciaIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None


class FestivoIn(BaseModel):
    nombre: str
    fecha: date
    recurrente: bool = False


# ============================
# ACCIÓN DELEGADA
# ============================

class DelegatedActionRequest(BaseModel):
    """
    Modelo que debe enviar el ADMINISTRATIVO para actuar
    sobre acciones del tutor.
    """
    id_tutor_a_actuar: int
