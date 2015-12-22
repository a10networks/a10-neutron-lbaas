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
#    under the License.


from django.conf.urls import patterns
from django.conf.urls import url

from a10_neutron_lbaas.dashboard.a10devices import views


urlpatterns = patterns(
    'a10_neutron_lbaas.dashboard.a10devices.views',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^addappliance$', views.AddApplianceView.as_view(), name='addappliance'),
    url(r'^addimage$', views.AddImageView.as_view(), name="addimage")
)
