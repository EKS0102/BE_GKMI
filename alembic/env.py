from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from config import DATABASE_URL
from database.database import Base

# Import model agar masuk ke Base.metadata
from models.jemaat import Jemaat
from models.user import User


# =========================================================
# ALEMBIC CONFIG
# =========================================================

config = context.config


# =========================================================
# LOGGING
# =========================================================

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# =========================================================
# TARGET METADATA
# =========================================================

target_metadata = Base.metadata


# =========================================================
# OFFLINE MIGRATION
# =========================================================

def run_migrations_offline() -> None:
    url = DATABASE_URL

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={
            "paramstyle": "named"
        },
    )

    with context.begin_transaction():
        context.run_migrations()


# =========================================================
# ONLINE MIGRATION
# =========================================================

def run_migrations_online() -> None:
    configuration = config.get_section(
        config.config_ini_section,
        {}
    )

    configuration["sqlalchemy.url"] = DATABASE_URL

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:

        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


# =========================================================
# RUN
# =========================================================

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()