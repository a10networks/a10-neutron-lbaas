# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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

import json
import logging
import threading

LATE_INIT_LOCK = threading.Lock()

LOG = logging.getLogger(__name__)


class HandlerBase(object):

    def __init__(self, a10_driver):
        self.a10_driver = a10_driver
        self.openstack_driver = self.a10_driver.openstack_driver

        if self.a10_driver.provider is None:
            with LATE_INIT_LOCK:
                if self.a10_driver.provider is None:
                    for prov, driver in self.openstack_driver.plugin.drivers.items():
                        if driver is self.openstack_driver:
                            self.a10_driver._late_init(prov)
                            break

        self.hooks = a10_driver.hooks

    def _model_type(self):
        return self.__class__.__name__.lower().replace('handler', '')

    def _name(self, obj):
        if isinstance(obj, dict):
            return obj['id']
        else:
            return obj.id

    def _meta_name(self, lbaas_obj):
        return self.meta(lbaas_obj, 'name', self._name(lbaas_obj))

    def _pool_name(self, context, pool_id=None, pool=None):
        if not pool:
            pool = self.neutron.pool_get(context, pool_id)
        if not pool_id:
            pool_id = pool.id
        return self.meta(pool, 'name', pool_id)

    def meta(self, lbaas_obj, key, default):
        if isinstance(lbaas_obj, dict):
            m = lbaas_obj.get('a10_meta', '{}')
        elif hasattr(lbaas_obj, 'a10_meta'):
            m = lbaas_obj.a10_meta
        else:
            return default
        try:
            d = json.loads(m)
        except Exception:
            return default
        return d.get(key, default)
