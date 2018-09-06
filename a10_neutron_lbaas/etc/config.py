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


#
# Global settings
#

# Should the driver check that A10 appliances are alive before
# successfullAy initializing?

# verify_appliances = False

# Should the driver store some meta-info in a database?
# Needed for tenant<->appliance persistence if the number of appliances
# is changed for any reason. Setting this to true means that you will
# also need to run "a10-manage upgrade" after installing or upgrading
# the a10-neutron-lbaas package.
# Recommended for all new installs.

# use_database = False

# The SQLAlchemy connection string to use to connect to the database.
# If None, and use_database is True, the driver will attempt to use
# the configured neutron database.

# database_connection = None

# Sometimes we need things from neutron. We will look in the usual places,
# but this is here if you need to override the location.

# neutron_conf_dir = '/etc/neutron'

# If True, use the OpenStack lbaas member object UUID as the server name
# in ACOS. Recommended for all new installs using ACOS 4.0.0 or greater.

# member_name_use_uuid = False

# If not None, use this keystone auth URL instead of the one from the
# neutron.conf file.

# keystone_auth_url = None

# Which version of the keystone protocol to use

# keystone_version = 2

# Certain functions of this driver can be overridden by passing in an alternate
# set of plumbing hooks, including scheduling where a tenant's VIPs are going
# to be created, and what to do after object creation.
#
# The default hooks class is the first, PlumbingHooks, which is meant for
# hardware appliances and manually orchestrated A10 devices. This hook
# primarily makes use of the 'devices' hash table below to find available
# ACOS devices.
#
# The second hooks class provided is the VThunderPlumbingHooks, which will
# spawn a virtual appliance for every VIP, inside a service tenant space.
# It's settings primarily come from the 'vthunder' hash defined at the
# bottom of this file.
#
# More advanced hooks/schedulers can be added by the operator or by
# A10 professional services.

# import a10_neutron_lbaas.plumbing.simple as hooks
# plumbing_hooks_class = hooks.PlumbingHooks

# import a10_neutron_lbaas.plumbing.vthunder_per_vip as hooks
# plumbing_hooks_class = hooks.VThunderPerVIPPlumbingHooks

# Nova API version; defaults to '2.1' (hint: use '2' for kilo.)

# nova_api_version = '2.1'

# # License the launched instances
#
#     'license_manager': {
#              "hosts": [
#                     {"ip": "pdx.a10cloud.com", "port": 443},
#                     {"ip": "sfo.a10cloud.com", "port": 443},
#                     {"ip": "iad.a10cloud.com", "port": 443}
#             ],
#             "serial": "SNxxxxxxxxxxxxxxxx",
#             "instance-name": "openstack_instance",
#             "bandwidth-base": 100,
#             "interval": 3,
#             "use-mgmt-port": True
#     },

# # Configure dns resolver
#
#     'dns_resolver': {
#         'primary': '192.0.2.4',
#         'secondary': '192.0.2.5',
#     },

# # Configure statistics collection
#
#     'sflow_collector': {
#          'host': '10.20.100.7',
#          'port': 6343
#     }

#     # The following are required if you wish to use a service tenant.
#     'service_tenant': {
#         'tenant_name': 'a10-service',
#         'username': '',
#         'password': ''
#     }
# }
vport_defaults = {}
