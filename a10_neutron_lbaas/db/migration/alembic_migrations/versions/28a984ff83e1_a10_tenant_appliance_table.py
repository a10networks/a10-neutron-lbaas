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

"""a10_tenant_appliance table

Revision ID: 28a984ff83e1
Revises: 3f3f44eb3cd3
Create Date: 2015-11-05 17:12:42.616176

"""

# revision identifiers, used by Alembic.
revision = '28a984ff83e1'
down_revision = '3f3f44eb3cd3'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'a10_tenant_appliance',
        sa.Column('tenant_id', sa.String(255), primary_key=True, nullable=False),
        sa.Column('a10_appliance_id',
                  sa.String(36),
                  sa.ForeignKey('a10_appliances_slb.id'),
                  nullable=False)
    )


def downgrade():
    op.drop_table('a10_tenant_appliance')
