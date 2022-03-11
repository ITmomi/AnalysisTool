"""v1_2_0

Revision ID: ec4de57515dd
Revises: 17ea2217592a
Create Date: 2022-01-07 10:12:52.093400

"""
from alembic import op
import sqlalchemy as sa
import logging

from config import app_config
from migrations.resource.v1_2_0.initialize import init_db_v1_2_0


logger = logging.getLogger(app_config.LOG)

# revision identifiers, used by Alembic.
revision = '000100020000'
down_revision = '000100010000'
branch_labels = None
depends_on = None


def upgrade():
    logger.info(f'upgrade start {revision}')
    init_db_v1_2_0()
    logger.info(f'upgrade end {revision}')


def downgrade():
    pass
