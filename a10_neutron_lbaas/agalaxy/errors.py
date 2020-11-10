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


class AGalaxyException(Exception):
    def __init__(self, code=1, msg=''):
        self.code = code
        self.msg = msg
        super(AGalaxyException, self).__init__(msg)

    def __str__(self):
        return "%d %s" % (self.code, self.msg)


class NotFound(AGalaxyException):
    pass