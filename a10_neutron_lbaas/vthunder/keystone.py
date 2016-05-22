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

from keystoneauth1.identity import v2
from keystoneauth1.identity import v3
from keystoneauth1 import session
from keystoneclient.v2_0 import client as keystone_v2_client
from keystoneclient.v3 import client as keystone_v3_client

import a10_neutron_lbaas.a10_exceptions as a10_ex


class KeystoneA10(object):

    def __init__(self, keystone_version, auth_url, vthunder_config=None, openstack_context=None):
        if vthunder_config is not None:
            (self._session, self._keystone_client) = self._get_keystone_pw(
                ks_version=keystone_version,
                auth_url=auth_url,
                tenant_name=vthunder_config['vthunder_tenant_name'],
                user=vthunder_config['vthunder_tenant_username'],
                password=vthunder_config['vthunder_tenant_password'])
        elif openstack_context is not None:
            (self._session, self._keystone_client) = self._get_keystone_token(
                ks_version=keystone_version,
                auth_url=auth_url,
                tenant_id=openstack_context.tenant_id,
                auth_token=openstack_context.auth_token)

    @property
    def session(self):
        return self._session

    @property
    def client(self):
        return self._keystone_client

    def _get_keystone_stuff(self, ks_version, auth):
        sess = session.Session(auth=auth)

        if int(ks_version) == 2:
            ks = keystone_v2_client.Client(session=sess)
        else:
            ks = keystone_v3_client.Client(session=sess)

        return (sess, ks)

    def _get_keystone_pw(self, ks_version, auth_url, user, password, tenant_name):
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

        return self._get_keystone_stuff(ks_version, auth)

    def _get_keystone_token(self, ks_version, auth_url, auth_token, tenant_id):
        if int(ks_version) == 2:
            auth = v2.Token(auth_url=auth_url, token=auth_token, tenant_id=tenant_id)
        elif int(ks_version) == 3:
            auth = v3.Token(auth_url=auth_url, token=auth_token, tenant_id=tenant_id)
        else:
            raise a10_ex.InvalidConfig('keystone version must be protovol version 2 or 3')

        return self._get_keystone_stuff(ks_version, auth)
