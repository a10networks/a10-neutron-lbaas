
class BaseSchedulingFilter(object):

    def __init__(self, driver, devices):
        self.driver = driver
        self.devices = devices

    # Return a list of acceptable devices.  Preferably just one by the end
    # of the filter chain.  A return of NO devices means that we accept the lbaas
    # object as a logical construct in the neutron db, but we do NOT write
    # anything to any A10 appliance.

    # TODO(dougwig) -- implement above 0 list semantics

    def select_device(self, a10_context, devices, tenant_id, lbaas_obj):
        # pass-through
        return self.devices
