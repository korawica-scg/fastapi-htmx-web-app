from fastapi import (
    Depends,
    FastAPI,
)
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import get_query_token
from .config import settings


def create_app():
    """FastAPI application factory
    :return:
    """
    # Initialize application
    app = FastAPI(
        title='FastAPI and HTMX',
        # dependencies=[Depends(get_query_token)],
        openapi_url='/api/v1/openapi.json',
        docs_url='/api/v1/docs',
    )

    # Mount the static folder to the app for use in Jinja2 template.
    # usages: `{{ url_for('static', path='/styles.css') }}`
    # docs: https://fastapi.tiangolo.com/advanced/templates/
    app.mount("/static", StaticFiles(directory="backend/static"), name="static")

    # Add CORS middleware to the app
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_methods=['*'],
        allow_headers=['*'],
        allow_credentials=True,
    )

    # Add internal routers to the app like admin
    # app.include_router(
    #     admin,
    #     prefix="/admin",
    #     tags=["admin"],
    #     dependencies=[Depends(get_token_header)],
    #     responses={418: {"description": "I'm a teapot"}},
    # )

    # Add routers to the app
    from .routers import users
    app.include_router(users, prefix='/api/v1')

    @app.get("/", include_in_schema=False)
    async def health() -> JSONResponse:
        return JSONResponse({"message": "It worked!!"})

    @app.on_event("startup")
    async def startup():
        from .database import async_engine
        from .database import Base

        # Drop and Create tables in database
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
    return app
