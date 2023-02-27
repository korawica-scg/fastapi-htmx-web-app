FastAPI and HTMX web application
===

This application will show that TODO application.

Start running this FastAPI application by follow command line:

```shell
$ pip install -r requirements.txt
$ uvicorn main:app --reload
```

```shell
$ curl http://localhost:8000/?token=test
```

Structure
---

The application structure design

- models: Data model that use ORM Object with SQLAlchemy
- schemas: Pydantic Base Model for create data class for models
- crud: Database CRUD process that control Create/Read/Update/Delete to the model.

- Optional
    - viewmodels - View models for gathering data for pages and partials.