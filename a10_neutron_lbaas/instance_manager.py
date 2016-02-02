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

import glanceclient.client as glance_client
import neutronclient.neutron.client as neutron_client
import novaclient.client as nova_client
import time
import uuid

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.a10_exceptions as a10_ex

pp = pprint.PrettyPrinter(indent=4)


LOG = logging.getLogger(__name__)

CREATE_TIMEOUT = 60

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
    def __init__(self, tenant_id, session=None,
                 nova_api=None, glance_api=None, neutron_api=None, config=None):
        self.tenant_id = tenant_id

        self._nova_api = nova_api or nova_client.Client(NOVA_VERSION, session=session)

        self._neutron_api = neutron_api or neutron_client.Client(NEUTRON_VERSION, session=session)

        self._glance_api = glance_api or glance_client.Client(GLANCE_VERSION, session=session)

        self._config = config or a10_config.A10Config()

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
        a10_record = self._create_instance(context)

        # TODO(mdurrant): Do something with the result of this call, like validation.
        self._neutron_api.create_a10_appliance({'a10_appliance': a10_record})
        return a10_record

    def _build_a10_appliance_record(self, instance, image, appliance, ip):
        """Build an a10_appliances_db record from Nova instance/image"""
        import json

        imgprops = json.loads(image.metadata["properties"])

        a10_appliance = {
            "tenant_id": self.tenant_id,
            "name": appliance["name"],
            # TODO(mdurrant): not sure this is populated
            "description": "",
            # need to get the network data out.
            "host": ip,
            "api_version": imgprops["api_version"],
            "username": imgprops["username"],
            "password": imgprops["password"],
            "protocol": imgprops["protocol"],
            "port": imgprops["port"]
        }

        return a10_appliance

    def _get_ip_addresses_from_instance(self, addresses):
        rv = ""
        if len(addresses.keys()) > 0:
            v4addresses = filter(lambda x: x["version"] == 4,
                                 addresses[addresses.keys()[0]])
            if len(v4addresses) > 0:
                addresses = map(lambda x: x["addr"], v4addresses)
                if len(addresses) > 0:
                    rv = addresses[0]
        return rv

    def _create_instance(self, context):
        server = self._build_server(context)
        image_id = context.get("image", None)
        flavor_id = context.get("flavor", None)
        net_ids = context.get("networks")
        image = self.get_image(identifier=image_id)
        flavor = self.get_flavor(identifier=flavor_id)

        networks = self.get_networks(net_ids)
        if image is None:
            raise a10_ex.ImageNotFoundError(MISSING_ERR_FORMAT.format("Image", image_id))

        if flavor is None:
            raise a10_ex.FlavorNotFoundError(MISSING_ERR_FORMAT.format("Flavor", flavor_id))

        if networks is None:
            msg = map(lambda x: MISSING_ERR_FORMAT.format("Network", x), net_ids)
            raise a10_ex.NetworksNotFoundError(msg)

        server["image"] = image.id
        server["flavor"] = flavor.id
        server["nics"] = [{'net-id': x} for x in networks]

        created_instance = self._nova_api.servers.create(**server)

        # Next 6 lines -  Added due to insane API on the other side
        created_instance.manager.client.last_request_id = None
        self._create_server_spinlock(created_instance)

        ip_address = self._get_ip_addresses_from_instance(created_instance.addresses)
        a10_record = self._build_a10_appliance_record(created_instance, image, server, ip_address)

        return a10_record

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
                and vm_state in active_statuses)):
                timeout = True
                break
            elif vm_state in fatal_statuses:
                raise Exception("Instance created in error state %s" % (vm_state))
                break
            
            if end_time - start_time > CREATE_TIMEOUT:
                import pdb; pdb.set_trace()
                timeout = True
                # TODO(mdurrant) - Specific exception
                raise Exception("Timed out creating instance.")
                break
            
            time.sleep(sleep_time)

    def delete_instance(self, instance_id):
        return self._nova_api.servers.delete(instance_id)

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

        return [id_func(available_networks[x]) for x in networks]

    def _default_instance(self):
        # Get all the a10 images
        image_filter = {
            "tag": ["a10"]
        }

        try:
            images = list(self._glance_api.images.list(filters=image_filter))
        except Exception as ex:
            raise a10_ex.ImageNotFoundError(
                "Unable to retrieve images from glance.  Error %s" % (ex))

        if images is None or len(images) < 1:
            raise a10_ex.FeatureNotConfiguredError("Launching instance requires configured images")

        # Pick an image, any image
        image_id = images[0].id

        # Get the flavor from config
        flavor = self._config.instance_defaults.get('flavor')

        if flavor is None:
            raise a10_ex.FeatureNotConfiguredError("Launching instance requires configured flavor")

        networks = self._config.instance_defaults.get('networks')

        if networks is None or len(networks) < 1:
            raise a10_ex.FeatureNotConfiguredError(
                "Launching instance requires configured networks")

        return {
            'image': image_id,
            'flavor': flavor,
            'networks': networks
        }

    def create_default_instance(self):
        """Create the default instance for this tenant
        """
        instance_configuration = self._default_instance()

        return self.create_instance(instance_configuration)
