# Copyright (C) 2015 A10 Networks Inc. All rights reserved.
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

from __future__ import absolute_import

from django.conf import settings
import logging
from openstack_dashboard.api import base
from openstack_dashboard.api.neutron import NeutronAPIDictWrapper

# a10 client that extends neutronclient.v2_0.client.Client
from a10_neutron_lbaas_client import client as neutron_client

LOG = logging.getLogger(__name__)

RV_KEY = "a10_appliance"
RV_KEY_PLURAL = "{0}s".format(RV_KEY)


class A10Appliance(NeutronAPIDictWrapper):
    """Wrapper for neutron Certificates"""
    def __init__(self, apiresource):
        super(A10Appliance, self).__init__(apiresource)


def neutronclient(request):
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    LOG.debug('neutronclient connection created using token "%s" and url "%s"'
              % (request.user.token.id, base.url_for(request, 'network')))
    LOG.debug('user_id=%(user)s, tenant_id=%(tenant)s' %
              {'user': request.user.id, 'tenant': request.user.tenant_id})
    c = neutron_client.Client(token=request.user.token.id,
                              auth_url=base.url_for(request, 'identity'),
                              endpoint_url=base.url_for(request, 'network'),
                              insecure=insecure,
                              ca_cert=cacert)
    return c


def get_a10_appliances(request, **kwargs):
    rv = []
    rv = neutronclient(request).list_a10_appliances(**kwargs).get(RV_KEY_PLURAL)
    return map(A10Appliance, rv)


def get_a10_appliance(request, id, **params):
    rv = None
    rv = neutronclient(request).get_a10_appliance(id).get(RV_KEY)
    return map(A10Appliance, rv)


def delete_a10_appliance(request, id):
    neutronclient(request).delete_a10_appliance(id)


def create_a10_appliance(request, **kwargs):
    rv = None
    body = {RV_KEY: kwargs}
    rv = neutronclient(request).create_a10_appliance(body=body).get(RV_KEY)
    return A10Appliance(rv)


def update_a10_appliance(request, **kwargs):
    rv = None
    body = {RV_KEY: kwargs}
    rv = neutronclient(request).update_a10_appliance(body).get(RV_KEY)
    return map(A10Appliance, rv)
