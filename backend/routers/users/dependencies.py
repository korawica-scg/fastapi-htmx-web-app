from fastapi import Header, HTTPException, Depends, status, Request
from fastapi import Cookie
from fastapi.security import OAuth2PasswordBearer
from fastapi.security.utils import get_authorization_scheme_param
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from pydantic import ValidationError
from typing import Optional, List
from ...config import settings
from ...securities import ALGORITHM
from ...database import get_session
from ..auth.schemas import TokenData
from .crud import get_user_by_username
from .models import User


# docs: https://nilsdebruin.medium.com/fastapi-how-to-add-basic-and-cookie-authentication-a45c85ef47d3
class OAuth2PasswordCustom:
    def __init__(
            self,
            login_url: str,
            auto_error: bool = True,
    ):
        self.login_url: str = login_url
        self.auto_error: bool = auto_error

    async def __call__(self, request: Request) -> Optional[str]:
        header_authorization: str = request.headers.get("Authorization")
        cookie_authorization: str = request.cookies.get("Authorization")

        header_scheme, header_param = get_authorization_scheme_param(
            header_authorization
        )
        cookie_scheme, cookie_param = get_authorization_scheme_param(
            cookie_authorization
        )

        if header_scheme.lower() == "bearer":
            authorization = True
            scheme = header_scheme
            param = header_param
        elif cookie_scheme.lower() == "bearer":
            authorization = True
            scheme = cookie_scheme
            param = cookie_param
        else:
            authorization = False
            scheme = ""
            param = ""

        if not authorization or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authenticated"
                )
            else:
                return None
        return param


oauth2_scheme = OAuth2PasswordCustom(
    login_url="/login/",
)


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        session: Session = Depends(get_session),
) -> Optional[User]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        username = payload.get("sub")
        if username is None:
            raise ValidationError
        token_data = TokenData(username=username)
    except (JWTError, ValidationError) as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    return get_user_by_username(session, username=token_data.username)


def get_current_user_required(
    user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="An authenticated user is required for that action.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_current_user_optional(
    user: Optional[User] = Depends(get_current_user)
) -> Optional[User]:
    return user
