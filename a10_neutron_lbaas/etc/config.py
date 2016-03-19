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


verify_appliances = False
use_database = False
database_connection = None

devices = {
    # # A sample ACOS 2.7.2 box, using the shared partition
    # "ax1": {
    #     "host": "10.10.100.20",
    #     "port": 8443,
    #     "username": "admin",
    #     "password": "a10",
    #     "api_version": "2.1",
    #     "v_method": "LSI",
    # },
    # # A sample ACOS 4.0.1 box, using a partition per tenant
    # "ax4": {
    #     "host": "10.10.100.20",
    #     "port": 443,
    #     "username": "admin",
    #     "password": "a10",
    #     "api_version": "3.0",
    #     "v_method": "ADP",
    # },
}
