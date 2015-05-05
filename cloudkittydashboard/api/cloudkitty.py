# -*- coding: utf-8 -*-
# Copyright 2015 Objectif Libre
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
import collections

from django.conf import settings
from horizon.utils.memoized import memoized  # noqa

from cloudkittyclient import client as ck_client
from openstack_dashboard.api import base


@memoized
def cloudkittyclient(request):
    """Initialization of Cloudkitty client."""

    endpoint = base.url_for(request, 'rating')
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    return ck_client.Client('1', endpoint,
                            token=(lambda: request.user.token.id),
                            insecure=insecure,
                            cacert=cacert)


def identify(what, name=False, key=None):
    if isinstance(what, collections.Iterable):
        for i in what:
            i.id = getattr(i, key or "%s_id" % i.key)
            if name:
                i.name = getattr(i, key or "%s_id" % i.key)
    else:
        what.id = getattr(what, key or "%s_id" % what.key)
        if name:
            what.name = getattr(what, key or "%s_id" % what.key)
    return what
