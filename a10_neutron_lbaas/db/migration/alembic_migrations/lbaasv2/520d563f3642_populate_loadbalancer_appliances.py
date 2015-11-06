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

"""populate loadbalancer appliances

Revision ID: 520d563f3642
Revises: 3f6b367e2485
Create Date: 2015-10-28 20:01:13.914029

"""

# revision identifiers, used by Alembic.
revision = '520d563f3642'
down_revision = '3f6b367e2485'
branch_labels = None
depends_on = None

from alembic import context
from alembic import op

from a10_neutron_lbaas import A10OpenstackLBV2
from a10_neutron_lbaas.db.migration.step import initialize_a10_slb_v2
import neutron.plugins.common.constants as constants


def upgrade():
    for provider, driver in context.config.drivers[constants.LOADBALANCERV2][0].items():
        if hasattr(driver, 'a10') and isinstance(driver.a10, A10OpenstackLBV2):
            upgrade_driver(provider, driver.a10)


def upgrade_driver(provider, a10):
    conn = op.get_bind()
    initialize_a10_slb_v2(conn, provider, a10)


def downgrade():
    pass
