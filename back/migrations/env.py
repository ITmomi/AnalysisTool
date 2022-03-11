from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context
import logging

import configparser
from config.app_config import DB_CONFIG_PATH
from dao import init_database, get_dbinfo
import psycopg2 as pg2
from config import app_config


logger = logging.getLogger(app_config.LOG)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
alembic_config = context.config

if not alembic_config.get_main_option('sqlalchemy.url'):
    init_database()

    db_config = get_dbinfo()
    with pg2.connect(**db_config) as conn:
        conn.autocommit = True
        with conn.cursor() as cur:
            cur.execute("SELECT EXISTS "
                        "(SELECT FROM information_schema.tables WHERE table_schema='%s' AND table_name='%s')"
                        % ('settings', 'information'))

            rows = cur.fetchone()
            if rows[0] is True:
                cur.execute("SELECT EXISTS "
                            "(SELECT FROM information_schema.tables WHERE table_schema='%s' AND table_name='%s')"
                            % ('migration', 'alembic_version'))

                rows = cur.fetchone()
                if rows[0] is False:
                    cur.execute('CREATE SCHEMA IF NOT EXISTS {schema}'.format(schema='migration'))
                    cur.execute("create table migration.alembic_version "
                                "(version_num varchar(32) not null constraint alembic_version_pkc primary key)")

                    cur.execute("select value from settings.information where key='version'")
                    version = cur.fetchone()[0]
                    logger.info(f'settings.information table exists. version : {version}')

                    [major, minor, rev] = version.split(sep='.')
                    major = '{0:04x}'.format(int(major))
                    minor = '{0:04x}'.format(int(minor))
                    rev = '{0:04x}'.format(int(rev))
                    version = f'{major}{minor}{rev}'

                    query = 'insert into migration.alembic_version(version_num) values(%s)'
                    cur.execute(query, tuple([version]))

    dbname = db_config['dbname']
    user = db_config['user']
    host = db_config['host']
    password = db_config['password']
    port = db_config['port']

    alembic_config.set_main_option('sqlalchemy.url', f'postgresql://{user}:{password}@localhost:{port}/{dbname}')

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# fileConfig(alembic_config.config_file_name)
# fileConfig('alembic.ini')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = alembic_config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        alembic_config.get_section(alembic_config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            include_schema=True,
            version_table_schema='migration'
        )

        connection.execute('CREATE SCHEMA IF NOT EXISTS {schema}'.format(schema='migration'))

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
