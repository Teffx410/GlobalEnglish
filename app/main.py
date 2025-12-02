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
