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

import logging
import uuid

from a10_openstack_lib.resources import a10_device_instance as a10_device_instance_resources
from neutron.db import common_db_mixin

from a10_neutron_lbaas import a10_config
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.neutron_ext.common import resources
from a10_neutron_lbaas.neutron_ext.extensions import a10DeviceInstance


LOG = logging.getLogger(__name__)


def _uuid_str():
    return str(uuid.uuid4())


class A10DeviceInstanceDbMixin(common_db_mixin.CommonDbMixin,
                               a10DeviceInstance.A10DeviceInstancePluginBase):

    def __init__(self, *args, **kwargs):
        super(A10DeviceInstanceDbMixin, self).__init__(*args, **kwargs)
        self.config = a10_config.A10Config()

    def _get_a10_device_instance(self, context, a10_device_instance_id):
        try:
            return self._get_by_id(context, models.A10DeviceInstance, a10_device_instance_id)
        except Exception:
            raise a10DeviceInstance.A10DeviceInstanceNotFoundError(a10_device_instance_id)

    def _make_a10_device_instance_dict(self, a10_device_instance_db, fields=None):
        res = {'id': a10_device_instance_db.id,
               'name': a10_device_instance_db.name,
               'description': a10_device_instance_db.description,
               'tenant_id': a10_device_instance_db.tenant_id,
               'username': a10_device_instance_db.username,
               'password': a10_device_instance_db.password,
               'api_version': a10_device_instance_db.api_version,
               'protocol': a10_device_instance_db.protocol,
               'port': a10_device_instance_db.port,
               'autosnat': a10_device_instance_db.autosnat,
               'v_method': a10_device_instance_db.v_method,
               'shared_partition': a10_device_instance_db.shared_partition,
               'use_float': a10_device_instance_db.use_float,
               'default_virtual_server_vrid': a10_device_instance_db.default_virtual_server_vrid,
               'ipinip': a10_device_instance_db.ipinip,
               # Not all device records are nova instances
               'nova_instance_id': a10_device_instance_db.nova_instance_id,
               'host': a10_device_instance_db.host,
               'write_memory': a10_device_instance_db.write_memory}
        return self._fields(res, fields)

    def _get_body(self, a10_device_instance):
        body = a10_device_instance[a10_device_instance_resources.RESOURCE]
        return resources.remove_attributes_not_specified(body)

    def create_a10_device_instance(self, context, a10_device_instance):
        body = self._get_body(a10_device_instance)
        with context.session.begin(subtransactions=True):
            instance_record = models.A10DeviceInstance(
                id=_uuid_str(),
                tenant_id=context.tenant_id,
                name=body.get('name', ''),
                description=body.get('description', ''),
                username=body['username'],
                password=body['password'],
                api_version=body['api_version'],
                protocol=body['protocol'],
                port=body['port'],
                autosnat=body['autosnat'],
                v_method=body['v_method'],
                shared_partition=body['shared_partition'],
                use_float=body['use_float'],
                default_virtual_server_vrid=body['default_virtual_server_vrid'],
                ipinip=body['ipinip'],
                # Not all device records are nova instances
                nova_instance_id=body.get('nova_instance_id'),
                write_memory=body.get('write_memory', False),
                host=body['host'])
            context.session.add(instance_record)

        return self._make_a10_device_instance_dict(instance_record)

    def get_a10_device_instance(self, context, a10_device_instance_id, fields=None):
        instance = self._get_a10_device_instance(context, a10_device_instance_id)
        return self._make_a10_device_instance_dict(instance, fields)

    def get_a10_device_instances(self, context, filters=None, fields=None,
                                 sorts=None, limit=None, marker=None,
                                 page_reverse=False):
        LOG.debug("A10DeviceInstanceDbMixin:get_a10_device_instances() tenant_id=%s" %
                  (context.tenant_id))
        return self._get_collection(context, models.A10DeviceInstance,
                                    self._make_a10_device_instance_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)

    def delete_a10_device_instance(self, context, id):
        with context.session.begin(subtransactions=True):
            LOG.debug("A10DeviceInstanceDbMixin:delete_a10_device_instances() id=%s" %
                      (id))
            instance = self._get_by_id(context, models.A10DeviceInstance, id)
            context.session.delete(instance)

    def update_a10_device_instance(self, context, id, a10_device_instance):
        with context.session.begin(subtransactions=True):
            instance = self._get_by_id(context, models.A10DeviceInstance,
                                       id)
            instance.update(**a10_device_instance.get("a10_device_instance"))

            return self._make_a10_device_instance_dict(instance)
