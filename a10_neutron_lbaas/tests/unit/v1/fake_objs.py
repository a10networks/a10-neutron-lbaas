# Copyright 2014, Doug Wiegley (dougwig), A10 Networks
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


class FakeModel(dict, object):
    def __getitem__(self, key, default=None):
        attr = getattr(self, key, default)
        return attr

    def get(self, key, default=None):
        return getattr(self, key, default)


class FakeVIP(FakeModel):
    def __init__(self, pers="", vip_id="id1"):
        super(FakeVIP, self).__init__()
        self.tenant_id = 'ten1'
        self.id = vip_id
        self.protocol = 'HTTP'
        self.admin_state_up = True
        self.address = '1.1.1.1'
        self.protocol_port = '80'
        self.pool_id = 'pool1'
        self.subnet_id = 'subnet1'
        self.root_loadbalancer = self
        if pers:
            self.session_persistence = {'type': pers}


class FakeHM(FakeModel):
    def __init__(self, type=None):
        super(FakeHM, self).__init__()
        self.id = "hm01"
        self.name = "hm01"
        self.tenant_id = 'tenv1'
        self.type = type
        self.delay = '5'
        self.timeout = 5
        self.max_retries = '5'
        self.pools = []
        self.root_loadbalancer = FakeVIP()
        if type in ['HTTP', 'HTTPS']:
            self.http_method = 'GET'
            self.url_path = '/'
            self.expected_codes = '200'

    def copy(self):
        return self


class FakePool(FakeModel):
    def __init__(self, protocol='TCP', method='ROUND_ROBIN'):
        super(FakePool, self).__init__()
        self.id = 'id1'
        self.tenant_id = 'ten1'
        self.protocol = protocol
        self.lb_method = method
        self.members = []
        self.root_loadbalancer = FakeVIP()


class FakeMember(FakeModel):
    def __init__(self, admin_state_up=True, pool_id='pool1'):
        super(FakeMember, self).__init__()
        self.address = '1.1.1.1'
        self.id = 'id1'
        self.tenant_id = 'ten1'
        self.admin_state_up = admin_state_up
        self.pool_id = pool_id
        self.protocol_port = '80'
        self.root_loadbalancer = FakeVIP()
