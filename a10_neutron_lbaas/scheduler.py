
class Scheduler(object):

    def __init__(self, driver, devices=None, get_devices_func=None):
        self.driver = driver
        if devices is not None:
            self.devices = devices
        elif get_device_func is not None:
            self.devices = get_devices_func()
        else:
            self.devices = self.driver.config.get_devices()

    def select_device(self, a10_context, tenant_id, lbaas_obj):
        devices = self.devices
        filters = map(lambda x: x(self.driver), config.get('device_scheduling_filters'))
        for x in filters:
            devices = x.select_device(devices, tenant_id, lbaas_obj)
            if len(devices) == 0:
                raise Error()
            elif len(devices) == 1:
                return devices[0]

        # If we get here, all of our filters ran and we have more than one
        # device to choose from. Just grab the first.
        log.WARNING("stuff choosing first your filters are junk")
        return devices[0]
