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

from a10_neutron_lbaas.plumbing.wrappers import AcosWrapper
from a10_neutron_lbaas.plumbing.wrappers import NeutronDbWrapper

import simple


LOG = log.getLogger(__name__)


VLAN_LOG_FMT = "VLAN:{0} Project:{1} Network:{2}"


class VlanPortBindingPlumbingHooks(simple.PlumbingHooks):
    def after_member_create(self, a10_context, os_context, member):
        pass

    def after_member_update(self, a10_context, os_context, member):
        pass

    def pre_vip_create_v1(self,a10_context, os_context, vip):
        # msg = "PRE_CREATE_V1 hook firing", vip, dir(vip)
        # LOG.debug(msg)
        # cidr = self._get_vip_cidr(a10_context, os_context, vip, v1=True)
        # self._create_nat_pool(a10_context, os_context, vip, v1=True)
        # return cidr
        pass

    def pre_vip_create_v2(self, a10_context, os_context, vip):
        # db = NeutronDbWrapper(os_context.session)
        # acos = AcosWrapper(a10_context.client)
        # config = a10_context.a10_driver.config
        # self._create_nat_pool(a10_context, os_context, vip, v1=False)
        # return self._get_vip_cidr(a10_context, os_context, vip)
        pass

    def after_vip_create(self, a10_context, os_context, vip):
        # Get the IDs of all the things we need.
        db = NeutronDbWrapper(os_context.session)
        acos = AcosWrapper(a10_context.client)
        config = a10_context.a10_driver.config
        # v2 obj model
        if hasattr(vip, "vip_port"):
            vip_port = vip.vip_port
            subnet_id = vip.vip_subnet_id
            subnet = db.get_subnet(subnet_id)
            port_id = vip_port.id
            network_id = vip_port.network_id
            tenant_id = vip.tenant_id
            vip_id = vip.id

        # v1 obj model
        else:
            subnet_id = vip["subnet_id"]
            port_id = vip["port_id"]
            subnet = db.get_subnet(subnet_id)
            network_id = subnet["network_id"]
            tenant_id = vip["tenant_id"]
            vip_id = vip["id"]


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
            LOG.info(
                "No VLAN ID for port {0} on segment {1}. Exiting hook.".format(port_id, segment.id))
            return
        # Format the string we're going to use a gazillion times for logging.
        #VE_LOG_ENTRY = VLAN_LOG_FMT.format(vlan_id, tenant_id, network_id)

        # Get the associated VE
        ve = acos.get_ve(vlan_id)
        # If the VE already exists, the VLAN already exists and in most cases we're done.
        # Log that this happened.
        # TODO(mdurrant) - Find a way to check if it's in another partition and gripe loudly.
        if ve:
           LOG.info("Configuration for {0} previously created".format(vlan_id))
           return

        # If DHCP, we can configure the interface with DHCP
        use_dhcp = config.get("plumb_vlan_dhcp")

        # Create the VLAN with configured interfaces
        interfaces = config.get("vlan_interfaces")
        acos.create_vlan(vlan_id, interfaces)

        # Get the MAC of the VE so we can create the port.
        ve_pre = acos.get_ve(vlan_id)
        ve_mac = ve_pre.get("ve", {}).get("oper", {}).get("mac")
        if not ve_mac:
            LOG.error("Could not retrieve VE MAC, port binding operation failed.")
            return
        ve_mac = self._format_mac(ve_mac)

        # Create a neutron port for VE interface using returned VE MAC
        ve_nport = db.create_port(network_id, tenant_id, ve_mac, network_id)
        # Get the vips port from neutron
        vip_port = db.get_port(port_id)
        vip_mac = vip_port["mac_address"]
        acos.update_vip(vip_id, vip_mac, vlan_id)
        LOG.info("Updated VIP {0} with mac {1} vlan {2}".format(vip_id, vip_mac, vlan_id))
        # TODO(mdurrant) - Should host be blank
        ve_portbinding = db.create_port_binding(ve_nport.id, "")
        # Set defaults
        ve_ip, ve_mask, ve_port = None, None, ve_nport.id

        if not use_dhcp:
            # Allocate IP from the subnet.
            ve_ip, ve_mask, ve_port = db.allocate_ip_for_subnet(subnet_id, ve_mac, ve_nport.id)

        LOG.info("Created VLAN {0} with interfaces {1}".format(str(vlan_id), str(interfaces)))
        ve_dict = self._build_ve_dict(vlan_id, ve_ip, ve_mask, use_dhcp)

        # Try to create it. If an exception is raised, it's logged and we stop here.
        ve_created = acos.create_ve(ve_dict)
        if not ve_created:
           LOG.error("Exception creating VE interface for VLAN:{0}".format(vlan_id))
           return

        # Log the created VE for troubleshooting purposes.
        LOG.info("Created VE {0}", str(vlan_id))

        # Get the IP address of the port
        # if use_dhcp:
        #    LOG.info("VE {0}", str(ve_created))

        # Else, it already exists and we're good
        LOG.info("Configured {0} with interface IP: {1}".format(
           vlan_id, ve_ip))
        # fin.

    def after_vip_update(self, a10_context, os_context, vip):
        pass

    def partition_delete_last(self, client, openstack_context, name, lbaas_obj):
        # After partition delete, remove any neutron ports created by this hook owned by the tenant
        # Make sure the last object is an LB. The data model ensures this but ... just in case.
    	# or type(lbaas_obj).__name__ != "LoadBalancer":
        if not lbaas_obj:
           LOG.info("No lbaas obj was set for cleanup, exiting cleanup")
           return

        db = NeutronDbWrapper(openstack_context.session)
        LOG.info("Cleanup ports for {0}".format(name))
        db.cleanup_vlan_ports(lbaas_obj)

    def _build_ve_dict(self, vlan_id, ip=None, mask=None, use_dhcp=None):
        rval = {"ifnum": vlan_id}
        if use_dhcp:
            rval["dhcp"] = use_dhcp
        if ip and mask:
            rval["ip_address"] = ip
            rval["ip_netmask"] = self._format_cidr(mask)

        return rval

    def _format_mac(self, raw_mac):
        raw_mac = raw_mac.replace(".", "")
        mac = ':'.join(a + b for a, b in zip(raw_mac[::2], raw_mac[1::2]))
        return mac

    def _format_cidr(self, cidr):
        # Takes "A.B.C.D/n" and returns the "/n" portion
        marker = "/"
        if cidr and cidr[0] != marker:
            beg = cidr.find(marker)
            cidr = cidr[beg:]
        return cidr

    def _get_vip_cidr(self, a10_context, os_context, vip, v1=False):
        db = NeutronDbWrapper(os_context.session)
        acos = AcosWrapper(a10_context.client)
        config = a10_context.a10_driver.config
        if v1 is True:
            sid = vip["subnet_id"]
        else:
            sid = vip.vip_subnet_id
        vip_subnet_info = db.get_subnet(sid)
        return self._format_cidr(vip_subnet_info.cidr)


    def _create_nat_pool(self, a10_context, os_context, vip, v1=False):
        msg = "CREATE_NAT", (v1 is True), v1, type(v1)
        LOG.debug(msg)
        db = NeutronDbWrapper(os_context.session)
        acos = AcosWrapper(a10_context.client)
        config = a10_context.a10_driver.config
        vip_cidr = self._get_vip_cidr(a10_context, os_context, vip, v1=v1)
        if v1 is True:
            try:
                acos.create_nat_pool(vip['id'], vip['address'], vip['address'], vip_cidr)
            except Exception as ex:
                raise ex
        else:
            try:
                acos.create_nat_pool(vip.id, vip.vip_address, vip.vip_address, vip_cidr)
            except Exception as ex:
                raise ex





