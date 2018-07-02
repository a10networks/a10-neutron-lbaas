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

import uuid


class FakeModel(object):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'fake-id-001')
        self.tenant_id = kwargs.get('tenant_id', 'get-off-my-lawn')
        self.root_loadbalancer = None
        self.name = kwargs.get("name", "fake-name")


class FakePort(FakeModel):

    def __init__(self, **kwargs):
        self.id = kwargs.get('id', 'fake-port-01')
        self.tenant_id = kwargs.get('tenant_id', "tenantsruinedmypicnic")
        self.name = id


class FakeLoadBalancer(FakeModel):

    def __init__(self, listeners=[]):
        super(FakeLoadBalancer, self).__init__()
        self.id = 'fake-lb-id-001'
        self.listeners = listeners
        self.vip_port_id = str(uuid.uuid4())
        self.vip_port = FakePort()
        self.vip_address = '5.5.5.5'
        self.admin_state_up = True
        self.vip_port = {"id": "vip-id-001", "tenant_id": "tenant_id", "name": "vip-id-001"}
        self.vip_port_id = self.vip_port["id"]
        self.root_loadbalancer = self
        self.vip_subnet_id = "fake-subnet-id-001"
        self.pools = []

    def stats_v21(self):
        self.ret_stats = {
            "bytes_in": 1337,
            "bytes_out": 347,
            "active_connections": 101,
            "total_connections": 1337,
            "extended_stats": {
                "loadbalancer_stat": {
                    "req_bytes": 1337,
                    "resp_bytes": 347,
                    "cur_conns": 101,
                    "tot_conns": 1337,
                    "listener_stat": [{
                        "req_bytes": 1337,
                        "resp_bytes": 347,
                        "name": "3LD3RB33R135",
                        "cur_conns": 101,
                        "tot_conns": 1337,
                        "pool_stat_list": {
                            "cur_conns": 0,
                            "member_stat_list": [{
                                "req_bytes": 0,
                            }]
                        }
                    }]
                }
            }
        }

        self.virt_server = {
            "virtual_server_stat": {
                "req_bytes": 1337,
                "resp_bytes": 347,
                "cur_conns": 101,
                "tot_conns": 1337,
                "vport_stat_list": [{
                    "req_bytes": 1337,
                    "resp_bytes": 347,
                    "cur_conns": 101,
                    "tot_conns": 1337,
                    "name": "3LD3RB33R135"
                }]
            }
        }

        self.virt_service = {
            "virtual_service": {
                "service_group": "3LD3RB33R135"}
        }

        self.serv_group = {
            'service_group_stat': {
                'cur_conns': 0,
                'member_stat_list': [{
                    'req_bytes': 0}]}
        }

    def stats_v30(self):
        self.ret_stats_v30 = {
            "bytes_in": 1337,
            "bytes_out": 347,
            "active_connections": 101,
            "total_connections": 1337,
            "extended_stats": {
                "loadbalancer_stat": {
                    "total_fwd_bytes": 1337,
                    "total_rev_bytes": 347,
                    "curr_conn": 101,
                    "total_conn": 1337,
                    "listener_stat": [{
                        "stats": {
                            "total_fwd_bytes": 1337,
                            "total_rev_bytes": 347,
                            "curr_conn": 101,
                            "total_conn": 1337}}],
                    "pool_stat_list": {
                        'curr_conn': 0,
                        "service_peak_conn": 0,
                        "member_list": [{
                            "stats": {
                                "curr_conn": 0}}]}}}
        }

        self.port_list = {
            "port-list": [{
                "stats": {
                    "total_fwd_bytes": 1337,
                    "total_rev_bytes": 347,
                    "curr_conn": 101,
                    "total_conn": 1337}}]
        }

        self.virt_server = {
            "virtual-server": {
                "port-list": [{
                    "service-group": "3LD3RB33R135"}]}
        }

        self.service_group = {
            "service-group": {
                "stats": {
                    "service_peak_conn": 0}}
        }

        self.members = {
            "member-list": [{
                "stats": {
                    "curr_conn": 0}}]
        }


class FakeListener(FakeModel):

    def __init__(self, protocol, port, admin_state_up=True, pool=None,
                 loadbalancer=None, container_id=None, containers=None):
        super(FakeListener, self).__init__()
        self.id = 'fake-listen-id-001'
        self.name = 'openstackname'
        self.protocol = protocol
        self.protocol_port = port
        self.admin_state_up = admin_state_up
        self.default_pool = pool or FakePool('HTTP', 'ROUND_ROBIN', None)
        self.default_pool_id = self.default_pool.id
        self.loadbalancer = loadbalancer
        self.default_tls_container_id = container_id
        self.sni_containers = containers
        self.root_loadbalancer = FakeLoadBalancer()


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
        self.root_loadbalancer = FakeLoadBalancer()
        self.pool_id = "fake-pool"


class FakePool(FakeModel):

    def __init__(self, protocol, method, persistence, listener=False,
                 members=[], hm=None):
        super(FakePool, self).__init__()
        self.id = 'fake-pool-id-001'
        self.protocol = protocol
        self.lb_algorithm = method
        if persistence is None:
            self.session_persistence = None
        else:
            self.session_persistence = FakePersistence(persistence)
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
        self.root_loadbalancer = FakeLoadBalancer()


class FakeHM(FakeModel):

    def __init__(self, prot, pool=None):
        super(FakeHM, self).__init__()
        self.id = 'fake-hm-id-001'
        self.name = 'hm1'
        self.type = prot
        self.delay = 7
        self.timeout = 7
        self.max_retries = 8
        self.http_method = 'GET'
        self.url_path = '/'
        self.expected_codes = '200'
        self.pool = pool
        self.root_loadbalancer = FakeLoadBalancer()


class FakeCertificateBinding(FakeModel):

    def __init__(self, id=None, certificate_id=None, listener_id=None):
        super(FakeCertificateBinding, self).__init__()
        self.id = id or "binding01"
        self.certificate_id = certificate_id or "certid01"
        self.listener_id = listener_id or 'fake-listen-id-001'

class FakeKeystoneClient(object):

    def __init__(self, parent_id='default'):
        self.parent_id = parent_id
        self.domain_id = 'default'
