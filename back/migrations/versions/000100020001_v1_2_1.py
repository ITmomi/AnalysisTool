"""v1_2_1

Revision ID: 53108c5a7235
Revises: 000100020000
Create Date: 2022-01-10 14:30:53.445813

"""
from alembic import op
import sqlalchemy as sa
import logging

from config import app_config
from migrations.resource.v1_2_1.initialize import init_db_v1_2_1


logger = logging.getLogger(app_config.LOG)

# revision identifiers, used by Alembic.
revision = '000100020001'
down_revision = '000100020000'
branch_labels = None
depends_on = None


def upgrade():
    logger.info(f'upgrade start {revision}')
    init_db_v1_2_1()
    logger.info(f'upgrade end {revision}')


def downgrade():
    pass
