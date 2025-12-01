# app/models.py

from pydantic import BaseModel
from typing import Optional, Literal
from datetime import date, time, datetime

# ============================
# CONFIGURACIÓN (ADMINISTRADOR)
# ============================

# Modelos base para la gestión de tipos de datos estáticos por el ADMINISTRADOR.
# Esto incluye roles, menús (no implementado aquí), y tipos de documentos.

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
    """Modelo para el calendario de semanas del programa, creado 1 sola vez por el ADMINISTRADOR."""
    nombre_semana: str
    fecha_inicio: date
    fecha_fin: date
    anio: int

class SemanaCreate(SemanaBase):
    pass

class SemanaOut(SemanaBase):
    id_semana: int


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

# Nota: El rol se gestionará al crear el USUARIO. En la Persona solo definimos su información.
class PersonaCreate(BaseModel):
    id_tipo_doc: int
    num_documento: str
    nombre: str
    telefono: Optional[str] = None
    correo: Optional[str] = None

class PersonaUpdate(BaseModel):
    id_tipo_doc: Optional[int] = None
    num_documento: Optional[str] = None
    nombre: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None

class PersonaOut(PersonaCreate):
    id_persona: int


class UsuarioCreate(BaseModel):
    """Modelo para la creación de un Usuario asociado a una Persona y un Rol."""
    id_persona: int
    id_rol: int # ID del rol (TUTOR, ADMINISTRATIVO, ADMINISTRADOR)
    nombre_user: str
    # La contraseña se envía en texto plano para ser hasheada
    contrasena: str 
    # El ADMINISTRADOR puede enviar la contraseña por correo
    enviar_correo: bool = True 

class UsuarioLogin(BaseModel):
    """Modelo para la solicitud de login."""
    nombre_user: str
    contrasena: str
    
class UsuarioOut(BaseModel):
    """Modelo de salida simplificado para el usuario."""
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
# (Esto define qué Aulas tiene asignadas un TUTOR/ADMINISTRATIVO)
# ============================

class TutorAulaAssign(BaseModel):
    """Asignar una Persona (con rol Tutor o Administrativo) a un Aula."""
    id_aula: int
    id_persona: int # ID de la persona (Tutor)
    fecha_inicio: date
    motivo_cambio: Optional[str] = None

class TutorAulaUnassign(BaseModel):
    id_aula: int
    fecha_fin: date


# ============================
# ESTUDIANTES / HISTORICO
# ============================

class EstudianteIn(BaseModel):
    id_tipo_doc: int
    num_documento: str
    nombres: str
    apellidos: Optional[str]
    telefono: Optional[str]
    fecha_nacimiento: Optional[date]
    correo: Optional[str]
    score_entrada: Optional[float] = None
    score_salida: Optional[float] = None

class EstudianteUpdate(BaseModel):
    # Permitir al Administrativo actualizar solo scores
    score_entrada: Optional[float] = None
    score_salida: Optional[float] = None
    # Permitir otros campos
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    # ... otros campos de la persona

class EstudianteOut(EstudianteIn):
    id_estudiante: int

class HistoricoAulaEstudianteIn(BaseModel):
    """Modelo para ingresar estudiantes a un aula."""
    id_estudiante: int
    id_aula: int
    fecha_inicio: Optional[date] = None

class CambioEstudianteAulaIn(BaseModel):
    """Modelo para MOVER estudiantes de un aula a otra (cierra histórico anterior y abre uno nuevo)."""
    id_estudiante: int
    id_aula_origen: int
    id_aula_destino: int
    fecha_fin_origen: date # Fecha de fin en el aula original
    fecha_inicio_destino: date # Fecha de inicio en la nueva aula


# ============================
# ASISTENCIA, NOTAS Y REPOSICIÓN
# ============================

class AsistenciaAulaBase(BaseModel):
    """Modelo base para registrar la clase dictada por el Tutor."""
    id_aula: int
    # ID de la asignación Tutor-Aula (para saber quién dictó la clase)
    id_tutor_aula: int 
    id_horario: int
    id_semana: int
    fecha_clase: date
    hora_inicio: time
    hora_fin: Optional[time] = None
    dictada: Literal['S', 'N']
    horas_dictadas: int
    reposicion: Literal['S', 'N'] = "N"
    fecha_reposicion: Optional[date] = None # Campo para el requisito de reposición
    id_motivo: Optional[int] = None # Motivo de no asistencia a clase
    corresponde_horario: int
    es_festivo: int # 1 si es festivo, 0 si no

class AsistenciaAulaOut(AsistenciaAulaBase):
    id_asist: int


class RegistrarNotaIn(BaseModel):
    id_estudiante: int
    id_componente: int
    nota: float


class RegistrarAsistenciaEstudianteIn(BaseModel):
    id_asist: int # La clase dictada que se tomó como referencia
    id_estudiante: int
    asistio: Literal['S', 'N']
    observacion: Optional[str] = None


class RegistrarAsistenciaTutor(BaseModel):
    """Modelo para que el ADMINISTRATIVO verifique la asistencia del Tutor."""
    id_tutor: int
    fecha: date
    asistio: Literal['S', 'N']
    observacion: Optional[str] = None


# ============================
# MOTIVO Y FESTIVOS
# ============================

class MotivoNoAsistenciaIn(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class FestivoIn(BaseModel):
    nombre: str
    fecha: date
    recurrente: bool = False # Es un festivo que se repite cada año

# ============================
# PERIODO / COMPONENTE DE NOTAS
# ============================

class PeriodoIn(BaseModel):
    nombre: str
    fecha_inicio: date
    fecha_fin: date

class ComponenteIn(BaseModel):
    nombre: str
    porcentaje: float
    # El programa se refiere al tipo de programa (e.g., Nivelación, Taller)
    tipo_programa: str 
    id_periodo: int

# ============================
# SOLICITUD DE ACCIÓN DELEGADA
# ============================

class DelegatedActionRequest(BaseModel):
    """
    Modelo especial para el ADMINISTRATIVO que solicita actuar sobre un Tutor.
    Se usará como parámetro de consulta o en el cuerpo de la solicitud
    en las rutas de TUTOR (Asistencia/Notas/Reportes).
    """
    id_tutor_a_actuar: int # El ID de la persona (TUTOR) sobre la que se actuará
