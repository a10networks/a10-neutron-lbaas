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

from netaddr import IPRange, IPSet, IPAddress
from oslo_utils import uuidutils

from neutron.db.models.segment import NetworkSegment, SegmentHostMapping
from neutron.db.models_v2 import IPAllocation, IPAllocationPool, Route, SubnetRoute, Port, Subnet, Network
from neutron.plugins.ml2.models import PortBinding, PortBindingLevel

from a10_neutron_lbaas.db import models

class AcosWrapper(object):
    def __init__(self, client, *args, **kwargs):
        self._client = client

    def create_vlan(self,  vlan_id, interfaces={}):
        try:
            return self._client.vlan.create(vlan_id, ve=True, **interfaces)
        except Exception as ex:
            raise ex
        
    def create_ve(self, vlan_id, ip, mask, dhcp=False):
        try:
            return self._client.interface.ve.create(vlan_id, ip_address=ip, ip_mask=mask, dhcp=dhcp)
        #TODO(mdurrant) Narrow exception handling.
        except Exception as ex:
            raise ex

    def get_ve(self, ve_ifnum):
        rv = {}
        import pdb;pdb.set_trace()
        try:
            ve = self._client.interface.ve.get_oper(ve_ifnum)
            rv = ve
        # TODO)mdurrant) Narrow exception handling
        except Exception as ex:
            raise ex
        return rv
    

class NeutronDbWrapper(object):
    """Wraps neutron DB ops for easy testing""" 
    def __init__(self, session, *args, **kwargs):
        self._session = session 

    def get_segment(self, port_id, level):
        import pdb; pdb.set_trace()
        binding_level = self._session.query(PortBindingLevel).filter_by(port_id=port_id, level=level).first()
        segment = self._session.query(NetworkSegment).filter_by(id=binding_level.segment_id).first()
        return segment

    def get_subnet(self, id):
        subnet = self._session.query(Subnet).filter_by(id)
        return subnet

    def allocate_ip_for_subnet(self, subnet_id, mac):
        """Allocates an IP from the specified subnet and creates a port with the returned IP and MAC"""
        # Get an available IP and mark it as used before someone else does
        # If there's no IP, , log it and return an error
        # If we successfully get an IP, create a port with the specified MAC and device data
        # If port creation fails, deallocate the IP
        ip = "10.10.10.10" 
        port = {} 
        mask = "255.0.0.0"
        return ip, mask, port
         

    def get_ipallocationpool_by_subnet_id(self, subnet_id):
        return _session.query(models_v2.IPAllocationPool).filter(models_v2.IPAllocationPool.subnet_id == subnet_id).first()

    def get_ipallocations_by_subnet_id(self, subnet_id):
        return _session.query(models_v2.IPAllocation).filter_by(subnet_id=subnet_id).all()

    def create_port(self, record):
        with _session.begin(subtransactions=True):
            port = models_v2.Port(
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
            session.add(port)

            return port

    def get_ipallocation_with_port_by_subnet_id(self, subnet_id, ip_address, port_name):
        result = _session.query(models_v2.IPAllocation, models_v2.Port)\
            .join(models_v2.Port, models_v2.Port.name == port_name)\
            .filter_by(models_v2.IPAllocation.ip_address == ip_address and\
              models_v2.IPAllocation.port_id == port_name and\
              subnet_id == models_v2.IPAllocation.subnet_id).first()
        return result

    def create_ipallocation(self, ipa):
        with _session.begin(subtransactions=True):
            ipallocation = models_v2.IPAllocation(
                ip_address=ipa["ip_address"],
                network_id=ipa["network_id"],
                port_id=ipa["port_id"],
                subnet_id=ipa["subnet_id"]
            )
            session.add(ipallocation)

        return ipallocation

    def a10_allocate_ip_from_dhcp_range(self, subnet, interface_id):
        """Search for an available IP.addr from unallocated IPAllocationPool range.
        If no addresses are available then an error is raised. Returns the address as a string.
        This search is conducted by a difference of the IPAllocationPool set_a and the current IP
        allocations.
        """
        subnet_id = subnet["id"]
        network_id = subnet["network_id"]
        project_id = subnet["project_id"]

        ip_range_result = self.get_ipallocationpool_by_subnet_id(subnet_id)
        ip_in_use_list = (self.get_ipallocations_by_subnet_id(subnet_id))

        set_a = IPSet(IPRange(ip_range_result.first_ip, ip_range_result.last_ip))
        set_b = IPSet()

        for in_use in ip_in_use_list:
            set_b.add(in_use.ip_address)

        # just catch the error if they key is not present means difference returned 0.
        try:
            result = str(IPAddress((set_a - set_b).pop()))
        except KeyError:
            msg = "Can not allocate ip address for VTEP"
            log.error(msg)
            raise a10ex(msg)

        mark_in_use = {
            "ip_address": result,
            "network_id": network_id,
            "port_id": self.create_a10_port(project_id, nterface_id, network_id),
            "subnet_id": subnet["id"]
        }

        self.create_ipallocation(mark_in_use)

        return result

    def create_a10_port(self, tenant_id, lif_id, net_id, owner=None, mac_address=None):
        port_name = "A10_DEV_{0}_PART_{1}_LIF_{2}".format("VXLAN", tenant_id[0:13],
                                                          lif_id)

        mac = [random.randint(0x00, 0xff), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
        mac_last = ':'.join(map(lambda x: "%02x" % x, mac))
        macaddress = mac_address or "00:1F:A0:{0}".format(mac_last)
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
            log.exception(ex)

        return port["id"]

    def update_port(self, port_id, mac):
        with _session.begin(subtransactions=True):
            port = _session.query(Port).filter_by(id=port_id).first()
            port.mac_address = mac
            session.add(port)             
