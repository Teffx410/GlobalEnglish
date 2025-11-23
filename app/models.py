# app/models.py
from pydantic import BaseModel
from typing import Optional
from datetime import date

class InstitucionIn(BaseModel):
    nombre_inst: str
    jornada: Optional[str] = None
    dir_principal: Optional[str] = None

class InstitucionOut(InstitucionIn):
    id_institucion: int

class SedeIn(BaseModel):
    id_institucion: int
    direccion: Optional[str] = None
    es_principal: Optional[str] = 'N'

class SedeOut(SedeIn):
    id_sede: int


class PersonaIn(BaseModel):
    tipo_doc: Optional[str]
    nombre: str
    telefono: Optional[str]
    correo: Optional[str]
    rol: Optional[str]

class PersonaOut(PersonaIn):
    id_persona: int

class AulaIn(BaseModel):
    id_institucion: int
    id_sede: int
    grado: str

class AulaOut(AulaIn):
    id_aula: int

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
