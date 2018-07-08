from a10_neutron_lbaas.neutron_ext.services.a10_device.plugin import A10DevicePlugin


class A10DeviceInstancePlugin(A10DevicePlugin):
   """For backwards compatibility with the service_plugin name used in the neutron.conf file:
   a10_neutron_lbaas.neutron_ext.services.a10_device_instance.plugin.A10DeviceInstancePlugin
   """
   pass
