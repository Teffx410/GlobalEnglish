# app/auth.py
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from app.db import get_conn

SECRET = os.getenv("JWT_SECRET", "change_this_secret")
security = HTTPBearer()

def create_token(payload: dict):
    """Crea un token JWT a partir de un payload."""
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str):
    """Decodifica el token JWT. Lanza HTTPException si es inválido."""
    try:
        # Nota: La librería python-jose es la recomendada, pero usando jwt.decode estándar.
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expirado")
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=401, detail="Firma de token inválida")
    except Exception as e:
        raise HTTPException(status_code=401, detail="Token inválido")

# MODIFICACIÓN CLAVE: require_role como CLOUSURE/ENVOLTURA
def require_role(required_roles: list[str]):
    """
    Devuelve una función de dependencia que verifica si el usuario autenticado
    tiene alguno de los roles permitidos.
    
    Uso en FastAPI: dependencies=[Depends(require_role(["ADMINISTRADOR", "ADMINISTRATIVO"]))]
    """
    def role_checker(token: HTTPAuthorizationCredentials = Security(security)):
        # 1. Decodificar el token para obtener los datos
        data = decode_token(token.credentials)
        user_rol = data.get("rol")
        
        # 2. Verificar el rol
        if not user_rol or user_rol not in required_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Acceso denegado. Rol '{user_rol}' no autorizado."
            )
        # 3. Retornar los datos decodificados (payload)
        # Esto permite que el endpoint acceda al id_persona y otros datos si es necesario.
        return data
    return role_checker