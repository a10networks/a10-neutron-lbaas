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

"""populate vip appliances

Revision ID: 4657b284f454
Revises: 38bfe6f0fe53
Create Date: 2015-10-26 21:18:29.541590

"""

# revision identifiers, used by Alembic.
revision = '4657b284f454'
down_revision = '38bfe6f0fe53'
branch_labels = None
depends_on = None


def upgrade():
    """This step moved to populate vip, tenant appliances
    to also populate the a10_tenant_appliance table
    """

    pass


def downgrade():
    pass
