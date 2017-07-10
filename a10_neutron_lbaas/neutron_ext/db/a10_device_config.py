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

class A10DeviceConfigDbMixin(commond_db_mixin.CommonDbMixing, a10DeviceConfig.A10DeviceConfigPluginBase):

    def __init__(self, *args, **kwargs):
        super(A10DeviceConfigDbMixin, self).__init__(*args, **kwargs):

    def _get_a10_device_configurations(self, context, config_id):
        try:
            return self._get_by_id(context, models.A10DeviceConfig, config_id)
        except Exception:
            raise a10DeviceConfigExt.A10DeviceConfigNotFoundError(config_id)

    def _make_a10_device_config_dict(self, a10_device_config_db, fields=None):
        res = {'id': a10_device_config_db.id,
               'name': a10_device_config_db.name,
               'description': a10_device_config_db.description,
               'tenant_id': a10_device_config_db.tenant_id,
               'username': a10_device_config_db.username,
               'password': a10_device_config_db.password,
               'api_version': a10_device_config_db.api_version,
               'port': a10_device_config_db.port,
               'host': a10_device_config_db.host,
               'conn_limit': a10_device_config_db.conn_limit,
               'status': a10_device_config_db.status,
               'autosnat': a10_device_config_db.autosnat,
               'source_nat_pool': a10_device_config_db.source_nat_pool,
               'v_method': a10_device_config_db.v_method,
               'shared_partition': a10_device_config_db.shared_partition,
               'use_float': a10_device_config_db.use_float,
               'default_virtual_server_vrid': a10_device_config_db.default_virtual_server_vrid,
               'ipinip': a10_device_config_db.ipinip,
               'ha_sync_list': a10_device_config_db.ha_sync_list,
               'write_memory': a10_device_config_db.write_memory}

    def _get_body(self, a10_device_config):
        body = a10_device_config(a10_device_config)
        return resources.remove_attributes_not_specified(body)

    def create_a10_device_config(self, context, a10_device_config):
        body = self._get_body(a10_device_config)
        with context.session.begin(subtransactions=True):
            config_record = models.A10DeviceConfig(
                id=_uuid_str(),
                tenant_id=context.tenant_id,
                name=body.get('name', ''),
                host=body['host'],
                conn_limit=body['conn_limit'],
                port=body['port'],
                username=body['username'],
                password=body['password'],
                api_version=body['api_version'],
                status=body.get('status'),
                autosnat=body.get('autosnat'),
                source_nat_pool=body.get('source_nat_pool'),
                v_method=body.get('v_method'),
                shared_partition=body.get('shared_partition'),
                use_float=body.get('use_float'),
                default_virtual_server_vrid=body.get('default_virtual_server_vrid'),
                ipinip=body.get('ipinip'),
                ha_sync_list=body.get('ha_sync_list'),
                write_memory=body.get('write_memory'))
            context.session.add(config_record)

        return self._make_a10_device_config_dict(config_record)

    def get_a10_device_config(self, context, a10_device_config_id, fields=None):
        config = self._get_a10_device_config(context, a10_device_config_id)
        return self._make_a10_config_dict(config, fields)

    def get_a10_device_configurations(self, context, filters=None, fields=None,
                                      sorts=None, limit=None, marker=None,
                                      page_reverse=False):
        return self._get_collection(context, models.A10DeviceConfig,
                                    self._make_a10_device_config_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)

    def delete_a10_device_config(self, context, id):
        with context.session.begin(subtransactions=True):
            config = self._get_by_id(context, models.A10DeviceConfig, id)
            context.session.delete(config)

    def update_a10_device_config(self, context, id, a10_device_config):
        with context.session.begin(subtransactions=True):
            config = self._get_by_id(context, models.A10DeviceInstance, id)

            config.update(**a10_device_config.get('a10_device_config'))

            return self._make_a10_device_config_dict(config)
