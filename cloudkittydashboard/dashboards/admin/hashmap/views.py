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
from horizon import tabs
from horizon import views

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards.admin.hashmap import forms as hashmap_forms
from cloudkittydashboard.dashboards.admin.hashmap \
    import tables as hashmap_tables


class IndexView(tables.DataTableView):
    table_class = hashmap_tables.ServicesTable
    template_name = "admin/hashmap/services_list.html"

    def get_data(self):
        out = api.cloudkittyclient(self.request).hashmap.services.list()
        return api.identify(out)


class ServiceView(tabs.TabbedTableView):
    tab_group_class = hashmap_tables.ServiceTabs
    template_name = 'admin/hashmap/service_details.html'

    def get(self, *args, **kwargs):
        service = api.cloudkittyclient(self.request).hashmap.services.get(
            service_id=kwargs['service_id']
        )
        self.request.service_id = service.service_id
        self.page_title = "Hashmap Service : %s" % service.name
        return super(ServiceView, self).get(*args, **kwargs)


class ServiceCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateServiceForm
    form_id = "create_service"
    modal_header = _("Create Service")
    page_title = _("Create Service")
    success_url = reverse_lazy('horizon:admin:hashmap:index')
    submit_url = reverse_lazy('horizon:admin:hashmap:service_create')
    template_name = 'horizon/common/modal_form.html'

    def get_object_id(self, obj):
        return obj.service_id


class FieldView(tabs.TabbedTableView):
    tab_group_class = hashmap_tables.FieldTabs
    template_name = 'admin/hashmap/field_details.html'

    def get(self, *args, **kwargs):
        field = api.cloudkittyclient(self.request).hashmap.fields.get(
            field_id=kwargs['field_id']
        )
        self.request.field_id = field.field_id
        self.page_title = "Hashmap Field : %s" % field.name
        return super(FieldView, self).get(*args, **kwargs)


class FieldCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateFieldForm
    form_id = "create_field"
    modal_header = _("Create Field")
    page_title = _("Create Field")
    template_name = 'horizon/common/modal_form.html'
    success_url = 'horizon:admin:hashmap:service'
    submit_url = 'horizon:admin:hashmap:field_create'

    def get_object_id(self, obj):
        return obj.field_id

    def get_context_data(self, **kwargs):
        context = super(FieldCreateView, self).get_context_data(**kwargs)
        context["service_id"] = self.kwargs['service_id']
        args = (self.kwargs['service_id'],)
        context['submit_url'] = reverse_lazy(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {"service_id": self.kwargs["service_id"]}

    def get_success_url(self, **kwargs):
        args = (self.kwargs['service_id'],)
        return reverse_lazy(self.success_url, args=args)


class ServiceMappingCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateServiceMappingForm
    form_id = "create_mapping"
    modal_header = _("Create Mapping")
    page_title = _("Create Mapping")
    template_name = 'horizon/common/modal_form.html'
    success_url = 'horizon:admin:hashmap:service'
    submit_url = 'horizon:admin:hashmap:service_mapping_create'

    def get_object_id(self, obj):
        return obj.mapping_id

    def get_context_data(self, **kwargs):
        context = super(ServiceMappingCreateView,
                        self).get_context_data(**kwargs)
        context["service_id"] = self.kwargs.get('service_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['service_id'], ))
        return context

    def get_initial(self):
        return {"service_id": self.kwargs.get("service_id")}

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:service',
                       args=(self.kwargs['service_id'],))


class ServiceMappingEditView(ServiceMappingCreateView):
    form_class = hashmap_forms.EditServiceMappingForm
    form_id = "update_mapping"
    modal_header = _("Update Mapping")
    page_title = _("Update Mapping")
    submit_url = 'horizon:admin:hashmap:service_mapping_edit'
    success_url = 'horizon:admin:hashmap:service_mapping_edit'

    def get_initial(self):
        out = api.cloudkittyclient(self.request).hashmap.mappings.get(
            mapping_id=self.kwargs['mapping_id'])
        self.initial = out.to_dict()
        return self.initial

    def get_context_data(self, **kwargs):
        context = super(ServiceMappingEditView,
                        self).get_context_data(**kwargs)
        context["mapping_id"] = self.kwargs.get('mapping_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['mapping_id'], ))
        return context

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:service',
                       args=(self.initial['service_id'], ))


class FieldMappingCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateFieldMappingForm
    form_id = "create_field_mapping"
    modal_header = _("Create Field Mapping")
    page_title = _("Create field Mapping")
    template_name = 'horizon/common/modal_form.html'
    submit_url = 'horizon:admin:hashmap:field_mapping_create'
    success_url = 'horizon:admin:hashmap:field_mapping_create'

    def get_object_id(self, obj):
        return obj.mapping_id

    def get_context_data(self, **kwargs):
        context = super(FieldMappingCreateView,
                        self).get_context_data(**kwargs)
        context["field_id"] = self.kwargs.get('field_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['field_id'], ))
        return context

    def get_initial(self):
        return {"field_id": self.kwargs.get("field_id")}

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:field',
                       args=(self.kwargs['field_id'], ))


class FieldMappingEditView(FieldMappingCreateView):
    form_class = hashmap_forms.EditFieldMappingForm
    form_id = "update_field_mapping"
    modal_header = _("Update Field Mapping")
    page_title = _("Update Field Mapping")
    submit_url = 'horizon:admin:hashmap:field_mapping_edit'

    def get_initial(self):
        out = api.cloudkittyclient(self.request).hashmap.mappings.get(
            mapping_id=self.kwargs['mapping_id'])
        self.initial = out.to_dict()
        return self.initial

    def get_context_data(self, **kwargs):
        context = super(FieldMappingEditView,
                        self).get_context_data(**kwargs)
        context["mapping_id"] = self.kwargs.get('mapping_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['mapping_id'], ))
        return context

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:field',
                       args=(self.initial['field_id'], ))


class GroupCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateGroupForm
    form_id = "create_group"
    modal_header = _("Create Group")
    page_title = _("Create Group")
    template_name = 'horizon/common/modal_form.html'
    submit_url = 'horizon:admin:hashmap:group_create'
    success_url = 'horizon:admin:hashmap:group_create'

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:service',
                       args=(self.kwargs['service_id'],))

    def get_object_id(self, obj):
        return obj.group_id

    def get_context_data(self, **kwargs):
        context = super(GroupCreateView,
                        self).get_context_data(**kwargs)
        context["service_id"] = self.kwargs.get('service_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['service_id'], ))
        return context

    '''
    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:group',
                       args=(kwargs['group_id'], ))
    '''


class ServiceThresholdCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateServiceThresholdForm
    form_id = "create_service_threshold"
    modal_header = _("Create Service Threshold")
    page_title = _("Create Service Threshold")
    template_name = 'horizon/common/modal_form.html'
    success_url = 'horizon:admin:hashmap:service'
    submit_url = 'horizon:admin:hashmap:service_threshold_create'

    def get_object_id(self, obj):
        return obj.field_id

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:service',
                       args=(self.kwargs['service_id'],))

    def get_context_data(self, **kwargs):
        context = super(ServiceThresholdCreateView,
                        self).get_context_data(**kwargs)
        context["service_id"] = self.kwargs.get('service_id')
        args = (context['service_id'],)
        context['submit_url'] = reverse_lazy(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {"service_id": self.kwargs["service_id"]}


class ServiceThresholdEditView(ServiceThresholdCreateView):
    form_class = hashmap_forms.EditServiceThresholdForm
    form_id = "update_service_threshold"
    modal_header = _("Update Service Threshold")
    page_title = _("Update Service Threshold")
    submit_url = 'horizon:admin:hashmap:service_threshold_edit'

    def get_initial(self):
        out = api.cloudkittyclient(self.request).hashmap.thresholds.get(
            threshold_id=self.kwargs['threshold_id'])
        self.initial = out.to_dict()
        return self.initial

    def get_context_data(self, **kwargs):
        context = super(ServiceThresholdEditView,
                        self).get_context_data(**kwargs)
        context["threshold_id"] = self.kwargs.get('threshold_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['threshold_id'], ))
        return context

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:service',
                       args=(self.initial['service_id'], ))


class ServiceThresholdView(tabs.TabbedTableView):
    tab_group_class = hashmap_tables.ServiceThresholdsTab

    def get(self, *args, **kwargs):
        threshold = api.cloudkittyclient(self.request).hashmap.thresholds.get(
            threshold_id=kwargs['threshold_id']
        )
        self.request.threshold_id = threshold.threshold_id
        self.page_title = "Hashmap Threshold : %s" % threshold.threshold_id
        return super(ServiceThresholdView, self).get(*args, **kwargs)

    def get_data(self):
        out = api.cloudkittyclient(self.request).hashmaps.thresholds.list(
            threshold_id=self.kwargs['threshold_id'])
        return api.identify(out)


class FieldThresholdCreateView(forms.ModalFormView):
    form_class = hashmap_forms.CreateFieldThresholdForm
    form_id = "create_field_threshold"
    modal_header = _("Create Field Threshold")
    page_title = _("Create Field Threshold")
    template_name = 'horizon/common/modal_form.html'
    success_url = 'horizon:admin:hashmap:field'
    submit_url = 'horizon:admin:hashmap:field_threshold_create'

    def get_object_id(self, obj):
        return obj.field_id

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:field',
                       args=(self.kwargs['field_id'],))

    def get_context_data(self, **kwargs):
        context = super(FieldThresholdCreateView,
                        self).get_context_data(**kwargs)
        context["field_id"] = self.kwargs.get('field_id')
        args = (context['field_id'],)
        context['submit_url'] = reverse_lazy(self.submit_url, args=args)
        return context

    def get_initial(self):
        return {"field_id": self.kwargs["field_id"]}


