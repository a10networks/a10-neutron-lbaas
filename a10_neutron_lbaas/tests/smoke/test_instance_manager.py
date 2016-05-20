#! /usr/bin/python
# Copyright 2015,  A10 Networks
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

USERNAME = "admin"
PASSWORD = "password"
PROJECT_ID = "admin"
VERSION = "2"

import time
import uuid

from keystoneclient.auth.identity import v2
from keystoneclient import session
import neutronclient.v2_0.client as neutron_client
import novaclient.client as nova_client

from a10_neutron_lbaas import instance_manager as im

auth = v2.Password(auth_url="http://localhost:35357/v2.0",
                   username=USERNAME,
                   password=PASSWORD, tenant_name="admin")
sess = session.Session(auth=auth)
token = sess.user.token
nova = nova_client.Client(VERSION, session=sess)
neutron = neutron_client.Client(auth_url=auth.auth_url,
                                username=auth.username,
                                password=auth.password,
                                tenant_name="admin")

imgr = im.InstanceManager(auth, nova_api=nova, neutron_api=neutron)
data_netid = "02d13222-05d0-43b3-8bd2-16dfe765baaf"
mgmt_netid = "e7380ef5-72d5-447c-bdc6-a5604355689f"

imgname = "cirros-0.3.0-x86_64-disk"
flav = "m1.small"

nics = [
    {"net-id": mgmt_netid},
    # {"net-id": data_netid},
    # {"net-id": data_netid},
    # {"net-id": data_netid},
    # {"net-id": data_netid},
]

device = {
    "name": str(uuid.uuid4()),
    "image": imgname,
    "flavor": flav,
    "meta": {},
    "files": {},
    "networks": nics,
    "min_count": 1,  # optional extension
    "max_count": 1,  # optional extension
    "security_groups": [],
    "userdata": None,
    "key_name": None,  # optional extension
    "availability_zone": None,
    "block_device_mapping": None,  # optional extension
    "block_device_mapping_v2": None,  # optional extension
    "scheduler_hints": {},  # optional extension
    "config_drive": False,  # optional extension
    "disk_config": "AUTO",   # AUTO or MANUAL # optional extension
    "admin_pass": "secrete"  # optional extension
}

print("Device {0}".format(device))
c_inst = imgr.create_instance(None, device)
time.sleep(2)
g_inst = imgr.get_instance(c_inst.id)
inst = g_inst.__dict__
print(inst)
server = inst.get("server")
addresses = inst.get("addresses", {})

try:
    for x in dict(addresses):
        addr = dict(addresses.get(x))
except Exception:
    pass

imgr.delete_instance(inst.get("id"))
