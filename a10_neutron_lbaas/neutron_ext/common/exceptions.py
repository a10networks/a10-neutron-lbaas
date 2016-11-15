
try:
    import neutron_lib.exceptions as lib_exceptions
except ImportError:
    lib_exceptions = None

try:
    from neutron.common import old_exceptions
except ImportError:
    old_exceptions = None



def _find(*args):
    for f in args:
        try:
            return f()
        except AttributeError:
            pass



NotFound = _find(lambda: old_exceptions.NotFound,
                 lambda: lib_exceptions.NotFound)
InUse = _find(lambda: old_exceptions.InUse,
              lambda: lib_exceptions.InUse)
