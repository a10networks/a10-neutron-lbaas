# Copyright 2012 New Dream Network, LLC (DreamHost)
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
#

import itertools
import os

import a10_neutron_lbaas.db.migration.mocks as mocks
import a10_neutron_lbaas.localization as localization
from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import migration as alembic_migration
from alembic.runtime.environment import EnvironmentContext
from alembic import script as alembic_script
from alembic import util as alembic_util
from oslo_config import cfg

import neutron.db.servicetype_db as servicetype_db
import neutron.services.service_base as service_base
import neutron_lbaas.services.loadbalancer.plugin as neutron_lbaas_plugin

SCRIPT_LOCATION = 'a10_neutron_lbaas.db.migration:alembic_migrations'

# Neutron is finicky. Sometimes _ is defined, sometimes it isn't
localization.install()

_db_opts = [
    cfg.StrOpt('connection',
               deprecated_name='sql_connection',
               default='',
               help=_('URL to database')),
]

CONF = cfg.CONF
try:
    CONF.register_opts(_db_opts, 'database')
except cfg.DuplicateOptError:
    pass

# There's an existing verbose option.
# It conflicts with --verbose
# It's deprecated, so we can't just use it instead.
# Kill it.
try:
    CONF.unregister_opt(CONF._opts['verbose']['opt'])
except Exception:
    # With fire!
    pass


def do_alembic_command(config, cmd, *args, **kwargs):
    try:
        getattr(alembic_command, cmd)(config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(str(e))


def do_query(config, cmd):
    do_alembic_command(config, cmd,
                       verbose=CONF.command.verbose)


def do_upgrade(config, cmd):
    if not CONF.command.revision and not CONF.command.delta:
        raise SystemExit(_('You must provide a revision or relative delta'))

    if CONF.command.delta:
        revision = '+' + str(CONF.command.delta)
    else:
        revision = CONF.command.revision

    if CONF.command.sql:
        do_alembic_command(config, cmd, revision, sql=CONF.command.sql)
    else:
        _install(config, revision)


def do_downgrade(config, cmd):
    if not CONF.command.revision and not CONF.command.delta:
        raise SystemExit(_('You must provide a revision or relative delta'))

    if CONF.command.delta:
        revision = '-' + str(CONF.command.delta)
    else:
        revision = CONF.command.revision

    do_alembic_command(config, cmd, revision, sql=CONF.command.sql)


def do_stamp(config, cmd):
    do_alembic_command(config, cmd,
                       CONF.command.revision,
                       sql=CONF.command.sql)


def do_revision(config, cmd):
    do_alembic_command(config, cmd,
                       message=CONF.command.message,
                       autogenerate=CONF.command.autogenerate,
                       sql=CONF.command.sql,
                       head=CONF.command.head)


class IterStack(object):
    def __init__(self):
        self.stack = []

    def pushAll(self, iter):
        self.stack.append(iter.__iter__())

    def __iter__(self):
        return self

    def next(self):
        while True:
            if not self.stack:
                raise StopIteration()
            try:
                return self.stack[-1].next()
            except StopIteration:
                self.stack.pop()


def _postorder(expand, initial, key=lambda x: x):
    class NodeOp(object):
        def __init__(self, node):
            self.node = node

        def is_done(self):
            return False

        def expand(self):
            return []

    class Yield(NodeOp):
        def is_done(self):
            return True

    class Expand(NodeOp):
        def expand(self):
            return itertools.chain(
                itertools.imap(Expand, expand(self.node)),
                [Yield(self.node)])

    stack = IterStack()
    stack.pushAll(itertools.imap(Expand, initial))

    yielded = set()
    for node_op in stack:
        node_key = key(node_op.node)
        if node_key in yielded:
            continue
        stack.pushAll(node_op.expand())
        if node_op.is_done():
            yield node_op.node
            yielded.add(node_key)


def postorder(expand, initial, where=lambda x: True, **kw):
    return _postorder(lambda x: filter(where, expand(x)), filter(where, initial), **kw)


def _all_ancestors(script, revs, where=lambda x: True):
    revisions = script.get_revisions(revs)
    expand = lambda r: script.get_revisions(r._all_down_revisions)
    key = lambda r: r.revision
    return postorder(expand, revisions, where=where, key=key)


def _iter_ancestors(script, lower, upper):
    skip = set(itertools.imap(lambda r: r.revision, _all_ancestors(script, lower)))
    return _all_ancestors(script, upper, lambda r: r.revision not in skip)


def _install(config, destination_rev, script=None):
    """Just like alembic.command.upgrade, but actually works"""

    script = script or alembic_script.ScriptDirectory.from_config(config)

    def install(installed_rev, context):
        revisions_to_install = list(_iter_ancestors(script, installed_rev, destination_rev))
        return [
            alembic_migration.MigrationStep.upgrade_from_script(
                script.revision_map, revision)
            for revision in revisions_to_install
        ]

    with EnvironmentContext(
        config,
        script,
        fn=install,
        destination_rev=destination_rev
    ):
        script.run_env()


class InstallSuccess(object):
    def __init__(self, head):
        self.head = head
        self.status = 'UPGRADED'
        self.description = 'At {0}'.format(head.revision)


class InstallFailure(object):
    def __init__(self, head, exception):
        self.head = head
        self.exception = exception
        self.status = 'ERROR'
        self.description = str(exception)


def do_install(config, cmd):
    script = alembic_script.ScriptDirectory.from_config(config)
    heads = script.get_revisions(script.get_heads())

    status = dict()

    for head in heads:
        config.print_stdout('Upgrading {0}'.format(', '.join(head.branch_labels)))
        try:
            _install(config, head.revision, script=script)
            result = InstallSuccess(head)
            status.update(dict((label, result) for label in head.branch_labels))
        except Exception as e:
            result = InstallFailure(head, e)
            status.update(dict((label, result) for label in head.branch_labels))
            try:
                alembic_util.err(str(e))
            except BaseException:
                # Err logs the error, but also exits
                pass

    config.print_stdout('')
    config.print_stdout('Summary')
    longest_label = len(max(status.keys(), key=len))
    for label, result in sorted(status.items()):
        config.print_stdout('{0}  {1:<8}  {2}'.format(
            label.ljust(longest_label),
            result.status,
            result.description))

    return status


def add_command_parsers(subparsers):
    for name in ['current', 'history', 'branches', 'heads']:
        parser = subparsers.add_parser(name)
        parser.add_argument('--verbose', action='store_true')
        parser.set_defaults(func=do_query)

    parser = subparsers.add_parser('upgrade')
    parser.add_argument('--delta', type=int)
    parser.add_argument('--sql', action='store_true')
    parser.add_argument('revision', nargs='?')
    parser.set_defaults(func=do_upgrade)

    parser = subparsers.add_parser('downgrade')
    parser.add_argument('--delta', type=int)
    parser.add_argument('--sql', action='store_true')
    parser.add_argument('revision', nargs='?')
    parser.set_defaults(func=do_downgrade)

    parser = subparsers.add_parser('stamp')
    parser.add_argument('--sql', action='store_true')
    parser.add_argument('revision')
    parser.set_defaults(func=do_stamp)

    parser = subparsers.add_parser('revision')
    parser.add_argument('-m', '--message')
    parser.add_argument('--autogenerate', action='store_true')
    parser.add_argument('--sql', action='store_true')
    parser.add_argument('--head')
    parser.set_defaults(func=do_revision)

    parser = subparsers.add_parser('install')
    parser.set_defaults(func=do_install)


command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help=_('Available commands'),
                                handler=add_command_parsers)

