# Copyright 2016, A10 Networks
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

from contextlib import contextmanager

from a10_neutron_lbaas.db import api as db_api


@contextmanager
def a10_db_context(openstack_context, db_session=None):
    """Swaps out the database session on a neutron openstack context
    for an a10 database session.
    """

    with db_api.magic_session(db_session=db_session) as a10_db_session:
        neutron_db_session = openstack_context.session
        try:
            openstack_context.session = a10_db_session
            yield openstack_context
        finally:
            openstack_context.session = neutron_db_session
