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

# from django.core.urlresolvers import reverse
# from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

# from horizon import exceptions
# from horizon import forms
# from horizon import messages
from horizon import tabs
from horizon import workflows
# from horizon.utils import memoized


# from openstack_dashboard import api
# from openstack_dashboard.dashboards.project.loadbalancers \
#     import workflows as project_workflows

# import a10_neutron_lbaas.dashboard.a10devices.tables as p_tables
import a10_neutron_lbaas.dashboard.a10devices.tabs as p_tabs
import a10_neutron_lbaas.dashboard.a10devices.workflows as p_workflows


class IndexView(tabs.TabbedTableView):
    tab_group_class = p_tabs.A10Tabs
    template_name = "index_tab.html"
    page_title = _("A10 Appliances")


class AddApplianceView(workflows.WorkflowView):
    workflow_class = p_workflows.AddAppliance
    # template_name = "_add_appliance.html"


class AddImageView(workflows.WorkflowView):
    workflow_class = p_workflows.AddImage
    # template_name = "_add_image.html"
