import time
import string
import random
import logging
from logging.config import dictConfig
from fastapi import FastAPI
from fastapi import Request
from fastapi import Depends
from fastapi import Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse
from fastapi.utils import generate_unique_id
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from .dependencies import get_query_token, custom_generate_unique_id
from .config import settings


logger = logging.getLogger(__name__)


def create_app():
    """FastAPI application factory"""
    # Initialize application
    app = FastAPI(
        title='FastAPI and HTMX',
        description="Full Web application with FastAPI for backend and HTMX + CSS for frontend.",
        version="0.0.1",

        # Default from FastAPI: `generate_unique_id`
        # generate_unique_id_function=custom_generate_unique_id,

        # docs: https://fastapi.tiangolo.com/advanced/extending-openapi/
        openapi_url='/api/v1/openapi.json',
        openapi_tags=[
            {
                # Name is the same value as tags key.
                "name": "users",
                "description": "Operations with users. The **login** logic is also here.",
            },
            {
                # Name is the same value as tags key.
                "name": "tickets",
                "description": "Manage items. So _fancy_ they have their own docs.",
                "externalDocs": {
                    "description": "Items external docs",
                    "url": "https://fastapi.tiangolo.com/",
                },
            },
        ],
        docs_url='/api/v1/docs',
        redoc_url='/api/v1/redoc',
    )

    # Mount the static folder to the app for use in Jinja2 template.
    # usages: `{{ url_for('static', path='/styles.css') }}`
    # docs: https://fastapi.tiangolo.com/advanced/templates/
    app.mount("/static", StaticFiles(directory="backend/static"), name="static")

    # Add CORS (Cross-Origin Resource Sharing) middleware to the app.
    # ---
    # Is there any reason it is necessary to validate client-side if we just take
    # the API we've been validating before it will throw the following error Server-side
    # access to the API is allowed, so we need to define a domain. To access the API,
    # we will define CORS, which will allow more than one domain. Let us install it
    # in the API label.
    # docs: https://stackpython.co/tutorial/api-python-fastapi
    app.add_middleware(
        CORSMiddleware,

        # Define origins is a domain that allows access to more than 1 API and I
        # added it to the middleware of the app. This will affect every API.
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_methods=['*'],
        allow_headers=['*'],
        allow_credentials=True,
    )

    # Adds signed cookie-based HTTP sessions. Session information is readable but not modifiable.
    # Access or modify the session data using the request.session dictionary interface.
    # docs: https://www.starlette.io/middleware/#sessionmiddleware
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.SECRET_KEY,
        session_cookie='session',
        max_age=None,
        https_only=False,
    )

    # Middleware that logs the time every request takes.
    # docs: https://philstories.medium.com/fastapi-logging-f6237b84ea64
    @app.middleware('http')
    async def log_requests(request: Request, call_next):
        idem = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        logger.info(f"rid={idem} start request path={request.url.path}")
        start_time = time.time()
        response = await call_next(request)
        process_time = (time.time() - start_time) * 1000
        formatted_process_time = '{0:.2f}'.format(process_time)
        logger.info(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
        print(f"rid={idem} completed_in={formatted_process_time}ms status_code={response.status_code}")
        return response

    # Add internal routers to the app like admin
    # app.include_router(
    #     admin,
    #     prefix="/admin",
    #     tags=["admin"],
    #     dependencies=[Depends(get_token_header)],
    #     responses={418: {"description": "I'm a teapot"}},
    # )

    # Add routers to the application
    from .routers import api_router
    from .routers import ticket_view
    from .routers import user_view
    app.include_router(api_router, prefix=f'/api/v{settings.APP_VERSION}')
    app.include_router(ticket_view)
    app.include_router(user_view)

    @app.get("/", include_in_schema=False)
    def index() -> JSONResponse:
        return JSONResponse({"message": "Hello World"})

    @app.get(f"/api/v{settings.APP_VERSION}/health", include_in_schema=False)
    async def health() -> JSONResponse:
        return JSONResponse({"message": "It worked!!"})

    # Define event handlers (functions) that need to be executed before the application
    # starts up, or when the application is shutting down.
    # docs: https://fastapi.tiangolo.com/advanced/events/
    @app.on_event("startup")
    async def startup():
        """Handlers event before app start-up"""
        from .database import async_engine
        from .database import Base

        print("Start starting up event ... ")
        # Drop and Create tables in database without async
        async with async_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    @app.on_event("shutdown")
    def shutdown_event():
        """Handlers event before app shutting-down"""
        print("Start shutting down event ... ")

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return PlainTextResponse(str(exc.detail), status_code=exc.status_code)

    # RequestValidationError is a sub-class of Pydantic's ValidationError
    # docs: https://fastapi.tiangolo.com/tutorial/handling-errors/
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    return app

