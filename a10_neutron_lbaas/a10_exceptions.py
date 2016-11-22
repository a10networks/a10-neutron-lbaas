# Copyright 2013,  Mike Thompson,  A10 Networks.
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


class InternalError(Exception):
    pass


class InvalidConfig(Exception):
    pass


class InvalidDeviceConfig(Exception):
    pass


class UnsupportedFeature(Exception):
    pass


class DeviceConfigMissing(Exception):
    pass


class InstanceMissing(Exception):
    pass


class NoDatabaseURL(Exception):
    pass


class RequiresDatabase(Exception):
    pass


class ImageNotFoundError(Exception):
    pass


class FlavorNotFoundError(Exception):
    pass


class NetworksNotFoundError(Exception):
    pass


class IdentifierUnspecifiedError(Exception):
    pass


class ServiceUnavailableError(Exception):
    pass


class FeatureNotConfiguredError(Exception):
    pass


class NoDevicesAvailableError(Exception):
    pass


class NotImplemented(Exception):
    pass
