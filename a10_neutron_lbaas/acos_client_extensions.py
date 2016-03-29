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

import copy
import errno
import socket
import time

import requests.exceptions

from a10_neutron_lbaas import appliance_client_base
from a10_neutron_lbaas.logging_client import is_builtin
import acos_client.errors as acos_errors


def patient_client(original):
    return PatientProxy(original)


class PatientProxy(appliance_client_base.StupidSimpleProxy):
    def __init__(self, underlying, device_client=None):
        super(PatientProxy, self).__init__(underlying)
        self._device_client = device_client or underlying

    def __getattr__(self, attr):
        underlying = getattr(self._underlying, attr)

        if is_builtin(underlying):
            return underlying

        return PatientProxy(underlying, device_client=self._device_client)

    def __call__(self, *args, **kwargs):
        sleep_time = 1
        lock_time = 600
        skip_errs = [errno.EHOSTUNREACH, errno.ECONNREFUSED]
        skip_err_codes = [errno.errorcode[e] for e in skip_errs] + ['BadStatusLine']
        time_end = time.time() + lock_time

        before_call = lambda: None

        while time.time() < time_end:
            try:
                before_call()
                return self._underlying(*args, **kwargs)
            except (socket.error, requests.exceptions.ConnectionError) as e:
                if e.errno not in skip_errs and all(ec not in str(e) for ec in skip_err_codes):
                    raise
                    break
                before_call = lambda: None
            except acos_errors.InvalidSessionID as e:
                # Clear the invalid session id so the underlying client will reauthenticate
                self._device_client.session.session_id = None
                desired_partition = self._device_client.current_partition
                self._device_client.current_partition = 'shared'
                before_call = lambda: self._device_client.system.partition.active(desired_partition)

            time.sleep(sleep_time)

        before_call()
        return self._underlying(*args, **kwargs)
