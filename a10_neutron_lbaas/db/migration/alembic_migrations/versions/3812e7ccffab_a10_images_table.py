# Copyright 2015,  A10 Networks
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""a10_images table

Revision ID: 3812e7ccffab
Revises: 2c45cb7e1c1d
Create Date: 2015-12-01 17:43:33.695033

"""

# revision identifiers, used by Alembic.
revision = '3812e7ccffab'
down_revision = '2c45cb7e1c1d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'a10_images',
        sa.Column('id',
                  sa.String(36),
                  primary_key=True,
                  nullable=False),
        sa.Column('tenant_id', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('image_id', sa.String(36), nullable=False),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('api_version', sa.String(12), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('password', sa.String(255), nullable=False)
    )


def downgrade():
    op.drop_table('a10_images')
