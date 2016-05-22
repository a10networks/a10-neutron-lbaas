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

import mock

import a10_neutron_lbaas.tests.test_case as test_case

import a10_neutron_lbaas.a10_openstack_lb as a10_openstack_lb
import a10_neutron_lbaas.plumbing_hooks as plumbing_hooks


class SetupA10OpenstackLBBase(object):

    @property
    def a10_openstack_lb_class(self):
        return a10_openstack_lb.A10OpenstackLBBase

    @property
    def a10_openstack_lb_kws(self):
        return {}


class SetupA10OpenstackLBV1(object):
    @property
    def a10_openstack_lb_class(self):
        return a10_openstack_lb.A10OpenstackLBV1


class SetupA10OpenstackLBV2(object):
    @property
    def a10_openstack_lb_class(self):
        return a10_openstack_lb.A10OpenstackLBV2


class SetupPlumbingHooks(object):
    @property
    def a10_openstack_lb_kws(self):
        kws = super(SetupPlumbingHooks, self).a10_openstack_lb_kws
        kws2 = kws.copy()
        kws2['plumbing_hooks_class'] = plumbing_hooks.PlumbingHooks
        return kws2


class TestA10Openstack(SetupA10OpenstackLBBase, test_case.TestCase):

    def setUp(self):
        mock_driver = mock.MagicMock()
        with mock.patch('acos_client.Client'):
            self.a = self.a10_openstack_lb_class(mock_driver, **self.a10_openstack_lb_kws)

    def test_sanity(self):
        pass


class TestA10OpenstackPlumbingHooks(SetupPlumbingHooks, TestA10Openstack):
    pass


class TestA10OpenstackV1(SetupA10OpenstackLBV1, TestA10Openstack):
    pass


class TestA10OpenstackV1PlumbingHooks(SetupA10OpenstackLBV1, SetupPlumbingHooks, TestA10Openstack):
    pass


class TestA10OpenstackV2(SetupA10OpenstackLBV2, TestA10Openstack):
    pass


class TestA10OpenstackV2PlumbingHooks(SetupA10OpenstackLBV2, SetupPlumbingHooks, TestA10Openstack):
    pass
