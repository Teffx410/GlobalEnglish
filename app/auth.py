# app/auth.py
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
from app.db import get_conn

SECRET = os.getenv("JWT_SECRET", "change_this_secret")
security = HTTPBearer()

def create_token(payload: dict):
    return jwt.encode(payload, SECRET, algorithm="HS256")

def decode_token(token: str):
    try:
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(token: HTTPAuthorizationCredentials = Security(security), roles=None):
    data = decode_token(token.credentials)
    if roles and data.get("rol") not in roles:
        raise HTTPException(status_code=403, detail="Insufficient role")
    return data
