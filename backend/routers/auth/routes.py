from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Body, Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ...database import get_session
from ...securities import get_password_hash
from ...securities import create_access_token
from ...config import settings
from ...utils.utilities import (
    generate_password_reset_token,
    send_reset_password_email,
    verify_password_reset_token,
)
from ..users.schemas import User as SchemaUser
from ..users.models import User
from ..users.crud import get_user_by_email
from .crud import authenticate
from .crud import is_active
from .dependencies import get_current_user
from .schemas import Token, Message


auth = APIRouter(
    prefix='/auth',
    tags=["auth"],
)


@auth.post("/login/access-token", response_model=Token)
def login_access_token(
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm)
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests"""
    user = authenticate(
        session,
        email=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",

            # Add the header WWW-Authenticate to make the browser show the login prompt again.
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject={
                "sub": user.username,

                # OAuth2 with scopes.
                "scopes": form_data.scopes,
            },
            expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@auth.post("/login/test-token", response_model=SchemaUser)
def test_token(
        current_user: User = Security(get_current_user, scopes=["me"]),
) -> Any:
    """Test access token"""
    return current_user


@auth.post("/password-recovery/{email}", response_model=Message)
def recover_password(
        email: str,
        session: Session = Depends(get_session)
) -> Any:
    """Password Recovery"""
    user = get_user_by_email(session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    send_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )
    return {"msg": "Password recovery email sent"}


@auth.post("/reset-password/", response_model=Message)
def reset_password(
    token: str = Body(...),
    new_password: str = Body(...),
    session: Session = Depends(get_session),
) -> Any:
    """Reset password"""
    email = verify_password_reset_token(token)
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid token"
        )
    user = get_user_by_email(session, email=email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    elif not is_active(user):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )
    hashed_password = get_password_hash(new_password)
    user.hashed_password = hashed_password
    session.add(user)
    session.commit()
    return {"msg": "Password updated successfully"}
