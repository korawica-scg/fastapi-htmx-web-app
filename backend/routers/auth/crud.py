from typing import Optional
from sqlalchemy.orm import Session
from ..users.models import User
from ..users.crud import get_user_by_email
from ...securities import verify_password


def authenticate(
        session: Session,
        *,
        email: str,
        password: str,
) -> Optional[User]:
    user = get_user_by_email(session, email=email)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: User) -> bool:
    return user.is_active

