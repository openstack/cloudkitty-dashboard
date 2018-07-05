# Copyright 2015 Objectif Libre
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

import decimal
import json

from django import http
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import views

from cloudkittydashboard.api import cloudkitty as api


class IndexView(views.APIView):
    # A very simple class-based view...
    template_name = 'project/rating/index.html'

    def get_data(self, request, context, *args, **kwargs):
        # Add data to the context here...
        total = api.cloudkittyclient(request).report.get_total(
            tenant_id=request.user.tenant_id) or 0.00
        context['total'] = total
        return context


def quote(request):
    pricing = "0"
    if request.is_ajax():
        if request.method == 'POST':
            json_data = json.loads(request.body)
            try:
                pricing = decimal.Decimal(api.cloudkittyclient(request)
                                          .quotations.quote(json_data))
                pricing = pricing.normalize().to_eng_string()
            except Exception:
                exceptions.handle(request,
                                  _('Unable to retrieve price.'))

    return http.HttpResponse(json.dumps(pricing),
                             content_type='application/json')
