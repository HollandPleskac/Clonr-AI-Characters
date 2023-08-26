# Clonr backend server

to run locally, make sure you are at the root (the same level as the README.md you're reading) and run `python -m app.main` to boot up the server.

To build docker, you can just run the dockerfile here. I'll add the

## Migrations

We are using **Alembic** for handling migrations. In order to initialize a migrations directory (done only once for the entire project, it is likely already there) run the command

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

## Downloading models

It is advised to use the HF Downloader. This will launch multiple download threads, give progress bars for each, allow resumption from interrupted downloads, and also verify checksums upon completion of the download. You can also use a regex to filter out which files from a repository that you want (good idea for RWKV stuff, that guy is bonkers crazy)

An example flow looks like:

1. Go to huggingface spaces and copy the name of the repository. The format should look something like TheBlock/llama-7b-instruct
2. Run a script like the following

```python
from pathlib import Path
from clonr.utils import HFDownloader


if __name__ == "__main__":
    dl = HFDownloader()
    model_name = 'TheBloke/open-llama-7b-open-instruct-GGML'

    # pick your path
    output_dir = Path.home() / "llm-models" / "open-llama-7b-instruct"

    # This will download only the three types of quantized GGMLs listed below
    regex_filter = r'.*(q2_K|q5_1|q5_K_M).*'
    dl.download(
        model_name,
        output_dir=str(output_dir.resolve()), regex_filter=regex_filter
    )
```

## Testing

### Stripe

Properly testing the Stripe connection is difficult, since we are relying on the pricing table for creating customer checkout sessions. To test stripe, you must first install the Stripe CLI, then setup your own device as a webhook listener via
`stripe listen --forward-to localhost:8000/stripe/webhook --events "checkout.session.completed","customer.subscription.updated","customer.subscription.deleted"`

afterward, spin up the backend and stuff with docker compose. Finally, you can run python test_stripe.py to make sure everything is good
