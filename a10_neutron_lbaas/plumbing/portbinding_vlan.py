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

import base

class VxlanPortBindingPlumbingHooks(base.BasePlumbingHooks):
    def after_member_create(self, a10_context, os_context, member):
        pass

    def after_member_update(self, a10_context, os_context, member):
        pass

    def after_vip_create(self, a10_context, os_context, vip):
        # Get port ID
        # Get the network attached to the port ID
        # Get {vlan_id} associated with the network
            # If VE #{vlan_id} exists in _our_ partition, we're done.
            # If it exists in someone else's partition, raise an exception.
        # Create VLAN {vlan_id} w/ router interface on VE {vlan_id}
        # Create VE {vlan_id} allocating an IP from the IPv4 {subnet_id} associated with the network.
        

        # If we have a VE matching that VLAN ID in our partition, we're already plumbed.
            # If not, create it.
            # If it exists in someone else's partition, we have a problem
        # Update the port's MAC address to match the VE MAC
        # We're done 
        pass

    def after_vip_update(self, a10_context, os_context, vip):
        pass

