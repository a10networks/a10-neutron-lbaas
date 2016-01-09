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

"""Remove orphaned a10_slb_v1 slb

Revision ID: 2e7daa753e19
Revises: 5a960cad849b
Create Date: 2016-01-08 23:18:54.856154

"""

# revision identifiers, used by Alembic.
revision = '2e7daa753e19'
down_revision = '5a960cad849b'
branch_labels = None
depends_on = None

from alembic import op


def upgrade():
    conn = op.get_bind()
    conn.execute(
        "DELETE FROM a10_slb "
        "WHERE type='a10_slb_v1' "
        "AND id NOT IN (SELECT id FROM a10_slb_v1)")


def downgrade():
    pass
