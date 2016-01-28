# Copyright 2013,  Mike Thompson,  A10 Networks.
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


from mock import MagicMock
from mock import Mock

import tests.unit.test_base as test_base


class UnsupportedFeature(Exception):
    pass


class UnitTestBase(test_base.UnitTestBase):

    def __init__(self, *args):
        super(UnitTestBase, self).__init__(*args)
        self.version = 'v1'

    def _get_context(self):
        context = MagicMock()
        context.session = MagicMock()
        context.__enter__ = Mock(return_value=MagicMock())
        context.__exit__ = Mock(return_value=False)
        return context

    def _get_neutrondb(self):
        return MagicMock(portbindingport_create_or_update=Mock())
