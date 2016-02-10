# Copyright (C) 2016 A10 Networks Inc. All rights reserved.
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

from keystoneclient.auth.identity import generic as auth_plugin
from keystoneclient import session as keystone_session
from openstack_dashboard.api import base


def token_for(request):
    auth_url = base.url_for(request, 'identity')
    auth_token = request.user.token.unscoped_token
    project_name = request.user.token.project["name"]
    return auth_plugin.Token(token=auth_token,
                             project_name=project_name,
                             auth_url=auth_url)


def session_for(request):
    token = token_for(request)
    session = keystone_session.Session(auth=token)
    return session


def project_id_for(request):
    return request.user.token.project["id"]
