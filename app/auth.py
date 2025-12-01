# app/auth.py
from fastapi import HTTPException, Security, Depends, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from typing import Optional, Literal, Annotated

# ---------------------------------------------------------
# DEFINICIÓN DE ROLES
# ---------------------------------------------------------
ROLES = Literal['ADMINISTRADOR', 'ADMINISTRATIVO', 'TUTOR']

ROLE_HIERARCHY = {
    'TUTOR': 0,
    'ADMINISTRATIVO': 1,
    'ADMINISTRADOR': 2
}

def get_role_level(role: str) -> int:
    return ROLE_HIERARCHY.get(role.upper(), -1)


# ---------------------------------------------------------
# CONFIGURACIÓN DE JWT
# ---------------------------------------------------------
SECRET = os.getenv("JWT_SECRET", "change_this_secret")
security = HTTPBearer()


# ---------------------------------------------------------
# 1. MANEJO DE TOKENS
# ---------------------------------------------------------
def create_token(payload: dict) -> str:
    """Crea un token JWT con rol, id_persona e id_usuario."""
    return jwt.encode(payload, SECRET, algorithm="HS256")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado.")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Firma de token inválida.")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido.")


# ---------------------------------------------------------
# 2. OBTENER USUARIO DEL TOKEN
# ---------------------------------------------------------
async def get_current_user(token: HTTPAuthorizationCredentials = Security(security)):
    user = decode_token(token.credentials)

    if "id_persona" not in user or "rol" not in user:
        raise HTTPException(status_code=401, detail="Token incompleto.")

    return user


# ---------------------------------------------------------
# 3. AUTORIZACIÓN POR ROLES
# ---------------------------------------------------------
def requires_role(required_roles: list[ROLES]):
    """
    Permite acceso si el usuario tiene el rol requerido
    O un rol superior (ADMIN → ADMINISTRATIVO → TUTOR).
    """
    def role_checker(user: dict = Depends(get_current_user)):
        user_rol = user["rol"].upper()
        user_lvl = get_role_level(user_rol)

        for required in required_roles:
            required_lvl = get_role_level(required.upper())

            if user_lvl >= required_lvl:
                return user  # acceso permitido

        raise HTTPException(
            status_code=403,
            detail=f"No tiene permisos para esta operación (Rol actual: {user_rol})."
        )

    return role_checker


# ---------------------------------------------------------
# 4. DELEGACIÓN: SOBRE QUÉ PERSONA SE ACTÚA
# ---------------------------------------------------------
async def get_person_id_to_act_on(
    user: dict = Depends(get_current_user),
    id_tutor_a_actuar: Annotated[
        Optional[int],
        Query(
            description="ID del Tutor sobre el que actuará el ADMINISTRATIVO/ADMINISTRADOR."
        )
    ] = None
) -> int:
    """
    Lógica oficial del enunciado:
    - TUTOR solo actúa sobre sí mismo.
    - ADMINISTRATIVO DEBE elegir un tutor.
    - ADMINISTRADOR puede elegir un tutor, y si no lo hace actúa como él mismo.
    """

    rol = user["rol"].upper()
    id_usuario = user["id_persona"]

    # TUTOR: solo sobre sí mismo
    if rol == "TUTOR":
        if id_tutor_a_actuar and id_tutor_a_actuar != id_usuario:
            raise HTTPException(403, "Un TUTOR no puede actuar sobre otro TUTOR.")
        return id_usuario

    # ADMINISTRATIVO: OBLIGADO a elegir un tutor
    if rol == "ADMINISTRATIVO":
        if id_tutor_a_actuar is None:
            raise HTTPException(
                status_code=400,
                detail="Debe especificar el ID del Tutor sobre el que desea actuar."
            )
        return id_tutor_a_actuar

    # ADMINISTRADOR: puede elegir un tutor o actuar sobre sí mismo
    if rol == "ADMINISTRADOR":
        return id_tutor_a_actuar if id_tutor_a_actuar else id_usuario

    raise HTTPException(403, "Rol desconocido o no autorizado.")
