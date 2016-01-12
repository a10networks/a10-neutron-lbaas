# Copyright (C) 2014-2015, A10 Networks Inc. All rights reserved.
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

import logging

# from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from horizon import tables

LOG = logging.getLogger(__name__)


class AddApplianceAction(tables.LinkAction):
    name = "addappliance"
    verbose_name = _("Create Appliance")
    url = "horizon:project:a10appliances:addappliance"
    icon = "plus"
    classes = ("ajax-modal",)


class AddImageAction(tables.LinkAction):
    name = "addimage"
    verbose_name = _("Add Image")
    url = "horizon:project:a10appliances:addimage"
    icon = "plus"
    classes = ("ajax-modal",)


class DeleteImageAction(tables.LinkAction):
    name = "deleteimage"
    verbose_name = _("Delete Image")
    url = "horizon:project:a10appliances:deleteimage"


class A10ApplianceTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Hostname"), hidden=False)
    ip = tables.Column("host", verbose_name="Management IP")
    api_ver = tables.Column("api_version", verbose_name="API Version")

    class Meta(object):
        name = "a10appliancestable"
        verbose_name = _("A10 Appliances")
        table_actions = (AddApplianceAction,)
        row_actions = ()


class A10ImageTable(tables.DataTable):
    id = tables.Column("id", verbose_name=_("ID"), hidden=True)
    name = tables.Column("name", verbose_name=_("Name"))

    class Meta(object):
        name = "a10imagestable"
        verbose_name = _("A10 Images")
        table_actions = (AddImageAction,)
        row_actions = ()
