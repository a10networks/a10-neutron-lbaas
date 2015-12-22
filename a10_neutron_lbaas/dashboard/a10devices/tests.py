# Copyright 2015,  A10 Networks
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

from mox3.mox import IgnoreArg  # noqa
from mox3.mox import IsA  # noqa

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django import http

from horizon.workflows import views

from openstack_dashboard import api
from openstack_dashboard.test import helpers as test

from openstack_dashboard.dashboards.project.loadbalancers import workflows


class TestA10Dashboard(test.TestCase):
	class AttributeDict(dict):
	    def __getattr__(self, attr):
	        return self[attr]

	    def __setattr__(self, attr, value):
	        self[attr] = value

	"""
	Add image
		Handle exceptions
		Correct url resolution
		Correct view resolution

	"""
	DASHBOARD_NAME = "project"
	IMAGE_PATH_BASE = "horizon:project:a10images"
	APPLIANCE_PATH_BASE = "horizon:project:a10appliances"
	INDEX_FORMAT = "{0}:index"
	IMAGES_INDEX_PATH = INDEX_FORMAT.format(IMAGE_PATH_BASE)
	APPLIANCES_INDEX_PATH = INDEX_FORMAT.format(APPLIANCE_PATH_BASE)

	test_image = {}
	test_instance = {}

	test_image_list = []

	def setup_default_expectations(self):
		api.glance.image_create(
			IsA(http.HttpRequest), tenant_id=self.tenant.id
			).AndReturn(test_image)
		# Not sure we need to specify the types for builtins

		api.glance.image_list(IsA(http.HttpRequest), IsA(bool), IsA(str), IsA(str), IsA(dict), IsA(bool)).AndReturn(test_image_list)

	def test_image_index_url(self):
		self.setup_default_expectations()
		self.mox.ReplayAll()

		res = self.client.get(IMAGES_INDEX_PATH)
		self.assertTemplateUsed(res, "horizon/common/_detail_table.html")
		self.assertEqual(len(res.context["table"].data), len(self.image_list))


	# def test_get_images_calls_glance(self):
	# 	raise NotImplementedError("Not implemented!")

	# def test_