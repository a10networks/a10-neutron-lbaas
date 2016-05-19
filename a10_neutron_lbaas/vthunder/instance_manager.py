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

import logging
import pprint
import time
import uuid

from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v2_0 import client as keystone_v2_client
from keystoneclient.v3 import client as keystone_v3_client

import neutronclient.neutron.client as neutron_client

import novaclient.client as nova_client
import novaclient.exceptions as nova_exceptions

import a10_neutron_lbaas.a10_exceptions as a10_ex


pp = pprint.PrettyPrinter(indent=4)


LOG = logging.getLogger(__name__)

CREATE_TIMEOUT = 900

# TODO(mdurrant) - These may need to go into a configuration file.
GLANCE_VERSION = 2
KEYSTONE_VERSION = "2.0"
NOVA_VERSION = "2.1"
NEUTRON_VERSION = "2.0"
OS_INTERFACE_URLS = ["public", "publicURL"]

_default_server = {
    "id": None,
    "name": None,
    "image": None,
    "flavor": None,
    "meta": {},
    "files": {},
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
    "admin_pass": None  # optional extension
}

MISSING_ERR_FORMAT = "{0} with name or id {1} could not be found"


class InstanceManager(object):
    def __init__(self, ks_version, auth_url, vthunder_tenant_name, user, password,
                 nova_api=None, glance_api=None, neutron_api=None):

        (session, keystone) = self._get_keystone(
            ks_version, auth_url, user, password, vthunder_tenant_name)

        # glance_endpoint = keystone.service_catalog.url_for(service_type='image',
        #                                                    endpoint_type='publicURL')
        # self._nova_api = nova_api or nova_client.Client(NOVA_VERSION, session=session)
        # self._neutron_api = neutron_api or neutron_client.Client(NEUTRON_VERSION, session=session)
        # self._glance_api = glance_api or glance_client.Client(
        #     GLANCE_VERSION, endpoint=glance_endpoint, session=session)

        # glance_endpoint = keystone.service_catalog.url_for(service_type='image',
        #                                                    endpoint_type='publicURL')
        self._nova_api = nova_api or nova_client.Client(NOVA_VERSION, session=session)
        self._neutron_api = neutron_api or neutron_client.Client(NEUTRON_VERSION, session=session)

    def _get_keystone(self, ks_version, auth_url, user, password, tenant_name):
        if int(ks_version) == 2:
            auth = v2.Password(
                auth_url=auth_url, username=user, password=password,
                tenant_name=tenant_name)
        elif int(ks_version) == 3:
            auth = v3.Password(
                auth_url=auth_url, username=user, password=password,
                project_name=tenant_name)
        else:
            raise a10_ex.InvalidConfig('keystone version must be protovol version 2 or 3')

        sess = session.Session(auth=auth)

        if int(ks_version) == 2:
            ks = keystone_v2_client.Client(session=sess)
        else:
            ks = keystone_v3_client.Client(session=sess)

        return (sess, ks)

    def _build_server(self, instance):
        retval = {}
        for k in _default_server:
            retval[k] = instance.get(k, _default_server[k])

        retval['name'] = retval['name'] or 'a10-' + str(uuid.uuid4())

        return retval

    def list_instances(self, detailed=True, search_opts=None,
                       marker=None, limit=None, sort_keys=None, sort_dirs=None):
        return self._nova_api.servers.list(detailed, search_opts, marker, limit,
                                           sort_keys, sort_dirs)

    def create_instance(self, context):
        return self._create_instance(context)

    def _get_ip_addresses_from_instance(self, addresses, mgmt_network_name):
        address_block = addresses[mgmt_network_name]
        v4addresses = filter(lambda x: x["version"] == 4,
                             address_block)
        return v4addresses[0]["addr"]

    def _create_instance(self, context):
        server = self._build_server(context)
        image_id = context.get("image", None)
        flavor_id = context.get("flavor", None)
        net_ids = context.get("networks")
        flavor = self.get_flavor(identifier=flavor_id)

        networks = self.get_networks(net_ids)

        if flavor is None:
            raise a10_ex.FlavorNotFoundError(MISSING_ERR_FORMAT.format("Flavor", flavor_id))

        if networks is None:
            msg = map(lambda x: MISSING_ERR_FORMAT.format("Network", x), net_ids)
            raise a10_ex.NetworksNotFoundError(msg)

        server["image"] = image_id
        server["flavor"] = flavor.id
        server["nics"] = [{'net-id': x['id']} for x in networks]

        created_instance = self._nova_api.servers.create(**server)

        # Next 6 lines -  Added due to insane API on the other side
        created_instance.manager.client.last_request_id = None
        self._create_server_spinlock(created_instance)

        # Get the IP address of the first interface (should be management)
        ip_address = self._get_ip_addresses_from_instance(
            created_instance.addresses, networks[0]['name'])

        return {
            'name': server['name'],
            'instance': created_instance,
            'ip_address': ip_address,
            'nova_instance_id': created_instance.id
        }

    def _create_server_spinlock(self, created_instance):
        created_id = created_instance.id
        timeout = False
        start_time = time.time()
        sleep_time = 0.25

        pending_statuses = ["INITALIZED"]
        active_statuses = ["ACTIVE"]
        fatal_statuses = ["ERROR",
                          "SOFT_DELETED",
                          "HARD_DELETED",
                          "STOPPED",
                          "PAUSED"]

        while not timeout:
            get_instance = self._nova_api.servers.get(created_id)
            vm_state = getattr(get_instance, "OS-EXT-STS:vm_state").upper()
            end_time = time.time()
            if ((get_instance.id == created_id and len(get_instance.addresses) > 0
                    and vm_state in active_statuses + pending_statuses)):
                timeout = True
                break
            elif vm_state in fatal_statuses:
                raise Exception("Instance created in error state %s" % (vm_state))
                break

            if end_time - start_time > CREATE_TIMEOUT:
                timeout = True
                raise Exception("Timed out creating instance.")
                break

            time.sleep(sleep_time)

    def delete_instance(self, instance_id):
        try:
            return self._nova_api.servers.delete(instance_id)
        except nova_exceptions.NotFound:
            pass

    def get_instance(self, instance):
        return self._nova_api.servers.get(instance)

    def get_flavor(self, identifier=None):
        result = None
        if identifier is None:
            raise a10_ex.IdentifierUnspecifiedError(
                "Parameter identifier must specify flavor id or name")
        flavor_filter = (lambda x: x is not None and
                         ((hasattr(x, "name") and x.name == identifier)
                          or (hasattr(x, "id") and x.id == identifier)))
        filtered = filter(flavor_filter, self._nova_api.flavors.list())
        # TODO(mdurrant): What if we accidentally hit multiple flavors?
        if filtered and len(filtered) > 0:
            result = filtered[0]
        return result

    def get_image(self, identifier=None):
        result = None
        images = []
        if identifier is None:
            raise a10_ex.IdentifierUnspecifiedError(
                "Parameter identifier must specify image id or name")
        img_filter = (lambda x: x is not None and
                      ((hasattr(x, "name") and x.name == identifier)
                       or (hasattr(x, "id") and x.id == identifier)))
        try:
            images = self._nova_api.images.list()
        except Exception as ex:
            raise a10_ex.ImageNotFoundError(
                "Unable to retrieve images from nova.  Error %s" % (ex))
        filtered = filter(img_filter, images)
        if filtered:
            result = filtered[0]
        return result

    def _handle_missing_networks(self, not_found):
        msg_format = "Network {0} was not found by ID or name."
        msgs = []
        for net in not_found:
            msgs.append(msg_format.format(net))
        ex_msg = "\n".join(msgs)
        LOG.exception(ex_msg)
        raise a10_ex.NetworksNotFoundError(ex_msg)

    def get_networks(self, networks=[]):
        network_list = {"networks": []}
        net_list = []

        if networks is None or len(networks) < 1:
            raise a10_ex.IdentifierUnspecifiedError(
                "Parameter networks must be specified.")

        try:
            network_list = self._neutron_api.list_networks()
            net_list = network_list.get("networks", [])
        # TODO(mdurrant) - Create specific exceptions.
        except Exception as ex:
            LOG.exception(
                "Unable to retrieve networks from neutron.\nError %s" % (ex))

        # TODO(mdurrant-jk-cshock) - Look up networks by name too
        id_func = (lambda x: x.get("net-id",
                   x.get("uuid", x.get("id"))) if x is not None else None)

        networks_by_id = dict((id_func(x), x) for x in net_list)
        networks_by_name = dict((x.get("name"), x) for x in net_list)
        available_networks = networks_by_name.copy()
        available_networks.update(networks_by_id)

        missing_networks = [x for x in networks if x not in available_networks.keys()]

        if any(missing_networks):
            self._handle_missing_networks(missing_networks)

        return [{
            'id': id_func(available_networks[x]),
            'name': available_networks[x].get('name', '')
        } for x in networks]

    def _device_instance(self, vthunder_config, name=None):
        # Pick an image, any image
        image_id = vthunder_config['glance_image']
        if image_id is None:
            raise a10_ex.FeatureNotConfiguredError("Launching instance requires configured image")

        # Get the flavor from config
        flavor = vthunder_config['nova_flavor']
        if flavor is None:
            raise a10_ex.FeatureNotConfiguredError("Launching instance requires configured flavor")

        mgmt_network = vthunder_config.get("vthunder_management_network")

        networks = [mgmt_network] if mgmt_network else []
        networks += vthunder_config.get('vthunder_data_networks')

        if networks is None or len(networks) < 1:
            raise a10_ex.FeatureNotConfiguredError(
                "Launching instance requires configured networks")

        return {
            'name': name,
            'image': image_id,
            'flavor': flavor,
            'networks': networks
        }

    def create_device_instance(self, vthunder_config, name=None):
        instance_configuration = self._device_instance(vthunder_config, name=name)

        return self._create_instance(instance_configuration)

    def _plumb_port(self, server, network_id, wrong_ips):
        """Look for an existing port on the network
        Add one if it doesn't exist
        """

        for attached_interface in server.interface_list():
            if attached_interface.net_id == network_id:
                if any(map(lambda x: x['ip_address'] in wrong_ips, attached_interface.fixed_ips)):
                    continue
                return attached_interface

        return server.interface_attach(None, network_id, None)

    def plumb_instance(self, instance_id, network_id, allowed_ips, wrong_ips=[]):
        server = self._nova_api.servers.get(instance_id)

        interface = self._plumb_port(server, network_id, wrong_ips=wrong_ips)

        port = self._neutron_api.show_port(interface.port_id)

        allowed_address_pairs = port["port"].get("allowed_address_pairs", [])
        new_address_pairs = map(lambda ip: {"ip_address": ip}, allowed_ips)

        merged_address_pairs = distinct_dicts(allowed_address_pairs + new_address_pairs)

        self._neutron_api.update_port(interface.port_id, {
            "port": {
                "allowed_address_pairs": merged_address_pairs
            }
        })

        return interface.fixed_ips[0]['ip_address']

    def plumb_instance_subnet(self, instance_id, subnet_id, allowed_ips, wrong_ips=[]):
        subnet = self._neutron_api.show_subnet(subnet_id)
        network_id = subnet["subnet"]["network_id"]
        return self.plumb_instance(instance_id, network_id, allowed_ips, wrong_ips=wrong_ips)


def distinct_dicts(dicts):
    hashable = map(lambda x: tuple(sorted(x.items())), dicts)
    return map(dict, set(hashable))
