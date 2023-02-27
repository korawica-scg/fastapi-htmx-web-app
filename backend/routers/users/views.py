from datetime import timedelta
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Request
from fastapi import APIRouter, Depends, status
from fastapi.responses import RedirectResponse, Response
from .crud import CreateUser
from sqlalchemy.orm import Session
from ...dependencies import get_templates
from ...database import get_session
from ...config import settings
from ...securities import create_access_token
from ..auth.crud import authenticate
from .schemas import UserCreateForm

users = APIRouter(
    tags=["user-views"],
    responses={
        # 404: {"description": "Not found"}
    },
)


@users.get('/register/', response_class=HTMLResponse)
def register(
        request: Request,
        template: Jinja2Templates = Depends(get_templates),
):
    context = {"request": request, "content": "register"}
    return template.TemplateResponse('users/index.html', context=context)


@users.post("/register/")
async def register(
        response: Response,
        user: UserCreateForm = Depends(UserCreateForm.as_form),
        service: CreateUser = Depends(CreateUser)
):
    user = await service.execute(user)
    response.headers["HX-Redirect"] = "/login/"
    response.status_code = status.HTTP_303_SEE_OTHER
    return {}


@users.get('/login/', response_class=HTMLResponse)
def login(
        request: Request,
        template: Jinja2Templates = Depends(get_templates),
):
    context = {"request": request, "content": "login"}
    return template.TemplateResponse('users/index.html', context=context)


@users.post('/login/')
async def login(
    response: Response,
    session: Session = Depends(get_session),
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm),
):
    user = authenticate(
        session,
        email=form_data.username,
        password=form_data.password,
    )
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject={
            "sub": user.username,

            # OAuth2 with scopes.
            "scopes": form_data.scopes,
        },
        expires_delta=access_token_expires
    )
    response.set_cookie(
        key='access_token',
        value=access_token,
        expires=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
    response.headers["HX-Redirect"] = "/ticket/"
    response.status_code = status.HTTP_302_FOUND
    return {}
