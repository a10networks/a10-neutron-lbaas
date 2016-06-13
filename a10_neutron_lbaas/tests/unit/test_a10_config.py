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

import test_base


class TestA10Config(test_base.UnitTestBase):

    def test_verify_appliances(self):
        self.assertTrue(self.a.config.get('verify_appliances'))

    def test_num_appliances(self):
        # Everytime we update the test config, this test has to be updated
        # A better test would seem to be be parsnig the JSON structure found in the file
        # and comparing that against what we get in devices.
        # This actually tests the number of devices with status == True
        self.assertEqual(10, len(self.a.config.get_devices()))

    def test_expected_ports(self):
        self.assertEqual(8443, self.a.config.get_device('ax1')['port'])
        self.assertEqual(80, self.a.config.get_device('ax3')['port'])
        self.assertEqual(443, self.a.config.get_device('ax4')['port'])

    def test_expected_protocols(self):
        self.assertEqual('https', self.a.config.get_device('ax1')['protocol'])
        self.assertEqual('http', self.a.config.get_device('ax3')['protocol'])
        self.assertEqual('https', self.a.config.get_device('ax4')['protocol'])

    def test_v_method(self):
        for k, v in self.a.config.get_devices().items():
            self.assertEqual('LSI', v['v_method'].upper())

    def test_alternate_shared_partition(self):
        self.assertTrue(self.a.config.get_device('axadp-alt')['shared_partition'])

    def test_ip_in_ip(self):
        expected = True
        actual = False
        for k, v in self.a.config.get_devices().items():
            if "ip_in_ip" in v:
                actual = v['ip_in_ip']
                self.assertEqual(expected, actual)

    # TODO(dougwig) -- test new a10_config members
    # def test_image_defaults(self):
    #     self.assertIsNotNone(self.a.config.image_defaults)

    # def test_image_defaults_members(self):
    #     image_defaults = self.a.config.image_defaults
    #     actual = image_defaults.keys()
    #     expected = ["name", "id", "visibility", "tags", "min_disk",
    #                 "min_ram", "container_format", "protected",
    #                 "properties", "disk_format"]
    #     self.assertListEqual(sorted(expected), sorted(actual))

    # def test_instance_defaults(self):
    #     self.assertIsNotNone(self.a.config.instance_defaults)

    def test_backwards_compat(self):
        self.assertEqual(self.a.config.get_devices(), self.a.config.devices)
        self.assertEqual(self.a.config.get_devices(), self.a.config.config.devices)
        self.assertEqual(self.a.config.get(
            'database_connection'), self.a.config.database_connection)
        self.assertEqual(self.a.config.get('use_database'), self.a.config.use_database)
        self.assertEqual(self.a.config.get('verify_appliances'), self.a.config.verify_appliances)
        self.assertEqual(self.a.config.get(
            'database_connection'), self.a.config.config.database_connection)
        self.assertEqual(self.a.config.get('use_database'), self.a.config.config.use_database)
        self.assertEqual(self.a.config.get(
            'verify_appliances'), self.a.config.config.verify_appliances)


class TestA10ConfigProvider(test_base.UnitTestBase):

    def setUp(self):
        super(TestA10ConfigProvider, self).setUp({'provider': 'prov1'})

    def test_top_level(self):
        self.assertEqual(self.a.config.get('who_should_win'), 'the-doctor')
        self.assertEqual(self.a.config.get('best_spaceship'), 'tardis')

    def test_vthunder_api_version(self):
        v = self.a.config.get_vthunder_config()
        self.assertEqual(v['api_version'], '9.9')
        self.assertEqual(v['nova_flavor'], 'acos.min')
