
class BaseSchedulingFilter(object):

    def __init__(self, driver):
        self.driver = driver

    def select_device(self, a10_context, devices, tenant_id, lbaas_obj):
        # pass-through
        return self.devices
