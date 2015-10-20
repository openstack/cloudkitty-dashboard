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

from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
from horizon import forms
from horizon import tables
from horizon import views

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.admin.pyscripts import forms \
    as pyscripts_forms
from cloudkittydashboard.dashboards.admin.pyscripts import tables \
    as pyscripts_tables


class IndexView(tables.DataTableView):
    table_class = pyscripts_tables.PyScriptsTable
    template_name = 'admin/pyscripts/pyscripts_list.html'

    def get_data(self):
        data = api.cloudkittyclient(self.request).pyscripts.scripts.list()
        data = api.identify(data, name=False)
        return data


class ScriptCreateView(forms.ModalFormView):
    form_class = pyscripts_forms.CreateScriptForm
    form_id = "create_script"
    modal_header = _("Create Script")
    page_title = _("Create Script")
    submit_url = reverse_lazy('horizon:admin:pyscripts:script_create')
    success_url = reverse_lazy('horizon:admin:pyscripts:index')
    template_name = 'admin/pyscripts/form.html'

    def get_object_id(self, obj):
        return obj


class ScriptUpdateView(forms.ModalFormView):
    form_class = pyscripts_forms.EditScriptForm
    form_id = "update_script"
    modal_header = _("Update Script")
    page_title = _("Update Script")
    submit_url = 'horizon:admin:pyscripts:script_update'
    success_url = 'horizon:admin:pyscripts:script_update'
    template_name = 'admin/pyscripts/form.html'

    def get_initial(self):
        script = api.cloudkittyclient(self.request).pyscripts.scripts.get(
            script_id=self.kwargs['script_id'])
        self.initial = script.to_dict()
        self.initial['script_data'] = self.initial['data']
        return self.initial

    def get_context_data(self, **kwargs):
        context = super(ScriptUpdateView, self).get_context_data(**kwargs)
        context['script_id'] = self.kwargs.get('script_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['script_id'], ))
        return context

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:pyscripts:index')


class ScriptDetailsView(views.APIView):
    template_name = 'admin/pyscripts/details.html'
    page_title = _("Script Details : {{ script.name }}")

    def get_data(self, request, context, *args, **kwargs):
        script_id = kwargs.get("script_id")
        try:
            script = api.cloudkittyclient(self.request).pyscripts.scripts.get(
                script_id=script_id)
        except Exception:
            script = None
        context['script'] = script
        return context
