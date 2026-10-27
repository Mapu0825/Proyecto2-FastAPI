import os 
import secrets
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def require_admin(key: str = Security(api_key_header)):
    esperada = os.getenv("API_KEY", "")
    if not key or not esperada or not secrets.compare_digest(key, esperada):
        raise HTTPException(status_code=401, detail="API key invalida o ausente")
