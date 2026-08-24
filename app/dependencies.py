from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError

from . import constants
from .database import users as users_col
from .models import User
from .security import decode_access_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

ALREADY_AUTH_ERROR = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Не удалось проверить учётные данные",
    headers={"WWW-Authenticate": "Bearer"},
)


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    try:
        payload = decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise ALREADY_AUTH_ERROR
    except InvalidTokenError:
        raise ALREADY_AUTH_ERROR

    doc = await users_col.find_one({"username": username})
    if not doc or not doc.get("is_active", True):
        raise ALREADY_AUTH_ERROR
    return User(**doc)


def require_admin(user: User = Depends(get_current_user)) -> User:
    if constants.ROLE_ADMIN not in user.roles:
        raise HTTPException(status_code=403, detail="Нет прав администратора")
    return user


def require_full(user: User = Depends(get_current_user)) -> User:
    # «full» действует ТОЛЬКО в связке с «admin»
    if constants.ROLE_ADMIN not in user.roles or constants.ROLE_FULL not in user.roles:
        raise HTTPException(status_code=403, detail="Требуется роль admin + full")
    return user


def is_admin(user: User) -> bool:
    return constants.ROLE_ADMIN in user.roles


def is_full(user: User) -> bool:
    return constants.ROLE_ADMIN in user.roles and constants.ROLE_FULL in user.roles


def get_optional_user(user: Optional[User] = None) -> Optional[User]:
    return user