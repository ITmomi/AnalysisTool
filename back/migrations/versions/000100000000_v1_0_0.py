"""V1.0.0

Revision ID: 833270ea9330
Revises: 
Create Date: 2022-01-07 08:50:36.949983

"""
from alembic import op
import sqlalchemy as sa
import logging

from config import app_config
from migrations.resource.v1_0_0.initialize import init_db_v1_0_0

logger = logging.getLogger(app_config.LOG)


# revision identifiers, used by Alembic.
revision = '000100000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    logger.info(f'upgrade start {revision}')
    init_db_v1_0_0()
    logger.info(f'upgrade end {revision}')


def downgrade():
    pass



