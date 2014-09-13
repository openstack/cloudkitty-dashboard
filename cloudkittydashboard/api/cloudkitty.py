# -*- coding: utf-8 -*-
# Copyright 2014 Objectif Libre
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
# @author: François Magimel (linkid)

"""
The API for the CloudKitty Horizon plugin.
"""

import logging

from cloudkittyclient import client as cloudkitty_client

from openstack_dashboard.api import base


LOG = logging.getLogger(__name__)


def cloudkittyclient(request):
    """Initialization of CloudKitty client."""
    username = request.user.username
    token = request.user.token.id
    tenant_name = request.user.tenant_id
    endpoint = base.url_for(request, 'billing')
    auth_url = base.url_for(request, 'identity')

    LOG.debug('cloudkittyclient connection created using token "%s" '
              'and endpoint "%s"' % (request.user.token.id, endpoint))

    return cloudkitty_client.Client('1',
                                    username=username,
                                    token=token,
                                    tenant_name=tenant_name,
                                    auth_url=auth_url,
                                    endpoint=endpoint)
