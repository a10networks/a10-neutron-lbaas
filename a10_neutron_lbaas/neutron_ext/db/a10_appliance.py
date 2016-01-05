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

import neutron.db.common_db_mixin as common_db_mixin
from oslo_log import log as logging

import a10_neutron_lbaas.db.models as models
import a10_neutron_lbaas.neutron_ext.extensions.a10Appliance as a10Appliance
from a10_neutron_lbaas_client.resources import a10_appliance as a10_appliance_resources

LOG = logging.getLogger(__name__)


class A10ApplianceDbMixin(common_db_mixin.CommonDbMixin, a10Appliance.A10AppliancePluginBase):

    def _get_a10_appliance(self, context, a10_appliance_id):
        try:
            return self._get_by_id(context, models.A10ApplianceDB, a10_appliance_id)
        except Exception:
            raise a10Appliance.A10ApplianceNotFoundError(a10_appliance_id)

    def _make_a10_appliance_dict(self, a10_appliance_db, fields=None):
        res = {'id': a10_appliance_db['id'],
               'name': a10_appliance_db['name'],
               'tenant_id': a10_appliance_db['tenant_id'],
               'description': a10_appliance_db['description'],
               'host': a10_appliance_db['host'],
               'api_version': a10_appliance_db['api_version'],
               'username': a10_appliance_db['username'],
               'password': a10_appliance_db['password']}
        return self._fields(res, fields)

    def _ensure_a10_appliance_not_in_use(self, context, a10_appliance_id):
        with context.session.begin(subtransactions=True):
            slbs = context.session.query(models.A10SLB).\
                filter_by(a10_appliance_id=a10_appliance_id).\
                count()
            LOG.debug(
                "A10ApplianceDbMixin:_ensure_a10_appliance_not_in_use(): id={0}, len={1}".
                format(a10_appliance_id, slbs))

        if slbs > 0:
            raise a10Appliance.A10ApplianceInUseError(a10_appliance_id)

    def create_a10_appliance(self, context, a10_appliance):
        body = a10_appliance[a10_appliance_resources.RESOURCE]
        with context.session.begin(subtransactions=True):
            appliance_record = models.A10ApplianceDB(
                id=models.uuid_str(),
                name=body['name'],
                description=body['description'],
                host=body['host'],
                api_version=body['api_version'],
                username=body['username'],
                password=body['password'],
                tenant_id=context.tenant_id)
            context.session.add(appliance_record)

        return self._make_a10_appliance_dict(appliance_record)

    def update_a10_appliance(self, context, a10_appliance_id, a10_appliance):
        data = a10_appliance[a10_appliance_resources.RESOURCE]
        with context.session.begin(subtransactions=True):
            a10_appliance_db = self._get_a10_appliance(context, a10_appliance_id)
            a10_appliance_db.update(data)

        return self._make_a10_appliance_dict(a10_appliance_db)

    def delete_a10_appliance(self, context, a10_appliance_id):
        with context.session.begin(subtransactions=True):
            self._ensure_a10_appliance_not_in_use(context, a10_appliance_id)
            LOG.debug("A10ApplianceDbMixin:delete_a10_appliance(): a10_appliance_id={0}".format(
                a10_appliance_id))
            appliance = self._get_a10_appliance(context, a10_appliance_id)
            # Remove tenant affinities
            # The tenant partitions on the appliance should have been removed
            # when the last object was deleted
            context.session.query(models.A10TenantAppliance).\
                filter_by(a10_appliance_id=appliance.id).\
                delete()
            context.session.delete(appliance)

    def get_a10_appliance(self, context, a10_appliance_id, fields=None):
        appliance = self._get_a10_appliance(context, a10_appliance_id)
        return self._make_a10_appliance_dict(appliance, fields)

    def get_a10_appliances(self, context, filters=None, fields=None,
                           sorts=None, limit=None, marker=None,
                           page_reverse=False):
        LOG.debug("A10ApplianceDbMixin:get_a10_appliances() tenant_id=%s" % context.tenant_id)
        return self._get_collection(context, models.A10ApplianceDB,
                                    self._make_a10_appliance_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)
