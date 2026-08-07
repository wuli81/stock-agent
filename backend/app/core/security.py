"""API Key 鉴权与密钥工具。"""

import hashlib
import secrets

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import get_settings

_bearer = HTTPBearer(auto_error=False)


def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def generate_api_key() -> str:
    return "sk-" + secrets.token_urlsafe(32)


def verify_api_key(credentials: HTTPAuthorizationCredentials | None) -> str | None:
    """校验 Bearer Key，通过则返回该 Key，否则返回 None。"""
    if credentials is None:
        return None
    key = credentials.credentials
    if key in get_settings().api_key_list:
        return key
    return None


def require_api_key(credentials: HTTPAuthorizationCredentials | None = Security(_bearer)) -> None:
    if verify_api_key(credentials) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": 1001, "message": "鉴权失败"},
        )
