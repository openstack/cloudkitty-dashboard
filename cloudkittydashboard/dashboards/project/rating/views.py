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
import json

from django.conf import settings
from django import http
from django.utils.translation import ugettext_lazy as _
from horizon import exceptions
from horizon import tables

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.project.rating \
    import tables as rating_tables
from cloudkittydashboard.utils import TemplatizableDict


class IndexView(tables.DataTableView):
    table_class = rating_tables.SummaryTable
    template_name = 'project/rating/index.html'

    def get_data(self):
        summary = api.cloudkittyclient(self.request).report.get_summary(
            tenant_id=self.request.user.tenant_id,
            groupby=['tenant_id', 'res_type'])['summary']
        summary = api.identify(summary, key='res_type', name=True)
        summary.append(TemplatizableDict({
            'id': 'ALL',
            'res_type': 'TOTAL',
            'name': 'ALL',
            'rate': sum([float(i['rate']) for i in summary]),
        }))
        return summary


def quote(request):
    pricing = 0.0
    if request.is_ajax():
        if request.method == 'POST':
            json_data = json.loads(request.body)

            def __update_quotation_data(element, service):
                if isinstance(element, dict):
                    element['service'] = service
                else:
                    for elem in element:
                        __update_quotation_data(elem, service)

            try:
                service = getattr(
                    settings, 'CLOUDKITTY_QUOTATION_SERVICE', 'instance')
                __update_quotation_data(json_data, service)
                pricing = float(api.cloudkittyclient(request)
                                .rating.get_quotation(res_data=json_data))
            except Exception:
                exceptions.handle(request,
                                  _('Unable to retrieve price.'))

    return http.HttpResponse(json.dumps(pricing),
                             content_type='application/json')
