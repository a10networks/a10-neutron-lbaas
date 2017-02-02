# Copyright 2016,  A10 Networks
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
#    under the License.from neutron.db import model_base

import copy
import mock
import os

import alembic.command as alembic_command
import alembic.config as alembic_config
import alembic.op as op
import sqlalchemy

import a10_neutron_lbaas.db.migration as migration
import a10_neutron_lbaas.tests.db.session as session
import test_base


class TestMigrations(test_base.UnitTestBase):

    def setUp(self):
        super(TestMigrations, self).setUp()
        self.patch_create_engine = mock.patch.object(sqlalchemy,
                                                     'create_engine',
                                                     return_value=self.connection)
        self.patch_create_engine.__enter__()

        create_index = op.create_index
        drop_index = op.drop_index

        def create_uniquely_named_index(name, tname, *args, **kwargs):
            return create_index(tname + '_' + name, tname, *args, **kwargs)

        def drop_uniquely_named_index(name, *args, **kwargs):
            return drop_index((kwargs.get('table_name') or args[0]) + '_' + name, *args, **kwargs)

        self.patch_op_create_index = mock.patch.object(op,
                                                       'create_index',
                                                       side_effect=create_uniquely_named_index)
        self.patch_op_drop_index = mock.patch.object(op,
                                                     'drop_index',
                                                     side_effect=drop_uniquely_named_index)
        self.patch_op_create_index.__enter__()
        self.patch_op_drop_index.__enter__()

    def tearDown(self):
        self.patch_op_drop_index.__exit__()
        self.patch_op_create_index.__exit__()
        self.patch_create_engine.__exit__()
        super(TestMigrations, self).tearDown()

    def config(self):
        config = alembic_config.Config(
            os.path.join(os.path.dirname(migration.__file__), 'alembic.ini')
        )
        config.connection = self.connection
        return config

    def upgrade(self, revision):
        alembic_command.upgrade(self.config(), revision)

    def downgrade(self, revision):
        alembic_command.downgrade(self.config(), revision)

    def test_install(self):
        self.upgrade('heads')

    def test_install_schema_matches_model_schema(self):
        self.upgrade('heads')

        a10_models = session.a10_models()

        inspection = sqlalchemy.inspect(self.connection)

        tables = inspection.get_table_names()

        missing_tables = [model.__tablename__ for model in a10_models if
                          model.__tablename__ not in tables]
        self.assertEqual([], missing_tables,
                         "The following tables weren't created by installing {0}".
                         format(missing_tables))

        dialect = self.connection.dialect
        ddl_compiler = dialect.ddl_compiler(dialect, None)

        def normalize(schema_type):
            copied_type = copy.copy(schema_type)
            # We don't care about display width
            if getattr(copied_type, 'display_width', None) is not None:
                copied_type.display_width = None
            if type(schema_type) is sqlalchemy.sql.sqltypes.Text:
                copied_type.length = None

            normalized_type = copied_type.compile(dialect=dialect)

            # mysql has some weird synonyms
            if dialect.name == 'mysql':
                weird_synonyms = {
                    'BOOL': 'TINYINT',
                    'BOOLEAN': 'TINYINT',
                    'TEXT()': 'TEXT'
                }
                normalized_type = weird_synonyms.get(normalized_type, normalized_type)

            return normalized_type

        for model in a10_models:
            columns = inspection.get_columns(model.__tablename__)

            actual_columns = sorted([
                {
                    'nullable': c['nullable'],
                    'default': c['default'],
                    'type': normalize(c['type']),
                    'name': unicode(c['name'])
                }
                for c in columns],
                key=lambda x: x['name'])

            mapper = sqlalchemy.inspect(model)

            expected_columns = sorted([
                {
                    'nullable': c.nullable,
                    'default': ddl_compiler.get_column_default_string(c),
                    'type': normalize(c.type),
                    'name': unicode(c.name)
                }
                for c in mapper.columns
                if c.table.name == model.__tablename__],
                key=lambda x: x['name'])

            if (actual_columns != expected_columns):
                print ("The model and installed columns for {0} don't match".
                       format(model.__tablename__))
                print ("Model columns    ", [c['name'] for c in expected_columns])
                print ("Installed columns", [c['name'] for c in actual_columns])
            self.assertEqual(expected_columns, actual_columns)

    def test_upgrade_heads_downgrade_base(self):
        self.upgrade('heads')
        self.downgrade('base')

    def test_upgrade_heads_downgrade_base_upgrade_heads(self):
        self.upgrade('heads')
        self.downgrade('base')
        self.upgrade('heads')
