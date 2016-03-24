import six
import six.moves.builtins

from oslo_log.helpers import logging as logging

from a10_neutron_lbaas import appliance_client_base

LOG = logging.getLogger(__name__)


def is_builtin(a):
    if six.callable(a):
        return False
    return type(a).__module__ == six.moves.builtins.__name__


class LoggingProxy(appliance_client_base.StupidSimpleProxy):
    def __init__(self, underlying, path=[]):
        super(LoggingProxy, self).__init__(underlying)
        self._path = path

    def __getattr__(self, attr):
        underlying = getattr(self._underlying, attr)

        if is_builtin(underlying):
            return underlying

        return LoggingProxy(underlying, path=self._path + [(self._underlying, attr)])

    def __call__(self, *args, **kwargs):
        simple_path = '.'.join(map(lambda x: x[1], self._path))

        path = ''.join(map(lambda x: '{0}.{1}'.format(type(x[0]), x[1]), self._path))

        call = '{0}({1}{2})'.format(
            path,
            ', '.join(map(repr, args)),
            ''.join(map(lambda x: ', {0}={1}'.format(x[0], repr(x[1])), kwargs.items())))

        LOG.debug("a10-neutron-lbaas calling %s on %s", simple_path, call)

        return self._underlying(*args, **kwargs)
