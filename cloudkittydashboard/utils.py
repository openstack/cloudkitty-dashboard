# -*- coding: utf-8 -*-
# Copyright 2018 Objectif Libre
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


class TemplatizableDict(dict):
    """Class allowing to pass a dict to horizon templates"""

    def __getattr__(self, key):
        if key in self.keys():
            return self[key]
        raise AttributeError("Object has no {} attribute".format(key))

    def __setattr__(self, key, val):
        self[key] = val


def formatRate(rate: float, prefix: str, postfix: str) -> str:
    rate = str(rate)
    if prefix:
        rate = prefix + rate
    if postfix:
        rate = rate + postfix
    return rate