CONF.register_cli_opt(command_opt)


def add_provider_configuration(type_manager, service_type):
    """Add provider configuration for neutron_lbaas service to the type_manager

    Only neutron versions liberty and newer require or support this
    """

    try:
        neutron_lbaas_plugin.add_provider_configuration(type_manager, service_type)
    except AttributeError:
        pass


class Drivers(object):
    def __init__(self):
        self.drivers = dict()
        self.plugin = mocks.UncallableMock(name='mock_neutron_plugin_base_v2')

    def __getitem__(self, key):
        try:
            return self.drivers[key]
        except KeyError:
            try:
                service_type_manager = servicetype_db.ServiceTypeManager.get_instance()
                add_provider_configuration(service_type_manager, key)
                self.drivers[key] = service_base.load_drivers(key, self.plugin)
            except BaseException:
                # Catch BaseException because load_drivers throws SystemExit
                # Pass becasue we'd just raise KeyError and the next line does that
                pass
            return self.drivers[key]


def run(drivers, **conf_args):
    config = alembic_config.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini')
    )
    config.set_main_option('script_location',
                           SCRIPT_LOCATION)
    # attach the Neutron conf to the Alembic conf
    config.neutron_config = CONF
    config.drivers = drivers

    CONF(**conf_args)
    return CONF.command.func(config, CONF.command.name)


def main():
    run(Drivers(), project='neutron')


if __name__ == "__main__":
    main()
