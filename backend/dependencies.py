from fastapi import HTTPException
from fastapi.routing import APIRoute
from fastapi.templating import Jinja2Templates
from .config import settings


async def get_query_token(token: str):
    """Get the token value from query string.

    implemented:

        ..> @router.get('...')
        ... async def index(token = Depends(get_query_token)):
        ...     return ...

    usages:

        ..> $ curl http://localhost:8000/?token=<token:string>

    """
    if token != "test":
        raise HTTPException(status_code=400, detail="No `test` token provided")


async def get_templates() -> Jinja2Templates:
    """Return Jinja2 template object for HTMLResponse in this application.

    implemented:

        .>> @router.get('...')
        ... async def display(templates: Jinja2Templates = Depends(templates)):
        ...     return ...

    """
    return Jinja2Templates(
        directory=f'{settings.BASE_DIR}/backend/templates',
        autoescape=True,

        # Strip left of spaces in any blocks of HTML template.
        lstrip_blocks=True,

        # # Handle multi-template folders in the FastAPI application with the Starlette.
        # # docs: https://accent-starlette.github.io/starlette-core/templating/
        # loader=jinja2.ChoiceLoader(
        #     [
        #         jinja2.FileSystemLoader("templates"),
        #         jinja2.PackageLoader("admin", "templates"),
        #     ]
        # )
    )


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"
