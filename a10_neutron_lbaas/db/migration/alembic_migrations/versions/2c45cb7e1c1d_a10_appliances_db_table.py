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

"""a10_appliances_db table

Revision ID: 2c45cb7e1c1d
Revises: 28a984ff83e1
Create Date: 2015-11-23 18:10:42.954538

"""

# revision identifiers, used by Alembic.
revision = '2c45cb7e1c1d'
down_revision = '28a984ff83e1'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'a10_appliances_db',
        sa.Column('id',
                  sa.String(36),
                  sa.ForeignKey('a10_appliances_slb.id'),
                  primary_key=True,
                  nullable=False),
        sa.Column('tenant_id', sa.String(255), nullable=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('description', sa.String(255), nullable=True),
        sa.Column('host', sa.String(255), nullable=False),
        sa.Column('api_version', sa.String(12), nullable=False),
        sa.Column('username', sa.String(255), nullable=False),
        sa.Column('password', sa.String(255), nullable=False),
        sa.Column('protocol', sa.String(255), nullable=False),
        sa.Column('port', sa.Integer, nullable=False)
    )


def downgrade():
    op.drop_table('a10_appliances_db')
