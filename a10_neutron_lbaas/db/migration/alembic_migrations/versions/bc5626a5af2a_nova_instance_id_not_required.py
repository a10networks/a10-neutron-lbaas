"""Nova instance ID not required

Revision ID: bc5626a5af2a
Revises: 3c7123f2aeba
Create Date: 2016-10-27 18:47:41.163902

"""

# revision identifiers, used by Alembic.
revision = 'bc5626a5af2a'
down_revision = '3c7123f2aeba'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('a10_device_instances',
                    sa.Column('nova_instance_id', sa.String(36), nullable=True))


def downgrade():
    op.alter_column('a10_device_instances',
                    sa.Column('nova_instance_id', sa.String(36), nullable=False))
