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
#    under the License.

try:
    import neutron.api.v2.attributes as old_attributes
except ImportError:
    old_attributes = None

try:
    import neutron_lib.constants as lib_constants
except ImportError:
    lib_constants = None

try:
    import neutron_lib.api.converters as nlib_converters
except ImportError:
    nlib_converters = None

try:
    import neutron_lib.api.validators as lib_validators
except ImportError:
    lib_validators = None


def _find(*args):
    for f in args:
        try:
            return f()
        except AttributeError:
            pass

convert_to_int = _find(lambda: old_attributes.convert_to_int,
                       lambda: nlib_converters.convert_to_int)

convert_kvp_list_to_dict = _find(lambda: old_attributes.convert_kvp_list_to_dict,
                                 lambda: nlib_converters.convert_kvp_list_to_dict)
convert_to_list = _find(lambda: old_attributes.convert_to_list,
                        lambda: nlib_converters.convert_to_list)
convert_kvp_to_list = _find(lambda: old_attributes.convert_kvp_to_list,
                            lambda: nlib_converters.convert_kvp_to_list)

ATTR_NOT_SPECIFIED = _find(lambda: old_attributes.ATTR_NOT_SPECIFIED,
                           lambda: lib_constants.ATTR_NOT_SPECIFIED)
PLURALS = _find(lambda: old_attributes.PLURALS,
                lambda: {})


def _add_validator_to(validators):
    def add_validator(type_name, validator):
        if type_name not in validators:
            validators[type_name] = validator
    return add_validator


def add_validators(validators):
    """Uniform way to add validators. Call this one!"""
    for type_name, validator in validators.items():
        add_validator(type_name, validator)

validators = _find(lambda: old_attributes.validators,
                   lambda: lib_validators.validators)

# Choose which way to add a validator based on whether validators has moved
add_validator = _find(lambda: _add_validator_to(old_attributes.validators),
                      lambda: lib_validators.add_validator)
