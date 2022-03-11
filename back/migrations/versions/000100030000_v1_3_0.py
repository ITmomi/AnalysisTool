"""v1_3_0

Revision ID: 1cd667fe64ce
Revises: 53108c5a7235
Create Date: 2022-01-10 14:31:05.072516

"""
from alembic import op
import sqlalchemy as sa
import logging

from config import app_config
from migrations.resource.v1_3_0.initialize import init_db_v1_3_0, import_rules, import_function


logger = logging.getLogger(app_config.LOG)

# revision identifiers, used by Alembic.
revision = '000100030000'
down_revision = '000100020001'
branch_labels = None
depends_on = None


def upgrade():
    logger.info(f'upgrade start {revision}')
    init_db_v1_3_0()
    import_rules()
    import_function()
    logger.info(f'upgrade end {revision}')


def downgrade():
    pass
