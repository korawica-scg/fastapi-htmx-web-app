import time
import string
import random
import logging
from logging.config import dictConfig
from fastapi import FastAPI
from fastapi import Depends
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from .dependencies import get_query_token
from .config import settings

# dictConfig(settings.LOGGING_CONF)
# dictConfig({
#     "version": 1,
#     'disable_existing_loggers': True,
#     'handlers': {
#         'console': {
#             "level": 'DEBUG',
#             "class": 'logging.StreamHandler',
#             "stream": "ext://sys.stdout",
#         }
#     },
#     'root': {
#         'handlers': ['console'],
#         'level': 'DEBUG'
#     }
# })
logger = logging.getLogger(__name__)


def create_app():
    """FastAPI application factory
    :return:
    """
    # Initialize application
    app = FastAPI(
        title='FastAPI and HTMX',
        version="0.0.1",
        # dependencies=[Depends(get_query_token)],
        openapi_url='/api/v1/openapi.json',
        openapi_tags=[
            {
                "name": "users",
                "description": "Operations with users. The **login** logic is also here.",
            },
            {
                "name": "tickets",
                "description": "Manage items. So _fancy_ they have their own docs.",
                "externalDocs": {
                    "description": "Items external docs",
                    "url": "https://fastapi.tiangolo.com/",
                },
            },
        ],
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
        return response

    # Add internal routers to the app like admin
    # app.include_router(
    #     admin,
    #     prefix="/admin",
    #     tags=["admin"],
    #     dependencies=[Depends(get_token_header)],
    #     responses={418: {"description": "I'm a teapot"}},
    # )

    # Add routers to the app
    from .routers import api_router
    from .routers import ticket_view
    app.include_router(api_router, prefix=f'/api/v{settings.APP_VERSION}')
    app.include_router(ticket_view, prefix=f'/view')

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
