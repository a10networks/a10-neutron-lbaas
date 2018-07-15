# Copyright 2014, A10 Networks
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

import acos_client

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.db import portbinding_db


import simple 

class VlanPortBindingPlumbingHooks(simple.PlumbingHooks):
    def after_member_create(self, a10_context, os_context, member):
        pass

    def after_member_update(self, a10_context, os_context, member):
        pass

    def after_vip_create(self, a10_context, os_context, vip):
        import pdb; pdb.set_trace()
        # Get the IDs of all the things we need. 
        vip_port = vip.vip_port
        subnet_id = vip.vip_subnet_id 
        port_id = vip_port.id
        network_id = vip_port.network_id
        acos_client = a10_context.client
        a10_config = a10_context.config
        # 
        # Get {network_id} attached to the port.network_id
        # Get the segment associated to {network_id} with the network matching our criteria
        segment = portbinding_db.get_network_segment(network_id)
        # Get {vlan_id} from the segment
        vlan_id = segment.segmentation_id
        # Get the associated VE
        ve = acos_client.interface.ve.get(vlan_id)
        # 
        if not ve:
            # If DHCP, we can configure the interface with DHCP
            use_dhcp = config.get("plumb_vlan_dhcp")
            if not use_dhcp:
                # Allocate IP from the subnet.
                ip,port = neutron_wrapper.allocate_ip(subnet_id)
            # Create the VLAN with configured interfaces
            interfaces = config.get("vlan_interfaces")
            created_vlan = self._create_vlan(acos_client, vlan_id, interfaces) 
            ve_dict = self._build_ve_dict(vlan_id, use_dhcp, ip, mask)
            # Try to create it. If we catch a "exists in another partition" error, raise it.
            created_ve = self._create_ve(acos_client, **ve_dict)
            ve_oper = acos_client.interface.ve.get_oper(vlan_id)
            ve_mac = ve_oper["mac"]

            # Set necessary IP routes
        # Update the port's MAC address to match the VE MAC
            neutron_wrapper.update_port(port_id, ve_mac)
        LOG.info("Completed configuration for VIP {id} IP:{ip} VLAN:{vlan_id}".format(ip=ip, id=vip.id, vlan_id=vlan_id))
        # Enjoy a cold beer cuz we're done. 
        

    def after_vip_update(self, a10_context, os_context, vip):
        pass

    def _create_ve(self, client, ifnum, ip, mask, use_dhcp):
        try:
            client.interface.ve.create(ifnum, ip, mask, dhcp=use_dhcp)
        #TODO(mdurrant) Narrow exception handling.
        except Exception as ex:
            raise ex 

    def _create_vlan(self, client, vlan_id, interfaces={}):
        try:
            client.vlan.create(vlan_id, ve=True, **interfaces)
        except Exception as ex:
            raise ex

    def _build_ve_dict(self, vlan_id, ip=None, mask=None, use_dhcp=None):
        rval = {"vlan_id": vlan_id}
        if use_dhcp:
            rval["dhcp"] = use_dhcp
        elif ip and mask:
            rval["ip"] = ip
            rval["mask"] = mask

        return rval 
        
