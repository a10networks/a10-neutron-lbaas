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

import logging
import uuid

from neutron.api.v2 import resource_helper
from neutron.db import common_db_mixin
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm.exc import NoResultFound

from a10_neutron_lbaas import a10_config
from a10_neutron_lbaas.db import models
from a10_neutron_lbaas.etc import defaults
from a10_neutron_lbaas.neutron_ext.common import attributes
from a10_neutron_lbaas.neutron_ext.common import constants
from a10_neutron_lbaas.neutron_ext.common import resources
from a10_neutron_lbaas.neutron_ext.extensions import a10Device

from a10_openstack_lib.resources import a10_device as a10_device_resources
from a10_openstack_lib.resources import validators


RESOURCE_ATTRIBUTE_MAP = resources.apply_template(a10_device_resources.RESOURCE_ATTRIBUTE_MAP,
                                                  attributes)


LOG = logging.getLogger(__name__)


def _uuid_str():
    return str(uuid.uuid4())


class A10DeviceDbMixin(common_db_mixin.CommonDbMixin,
                       a10Device.A10DevicePluginBase):

    def __init__(self, *args, **kwargs):
        super(A10DeviceDbMixin, self).__init__(*args, **kwargs)
        self.config = a10_config.A10Config()

    def _get_device_body(self, a10_device, resource):
        body = a10_device[resource]
        return resources.remove_attributes_not_specified(body)

    def _get_a10_device(self, context, a10_device_id):
        with context.session.begin(subtransactions=True):
            try:
                device_value_object_list = context.session.query(models.A10Device).filter_by(
                    id=a10_device_id).one()
            except NoResultFound:
                raise a10Device.A10DeviceNotFoundError(a10_device_id)
            return device_value_object_list

    def _rebuild_resources(self, resource_map):
        my_plurals = resource_helper.build_plural_mappings(
            {}, resource_map)
        attributes.PLURALS.update(my_plurals)
        resources = resource_helper.build_resource_info(my_plurals,
                                                        resource_map,
                                                        constants.A10_DEVICE)
        return resources

    def _add_device_kv(self, context, config, device_id):
        LOG.debug("A10DeviceDbMixin:_add_device_kv() config=%s" % (config))
        for k, v in config.items():
            device_value = {'a10_device_value': {'key_id': k,
                                                 'value': v,
                                                 'associated_obj_id':
                                                     device_id}}
            self.create_a10_device_value(context, device_value)

    def _make_a10_device_dict(self, a10_device_db, fields=None):
        res = {'description': a10_device_db.description,
               'id': a10_device_db.id,
               'name': a10_device_db.name,
               # Not all device records are nova instances
               'nova_instance_id': a10_device_db.nova_instance_id,
               'tenant_id': a10_device_db.tenant_id,

               'api_version': a10_device_db.api_version,
               'host': a10_device_db.host,
               'password': a10_device_db.password,
               'username': a10_device_db.username,

               'port': a10_device_db.port,
               'protocol': a10_device_db.protocol,

               'extra_resources': []}

        for device_value in a10_device_db.a10_opts:
            key = device_value.associated_key.name
            value = device_value.value
            (extra_resource, value) = self._make_extra_resource(key, value, 'a10_device')
            res[str(key)] = value
            if extra_resource:
                res['extra_resources'].append({str(key): extra_resource})

        return self._fields(res, fields)

    def _make_extra_resource(self, key, value, resource):
        '''
        Return mapped_resource dict, created from values in a10_openstack_lib.
        If no values in RESOURCE_ATTRIBUTE_MAP then return an empty
        mapped_resource
        '''
        device_type = resource + 's'

        if (key in RESOURCE_ATTRIBUTE_MAP[device_type].keys()
                and RESOURCE_ATTRIBUTE_MAP[device_type][key]['is_a10_opt']):
            mapped_resource = RESOURCE_ATTRIBUTE_MAP[device_type][key]

            if 'type:boolean' in mapped_resource['validate'].keys():
                value = mapped_resource['convert_to'](int(value))
                LOG.debug("A10DeviceDbMixin:_make_extra_resource() convert %s to bool %s" %
                          (key, value))
        else:
            LOG.error("A10DeviceDbMixin:_make_extra_resource() key %s isn't valid" % (key))
            mapped_resource = None

        return mapped_resource, value

    def validate_a10_opts(self, a10_opts, resource):
        LOG.debug("A10DeviceDbMixin:_get_a10_opts() a10_opts=%s, resource=%s" %
                  (a10_opts, resource))

        device_type = resource + 's'

        # Filter for options with commas in them
        # Split comma separated strings into separate options
        # append all options to new list
        opts = []
        for opt in a10_opts:
            if ',' in opt:
                for sub_opt in opt.split(','):
                    opts.append(sub_opt)
            else:
                opts.append(opt)

        # Inspect each option looking for key value pairs
        # Treat all values as strings
        # Assume an option name with no value is Boolean True
        # Appending 'no-' to any Boolean option will set it to False for updates
        # Lookup the type of any option with 'no-' prefix.  If not boolean, then
        # it will be set to None (which will be NULL in the db)
        opts_dict = {}
        valid_opts = RESOURCE_ATTRIBUTE_MAP[device_type].keys()
        for opt in opts:
            #If a Key/Value assignment
            if '=' in opt:
                (k, v) = opt.split('=')
                if k in valid_opts:
                    opts_dict[k.replace('-', '_').strip()] = v.strip()
                else:
                    LOG.error("A10DeviceDbMixin:_get_a10_opts() invalid a10_opts option: %s" % (k))
            #Else a Boolean Option
            else:
                if opt in valid_opts:
                    opts_dict[opt.replace('-', '_').strip()] = True
                elif opt.startswith('no-'):
                    false_opt = opt.replace('no-', '').strip()
                    if false_opt in valid_opts:
                        for opt_type in RESOURCE_ATTRIBUTE_MAP[
                                device_type].get(false_opt).get(
                                'validate').keys():
                            if "type:boolean" in opt_type:
                                opts_dict[false_opt.replace('-', '_').strip()] = False
                            elif opt_type.startswith("type:"):
                                opts_dict[false_opt] = None
                    else:
                        LOG.error("A10DeviceDbMixin:_get_a10_opts() invalid a10_opts option: %s" % (false_opt))
                else:
                    LOG.error("A10DeviceDbMixin:_get_a10_opts() invalid a10_opts option: %s" % (opt))

        LOG.debug("A10DeviceDbMixin:_get_a10_opts() opts_dict=%s " % (opts_dict))
        return opts_dict

    def a10_device_body_defaults(self, body, tenant_id, device_id, resource='a10_device'):
        '''
        Create full device record including provided device_id and tenant_id.
        Populate default values if option is not specified
        Convert a10_opts dict to flat device record ready to insert into db
        provide resource name if a10_vthunder type
        '''

        device_record = {'id': device_id,
                         'tenant_id': tenant_id,
                         'name': body.get('name', ''),
                         'description': body.get('description', ''),
                         'host': body['host'],
                         'username': body['username'],
                         'password': body['password'],
                         'api_version': body['api_version'],
                         # Not all device records are nova instances
                         'nova_instance_id': body.get('nova_instance_id'),
                         'port': int(body.get(
                             'port', defaults.DEVICE_OPTIONAL_DEFAULTS['port'])),
                         'protocol': body.get(
                             'protocol', defaults.DEVICE_OPTIONAL_DEFAULTS['protocol'])}
        return device_record

    def a10_opts_defaults(self, a10_opts={}, resource='a10_device'):

        if resource in 'a10_device':

            full_a10_opts = {
                'autosnat': a10_opts.get(
                    'autosnat', defaults.DEVICE_OPTIONAL_DEFAULTS['autosnat']),
                'conn_limit': a10_opts.get(
                    'conn_limit', defaults.DEVICE_OPTIONAL_DEFAULTS['conn_limit']),
                'default_virtual_server_vrid': a10_opts.get(
                    'default_virtual_server_vrid',
                    defaults.DEVICE_OPTIONAL_DEFAULTS[
                        'default_virtual_server_vrid']),
                'ipinip': a10_opts.get(
                    'ipinip', defaults.DEVICE_OPTIONAL_DEFAULTS['ipinip']),
                'source_nat_pool': a10_opts.get(
                    'source_nat_pool',
                    defaults.DEVICE_OPTIONAL_DEFAULTS['source_nat_pool']),
                'shared_partition': a10_opts.get(
                    'shared_partition',
                    defaults.DEVICE_OPTIONAL_DEFAULTS['shared_partition']),
                'use_float': a10_opts.get(
                    'use_float',
                    defaults.DEVICE_OPTIONAL_DEFAULTS['use_float']),
                'v_method': a10_opts.get(
                    'v_method',
                    defaults.DEVICE_OPTIONAL_DEFAULTS['v_method']),
                'write_memory': a10_opts.get(
                    'write_memory',
                    defaults.DEVICE_OPTIONAL_DEFAULTS['write_memory'])}

        elif resource in 'a10_vthunder':

            full_a10_opts = {
                'protocol': a10_opts.get(
                    'protocol',
                    defaults.VTHUNDER_OPTIONAL_DEFAULTS['protocol']),
                'autosnat': a10_opts.get(
                    'autosnat',
                    defaults.VTHUNDER_OPTIONAL_DEFAULTS['autosnat']),
                'v_method': a10_opts.get(
                    'v_method',
                    defaults.VTHUNDER_OPTIONAL_DEFAULTS['v_method']),
                'shared_partition': a10_opts.get(
                    'shared_partition',
                    defaults.VTHUNDER_OPTIONAL_DEFAULTS['shared_partition']),
                'use_float': a10_opts.get(
                    'use_float',
                    defaults.VTHUNDER_OPTIONAL_DEFAULTS['use_float']),
                'default_virtual_server_vrid': a10_opts.get(
                    'default_virtual_server_vrid', None),
                'ipinip': a10_opts.get(
                    'ipinip', defaults.VTHUNDER_OPTIONAL_DEFAULTS['ipinip']),
                'write_memory': a10_opts.get(
                    'write_memory',
                    defaults.VTHUNDER_OPTIONAL_DEFAULTS['write_memory'])}

        return full_a10_opts

    def create_a10_device(self, context, a10_device, resource='a10_device'):
        body = self._get_device_body(a10_device, resource)
        device_id = _uuid_str()

        LOG.debug("A10DeviceDbMixin:create_a10_device() body=%s" %
                  (body))

        a10_opts = {}
        a10_opts.update(self.validate_a10_opts(body.pop('a10_opts', []), resource))
        a10_opts = self.a10_opts_defaults(a10_opts, resource)

        LOG.debug("A10DeviceDbMixin:create_a10_device() before _config_keys_exist a10_opts=%s" %
                  (a10_opts))

        try:
            a10_opts = self._config_keys_exist(context, a10_opts)
        #Create the keys if they don't exist already
        except Exception:
            LOG.debug("A10DeviceDbMixin:create_a10_device() a key doesn't exist!")
            for key in a10_opts.keys():
                try:
                    self._get_a10_device_key_by_name(context, key)
                except Exception:
                    LOG.debug("A10DeviceDbMixin:create_a10_device() key:%s doesn't exist, creating..." %
                              (key))
                    self.create_a10_device_key(
                        context, {a10_device_resources.DEVICE_KEY: {'name': key}})
            a10_opts = self._config_keys_exist(context, a10_opts)

        with context.session.begin(subtransactions=True):
            device_record = models.A10Device(
                **self.a10_device_body_defaults(body,
                                                context.tenant_id,
                                                device_id,
                                                resource))
            context.session.add(device_record)

        self._add_device_kv(context, a10_opts, device_id)

        return self._make_a10_device_dict(device_record)

    def get_a10_device(self, context, a10_device_id, fields=None):
        device = self._get_a10_device(context, a10_device_id)
        return self._make_a10_device_dict(device, fields)

    def get_a10_devices(self, context, filters=None, fields=None,
                        sorts=None, limit=None, marker=None,
                        page_reverse=False):
        LOG.debug("A10DeviceDbMixin:get_a10_devices() tenant_id=%s" %
                  (context.tenant_id))

        # Catch database error when a10_device table doesn't exist yet and return an empty list
        try:
            return self._get_collection(context, models.A10Device,
                                        self._make_a10_device_dict,
                                        filters=filters, fields=fields,
                                        sorts=sorts, limit=limit,
                                        marker_obj=marker,
                                        page_reverse=page_reverse)
        except ProgrammingError as e:
            # NO_SUCH_TABLE = PyMySql 1146
            if '1146' in e.message:
                LOG.debug("A10DeviceDbMixin:get_a10_devices() Handling ",
                          "\"Table Doesn't Exist\" ProgrammingError ",
                          "Exception: %s" % (e.message))
                return ['Table is not there...']
            else:
                raise

    def delete_a10_device(self, context, device_id):
        with context.session.begin(subtransactions=True):
            LOG.debug("A10DeviceDbMixin:delete_a10_device() id=%s" %
                      (id))
            device = self._get_by_id(context, models.A10Device, device_id)
            values = self._get_associated_value_list(context, device.id)
            for value in values:
                self.delete_a10_device_value(context, value['id'])
            context.session.delete(device)

    def update_a10_device(self, context, device_id, a10_device, resource='a10_device'):
        LOG.debug("A10DeviceDbMixin:update_a10_device() id=%s" % (id))
        with context.session.begin(subtransactions=True):
            device = self._get_by_id(context, models.A10Device, device_id)
            LOG.debug("A10DeviceDbMixin:update_a10_device() device=%s" % (device))
            a10_opts = self.validate_a10_opts(
                a10_device.get(resource).pop('a10_opts', []), resource)
            for a10_opt in a10_opts.keys():
                self.update_a10_device_value(
                    context, self._get_a10_device_key_by_name(context, a10_opt).id,
                    device_id, a10_opts[a10_opt])
            device.update(**a10_device.get(resource))
            return self._make_a10_device_dict(device)

    def _get_device_key_body(self, a10_device_key):
        body = a10_device_key[a10_device_resources.DEVICE_KEY]
        return resources.remove_attributes_not_specified(body)

    def _get_a10_device_key_by_name(self, context, key_name):
        try:
            return context.session.query(models.A10DeviceKey).filter_by(name=key_name).one()
        except Exception as e:
            LOG.debug("_get_a10_device_key_by_name key_name=%s, Error: %s" % (key_name, e))
            raise a10Device.A10DeviceNotFoundError(key_name)

    def _get_a10_device_key(self, context, key_id):
        try:
            return self._get_by_id(context, models.A10DeviceKey, key_id)
        except Exception as e:
            LOG.debug("_get_a10_device_key key_id=%s, Error: %s" % (key_id, e))
            raise a10Device.A10DeviceNotFoundError(key_id)

    def _config_keys_exist(self, context, config):
        for key in list(config.keys()):
            value = config[key]
            key_id = self._get_a10_device_key_by_name(context, key).id
            del config[key]
            config[key_id] = value
        return config

    def _make_a10_device_key_dict(self, a10_device_key_db, fields=None):
        res = {'id': a10_device_key_db.id,
               'name': a10_device_key_db.name,
               'description': a10_device_key_db.description}

        return self._fields(res, fields)

    def create_a10_device_key(self, context, a10_device_key):
        body = self._get_device_key_body(a10_device_key)
        with context.session.begin(subtransactions=True):
            device_key_record = models.A10DeviceKey(
                id=_uuid_str(),
                name=body.get('name', ''),
                description=body.get('description', ''))
            context.session.add(device_key_record)

        return self._make_a10_device_key_dict(device_key_record)

    def update_a10_device_key(self, context, id, a10_device_key):
        with context.session.begin(subtransactions=True):
            device_key_record = self._get_by_id(context, models.A10DeviceKey, id)
            device_key_record.update(**a10_device_key.get("a10_device_key"))

            return self._make_a10_device_key_dict(device_key_record)

    def delete_a10_device_key(self, context, id):
        with context.session.begin(subtransactions=True):
            LOG.debug("A10DeviceDbMixin:delete_a10_device_key() id={}".format(id))
            device_key = self._get_a10_device_key(context, id)

            context.session.delete(device_key)

    def get_a10_device_key(self, context, key_id, fields=None):
        device_key = self._get_a10_device_key(context, key_id)
        return self._make_a10_device_key_dict(device_key, fields)

    def get_a10_device_keys(self, context, filters=None, fields=None,
                            sorts=None, limit=None, marker=None,
                            page_reverse=False):
        LOG.debug("A10DeviceDbMixin:get_a10_device_key()")
        return self._get_collection(context, models.A10DeviceKey,
                                    self._make_a10_device_key_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)

    def _get_device_value_body(self, a10_device_value):
        body = a10_device_value[a10_device_resources.DEVICE_VALUE]
        return resources.remove_attributes_not_specified(body)

    def _get_a10_device_value(self, context, value_id):
        try:
            return self._get_by_id(context, models.A10DeviceValue, value_id)
        except Exception as e:
            LOG.error("_get_a10_device_value value_id=%s, Error: %s" % (value_id, e))
            raise a10Device.A10DeviceNotFoundError(value_id)

    def _make_a10_device_value_dict(self, a10_device_value_db, fields=None):
        res = {'id': a10_device_value_db.id,
               'tenant_id': a10_device_value_db.tenant_id,
               'key_id': a10_device_value_db.key_id,
               'associated_obj_id': a10_device_value_db.associated_obj_id,
               'value': a10_device_value_db.value}

        return self._fields(res, fields)

    def _get_associated_value(self, context, key_id, device_id):
        with context.session.begin(subtransactions=True):
            return context.session.query(
                models.A10DeviceValue).filter_by(
                associated_obj_id=device_id, key_id=key_id).one_or_none()

    def _get_associated_value_list(self, context, device_id):
        with context.session.begin(subtransactions=True):
            device_value_object_list = context.session.query(
                models.A10DeviceValue).filter_by(associated_obj_id=device_id).all()
            device_value_list = []
            for value in device_value_object_list:
                device_value_list.append(self._make_a10_device_value_dict(value))
        return device_value_list

    def create_a10_device_value(self, context, a10_device_value):
        body = self._get_device_value_body(a10_device_value)
        with context.session.begin(subtransactions=True):
            device_value_record = models.A10DeviceValue(
                id=_uuid_str(),
                tenant_id=context.tenant_id,
                key_id=body.get('key_id'),
                associated_obj_id=body.get('associated_obj_id'),
                value=body.get('value', ''))
            context.session.add(device_value_record)

        return self._make_a10_device_value_dict(device_value_record)

    def update_a10_device_value(self, context, key_id, device_id, value):
        with context.session.begin(subtransactions=True):
            device_value = self._get_associated_value(context, key_id, device_id)
            device_value.value = value
            device_value.update()

        return self._make_a10_device_value_dict(device_value)

    def delete_a10_device_value(self, context, id):
        with context.session.begin(subtransactions=True):
            LOG.debug("A10DeviceDbMixin:delete_a10_device_value() id={}".format(id))
            device_value = self._get_a10_device_value(context, id)

            context.session.delete(device_value)

    def get_a10_device_value(self, context, value_id, fields=None):
        device_value = self._get_a10_device_value(context, value_id)
        return self._make_a10_device_value_dict(device_value, fields)

    def get_a10_device_values(self, context, filters=None, fields=None,
                              sorts=None, limit=None, marker=None,
                              page_reverse=False):
        LOG.debug("A10DeviceDbMixin:get_a10_device_value()")
        return self._get_collection(context, models.A10DeviceValue,
                                    self._make_a10_device_value_dict, filters=filters,
                                    fields=fields, sorts=sorts, limit=limit,
                                    marker_obj=marker, page_reverse=page_reverse)
