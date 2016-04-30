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

from a10_neutron_lbaas.db import api as db_api
from a10_neutron_lbaas.db import models


def find_tenant_binding_by_tenant_id(tenant_id, db_session=None):
    db = db_session or db_api.get_session()
    return db.query(models.A10TenantBinding).filter(
            models.A10TenantBinding.tenant_id == tenant_id).one_or_none()

def find_device_instances(db_session=None):
    db = db_session or db_api.get_session()
    return db.query(models.A10DeviceInstances).all()

def find_device_instance_by_name(name, db_session=None):
    db = db_session or db_api.get_session()
    return db.query(models.A10DeviceInstances).filter(
            models.A10DeviceInstances.name == name).one_or_none()
