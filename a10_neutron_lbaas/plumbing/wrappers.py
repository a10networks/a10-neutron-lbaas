# Copyright (c) 2018 A10 Networks
#
# Heavily inspired by networking-arista
# Source at https://github.com/openstack/networking-arista
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import netaddr
import random

from oslo_log import log
from oslo_utils import uuidutils

from neutron.db.models import segment as segmodels
from neutron.db import models_v2 as nmodels
from neutron.plugins.ml2 import models as pmodels

from a10_neutron_lbaas.plumbing.utils import IPHelpers
from acos_client import errors as acos_exc

LOG = log.getLogger(__name__)
_HPB_TEST = True


class AcosWrapper(object):
    def __init__(self, client, *args, **kwargs):
        self._client = client

    def create_vlan(self, vlan_id, interfaces={}):
        try:
            return self._client.vlan.create(vlan_id, veth=True, **interfaces)
        except Exception as ex:
            raise ex

    def create_ve(self, ve_dict):
        try:
            return self._client.interface.ve.create(**ve_dict)
        # TODO(mdurrant) Narrow exception handling.
        except acos_exc.DhcpAcquireFailed:
            LOG.error("UNABLE TO CREATE VE INTERFACE {0}".format(str(ve_dict)))
            return None
        except Exception as ex:
            raise ex

    def get_ve(self, ve_ifnum):
        rv = {}
        try:
            ve = self._client.interface.ve.get_oper(ve_ifnum)
            rv = ve
        # TODO(mdurrant) Narrow exception handling
        except acos_exc.NotFound:
            # Eat the notfound error, return empty dict.
            pass
        except Exception as ex:
            raise ex
        return rv