class FieldThresholdEditView(FieldThresholdCreateView):
    form_class = hashmap_forms.EditFieldThresholdForm
    form_id = "update_field_threshold"
    modal_header = _("Update Field Threshold")
    page_title = _("Update Field Threshold")
    submit_url = 'horizon:admin:hashmap:field_threshold_edit'

    def get_initial(self):
        out = api.cloudkittyclient(self.request).hashmap.thresholds.get(
            threshold_id=self.kwargs['threshold_id'])
        self.initial = out.to_dict()
        return self.initial

    def get_context_data(self, **kwargs):
        context = super(FieldThresholdEditView,
                        self).get_context_data(**kwargs)
        context["threshold_id"] = self.kwargs.get('threshold_id')
        context['submit_url'] = reverse_lazy(self.submit_url,
                                             args=(context['threshold_id'], ))
        return context

    def get_success_url(self, **kwargs):
        return reverse('horizon:admin:hashmap:field',
                       args=(self.initial['field_id'], ))


class FieldThresholdView(tabs.TabbedTableView):
    tab_group_class = hashmap_tables.FieldThresholdsTab

    def get(self, *args, **kwargs):
        threshold = api.cloudkittyclient(self.request).hashmap.thresholds.get(
            threshold_id=kwargs['threshold_id']
        )
        self.request.threshold_id = threshold.threshold_id
        self.page_title = "Hashmap Threshold : %s" % threshold.threshold_id
        return super(FieldThresholdView, self).get(*args, **kwargs)

    def get_data(self):
        out = api.cloudkittyclient(self.request).hashmaps.thresholds.list(
            threshold_id=self.kwargs['threshold_id'])
        return api.identify(out)


class GroupView(tabs.TabbedTableView):
    tab_group_class = hashmap_tables.GroupsTab
    template_name = 'admin/hashmap/group_details.html'

    def get(self, *args, **kwargs):
        group = api.cloudkittyclient(self.request).hashmap.groups.get(
            group_id=kwargs['group_id']
        )
        self.request.group_id = group.group_id
        self.page_title = "Hashmap Group : %s" % group.name
        return super(GroupView, self).get(*args, **kwargs)

    def get_data(self):
        out = api.cloudkittyclient(self.request).hashmap.groups.list(
        )
        return api.identify(out)


class GroupDetailsView(views.APIView):
    template_name = 'admin/hashmap/group_details.html'
    page_title = _("Group Details")

    def get_data(self, request, context, *args, **kwargs):
        group_id = kwargs.get("group_id")
        ck_client = api.cloudkittyclient(self.request)

        try:
            group = ck_client.hashmap.groups.get(group_id=group_id)
        except Exception:
            group = None

        try:
            mappings = ck_client.hashmap.mappings.findall(group_id=group_id)
        except Exception:
            mappings = []

        try:
            thresholds = ck_client.hashmap.thresholds.findall(
                group_id=group_id)
        except Exception:
            thresholds = []

        values = {
            "mappings": {"fields": [], "services": []},
            "thresholds": {"fields": [], "services": []}
            }
        for key, value in dict(
                mappings=mappings, thresholds=thresholds).items():
            for entry in value:
                if entry.service_id:
                    values[key]['services'].append(entry)
                else:
                    values[key]['fields'].append(entry)
        context.update(values)
        context['group'] = group
        return context
