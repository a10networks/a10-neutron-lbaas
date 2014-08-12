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

import tests.unit.test_base as test_base


class FakeModel(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'fake-id-001')
        self.tenant_id = kwargs.get('tenant_id', 'get-off-my-lawn')


class FakeLoadBalancer(FakeModel):

    def __init__(self, listeners=[]):
        super(FakeLoadBalancer, self).__init__()
        self.id = 'fake-lb-id-001'
        self.listeners = listeners
        self.address = '5.5.5.5'
        self.admin_state_up = True


class FakeListener(FakeModel):

    def __init__(self, protocol, port, admin_state_up=True, pool=None,
                 loadbalancer=None):
        super(FakeListener, self).__init__()
        self.id = 'fake-listen-id-001'
        self.protocol = protocol
        self.port = port
        self.admin_state_up = admin_state_up
        self.default_pool = pool
        self.loadbalancer = loadbalancer


class FakePersistence(FakeModel):

    def __init__(self, persistence_type):
        super(FakePersistence, self).__init__()
        self.id = 'fake-pers-id-001'
        self.type = persistence_type


class FakeMember(FakeModel):

    def __init__(self, admin_state_up=True, pool=None,
                 id='fake-member-id-001',
                 address='2.2.2.2'):
        super(FakeMember, self).__init__()
        self.id = id
        self.address = address
        self.admin_state_up = admin_state_up
        self.pool = pool
        self.protocol_port = 80


class FakePool(FakeModel):

    def __init__(self, protocol, method, persistence, listener=False,
                 members=[], hm=None):
        super(FakePool, self).__init__()
        self.id = 'fake-pool-id-001'
        self.protocol = protocol
        self.lb_algorithm = method
        if persistence is None:
            self.sessionpersistence = None
        else:
            self.sessionpersistence = FakePersistence(persistence)
        if listener:
            self.listener = FakeListener(protocol, 2222, pool=self,
                                         loadbalancer=FakeLoadBalancer())
        else:
            self.listener = None
        for member in members:
            member.pool = self
        self.members = members
        self.healthmonitor = hm
        if hm is not None:
            self.healthmonitor.pool = self


class FakeHM(FakeModel):

    def __init__(self, prot, pool=None):
        super(FakeHM, self).__init__()
        self.id = 'fake-hm-id-001'
        self.name = 'hm1'
        self.type = prot
        self.delay = 6
        self.timeout = 7
        self.max_retries = 8
        self.http_method = 'GET'
        self.url_path = '/'
        self.expected_codes = '200'
        self.pool = pool


class UnitTestBase(test_base.UnitTestBase):

    def __init__(self, *args):
        super(UnitTestBase, self).__init__(*args)
        self.version = 'v2'
