from fastapi import FastAPI
# from fastapi.logger import logger
from backend.app import create_app
import uvicorn
import logging

# gunicorn_logger = logging.getLogger('gunicorn.error')
# logger.handlers = gunicorn_logger.handlers


app: FastAPI = create_app()


if __name__ == '__main__':
    # logger.setLevel(logging.DEBUG)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
else:
    # logger.setLevel(gunicorn_logger.level)
    ...
