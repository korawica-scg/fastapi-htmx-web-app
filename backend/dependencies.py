from typing import Union
from fastapi import HTTPException
from fastapi.templating import Jinja2Templates


async def get_query_token(token: str):
    if token != "test":
        raise HTTPException(status_code=400, detail="No `test` token provided")


async def common_parameters(
    q: Union[str, None] = None, skip: int = 0, limit: int = 100
):
    return {"q": q, "skip": skip, "limit": limit}


def templates() -> Jinja2Templates:
    """
    usages:

        .>> @router.get('...')
        ... async def display(templates: Jinja2Templates = Depends(templates)):
        ...

    """
    return Jinja2Templates(
        directory='/templates',
        autoescape=True,
        lstrip_blocks=True,
        # Handle multi-template folders in the FastAPI application with the Starlette.
        # docs: https://accent-starlette.github.io/starlette-core/templating/
        # loader=jinja2.ChoiceLoader(
        #     [
        #         jinja2.FileSystemLoader("templates"),
        #         jinja2.PackageLoader("admin", "templates"),
        #     ]
        # )
    )
