# Copyright 2014 A10 Networks
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

import acos_client.errors as acos_errors

import handler_base_v2
import v2_context as a10

LOG = logging.getLogger(__name__)


class LoadbalancerHandler(handler_base_v2.HandlerBaseV2):

    def _set(self, set_method, c, context, lb):
        status = c.client.slb.UP
        if not lb.admin_state_up:
            status = c.client.slb.DOWN

        try:
            vip_meta = self.meta(lb, 'virtual_server', {})
            os_name = lb.name
            set_method(
                self._meta_name(lb),
                lb.vip_address,
                arp_disable=c.device_cfg.get('arp_disable'),
                status=status,
                vrid=c.device_cfg.get('default_virtual_server_vrid'),
                config_defaults=self._get_config_defaults(c, os_name),
                axapi_body=vip_meta)
        except acos_errors.Exists:
            pass

    def _create(self, c, context, lb):
        self._set(c.client.slb.virtual_server.create, c, context, lb)

    def _stats_v21(self, c, resp):
        if resp["virtual_server_stat"].get("vport_stat_list"):
            for stat in resp["virtual_server_stat"]["vport_stat_list"]:
                vs = c.client.slb.virtual_service.get(stat["name"])
                if vs["virtual_service"]["service_group"]:
                    pool = c.client.slb.service_group.stats(vs["virtual_service"]["service_group"])
                    stat["pool_stat_list"] = pool["service_group_stat"]

            resp["virtual_server_stat"]["listener_stat"] = resp["virtual_server_stat"].get(
                "vport_stat_list")
            del resp["virtual_server_stat"]["vport_stat_list"]

        resp["loadbalancer_stat"] = resp["virtual_server_stat"]
        del resp["virtual_server_stat"]

        return {
            "bytes_in": resp["loadbalancer_stat"]["req_bytes"],
            "bytes_out": resp["loadbalancer_stat"]["resp_bytes"],
            "active_connections": resp["loadbalancer_stat"]["cur_conns"],
            "total_connections": resp["loadbalancer_stat"]["tot_conns"],
            "extended_stats": resp}

    def _stats_v30(self, c, resp, name):
        stats = {}
        for ports in resp['port-list']:
            for k, v in ports['stats'].items():
                if stats.get(k):
                    stats[k] += v
                else:
                    stats[k] = v

        resp["loadbalancer_stat"] = stats
        resp["loadbalancer_stat"]["listener_stat"] = resp["port-list"]
        del resp["port-list"]

        virt_serv = c.client.slb.virtual_server.get(name)
        for port in virt_serv['virtual-server']['port-list']:
            if port.get("service-group"):
                pool = c.client.slb.service_group.stats(port["service-group"])
                resp["loadbalancer_stat"]["pool_stat_list"] = pool["service-group"]["stats"]
                members = c.client.slb.service_group.get(port["service-group"] + "/member/stats")
                if members:
                    stats = {}
                    for mems in members['member-list']:
                        for k, v in mems['stats'].items():
                            if stats.get(k):
                                stats[k] += v
                            else:
                                stats[k] = v
                    resp["loadbalancer_stat"]["pool_stat_list"].update(stats)
                    resp["loadbalancer_stat"]["pool_stat_list"]["member_list"] = members.get(
                        'member-list')

        return {
            "bytes_in": resp["loadbalancer_stat"]["total_fwd_bytes"],
            "bytes_out": resp["loadbalancer_stat"]["total_rev_bytes"],
            "active_connections": resp["loadbalancer_stat"]["curr_conn"],
            "total_connections": resp["loadbalancer_stat"]["total_conn"],
            "extended_stats": resp
        }

    def create(self, context, lb):
        LOG.debug('IN CREATE_TEST_V2')
        with a10.A10WriteStatusContext(self, context, lb, action='create') as c:
            #This is to modify the VIP creation hooks and setup the source nat pool as needed.
            self._create(c, context, lb)
            self.hooks.after_vip_create(c, context, lb)

    def update(self, context, old_lb, lb):
        with a10.A10WriteStatusContext(self, context, lb) as c:
            self._set(c.client.slb.virtual_server.update, c, context, lb)
            self.hooks.after_vip_update(c, context, lb)

    def _delete(self, c, context, lb):
        try:
            c.client.slb.virtual_server.delete(self._meta_name(lb))
        except acos_errors.NotFound:
            pass

    def delete(self, context, lb):
        with a10.A10DeleteContext(self, context, lb) as c:
            self._delete(c, context, lb)
            self.hooks.after_vip_delete(c, context, lb)

    def stats(self, context, lb):
        with a10.A10Context(self, context, lb) as c:
            name = self.meta(lb, 'id', lb.id)
            resp = c.client.slb.virtual_server.stats(name)

            if not resp:
                return {
                    "bytes_in": 0,
                    "bytes_out": 0,
                    "active_connections": 0,
                    "total_connections": 0,
                    "extended_stats": {}
                }

            if c.device_cfg.get('api_version') == "3.0":
                return self._stats_v30(c, resp, name)
            else:
                return self._stats_v21(c, resp)

    def refresh(self, context, lb):
        LOG.debug("LB Refresh called.")
        # Ensure all elements associated with this LB exist on the device.

    def _get_expressions(self, c):
        rv = {}
        rv = c.a10_driver.config.get_virtual_server_expressions()
        return rv

