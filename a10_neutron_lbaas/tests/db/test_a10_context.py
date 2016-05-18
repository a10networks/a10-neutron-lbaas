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
#    under the License.from neutron.db import model_base

import mock

import a10_neutron_lbaas.tests.unit.test_a10_openstack_lb as test_a10_openstack_lb
import test_base

import a10_neutron_lbaas.a10_context as a10_context
import a10_neutron_lbaas.vthunder.instance_manager as instance_manager


class TestA10Context(test_a10_openstack_lb.SetupA10OpenstackLBBase, test_base.UnitTestBase):

    def setUp(self):
        super(TestA10Context, self).setUp()

        # unit_config.setUp()

        mock_driver = mock.MagicMock()
        with mock.patch('acos_client.Client'):
            a10_driver = self.a10_openstack_lb_class(
                mock_driver,
                **self.a10_openstack_lb_kws)

        mock_handler = mock.MagicMock(openstack_driver=mock_driver, a10_driver=a10_driver)

        session = self.open_session()
        mock_openstack_context = mock.MagicMock(session=session)

        mock_openstack_lbaas_obj = mock.MagicMock(tenant_id='fake-tenant-id')

        self.a10_context = a10_context.A10Context(mock_handler,
                                                  mock_openstack_context,
                                                  mock_openstack_lbaas_obj)

    def test_inventory_find(self):
        """Test inventory and scheduling hooks in their almost-real environment"""

        # We really just want to patch glance, but oslo library loading is non-standard.
        mock_glance_client = mock.MagicMock()
        mock_glance_client.images.list.return_value = []

        InstanceManager = instance_manager.InstanceManager
        with mock.patch(
            'a10_neutron_lbaas.vthunder.instance_manager.InstanceManager'
        ) as mock_instance_manager:

            mock_instance_manager.side_effect = lambda *args, **kwargs: InstanceManager(
                *args,
                glance_api=mock_glance_client,
                **kwargs)

            # with self.a10_context:
            #     device = self.a10_context._get_device()

        # session = self.a10_context.db_operations.session
        # session.commit()
        # saved_device = session.query(models.A10ApplianceSLB).get(appliance.id)

        # self.assertEqual(appliance, saved_appliance)


class TestA10ContextPlumbingHooks(test_a10_openstack_lb.SetupPlumbingHooks, TestA10Context):
    pass


class TestA10ContextV1(test_a10_openstack_lb.SetupA10OpenstackLBV1, TestA10Context):
    pass


class TestA10ContextV1PlumbingHooks(test_a10_openstack_lb.SetupA10OpenstackLBV1,
                                    test_a10_openstack_lb.SetupPlumbingHooks,
                                    TestA10Context):
    pass


class SetupA10ContextV2(test_a10_openstack_lb.SetupA10OpenstackLBV2):

    def setUp(self):
        super(SetupA10ContextV2, self).setUp()
        self.a10_context.openstack_lbaas_obj.root_loadbalancer = mock.MagicMock(id='fake-lb-id')


class TestA10ContextV2(SetupA10ContextV2, TestA10Context):
    pass


class TestA10ContextV2PlumbingHooks(SetupA10ContextV2,
                                    test_a10_openstack_lb.SetupPlumbingHooks,
                                    TestA10Context):
    pass
