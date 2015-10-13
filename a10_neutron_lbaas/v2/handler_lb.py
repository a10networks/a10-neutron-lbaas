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

import logging

from a10_neutron_lbaas import a10_common

import acos_client.errors as acos_errors
import handler_base_v2
import v2_context as a10


LOG = logging.getLogger(__name__)


class LoadbalancerHandler(handler_base_v2.HandlerBaseV2):
    def __init__(self, a10_driver, openstack_manager, neutron=None):
        super(LoadbalancerHandler, self).__init__(a10_driver, openstack_manager, neutron)
        # self.neutrondb = neutron_db.NeutronDBV1()

    def _set(self, set_method, c, context, lb):
        status = c.client.slb.UP
        if not lb.admin_state_up:
            status = c.client.slb.DOWN

        try:
            vip_meta = self.meta(lb, 'virtual_server', {})
            a10_common._set_vrid_parameter(vip_meta, c.device_cfg)
            vip_args = {
                'virtual_server': vip_meta
            }
            set_method(
                self._meta_name(lb),
                lb.vip_address,
                status,
                axapi_args=vip_args)
        except acos_errors.Exists:
            pass

    def _create(self, c, context, lb):
        self._set(c.client.slb.virtual_server.create, c, context, lb)
        self.hooks.after_vip_create(c, context, lb)

    def create(self, context, lb):
        with a10.A10WriteStatusContext(self, context, lb) as c:
            self._create(c, context, lb)
            self._create_portbinding(c, context, lb)

    def update(self, context, old_lb, lb):
        with a10.A10WriteStatusContext(self, context, lb) as c:
            self._set(c.client.slb.virtual_server.update, c, context, lb)
            self.hooks.after_vip_update(c, context, lb)

    def _delete(self, c, context, lb):
        c.client.slb.virtual_server.delete(self._meta_name(lb))

    def delete(self, context, lb):
        with a10.A10DeleteContext(self, context, lb) as c:
            self._delete(c, context, lb)
            self.hooks.after_vip_delete(c, context, lb)

    def stats(self, context, lb):
        pass

    def refresh(self, context, lb):
        pass

    def _create_portbinding(self, c, context, lb):
        hostname = c.a10_driver.device_info["name"] or ""
        self.neutron.portbindingport_create_or_update_from_vip_id(context,
                                                                  lb.vip_port["id"],
                                                                  hostname)
