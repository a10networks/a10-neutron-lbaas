
class BaseSchedulingFilter(object):

    def __init__(self, driver, devices):
        self.driver = driver
        self.devices = devices

    def select_device(self, a10_context, devices, tenant_id, lbaas_obj):
        # pass-through
        return self.devices
