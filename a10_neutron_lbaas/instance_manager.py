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
import keystoneclient.auth.identity.generic as auth_plugin
import keystoneclient.client as keystone_client
import keystoneclient.session as keystone_session
import neutronclient.neutron.client as neutron_client
import novaclient.client as nova_client


import a10_neutron_lbaas.a10_exceptions as a10_ex
import a10_neutron_lbaas.dashboard.api.a10devices as a10api

pp = pprint.PrettyPrinter(indent=4)


LOG = logging.getLogger(__name__)

# TODO(mdurrant) - These may need to go into a configuration file.
GLANCE_VERSION = 1
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
    "networks": None,  # optional extension
    "scheduler_hints": {},  # optional extension
    "config_drive": False,  # optional extension
    "disk_config": "AUTO",   # AUTO or MANUAL # optional extension
    "admin_pass": None  # optional extension
}

MISSING_ERR_FORMAT = "{0} with name or id {1} could not be found"


class InstanceManager(object):
    def __init__(self, context=None, request=None, nova_api=None,
                 glance_api=None, neutron_api=None, keystone_api=None, a10_api=None):
        self.context = context
        self.user = request.user
        self.tenant_id = request.user.token.project["id"]
        self.endpoints = self._get_services_from_token(self.user.token)
        (self.auth_url, self.auth_token) = self._get_auth_from_token(self.user.token)
        self._validate_auth()
        session = keystone_session.Session(auth=self.token)
        self.session = session
        self._keystone_api = (keystone_api or keystone_client.Client(KEYSTONE_VERSION,
                              session=session, auth_url=self.auth_url))

        self._nova_api = nova_api or nova_client.Client(NOVA_VERSION, session=session,
                                                        auth_url=self.auth_url)

        self._neutron_api = neutron_api or neutron_client.Client(NEUTRON_VERSION,
                                                                 session=session,
                                                                 auth_url=self.auth_url)

        self._glance_api = glance_api or glance_client.Client(GLANCE_VERSION, session=session)
        self._a10_api = a10_api or a10api

    def _validate_auth(self):
        pass
        # if self.auth_url is None or self.auth_token is None:
        #     raise AttributeError("Auth URL and Token must be provided for authentication.")

    def _get_services_from_token(self, token):
        # This changes between keystone versions.
        res = {}
        if not token.serviceCatalog or len(token.serviceCatalog) < 1:
            raise AttributeError("FATAL: Service catalog not populated.")
        for x in token.serviceCatalog:
            # This is always returned as an array.
            endpoints = x.get("endpoints", [])
            urls = map(self.endpoint_public_url, endpoints)
            urls = filter(lambda x: x is not None, urls)

            if len(urls) > 0:
                res[x["type"]] = urls[0]
        return res

    def endpoint_public_url(self, endpoint):
        if endpoint.get('interface') == 'public':
            return endpoint['url']
        return endpoint.get('publicURL')

    def _get_auth_from_token(self, token):
        auth_url = None
        auth_token = token.unscoped_token

        if self.endpoints:
            auth_url = self.endpoints.get("identity", None)
        else:
            LOG.exception("Identity Service discovery failed.")

        self.token = auth_plugin.Token(token=auth_token,
                                       project_name=self.user.token.project["name"],
                                       auth_url=auth_url)

        return (auth_url, auth_token)

    def _build_server(self, instance):
        retval = {}
        for k in _default_server:
            retval[k] = instance.get(k, _default_server[k])

        return retval

    def list_instances(self, detailed=True, search_opts=None,
                       marker=None, limit=None, sort_keys=None, sort_dirs=None):
        return self._nova_api.servers.list(detailed, search_opts, marker, limit,
                                           sort_keys, sort_dirs)

    def create_instance(self, request, context):
        return self._create_instance(request, context)

    def _build_a10_appliance_record(self, instance, image, appliance, ip):
        """Build an a10_appliances_db record from Nova instance/image"""
        import json

        imgprops = json.loads(image.metadata["properties"])

        rv = {
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

        return rv

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

    def _create_instance(self, request, context):
        server = self._build_server(context)
        image_id = context.get("image", None)
        flavor_id = context.get("flavor", None)
        net_ids = context.get("networks")
        image = self.get_image(request, identifier=image_id)
        flavor = self.get_flavor(request, identifier=flavor_id)

        networks = self.get_networks(request, net_ids)
        if image is None:
            raise a10_ex.ImageNotFoundError(MISSING_ERR_FORMAT.format("Image", image_id))

        if flavor is None:
            raise a10_ex.FlavorNotFoundError(MISSING_ERR_FORMAT.format("Flavor", flavor_id))

        if networks is None:
            msg = map(lambda x: MISSING_ERR_FORMAT.format("Network", x), net_ids)
            raise a10_ex.NetworksNotFoundError(msg)

        server["image"] = image.id
        server["flavor"] = flavor.id
        server["networks"] = networks
        created_instance = self._nova_api.servers.create(**server)
        # Next 6 lines -  Added due to insane API on the other side
        created_instance.manager.client.last_request_id = None

        try:
            created_instance.get()
        except Exception as ex:
            ex
            pass
        
        ip_address = self._get_ip_addresses_from_instance(created_instance.addresses)
        a10_record = self._build_a10_appliance_record(created_instance, image, server, ip_address)

        # TODO(mdurrant): Do something with the result of this call, like validation.
        self._a10_api.create_a10_appliance(request, **a10_record)
        return created_instance

    def delete_instance(self, instance_id):
        return self._nova_api.servers.delete(instance_id)

    def get_instance(self, instance):
        return self._nova_api.servers.get(instance)

    def get_flavor(self, context, identifier=None):
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

    def get_image(self, context, identifier=None):
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

    def get_networks(self, context, networks=[]):
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

        id_func = (lambda x: x.get("net-id",
                   x.get("uuid", x.get("id", None))) if x is not None else None)

        available_networks = dict((id_func(x), x) for x in net_list)

        missing_networks = [x for x in networks if x not in available_networks.keys()]

        if any(missing_networks):
            self._handle_missing_networks(missing_networks)

        return [id_func(available_networks[x]) for x in networks]
