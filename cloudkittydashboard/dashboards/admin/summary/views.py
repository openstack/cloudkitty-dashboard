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

from django.utils.translation import gettext_lazy as _
from horizon import tables

from openstack_dashboard.api import keystone as api_keystone

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.admin.summary import tables as sum_tables


class IndexView(tables.DataTableView):
    template_name = 'admin/rating_summary/index.html'
    table_class = sum_tables.SummaryTable

    def get_data(self):
        summary = api.cloudkittyclient(self.request).report.get_summary(
            groupby=['tenant_id'], all_tenants=True)['summary']

        tenants, _ = api_keystone.tenant_list(self.request)
        tenants = {tenant.id: tenant.name for tenant in tenants}
        summary.append({
            'tenant_id': 'ALL',
            'rate': sum([float(item['rate']) for item in summary]),
        })
        summary = api.identify(summary, key='tenant_id')
        for tenant in summary:
            tenant['name'] = tenants.get(tenant.id, '-')
        summary[-1]['name'] = 'Cloud Total'
        return summary


class TenantDetailsView(tables.DataTableView):
    template_name = 'admin/rating_summary/details.html'
    table_class = sum_tables.TenantSummaryTable
    page_title = _("Script Details : {{ table.project_id }}")

    def _get_cloud_total_summary(self):
        return api.cloudkittyclient(self.request).report.get_summary(
            groupby=['res_type'], all_tenants=True)['summary']

    def get_data(self):
        tenant_id = self.kwargs['project_id']
        if tenant_id == 'ALL':
            summary = self._get_cloud_total_summary()
        else:
            summary = api.cloudkittyclient(self.request).report.get_summary(
                groupby=['res_type'], tenant_id=tenant_id)['summary']

        summary.append({
            'tenant_id': tenant_id,
            'res_type': 'TOTAL',
            'rate': sum([float(item['rate']) for item in summary]),
        })
        summary = api.identify(summary, key='res_type', name=True)
        return summary
