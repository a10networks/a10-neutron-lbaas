import copy

import acos_client

def patient_client(original):
    self = copy.copy(original)

    self.http = patient_http(self.http)

    return self

def patient_http(original):
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
