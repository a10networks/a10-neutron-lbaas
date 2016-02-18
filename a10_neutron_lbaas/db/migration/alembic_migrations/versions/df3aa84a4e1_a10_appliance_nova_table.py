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

"""A10 Appliance Nova Column 

Revision ID: df3aa84a4e1
Revises: 2c45cb7e1c1d
Create Date: 2016-02-13 00:08:18.780231

"""

# revision identifiers, used by Alembic.
revision = 'df3aa84a4e1'
down_revision = '2c45cb7e1c1d'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("a10_appliances_db", 
        sa.Column("nova_instance_id", sa.String(36), nullable=True)
    )


def downgrade():
    op.drop_column("a10_appliances_db", "nova_instance_id")
