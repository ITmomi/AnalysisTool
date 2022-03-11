"""v1_1_0

Revision ID: 17ea2217592a
Revises: 833270ea9330
Create Date: 2022-01-07 10:12:44.886435

"""
from alembic import op
import sqlalchemy as sa
import logging

from config import app_config
from migrations.resource.v1_1_0.initialize import init_db_v1_1_0


logger = logging.getLogger(app_config.LOG)

# revision identifiers, used by Alembic.
revision = '000100010000'
down_revision = '000100000000'
branch_labels = None
depends_on = None


def upgrade():
    logger.info(f'upgrade start {revision}')
    init_db_v1_1_0()
    logger.info(f'upgrade end {revision}')


def downgrade():
    pass


