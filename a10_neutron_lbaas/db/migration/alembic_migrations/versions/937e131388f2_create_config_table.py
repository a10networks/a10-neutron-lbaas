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

"""create config table

Revision ID: 937e131388f2
Revises: c4e1caaa618d
Create Date: 2017-09-04 02:25:21.904385

"""

# revision identifiers, used by Alembic.
revision = '937e131388f2'
down_revision = 'c4e1caaa618d'
branch_labels = None
depends_on = None

from alembic import op  # noqa
import sqlalchemy as sa  # noqa


def upgrade():
    try:
        op.rename_table(
            'a10_device_instances',
            'a10_devices'
        )
    except Exception:
        pass

    op.create_table(
        'a10_device_key',
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.String(1024), nullable=False),
    )

    op.create_table(
        'a10_device_value',
        sa.Column('tenant_id', sa.String(36), nullable=False),
        sa.Column('id', sa.String(36), primary_key=True, nullable=False),
        sa.Column('created_at', sa.DateTime, nullable=False),
        sa.Column('updated_at', sa.DateTime, nullable=False),
        sa.Column('associated_obj_id', sa.String(36),
                  sa.ForeignKey('a10_devices.id'), nullable=False),
        sa.Column('key_id', sa.String(36), sa.ForeignKey('a10_device_key.id'),
                  nullable=False),
        sa.Column('value', sa.String(255), nullable=False),
    )


def downgrade():
    try:
        op.rename_table(
            'a10_devices',
            'a10_device_instances'
        )
    except Exception:
        pass

    op.drop_table('a10_device_value')
    op.drop_table('a10_device_key')
