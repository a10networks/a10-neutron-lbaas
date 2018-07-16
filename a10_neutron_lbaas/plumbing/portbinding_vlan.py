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

from oslo_log import log

from a10_neutron_lbaas import a10_exceptions as ex
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.db import portbinding_db
from a10_neutron_lbaas.plumbing.wrappers import NeutronDbWrapper
from a10_neutron_lbaas.plumbing.wrappers import AcosWrapper

import simple 


LOG = log.getLogger(__name__)

class VlanPortBindingPlumbingHooks(simple.PlumbingHooks):
    def after_member_create(self, a10_context, os_context, member):
        pass

    def after_member_update(self, a10_context, os_context, member):
        pass

    def after_vip_create(self, a10_context, os_context, vip):
        # Get the IDs of all the things we need. 
        db = NeutronDbWrapper(os_context.session)
        acos = AcosWrapper(a10_context.client)
        config = a10_context.a10_driver.config

        vip_port = vip.vip_port
        subnet_id = vip.vip_subnet_id 
        port_id = vip_port.id
        network_id = vip_port.network_id

        # Initialize sentinel values
        # ve, ve_ip, ve_port, ve_mask, ve_mac = None, None, None, None, None

        try:
            binding_level = config.get("vlan_binding_level")
        except Exception as ex:
            # If binding_level isn't configured, there is a lot that can go wrong.
            # Log an error and bail.
            # TODO(mdurrant) Narrow exception handling retrieving binding level
            raise ex
 
        # Get {network_id} attached to the port.network_id
        # Get the segment associated to {network_id} with the network matching our criteria
        segment = db.get_segment(port_id, binding_level)
        # Get {vlan_id} from the segment
        vlan_id = segment.segmentation_id
        ve = None 
        # Is there one assigned to the segment?
        if not vlan_id:
            LOG.info("No VLAN ID associated with port {0} on segment {1}. Exiting port binding procedure.".format(port_id, segment.id))
            return
        # Get the associated VE if so.

        ve = acos.get_ve(vlan_id)
        # If the VE already exists, the VLAN already exists and in most cases we're done.
        # Log that this happened.
        # TODO(mdurrant) - Find a way to check if it's in another partition and gripe loudly.
        if ve:
            LOG.info("Configuration for VLAN {0} has been completed by a previously created VIP".format(vlan_id)) 
            return

        # If DHCP, we can configure the interface with DHCP
        use_dhcp = config.get("plumb_vlan_dhcp")
        interfaces = config.get("vlan_interfaces")

        # Create the VLAN with configured interfaces
        # interfaces = config.get("vlan_interfaces")
        created_vlan = acos.create_vlan(vlan_id, interfaces)
        # Get the MAC of the VE so we can create the port.
        ve_pre = acos.get_ve(vlan_id)
        ve_mac = ve_pre.get("ve").get("oper").get("mac")
        ve_mac = self._format_mac(ve_mac)

        if not use_dhcp:                                                         
            # Allocate IP from the subnet.                                       
            ve_ip,ve_mask, ve_port = db.allocate_ip_for_subnet(subnet_id, ve_mac)

        LOG.info("Created VLAN {0} with interfaces {1}".format(str(vlan_id), str(interfaces)))
        ve_dict = self._build_ve_dict(vlan_id, ve_ip, ve_mask, use_dhcp)
        # Try to create it. If we catch a "exists in another partition" error, raise it.
        created_ve = acos.create_ve(**ve_dict)
        ve_post = acos.get_ve(vlan_id)
        # If the created VE doesn't have an IP, we kinda need to wait til it has one.

        LOG.info("Created VE {0}", ve_dict)
        # Set necessary IP routes
        # 
        # Else, it already exists and we're good
        LOG.info("Completed configuration for VIP {id} IP:{ip} VLAN:{vlan_id}".format(ip=ve_ip, id=vip.id, vlan_id=vlan_id))
        # fin. 

    def after_vip_update(self, a10_context, os_context, vip):
        pass

    def _build_ve_dict(self, vlan_id, ip=None, mask=None, use_dhcp=None):
        rval = {"vlan_id": vlan_id}
        if use_dhcp:
            rval["dhcp"] = use_dhcp
        if ip and mask:
            rval["ip"] = ip
            rval["mask"] = mask

        return rval 

    def _format_mac(self, raw_mac):
        raw_mac = raw_mac.replace(".", "")
        mac = ':'.join(a+b for a,b in zip(raw_mac[::2], raw_mac[1::2]))
        return mac
