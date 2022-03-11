from alembic import command
from alembic.config import Config
from config import app_config


def migration_db():
    alembic_cfg = Config()
    alembic_cfg.set_main_option('script_location', 'migrations')

    major = '{0:04X}'.format(int(app_config.APP_MAJOR))
    minor = '{0:04X}'.format(int(app_config.APP_MINOR))
    rev = '{0:04X}'.format(int(app_config.APP_REVISION))

    # logger = logging.getLogger(app_config.LOG)

    version = f'{major}{minor}{rev}'

    # logger.info(f'Database upgrade to {version}')
    command.upgrade(alembic_cfg, version)
