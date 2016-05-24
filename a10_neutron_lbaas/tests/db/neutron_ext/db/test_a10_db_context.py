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

import mock

import a10_neutron_lbaas.neutron_ext.db.a10_db_context as a10_db_context
import a10_neutron_lbaas.tests.db.test_base as test_base


class TestA10DbContext(test_base.UnitTestBase):

    def test_context_session_is_a10_session(self):
        db_session = self.open_session()

        context = mock.MagicMock(session=object())

        with a10_db_context.a10_db_context(context, db_session=db_session):
            self.assertIs(context.session, db_session)

    def test_context_session_is_restored(self):
        db_session = self.open_session()

        session = object()

        context = mock.MagicMock(session=session)

        class ExpectedException(Exception):
            pass

        try:
            with a10_db_context.a10_db_context(context, db_session=db_session):
                raise ExpectedException()
        except ExpectedException:
            pass

        self.assertIs(context.session, session)
