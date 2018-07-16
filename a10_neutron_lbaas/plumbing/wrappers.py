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

from oslo_log import log

import netaddr

from oslo_utils import uuidutils

from neutron.db.models import segment as segmodels
from neutron.db import models_v2 as nmodels
from neutron.plugins.ml2 import models as pmodels

from a10_neutron_lbaas.db import models
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

    def create_ve(self, vlan_id, ip, mask, dhcp=False):
        mask = self._format_cidr(mask)

        try:
            return self._client.interface.ve.create(vlan_id, ip_address=ip,
                                                    ip_netmask=self._format_cidr(mask), dhcp=dhcp)
        # TODO(mdurrant) Narrow exception handling.
        except Exception as ex:
            raise ex

    def get_ve(self, ve_ifnum):
        rv = {}
        try:
            ve = self._client.interface.ve.get_oper(ve_ifnum)
            rv = ve
        # TODO(mdurrant) Narrow exception handling
        except acos_exc.NotFound as notfound_ex:
            # Eat the notfound error, return empty dict.
            pass
        except Exception as ex:
            raise ex
        return rv

    def _format_cidr(self, cidr):
        marker = "/"
        if cidr[0] != marker:
            beg = cidr.find(marker)
            cidr = cidr[beg:]
        return cidr


class NeutronDbWrapper(object):
    """Wraps neutron DB ops for easy testing"""
    def __init__(self, session, *args, **kwargs):
        self._session = session

    def get_segment(self, port_id, level):
        if _HPB_TEST:
            port = self._session.query(nmodels.Port).filter_by(id=port_id).first()
            segment = self._session.query(segmodels.NetworkSegment).filter_by(
                network_id=port.network_id).first()
            return segment

        binding_level = self._session.query(pmodels.PortBindingLevel).filter_by(port_id=port_id, level=level).first()
        if binding_level:
            segment = self._session.query(segmodels.NetworkSegment).filter_by(id=binding_level.segment_id).first()
            return segment
        # No binding leve
        LOG.error("Could not find binding level for port:{0} level:{1}".format(port_id, level))

    def get_subnet(self, id):
        subnet = self._session.query(nmodels.Subnet).filter_by(id=id).first()
        return subnet

    def allocate_ip_for_subnet(self, subnet_id, mac):
        """Allocates an IP from the specified subnet and creates a port with the returned IP and MAC"""
        # Get an available IP and mark it as used before someone else does
        # If there's no IP, , log it and return an error
        # If we successfully get an IP, create a port with the specified MAC and device data
        # If port creation fails, deallocate the IP
        subnet = self.get_subnet(subnet_id)
        ip, mask, port_id = self.a10_allocate_ip_from_dhcp_range(subnet, "vlan", mac)
        return ip, mask, port_id


    def get_ipallocationpool_by_subnet_id(self, subnet_id):
        return self._session.query(nmodels.IPAllocationPool).filter(nmodels.IPAllocationPool.subnet_id == subnet_id).first()

    def get_ipallocations_by_subnet_id(self, subnet_id):
        return self._session.query(nmodels.IPAllocation).filter_by(nmodels.subnet_id=subnet_id).all()

    def create_port(self, record):
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
            .filter_by(nmodels.IPAllocation.ip_address == ip_address and\
              nmodels.IPAllocation.port_id == port_name and\
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

    def a10_allocate_ip_from_dhcp_range(self, subnet, interface_id, mac):
        """Search for an available IP.addr from unallocated nmodels.IPAllocationPool range.
        If no addresses are available then an error is raised. Returns the address as a string.
        This search is conducted by a difference of the nmodels.IPAllocationPool set_a and the current IP
        allocations.
        """
        subnet_id = subnet["id"]
        network_id = subnet["network_id"]
        project_id = subnet["project_id"]

        ip_range_result = self.get_ipallocationpool_by_subnet_id(subnet_id)
        ip_in_use_list = (self.get_ipallocations_by_subnet_id(subnet_id))

        set_a = netaddr.IPSet(netaddr.IPRange(ip_range_result.first_ip, ip_range_result.last_ip))
        set_b = netaddr.IPSet()

        for in_use in ip_in_use_list:
            set_b.add(in_use.ip_address)

        # just catch the error if they key is not present means difference returned 0.
        try:
            result = str(netaddr.IPAddress((set_a - set_b).pop()))
        except KeyError:
            msg = "Can not allocate ip address for VTEP"
            log.error(msg)
            raise a10ex(msg)


        mark_in_use = {
            "ip_address": result,
            "network_id": network_id,
            "port_id": self.create_a10_port(project_id, interface_id, network_id, mac_address=mac),
            "subnet_id": subnet["id"]
        }

        self.create_ipallocation(mark_in_use)

        return result, subnet["cidr"], mark_in_use["port_id"]

    def create_a10_port(self, tenant_id, lif_id, net_id, owner=None, mac_address=None):
        port_name = "A10_DEV_{0}_PART_{1}_LIF_{2}".format("VXLAN", tenant_id[0:13],
                                                          lif_id)

        if not mac_address:
            mac_address = [random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
            mac_last = ':'.join(map(lambda x: "%02x" % x, mac_address))
            mac_address = "00:1F:A0:{0}".format(mac_last)
        macaddress = mac_address
        device_owner = owner or "network:a10networks"

        port = {
            "id": uuidutils.generate_uuid(),
            "tenant_id": tenant_id,
            "name": port_name,
            "network_id": net_id,
            "mac_address": macaddress,
            "admin_state_up": 1,
            "status": 'ACTIVE',
            "device_id": tenant_id+net_id,
            "device_owner": "network:vxlan"
        }

        try:
            port = self.create_port(port)
        except Exception as ex:
            LOG.exception(ex)

        return port["id"]

    def update_port(self, port_id, mac):
        with self._session.begin(subtransactions=True):
            port = self._session.query(nmodels.Port).filter_by(id=port_id).first()
            port.mac_address = mac
            self._session.add(port)
