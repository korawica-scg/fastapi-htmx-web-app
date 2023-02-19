from fastapi import (
    Depends,
    HTTPException,
    status, Security,
)
from fastapi.security import (
    OAuth2PasswordBearer,
    SecurityScopes,
)
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session
from ...database import get_session
from ...securities import ALGORITHM
from ...config import settings
from ..users.models import User
from ..users.crud import get_user, get_user_by_username
from .schemas import TokenPayload, TokenData
from .crud import (
    is_active,
    is_superuser,
)


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/login/access-token",

    # OAuth2 with scopes is the mechanism used by many big authentication providers,
    # like Facebook, Google, GitHub, Microsoft, Twitter, etc. They use it to provide
    # specific permissions to users and applications.
    # ---
    # This is the same mechanism used when you give permissions while logging in with
    # Facebook, Google, GitHub, etc:
    # docs: https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/
    scopes={
        "me": "Read information about the current user.",
        "tickets": "Read ticket items."
    },
)


async def get_current_user(
        security_scopes: SecurityScopes,
        session: Session = Depends(get_session),
        token: str = Depends(reusable_oauth2),
) -> User:
    # OAuth2 with scopes
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise ValidationError
        # OAuth2 with scopes
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": authenticate_value},
        ) from err
    if user := get_user_by_username(session, username=token_data.username):
        # OAuth2 with scopes
        for scope in security_scopes.scopes:
            if scope not in token_data.scopes:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        return user
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="User not found",
        headers={"WWW-Authenticate": authenticate_value},
    )


async def get_current_active_user(
        current_user: User = Security(get_current_user, scopes=["me"]),
) -> User:
    if not is_active(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


async def get_current_active_superuser(
        current_user: User = Security(get_current_user, scopes=["me"]),
) -> User:
    if not is_superuser(current_user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The user doesn't have enough privileges"
        )
    return current_user
