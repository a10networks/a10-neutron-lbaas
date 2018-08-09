#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software #    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

"""Remove columns moving to kv tables

Revision ID: f0f0f3640e8d
Revises: 937e131388f2
Create Date: 2018-08-28 04:49:14.985299

"""

# revision identifiers, used by Alembic.
revision = 'f0f0f3640e8d'
down_revision = '937e131388f2'
branch_labels = None
depends_on = None

from alembic import op  # noqa
import sqlalchemy as sa  # noqa


def upgrade():
    op.drop_column('a10_devices', 'autosnat')
    op.drop_column('a10_devices', 'default_virtual_server_vrid')
    op.drop_column('a10_devices', 'ipinip')
    op.drop_column('a10_devices', 'shared_partition')
    op.drop_column('a10_devices', 'use_float')
    op.drop_column('a10_devices', 'v_method')
    op.drop_column('a10_devices', 'write_memory')
    op.alter_column('a10_device_value', 'value', existing_type=sa.String(255), nullable=True)

def downgrade():
    op.add_column('a10_devices',
                  sa.Column('autosnat', sa.Boolean(), nullable=False)
                  )
    op.add_column('a10_devices',
                  sa.Column('default_virtual_server_vrid', sa.Integer,
                            nullable=True)
                  )
    op.add_column('a10_devices',
                  sa.Column('ipinip', sa.Boolean(), nullable=False)
                  )
    op.add_column('a10_devices',
                  sa.Column('shared_partition', sa.String(1024),
                            nullable=False)
                  )
    op.add_column('a10_devices',
                  sa.Column('use_float', sa.Boolean(), nullable=False)
                  )
    op.add_column('a10_devices',
                  sa.Column('v_method', sa.String(32), nullable=False)
                  )
    op.add_column('a10_devices',
                  sa.Column('write_memory', sa.Boolean(), nullable=False)
                  )
    op.alter_column('a10_device_value', 'value', existing_type=sa.String(255), nullable=False)
