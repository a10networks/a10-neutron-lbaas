# Copyright 2016 A10 Networks
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

import mock

import fake_objs
import test_base

import a10_neutron_lbaas.a10_exceptions as a10_ex


class TestPools(test_base.UnitTestBase):
    def test_sanity(self):
        pass

    def test_create(self):
        methods = {
            'ROUND_ROBIN':
                self.a.last_client.slb.service_group.ROUND_ROBIN,
            'LEAST_CONNECTIONS':
                self.a.last_client.slb.service_group.LEAST_CONNECTION,
            'SOURCE_IP':
                self.a.last_client.slb.service_group.WEIGHTED_LEAST_CONNECTION,
        }
        protocols = {
            'TCP': self.a.last_client.slb.service_group.TCP,
            'UDP': self.a.last_client.slb.service_group.UDP,
        }

        persistences = [None, 'SOURCE_IP', 'HTTP_COOKIE', 'APP_COOKIE']
        listeners = [False, True]

        for p in protocols.keys():
            for m in methods.keys():
                for pers in persistences:
                    for listener in listeners:
                        self.a.reset_mocks()
                        saw_exception = False

                        pool = fake_objs.FakePool(p, m, pers, listener)
                        try:
                            self.a.pool.create(None, pool)
                        except a10_ex.UnsupportedFeature as e:
                            if pers == 'APP_COOKIE':
                                saw_exception = True
                            else:
                                raise e

                        self.print_mocks()

                        # (self.a.last_client.slb.service_group.create.
                        #     assert_called_with(
                        #     pool.id,
                        #     axapi_args={"service_group": {}},
                        #     lb_method=methods(m),
                        #     protocol=protocols(p)))

                        if not saw_exception:
                            n = str(self.a.last_client.mock_calls).index(
                                'slb.service_group.create')
                            self.assertTrue(n >= 0)

                        if pers == 'SOURCE_IP':
                            (self.a.last_client.slb.template.
                                src_ip_persistence.create.
                                assert_called_with(pool.id))
                        elif pers == 'HTTP_COOKIE':
                            (self.a.last_client.slb.template.
                                cookie_persistence.create.
                                assert_called_with(pool.id))
                        elif pers == 'APP_COOKIE':
                            (self.a.last_client.slb.template.
                                cookie_persistence.create.
                                assert_called_with(pool.id))

    def test_update(self):
        pers1 = None
        pers2 = None
        old_pool = fake_objs.FakePool('TCP', 'LEAST_CONNECTIONS', pers1, True)
        pool = fake_objs.FakePool('TCP', 'ROUND_ROBIN', pers2, True)
        self.a.pool.update(None, pool, old_pool)
        self.print_mocks()
        self.a.last_client.slb.service_group.update.assert_called_with(
            pool.id,
            axapi_args={"service_group": {}},
            lb_method=mock.ANY,
            protocol=mock.ANY)

    def test_delete(self):
        members = [[], [fake_objs.FakeMember()]]
        hms = [None, fake_objs.FakeHM('PING')]
        persistences = [None, 'SOURCE_IP', 'HTTP_COOKIE']
        listeners = [False, True]

        for m in members:
            for hm in hms:
                for pers in persistences:
                    for lst in listeners:
                        self.a.reset_mocks()

                        pool = fake_objs.FakePool('TCP', 'ROUND_ROBIN',
                                                  pers, lst,
                                                  members=m,
                                                  hm=hm)
                        self.a.pool.delete(None, pool)

                        self.print_mocks()

                        (self.a.last_client.slb.service_group.delete.
                            assert_called_with(pool.id))

                        if pers == 'SOURCE_IP':
                            (self.a.last_client.slb.template.
                                src_ip_persistence.delete.
                                assert_called_with(pool.id))
                        elif pers == 'HTTP_COOKIE':
                            (self.a.last_client.slb.template.
                                cookie_persistence.delete.
                                assert_called_with(pool.id))

    def _test_stats(self):
        pool = fake_objs.FakePool('TCP', 'ROUND_ROBIN', None, False)
        actual = self.a.pool.stats(None, pool)
        return pool, actual

    def test_stats_calls_service_group_stats(self):
        pool, actual = self._test_stats()
        (self.a.last_client.slb.service_group.stats.
            assert_called_with(pool.id))

    def test_stats_returns_stats(self):
        pool, actual = self._test_stats()
        self.assertIn("stats", actual)

    def test_stats_returns_members(self):
        pool, actual = self._test_stats()
        self.assertIn("members", actual)
