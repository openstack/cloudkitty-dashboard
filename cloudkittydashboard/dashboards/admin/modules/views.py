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

from django.urls import reverse
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from horizon import forms
from horizon import tables
from horizon import views

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.admin.modules import forms as module_forms
from cloudkittydashboard.dashboards.admin.modules import tables as admin_tables


class IndexView(tables.DataTableView):
    # A very simple class-based view...
    template_name = 'admin/rating_modules/index.html'
    table_class = admin_tables.ModulesTable

    def get_data(self):
        modules = api.cloudkittyclient(
            self.request).rating.get_module()['modules']
        modules = api.identify(modules, key='module_id', name=True)
        return modules


class ModuleDetailsView(views.APIView):
    template_name = 'admin/rating_modules/details.html'
    page_title = _("Rating Module Details")

    def get_data(self, request, context, *args, **kwargs):
        module_id = kwargs.get("module_id")
        try:
            module = api.cloudkittyclient(self.request).rating.get_module(
                module_id=module_id)
            context['hotconfig'] = module['hot-config']
            context['module'] = module
        except Exception:
            context['hotconfig'] = False
            context['module'] = {}
        return context


class PriorityModuleEditView(forms.ModalFormView):
    form_class = module_forms.EditPriorityForm
    form_id = "edit_priority"
    modal_header = _("Edit Module Priority")
    page_title = _("Edit module priority")
    submit_url = "horizon:admin:rating_modules:edit_priority"
    success_url = "horizon:admin:rating_modules:edit_priority"
    template_name = "admin/rating_modules/priority_edit.html"

    def get_initial(self):
        module = api.cloudkittyclient(self.request).rating.get_module(
            module_id=self.kwargs['module_id'])
        self.initial = module
        return self.initial

    def get_object_id(self, obj):
        return obj.module_id

    def get_context_data(self, **kwargs):
        context = super(
            PriorityModuleEditView, self).get_context_data(**kwargs)
        context['module_id'] = self.kwargs.get('module_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['module_id'], ))
        return context

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:rating_modules:index')
