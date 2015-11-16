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

import unittest


def assertIn(expected, actual):
    if expected not in actual:
        raise Exception("Expected to find {0} in {1}".format(expected, actual))


def assertIsNot(a, b):
    if a is b:
        raise Exception("Expected {0} to not be {1}".format(a, b))


class TestCase(unittest.TestCase):
    """unittest.TestCase with portable or custom assertions"""

    def __init__(self, *args):
        super(TestCase, self).__init__(*args)

        self._patch("assertIn", assertIn)
        self._patch("assertIsNot", assertIsNot)

    def _patch(self, key, value):
        if not hasattr(self, key):
            setattr(self, key, value)
