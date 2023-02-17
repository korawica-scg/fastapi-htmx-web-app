# Pull base image
FROM python:3.9

# Set environment varibles
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Method: 01 ---------------------
#RUN addgroup --system fastapi \
#    && adduser --system --ingroup fastapi fastapi
#COPY --chown=fastapi:fastapi ./requirements.txt /requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#COPY --chown=fastapi:fastapi ./start /start
#RUN sed -i 's/\r$//g' /start
#RUN chmod +x /start
#COPY --chown=fastapi:fastapi . /app
#WORKDIR /app

# >>> start file
#!/bin/bash
  #
  #set -o errexit
  #set -o pipefail
  #set -o nounset
  #
  #uvicorn main:app --port 8001 --host 0.0.0.0


# Method: 02 ---------------------
WORKDIR /code/

# Install dependencies
RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install --system --dev

COPY . /code/

EXPOSE 8000