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

"""lbaasv2 slb table

Revision ID: 3f6b367e2485
Revises: 1f771cf50bd1
Create Date: 2015-10-21 21:34:51.435115

"""

# revision identifiers, used by Alembic.
revision = '3f6b367e2485'
down_revision = '1f771cf50bd1'
branch_labels = None
depends_on = '3f3f44eb3cd3'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'a10_slb_v2',
        sa.Column('id',
                  sa.String(36),
                  sa.ForeignKey('a10_slb.id'),
                  primary_key=True,
                  nullable=False),
        sa.Column('lbaas_loadbalancer_id',
                  sa.String(36),
                  sa.ForeignKey('lbaas_loadbalancers.id'),
                  unique=True,
                  nullable=False)
    )


def downgrade():
    op.drop_table('a10_slb_v2')
