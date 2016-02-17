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


def patient_client(original):
    self = copy.copy(original)

    self.http = patient_http(self.http)

    return self


def patient_http(original):
    import pdb; pdb.set_trace()
    self = copy.copy(original)

    underlying_request = self.request

    def request(*args, **kwargs):
        sleep_time = 1
        lock_time = 600
        skip_errs = [errno.EHOSTUNREACH]
        time_end = time.time() + lock_time

        while time.time() < time_end:
            try:
                return underlying_request(*args, **kwargs)
            except socket.error as e:
                last_e = e
                if e.errno not in skip_errs:
                    raise
                    break

            time.sleep(sleep_time)

        return underlying_request(*args, **kwargs)

    self.request = request

    return self
