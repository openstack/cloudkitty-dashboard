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

from django.utils.translation import ugettext_lazy as _
from horizon import tables
from horizon import views

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.admin.modules import tables as admin_tables


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'admin/rating_modules/index.html'
    table_class = admin_tables.ModulesTable

    def get_data(self):
        # Add data to the context here...
        modules = api.identify(
            api.cloudkittyclient(self.request).modules.list(),
            name=True
        )
        return modules


class ModuleDetailsView(views.APIView):
    template_name = 'admin/rating_modules/details.html'
    page_title = _("Rating Module Details")

    def get_data(self, request, context, *args, **kwargs):
        module_id = kwargs.get("module_id")
        try:
            module = api.cloudkittyclient(self.request).modules.get(
                module_id=module_id)
        except Exception:
            module = None
        context['hotconfig'] = module._info['hot-config']
        context['module'] = module
        return context
