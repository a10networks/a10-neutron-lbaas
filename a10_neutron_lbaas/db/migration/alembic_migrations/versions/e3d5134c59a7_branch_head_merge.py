"""Branch head merge

Revision ID: e3d5134c59a7
Revises: 08dacae1fb67, bc5626a5af2a
Create Date: 2016-12-13 18:33:01.305065

"""

# revision identifiers, used by Alembic.
revision = 'e3d5134c59a7'
down_revision = ('08dacae1fb67', 'bc5626a5af2a')
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    pass


def downgrade():
    pass
