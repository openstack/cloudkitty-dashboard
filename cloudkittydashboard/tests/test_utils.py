# Copyright 2019 Objectif Libre
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
import unittest

from cloudkittydashboard import utils


class TemplatizableDictTest(unittest.TestCase):

    def test_hasattr_attr_exists(self):
        obj = utils.TemplatizableDict(a=1, b=2)
        self.assertTrue(hasattr(obj, 'a'))

    def test_hasattr_attr_does_not_exist(self):
        obj = utils.TemplatizableDict(a=1, b=2)
        self.assertFalse(hasattr(obj, 'c'))
