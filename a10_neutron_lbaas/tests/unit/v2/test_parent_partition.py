import a10_neutron_lbaas.v2.v2_context as a10
import mock

import fake_objs
import mocks
import test_base


class TestA10PartitionKey(test_base.UnitTestBase):
    def _build_openstack_context(self):
        admin_context = {
            "tenant_id": "admin"
        }

        return mock.Mock(get_admin_context=mock.Mock(return_value=admin_context))

    def setUp(self, **kwargs):
        super(TestA10PartitionKey, self).setUp(**kwargs)
        self.handler = self.a.pool
        self.ctx = self._build_openstack_context()
        self.m = fake_objs.FakeLoadBalancer()

    def test_use_parent(self):
        fake_keystone = mock.MagicMock()
        fake_keystone.client.projects.get = mock.MagicMock(return_value=fake_objs.FakeKeystoneClient("brick"))
        a10.a10_context.keystone_helpers.KeystoneFromContext = mock.MagicMock(return_value=fake_keystone)

        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_key, "brick")

    def test_use_parent_no_parent(self):
        fake_keystone = mock.MagicMock()
        fake_keystone.client.projects.get = mock.MagicMock(return_value=fake_objs.FakeKeystoneClient())
        a10.a10_context.keystone_helpers.KeystoneFromContext = mock.MagicMock(return_value=fake_keystone)

        with a10.A10WriteContext(self.handler, self.ctx, self.m, device_name='axadp-noalt') as c:
            self.assertEqual(c.partition_key, "get-off-my-lawn")
