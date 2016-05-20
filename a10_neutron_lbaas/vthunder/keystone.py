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

    def __init__(self, keystone_version, auth_url, vthunder_config):
        (self._session, self._keystone_client) = self._get_keystone(
            ks_version=keystone_version,
            auth_url=auth_url,
            tenant_name=vthunder_config['vthunder_tenant_name'],
            user=vthunder_config['vthunder_tenant_username'],
            password=vthunder_config['vthunder_tenant_password'])

    @property
    def session(self):
        return self._session

    @property
    def client(self):
        return self._keystone_client

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
