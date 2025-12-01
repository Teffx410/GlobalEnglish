# app/auth.py
from fastapi import HTTPException, Security, Depends, Query, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from typing import Optional, Literal, Annotated
# from app.db import get_conn # Asumo que get_conn está definida en app/db

# Definición de roles para fácil referencia
ROLES = Literal['ADMINISTRADOR', 'ADMINISTRATIVO', 'TUTOR']

# Clave secreta para JWT. Usar una variable de entorno segura en producción.
SECRET = os.getenv("JWT_SECRET", "change_this_secret")
security = HTTPBearer()

# =======================================================
# 1. FUNCIONES DE TOKEN
# =======================================================

def create_token(payload: dict) -> str:
    """Crea un token JWT a partir de un payload."""
    # Asegúrate de incluir el rol, id_persona y id_usuario en el payload
    # Ejemplo de payload: {"id_usuario": 1, "id_persona": 5, "rol": "ADMINISTRATIVO"}
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str) -> dict:
    """Decodifica el token JWT. Lanza HTTPException si es inválido."""
    try:
        # Usa la librería jwt estándar de Python
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado. Por favor, inicie sesión de nuevo.")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Firma de token inválida.")
    except Exception:
        raise HTTPException(status_code=401, detail="Token inválido o malformado.")

# =======================================================
# 2. DEPENDENCIAS DE AUTENTICACIÓN
# =======================================================

async def get_current_user(token: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """Dependencia para obtener el payload del usuario autenticado."""
    user_data = decode_token(token.credentials)
    
    # Comprobar que los campos mínimos necesarios existan
    if 'id_persona' not in user_data or 'rol' not in user_data:
        raise HTTPException(status_code=401, detail="Token incompleto. Faltan datos de persona/rol.")

    return user_data

# =======================================================
# 3. DEPENDENCIAS DE AUTORIZACIÓN (JERARQUÍA DE ROLES)
# =======================================================

# Definición de la jerarquía de roles para la herencia de permisos
ROLE_HIERARCHY = {
    'TUTOR': 0,
    'ADMINISTRATIVO': 1,
    'ADMINISTRADOR': 2
}

def get_role_level(role: str) -> int:
    """Obtiene el nivel numérico de un rol para la jerarquía."""
    return ROLE_HIERARCHY.get(role.upper(), -1)

def requires_role(required_roles: list[ROLES]):
    """
    Dependencia de autorización que verifica si el usuario tiene el rol requerido
    o un rol superior en la jerarquía (ADMINISTRADOR hereda permisos).
    """
    def role_checker(user: dict = Depends(get_current_user)):
        user_rol = user.get("rol", "").upper()
        
        # 1. Obtener el nivel del rol del usuario
        user_level = get_role_level(user_rol)
        
        # 2. Iterar sobre los roles requeridos para la ruta
        for required_role in required_roles:
            required_level = get_role_level(required_role.upper())
            
            # Si el usuario tiene el mismo rol O un nivel superior, el acceso es concedido.
            if user_level >= required_level:
                return user # Retorna el payload del usuario
        
        # Si no se cumple ningún requisito
        raise HTTPException(
            status_code=403,
            detail=f"Acceso denegado. Rol '{user_rol}' no tiene permisos para esta operación."
        )
    return role_checker


# =======================================================
# 4. DEPENDENCIAS DE LÓGICA DE NEGOCIO (DELEGACIÓN)
# =======================================================

async def get_person_id_to_act_on(
    user: dict = Depends(get_current_user),
    # Parámetro de consulta opcional, usado por el ADMINISTRATIVO
    id_tutor_a_actuar: Annotated[Optional[int], Query(description="ID de la persona (Tutor) sobre la que actuará el ADMINISTRATIVO.")] = None
) -> int:
    """
    Determina sobre qué ID de persona (Tutor) debe actuar la operación:
    - Si el usuario es TUTOR, solo actúa sobre sí mismo (ignora id_tutor_a_actuar).
    - Si el usuario es ADMINISTRATIVO o ADMINISTRADOR, usa id_tutor_a_actuar si se proporciona.
    - Si es ADMINISTRATIVO/ADMINISTRADOR y NO proporciona id_tutor_a_actuar, actúa sobre sí mismo.

    Este mecanismo implementa: "ADMINISTRATIVO podrá hacer lo mismo que el TUTOR,
    pero debe solicitar primero sobre que TUTOR va a actuar."
    """
    user_id_persona = user["id_persona"]
    user_rol = user["rol"].upper()

    # Si el rol es TUTOR, solo puede actuar sobre sus propios datos
    if user_rol == 'TUTOR':
        if id_tutor_a_actuar is not None and id_tutor_a_actuar != user_id_persona:
            # Esto previene que un TUTOR intente actuar sobre otro
            raise HTTPException(status_code=403, detail="Un TUTOR solo puede actuar sobre sus propios registros.")
        return user_id_persona
    
    # Si el rol es ADMINISTRATIVO o ADMINISTRADOR
    elif user_rol in ['ADMINISTRATIVO', 'ADMINISTRADOR']:
        # Si el ID de la persona a actuar está especificado, lo usa (Delegación)
        if id_tutor_a_actuar is not None:
            # Aquí podrías añadir una capa de CRUB para verificar que id_tutor_a_actuar exista y sea un TUTOR válido
            return id_tutor_a_actuar
        else:
            # Si no se especifica, asume que está actuando sobre sí mismo (e.g., registrando su propia clase si es ADMINISTRATIVO/TUTOR)
            return user_id_persona
            
    # Caso de rol no manejado (debería ser capturado por requires_role, pero por seguridad)
    raise HTTPException(status_code=403, detail="Rol de usuario no reconocido o no autorizado.")
        # 3. Retornar los datos decodificados (payload)
        # Esto permite que el endpoint acceda al id_persona y otros datos si es necesario.
        return data
    return role_checker