class NeutronDbWrapper(object):
    VLAN_PORT_NAME_FORMAT = "A10_VLANHBPHOOK_PROJECT_{project_id}_NET_{network_id}"
    VLAN_PORT_OWNER = "network:a10networks"

    """Wraps neutron DB ops for easy testing"""
    def __init__(self, session, *args, **kwargs):
        self._session = session

    def get_segment(self, port_id, level):
        if _HPB_TEST:
            port = self._session.query(nmodels.Port).filter_by(id=port_id).first()
            segment = self._session.query(segmodels.NetworkSegment).filter_by(
                network_id=port.network_id).first()
            return segment

        binding_level = self._session.query(pmodels.PortBindingLevel).filter_by(
            port_id=port_id, level=level).first()
        if binding_level:
            segment = self._session.query(segmodels.NetworkSegment).filter_by(
                id=binding_level.segment_id).first()
            return segment
        # No binding leve
        LOG.error("Could not find binding level for port:{0} level:{1}".format(port_id, level))

    def get_subnet(self, id):
        subnet = self._session.query(nmodels.Subnet).filter_by(id=id).first()
        return subnet

    def allocate_ip_for_subnet(self, subnet_id, mac, port_id):
        """Allocates an IP from the specified subnet and creates a port"""
        # Get an available IP and mark it as used before someone else does
        # If there's no IP, , log it and return an error
        # If we successfully get an IP, create a port with the specified MAC and device data
        # If port creation fails, deallocate the IP
        subnet = self.get_subnet(subnet_id)
        ip, mask, port_id = self.a10_allocate_ip_from_dhcp_range(subnet, "vlan", mac, port_id)
        return ip, mask, port_id

    def get_ipallocationpool_by_subnet_id(self, subnet_id):
        return self._session.query(nmodels.IPAllocationPool).filter(
            nmodels.IPAllocationPool.subnet_id == subnet_id).first()

    def get_ipallocations_by_subnet_id(self, subnet_id):
        return self._session.query(nmodels.IPAllocation).filter_by(subnet_id=subnet_id).all()

    def create_port(self, network_id, project_id, mac_address, device_id):
        device_owner = self.VLAN_PORT_OWNER
        device_id = network_id
        name = self.VLAN_PORT_NAME_FORMAT.format(project_id=project_id, network_id=network_id)
        port_dict = self._build_port_dict(project_id, name, network_id, mac_address, device_id, 
                                          device_owner)
        return self.create_port_from_dict(port_dict)

    def create_port_from_dict(self, record):
        with self._session.begin(subtransactions=True):
            port = nmodels.Port(
                id=uuidutils.generate_uuid(),
                tenant_id=record['tenant_id'],
                name=record["name"],
                network_id=record["network_id"],
                mac_address=record["mac_address"],
                admin_state_up=record["admin_state_up"],
                status=record["status"],
                device_id=record["device_id"],
                device_owner=record["device_owner"]
            )
            self._session.add(port)

            return port

    def get_ipallocation_with_port_by_subnet_id(self, subnet_id, ip_address, port_name):
        result = self._session.query(nmodels.IPAllocation, nmodels.Port)\
            .join(nmodels.Port, nmodels.Port.name == port_name)\
            .filter_by(nmodels.IPAllocation.ip_address == ip_address and
                       nmodels.IPAllocation.port_id == port_name and
                       subnet_id == nmodels.IPAllocation.subnet_id).first()
        return result

    def create_ipallocation(self, ipa):
        with self._session.begin(subtransactions=True):
            ipallocation = nmodels.IPAllocation(
                ip_address=ipa["ip_address"],
                network_id=ipa["network_id"],
                port_id=ipa["port_id"],
                subnet_id=ipa["subnet_id"]
            )
            self._session.add(ipallocation)

        return ipallocation

    def a10_allocate_ip_from_dhcp_range(self, subnet, interface_id, mac, port_id):
        """Search for an available IP.addr from unallocated nmodels.IPAllocationPool range.
        If no addresses are available then an error is raised. Returns the address as a string.
        This search is conducted by a difference of the nmodels.IPAllocationPool set_a
        and the current IP allocations.
        """
        subnet_id = subnet["id"]
        network_id = subnet["network_id"]
        project_id = subnet["project_id"]

        iprange_result = self.get_ipallocationpool_by_subnet_id(subnet_id)
        ip_in_use_list = [x.ip_address for x in self.get_ipallocations_by_subnet_id(subnet_id)]

        range_begin, range_end = iprange_result.first_ip, iprange_result.last_ip
        ip_address = IPHelpers.find_unused_ip(range_begin,range_end, ip_in_use_list)

        if not ip_address:
            msg = "Cannot allocate from subnet {0}".format(subnet) 
            LOG.error(msg)
            # TODO(mdurrant) - Raise neutron exception
            raise Exception

        mark_in_use = {
            "ip_address": ip_address, 
            "network_id": network_id,
            "port_id": port_id, 
            "subnet_id": subnet["id"]
        }

        self.create_ipallocation(mark_in_use)

        return ip_address, subnet["cidr"], mark_in_use["port_id"]


    def _build_port_dict(self, tenant_id, name, network_id, mac_address, device_id, device_owner):
        return {
            "id": uuidutils.generate_uuid(),
            "tenant_id": tenant_id,
            "name": name,
            "network_id": network_id,
            "mac_address": mac_address,
            "admin_state_up": 1,
            "status": "ACTIVE",
            "device_id": device_id,
            "device_owner": device_owner
        }

    def update_port(self, port_id, mac):
        with self._session.begin(subtransactions=True):
            port = self._session.query(nmodels.Port).filter_by(id=port_id).first()
            port.mac_address = mac
            self._session.add(port)

    def cleanup_vlan_ports(self, last_lb):
        vip_port = last_lb.vip_port
        network_id, port_id, tenant_id = vip_port.network_id, vip_port.id, vip_port.tenant_id
        port_name = self.VLAN_PORT_NAME_FORMAT.format(project_id=tenant_id,network_id=network_id)
        query_args = {
            "network_id": network_id,
            "project_id": tenant_id,
            # "name": port_name,
            "device_owner": self.VLAN_PORT_OWNER
        }

        with self._session.begin(subtransactions=True):
            port = self._session.query(nmodels.Port).filter_by(**query_args).first()
            if port:
                self._session.delete(port)
