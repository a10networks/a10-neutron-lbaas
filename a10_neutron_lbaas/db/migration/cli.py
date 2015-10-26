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

import os

from alembic import command as alembic_command
from alembic import config as alembic_config
from alembic import script as alembic_script
from alembic import util as alembic_util
from oslo.config import cfg

# Import neutron configuration declarations.
# Tgese modify cfg.CONF
import neutron.services.service_base as service_base

SCRIPT_LOCATION = 'a10_neutron_lbaas.db.migration:alembic_migrations'

_db_opts = [
    cfg.StrOpt('connection',
               deprecated_name='sql_connection',
               default='',
               help=_('URL to database')),
]

CONF = cfg.CONF
CONF.register_opts(_db_opts, 'database')


def do_alembic_command(config, cmd, *args, **kwargs):
    try:
        getattr(alembic_command, cmd)(config, *args, **kwargs)
    except alembic_util.CommandError as e:
        alembic_util.err(str(e))


def do_upgrade_downgrade(config, cmd):
    if not CONF.command.revision and not CONF.command.delta:
        raise SystemExit(_('You must provide a revision or relative delta'))

    revision = CONF.command.revision

    if CONF.command.delta:
        sign = '+' if CONF.command.name == 'upgrade' else '-'
        revision = sign + str(CONF.command.delta)
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


def add_command_parsers(subparsers):
    for name in ['current', 'history', 'branches', 'heads']:
        parser = subparsers.add_parser(name)
        parser.set_defaults(func=do_alembic_command)

    for name in ['upgrade', 'downgrade']:
        parser = subparsers.add_parser(name)
        parser.add_argument('--delta', type=int)
        parser.add_argument('--sql', action='store_true')
        parser.add_argument('revision', nargs='?')
        parser.set_defaults(func=do_upgrade_downgrade)

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


command_opt = cfg.SubCommandOpt('command',
                                title='Command',
                                help=_('Available commands'),
                                handler=add_command_parsers)

CONF.register_cli_opt(command_opt)


class Drivers(object):
    def __init__(self):
        self.drivers = dict()

    def __getitem__(self, key):
        try:
            return self.drivers[key]
        except Exception:
            self.drivers[key] = service_base.load_drivers(key, None)
            return self.drivers[key]


def main():
    config = alembic_config.Config(
        os.path.join(os.path.dirname(__file__), 'alembic.ini')
    )
    config.set_main_option('script_location',
                           SCRIPT_LOCATION)
    # attach the Neutron conf to the Alembic conf
    config.neutron_config = CONF
    config.drivers = Drivers()

    CONF(project='neutron')
    CONF.command.func(config, CONF.command.name)

if __name__ == "__main__":
    main()
