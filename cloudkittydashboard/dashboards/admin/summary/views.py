# Copyright 2018 Objectif Libre
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

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from horizon import tables

from openstack_dashboard.api import keystone as api_keystone

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.admin.summary import tables as sum_tables
from cloudkittydashboard import utils

rate_prefix = getattr(settings,
                      'OPENSTACK_CLOUDKITTY_RATE_PREFIX', None)
rate_postfix = getattr(settings,
                       'OPENSTACK_CLOUDKITTY_RATE_POSTFIX', None)


class IndexView(tables.DataTableView):
    template_name = 'admin/rating_summary/index.html'
    table_class = sum_tables.SummaryTable

    def get_data(self):
        summary = api.cloudkittyclient(
            self.request, version='2').summary.get_summary(
                groupby=['project_id'],
                response_format='object')

        tenants, unused = api_keystone.tenant_list(self.request)
        tenants = {tenant.id: tenant.name for tenant in tenants}
        data = summary.get('results')

        total = sum([r.get('rate') for r in data])
        data.append({
            'project_id': 'ALL',
            'rate': total,
        })
        data = api.identify(data, key='project_id')
        for tenant in data:
            tenant['tenant_id'] = tenant.get('project_id')
            tenant['name'] = tenants.get(tenant.id, '-')
            tenant['rate'] = utils.formatRate(tenant['rate'],
                                              rate_prefix, rate_postfix)
        data[-1]['name'] = _('Cloud Total')
        return data


class TenantDetailsView(tables.DataTableView):
    template_name = 'admin/rating_summary/details.html'
    table_class = sum_tables.TenantSummaryTable
    page_title = _("Script details: {{ table.project_id }}")

    def get_data(self):
        tenant_id = self.kwargs['project_id']

        if tenant_id == 'ALL':
            summary = api.cloudkittyclient(
                self.request, version='2').summary.get_summary(
                groupby=['type'], response_format='object')
        else:
            summary = api.cloudkittyclient(
                self.request, version='2').summary.get_summary(
                    filters={'project_id': tenant_id},
                    groupby=['type'], response_format='object')

        data = summary.get('results')
        total = sum([r.get('rate') for r in data])
        data.append({'type': 'TOTAL', 'rate': total})

        for item in data:
            item['rate'] = utils.formatRate(item['rate'],
                                            rate_prefix, rate_postfix)

        return data
