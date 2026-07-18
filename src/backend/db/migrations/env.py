"""Alembic environment.

Wired to the application's own metadata and settings so migrations are the
single, versioned way the schema evolves -- replacing the hand-rolled
`ALTER TABLE ... ADD COLUMN` checks that used to accumulate in init_db().

The database URL is resolved (highest priority first) from:
  1. `-x db_url=...` on the command line (used to autogenerate against a scratch
     DB so we never point autogenerate at the real chatbot.db), then
  2. settings.DATABASE_URL (the app's configured database).
"""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Make the application package importable when Alembic runs from the repo root.
_REPO_ROOT = Path(__file__).resolve().parents[4]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from src.backend.core.config import settings  # noqa: E402
from src.backend.db.database import Base  # noqa: E402
import src.backend.db.models  # noqa: E402,F401 -- registers every table on Base.metadata

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def _database_url() -> str:
    """CLI `-x db_url=...` wins, else the app's configured DATABASE_URL."""
    return (
        context.get_x_argument(as_dictionary=True).get("db_url")
        or settings.DATABASE_URL
    )


def run_migrations_offline() -> None:
    context.configure(
        url=_database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = _database_url()
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            # SQLite can't ALTER most columns in place; batch mode rebuilds the
            # table so future column/FK migrations work on SQLite too.
            render_as_batch=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
