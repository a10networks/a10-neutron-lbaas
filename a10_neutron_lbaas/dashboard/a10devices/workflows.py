# Copyright 2015 A10 Networks
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

import json
import logging
import uuid

from django.utils.translation import ugettext_lazy as _

import a10_neutron_lbaas.a10_config as a10_config
import a10_neutron_lbaas.instance_manager as im

import horizon.forms as forms
import horizon.workflows as workflows
import openstack_dashboard.api.glance as glance_api
import openstack_dashboard.api.neutron as neutron_api
import openstack_dashboard.api.nova as nova_api

# GITFLAG
import pprint
pp = pprint.PrettyPrinter(indent=4)

LOG = logging.getLogger(__name__)


class AddApplianceAction(workflows.Action):
    name = forms.CharField(max_length=80, label=_("Name"))
    flavor = forms.ChoiceField(label=_("Flavor"))
    image = forms.ChoiceField(label=_("Image"))
    # TODO(mdurrant): mgmt network/dp network/vip network
    networks = forms.ChoiceField(label=_("Networks"))

    def __init__(self, request, *args, **kwargs):
        super(AddApplianceAction, self).__init__(request, *args, **kwargs)
        # So we can get networks for the tenant
        tenant_id = request.user.tenant_id

        # default values
        network_choices = [((""), _("Select a network"))]
        flavor_choices = [((""), _("Select a flavor"))]
        image_choices = [((""), _("Select an image"))]

        # Get our data from the API
        networks = neutron_api.network_list_for_tenant(request, tenant_id=tenant_id)
        flavors = nova_api.flavor_list(request)
        (images, has_more, has_prev) = glance_api.image_list_detailed(request)

        # Build the list from IDs/names
        self._build_choices_list(network_choices, networks)
        self._build_choices_list(flavor_choices, flavors)
        self._build_choices_list(image_choices, images)

        # assign it to the choices
        self.fields["networks"].choices = network_choices
        self.fields["flavor"].choices = flavor_choices
        self.fields["image"].choices = image_choices

    class Meta(object):
        name = _("Add Appliance")
        permissions = ('openstack.services.network',)
        help_text_template = '_create_appliance_help.html'

    def _build_choices_list(self, target=[], choices=[], transform=lambda x: ((x.id, x.name))):
        for x in choices:
            target.append(transform(x))


class AddApplianceStep(workflows.Step):
    action_class = AddApplianceAction
    contributes = ("name", "flavor", "image", "networks")

    def contribute(self, data, context):
        context = super(AddApplianceStep, self).contribute(data, context)
        if data:
            return context


class AddAppliance(workflows.Workflow):
    slug = "addpool"
    name = _("Add Appliance")
    finalize_button_name = _("Add")
    success_message = _('Added appliance "%s".')
    failure_message = _('Unable to add appliance "%s".')
    success_url = "horizon:project:a10appliances:index"
    default_steps = (AddApplianceStep,)

    def format_status_message(self, message):
        name = self.context.get('name')
        return message % name

    def handle(self, request, context):
        # Create the instance manager, giving it the context so it knows how to auth
        instance_mgr = im.InstanceManager(context=context, request=request)
        instance_data = instance_mgr.create_instance(request, context)

        LOG.debug("Instance: {0}".format(instance_data))
        return True


class AddImageAction(workflows.Action):
    name = forms.CharField(max_length=80, label=_("Name"))
    location = forms.CharField(label=_("Image URL"))
    # image = forms.FileField(label=_("Image Data"))
    username = forms.CharField(label=_("Username"))
    password = forms.CharField(label=_("Password"))
    api_version = forms.ChoiceField(label=_("API Version"))

    def __init__(self, request, *args, **kwargs):
        super(AddImageAction, self).__init__(request, *args, **kwargs)
        self.tenant_id = request.user.tenant_id
        # TODO(mdurrant) - A10 versions need to come from a data source, not a hardcoded list.
        api_versions = [("2.1", "2.1"), ("3.0", "3.0")]
        self.fields["api_version"].choices = api_versions

    class Meta(object):
        name = _("Add Image")
        permissions = ('openstack.services.network',)
        help_text_template = '_create_image_help.html'


class AddImageStep(workflows.Step):
    action_class = AddImageAction
    contributes = ("name", "url", "username", "password", "api_version")

    def _build_properties(self, context):
            result = {'username': None,
                      'password': None,
                      'api_version': None}

            for x in result.keys():
                result[x] = context.get(x)
            return result

    def contribute(self, data, context):
        image_data = {}

        if data:
            image_props = self._build_properties(data)
            image_data = self._merge_defaults(data)
            self._clean_image_data(image_data)
            image_data["properties"] = json.dumps(image_props)
            image_data["location"] = str(image_data.get("location"))
            image_data["name"] = str(image_data.get("name"))
            image_data["id"] = str(uuid.uuid4())
        return image_data

    def _clean_image_data(self, image_data):
        # This removes form data so it doesn't get passed on
        # and create schema validation errors.
        # Said form data gets shoved in to the "properties"
        # property of the image.
        del_props = ['username', 'password', 'api_version']
        for x in del_props:
            if x in image_data:
                del(image_data[x])

    def _merge_defaults(self, context):
        """Merge the data specified by the user with our defaults  stored in config.py."""
        config = a10_config.A10Config()
        image_defaults = config.image_defaults

        for k, v in image_defaults.items():
            # If the value isn't already specified, use the default.
            transform = lambda x: x
            if k not in context:
                if isinstance(v, basestring):
                    transform = lambda x: str(x)

                context[k] = transform(v)
        return context


class AddImage(workflows.Workflow):
    slug = "addimage"
    name = _("Add Image")
    finalize_button_name = _("Add")
    success_message = _('Added image "%s".')
    failure_message = _('Unable to add image "%s".')
    success_url = "horizon:project:a10appliances:index"
    default_steps = (AddImageStep,)

    def format_status_message(self, message):
        name = self.context.get('name')
        return message % name

    def handle(self, request, context):
        LOG.debug("<ImageCreating> {0}".format(context))
        # Tell glance to create the image.
        created = glance_api.glanceclient(request, version=2).images.create(**context)
        LOG.debug("</ImageCreating> {0}".format(created))
        return True
