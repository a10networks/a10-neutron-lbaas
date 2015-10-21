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

"""core appliance and slb tables

Revision ID: 3f3f44eb3cd3
Revises:
Create Date: 2015-10-21 20:35:46.933440

"""

# revision identifiers, used by Alembic.
revision = '3f3f44eb3cd3'
down_revision = None
branch_labels = ('core',)
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'a10_appliances_slb',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('type', sa.String(50), nullable=False)
    )
    op.create_table(
        'a10_appliances_configured',
        sa.Column('id',
                  sa.String(36),
                  sa.ForeignKey('a10_appliances_slb.id'),
                  primary_key=True,
                  nullable=False),
        sa.Column('device_key', sa.String(255), nullable=False)
    )
    op.create_table(
        'a10_slb',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('a10_appliance_id',
                  sa.String(36),
                  sa.ForeignKey('a10_appliances_slb.id'),
                  nullable=False)
    )


def downgrade():
    op.drop_table('a10_slb')
    op.drop_table('a10_appliances_configured')
    op.drop_table('a10_appliances_slb')
