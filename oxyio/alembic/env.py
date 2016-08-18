# oxy.io
# File: alembic/env.py
# Desc: Alembic environment for generating migrations for oxy.io and its modules

from __future__ import with_statement

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from flask import current_app


def object_filter(module_name, obj, obj_name, type_, *args):
    '''
    Filters Alembic migrations.
    '''

    table_name = obj_name

    if hasattr(obj, 'table'):
        table_name = obj.table.name

    return table_name.startswith(module_name)


# Alembic config object, representing alembic.ini
config = context.config

# Setup logging from the config file
fileConfig(config.config_file_name)

# Set the database to that of the flask app
config.set_main_option(
    'sqlalchemy.url',
    current_app.config['SQLALCHEMY_DATABASE_URI']
)

# Set the metadata to our apps metadata
target_metadata = current_app.extensions['sqlalchemy'].db.metadata

# Get the module name
module_name = config.get_section_option('oxyio', 'module_name')

# kwargs to pass to context.configure in both online/offline modes
context_kwargs = {
    'target_metadata': target_metadata,
    'version_table': config.get_section_option('oxyio', 'versions_table'),
    'include_object': lambda *args, **kwargs: (
        object_filter(module_name, *args, **kwargs)
    )
}


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")

    context.configure(
        url=url,
        **context_kwargs
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    engine = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool
    )
    connection = engine.connect()

    context.configure(
        connection=connection,
        **context_kwargs
    )

    try:
        with context.begin_transaction():
            context.run_migrations()
    finally:
        connection.close()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
