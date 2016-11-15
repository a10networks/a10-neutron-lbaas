
try: 
    import neutron.common.constants as old_constants
except ImportError:
    old_constants = None

try: 
    import neutron.api.attributes as old_attributes
except ImportError:
    old_attributes = None

try:
    import neutron_lib.constants as lib_constants
except ImportError:
    lib_constants = None

try:
    import neutron_lib.api.converters as lib_converters
except ImportError:
    lib_converters = None

def _find(*args):
    for f in args:
        try:
            return f()
        except AttributeError:
            pass

convert_to_int = _find(lambda: old_attributes.convert_to_int,
                       lambda: lib_converters.convert_to_int)
ATTR_NOT_SPECIFIED = _find(lambda: old_constants.ATTR_NOT_SPECIFIED,
                           lambda: lib_constants.ATTR_NOT_SPECIFIED)
