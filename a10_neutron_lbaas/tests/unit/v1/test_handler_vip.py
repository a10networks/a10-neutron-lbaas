# Copyright 2014-2016 A10 Networks
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

import a10_neutron_lbaas.a10_exceptions as a10_ex
import fake_objs
import test_base


class TestVIP(test_base.UnitTestBase):
    def __init__(self, *args):
        super(TestVIP, self).__init__(*args)

    def test_create(self):
        self.a.vip.create(None, fake_objs.FakeVIP())
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('virtual_server.create' in s)
        self.assertTrue('1.1.1.1' in s)
        self.assertTrue('vport.create' in s)
        self.assertTrue('id1' in s)
        self.assertTrue('UP' in s)
        self.a.openstack_driver.plugin.get_pool.assert_called_with(
            None, 'pool1')
        self.assertTrue('HTTP' in s)

    def test_create_pers(self):
        self.a.vip.create(None, fake_objs.FakeVIP('HTTP_COOKIE'))
        s = str(self.a.last_client.mock_calls)
        self.assertTrue("c_pers_name='id1'" in s)

    def test_create_adds_slb(self):
        self.a.vip.create(None, fake_objs.FakeVIP())

    def test_create_unsupported(self):
        try:
            self.a.vip.create(None, fake_objs.FakeVIP('APP_COOKIE'))
        except a10_ex.UnsupportedFeature:
            pass

    def test_create_autosnat_false_v21(self):
        self._test_create_autosnat("2.1", False, "source_nat_auto")

    def test_create_autosnat_true_v21(self):
        self._test_create_autosnat("2.1", True, "source_nat_auto")

    def test_create_autosnat_true_v30(self):
        self._test_create_autosnat("3.0", True, "auto")

    def test_create_autosnat_false_v30(self):
        self._test_create_autosnat("3.0", False, "auto")

    def _test_create_autosnat(self, api_ver=None, autosnat=None, key="auto"):

        """
        Due to how the config is pulled in, we can't override the config
        version here and just expect it to work.
        """
        for k, v in self.a.config.get_devices().items():
            v['api_version'] = api_ver
            v['autosnat'] = autosnat

        vip = fake_objs.FakeVIP()

        self.a.vip.create(None, vip)
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('virtual_server.create' in s)
        self.assertIn('autosnat=%s' % autosnat, s)

    def test_create_default_vrid_none_v21(self):
        self._test_create_default_vrid("2.1", None)

    def test_create_default_vrid_set_v21(self):
        self._test_create_default_vrid("2.1", 7)

    def test_create_default_vrid_none_v30(self):
        self._test_create_default_vrid("3.0", None)

    def test_create_default_vrid_set_v30(self):
        self._test_create_default_vrid("3.0", 7)

    def _test_create_default_vrid(self, api_ver=None, default_vrid=None):

        """
        Due to how the config is pulled in, we override the config
        for all of the devices.
        """

        for k, v in self.a.config.get_devices().items():
            v['api_version'] = api_ver
            v['default_virtual_server_vrid'] = default_vrid

        vip = fake_objs.FakeVIP()
        self.a.vip.create(None, vip)

        create = self.a.last_client.slb.virtual_server.create
        create.assert_has_calls([mock.ANY])
        calls = create.call_args_list

        if default_vrid is not None:
            self.assertIn('vrid=%s' % default_vrid, str(calls))
        if default_vrid is None:
            foundVrid = any(
                'vrid' in x.get('axapi_args', {}).get('virtual_server', {})
                for (_, x) in calls)
            self.assertFalse(
                foundVrid,
                'Expected to find no vrid in {0}'.format(str(calls)))

    def _test_create_ipinip(self, ip_in_ip=False, api_ver="3.0"):
        vip = fake_objs.FakeVIP()

        for k, v in self.a.config.devices.items():
            v['ipinip'] = ip_in_ip
            v['api_version'] = api_ver

        self.a.vip.create(None, vip)
        s = str(self.a.last_client.mock_calls)
        self.assertIn('vport.create', s)
        self.assertIn('ipinip=%s' % ip_in_ip, s)

    def test_create_ip_in_ip_positive_v30(self):
        self._test_create_ipinip(True)

    def test_create_ip_in_ip_negative_v30(self):
        self._test_create_ipinip()

    def test_create_ip_in_ip_positive_v21(self):
        self._test_create_ipinip(True, api_ver="2.1")

    def test_create_ip_in_ip_negative_v21(self):
        self._test_create_ipinip(api_ver="2.1")

    def test_update(self):
        self.a.vip.update(None, fake_objs.FakeVIP(), fake_objs.FakeVIP())
        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('id1' in s)
        self.assertTrue('UP' in s)
        self.a.openstack_driver.plugin.get_pool.assert_called_with(
            None, 'pool1')
        self.assertTrue('HTTP' in s)

    def test_update_delete_pers(self):
        vip_id = "id2"
        self.a.vip.update(None, fake_objs.FakeVIP('SOURCE_IP', vip_id=vip_id), fake_objs.FakeVIP())
        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('id1' in s)
        self.assertTrue('UP' in s)
        self.a.openstack_driver.plugin.get_pool.assert_called_with(None, 'pool1')
        z = self.a.last_client.slb.template.src_ip_persistence.delete
        z.assert_called_with(vip_id)
        self.assertTrue('HTTP' in s)

    def test_update_change_pers(self):
        vip_id = "id2"
        self.a.vip.update(None, fake_objs.FakeVIP('SOURCE_IP', vip_id=vip_id),
                          fake_objs.FakeVIP('HTTP_COOKIE'))
        self.print_mocks()
        s = str(self.a.last_client.mock_calls)
        self.assertTrue('vport.update' in s)
        self.assertTrue('id1' in s)
        self.assertTrue('UP' in s)
        self.a.openstack_driver.plugin.get_pool.assert_called_with(None, 'pool1')
        z = self.a.last_client.slb.template.cookie_persistence.create
        z.assert_called_with("id1")
        self.assertTrue('HTTP' in s)

    def test_delete(self):
        self.a.vip.delete(None, fake_objs.FakeVIP())
        self.a.last_client.slb.virtual_server.delete.assert_called_with('id1')

    def test_delete_removes_slb(self):
        self.a.vip.delete(None, fake_objs.FakeVIP())

    def test_delete_pers(self):
        vip_id = "idx"
        self.a.vip.delete(None, fake_objs.FakeVIP('SOURCE_IP', vip_id=vip_id))
        self.a.last_client.slb.virtual_server.delete.assert_called_with(vip_id)
        z = self.a.last_client.slb.template.src_ip_persistence.delete
        z.assert_called_with(vip_id)
