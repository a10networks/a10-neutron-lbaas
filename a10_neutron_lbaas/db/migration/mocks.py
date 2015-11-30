# Copyright (C) 2015, A10 Networks Inc. All rights reserved.
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
#


def format_call(name, args, kw):
    all_args = [repr(arg) for arg in args] + ['{0}={1}'.format(k, repr(v)) for k, v in kw.items()]
    return '{0}({1})'.format(name, all_args)


class UncallableMock(object):
    def __init__(self, name=None):
        self.__name = name or object.__repr__(self)
        self.__dict = dict()

    def __call__(self, *args, **kw):
        raise NotImplementedError(format_call(self.__name, args, kw))

    def __getitem__(self, key):
        try:
            return self.__dict[key]
        except KeyError:
            self.__dict[key] = UncallableMock(name='{0}[{1}]'.format(self.__name, repr(key)))
            return self.__dict[key]

    def __str__(self):
        return self.__name

    def __repr__(self):
        return self.__name

    def __getattr__(self, name):
        self.__dict__[name] = UncallableMock(name='{0}.{1}'.format(self.__name, name))
        return self.__dict__[name]
