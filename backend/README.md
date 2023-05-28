# Clonr backend server

to run locally, make sure you are at the root (the same level as the README.md you're reading) and run `python -m app.main` to boot up the server.

To build docker, you can just run the dockerfile here. I'll add the


## Migrations

We are using __Alembic__ for handling migrations. In order to initialize a migrations directory (done only once for the entire project, it is likely already there) run the command

`alembic init -t async migrations`.

Then in the `alembic.ini` file, update the postgres URI to match that in app.db. Also, update env.py to import from `app.db import Base`, and set the target metadata to `Base.metadata`.

To generate an initial automatic revision using alembic, run the cli command `alembic revision --autogenerate -m "<NAME_OF_REVISION>"` If alembic is not installed locally you can also do this inside of docker via `docker exec -it <result of docker ps -a> alembic revision --autogenerate -m "<name_of_revision>"`

You'll likely need to tweak the actual migration. In particular, the very first migration uses a GUID that is DB agnostic and gets around the sqlalchemy UUID issue. this can be imported from fastapi_utils.GUID or from fastapi_users_db_sqlalchemy.

Alembic seems to have some bug, where it cannot both run CLI and programmatically. In order to run the CLI commands like alembic upgrade head, you need to make sure these are the last lines in migrations/env.py
```
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
```
To run programmatically, comment the above out.

Finally, if you already have postgres running from the pre-Alembic times, you might generate empty migrations. It's best to reset the DB and that should fix it.