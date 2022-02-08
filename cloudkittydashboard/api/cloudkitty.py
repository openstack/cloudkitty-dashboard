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
from collections import abc

from django.conf import settings
from horizon.utils.memoized import memoized  # noqa
from keystoneauth1.identity.v3 import Token

from cloudkittyclient import client as ck_client
from cloudkittydashboard import utils


@memoized
def cloudkittyclient(request, version='1'):
    """Initialization of Cloudkitty client."""
    cacert = getattr(settings, 'OPENSTACK_SSL_CACERT', None)
    insecure = getattr(settings, 'OPENSTACK_SSL_NO_VERIFY', False)
    auth_url = getattr(settings, 'OPENSTACK_KEYSTONE_URL', None)
    interface = getattr(settings, 'OPENSTACK_ENDPOINT_TYPE', 'publicURL')
    auth = Token(
        auth_url,
        token=request.user.token.id,
        project_id=request.user.project_id,
        domain_id=request.user.domain_id,
    )

    adapter_options = {
        'region_name': request.user.services_region,
        'interface': interface,
    }

    return ck_client.Client(
        version,
        auth=auth,
        cacert=cacert,
        insecure=insecure,
        adapter_options=adapter_options,
    )


def identify(what, name=False, key=None):
    if isinstance(what, abc.Iterable):
        for i in what:
            i['id'] = i.get(key or "%s_id" % i['key'])
            if name and not i.get('name'):
                i['name'] = i.get(key or "%s_id" % i['key'])
        what = [utils.TemplatizableDict(i) for i in what]
    else:
        what['id'] = what.get(key or "%s_id" % what['key'])
        if name and not i.get('name'):
            what['name'] = what.get(key or "%s_id" % what['key'])
        what = utils.TemplatizableDict(what)
    return what
