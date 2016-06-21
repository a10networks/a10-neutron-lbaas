"""v2 SSL Certificates

Revision ID: 08dacae1fb67
Revises: 2a280aba7701
Create Date: 2016-06-21 06:18:58.773598

"""

# revision identifiers, used by Alembic.
revision = '08dacae1fb67'
down_revision = '2a280aba7701'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'a10_certificatelistenerbindings'
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('certificate_id', sa.String(36), nullable=False),
        sa.Column('listener_id', sa.String(36), nullable=False)
    )


def downgrade():
    op.drop_table('a10_certificatelistenerbindings')