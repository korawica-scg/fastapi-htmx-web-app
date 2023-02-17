from fastapi import APIRouter
from .users.routes import users
from .tickets.routes import tickets
from .tickets.views import tickets as ticket_view
from .auth.routes import auth

api_router = APIRouter()
api_router.include_router(users)
api_router.include_router(tickets)
api_router.include_router(auth)
