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
from decimal import Decimal
import logging

from django.utils.translation import gettext_lazy as _
from horizon import exceptions as horizon_exceptions
from horizon import forms
from horizon import messages
from keystoneauth1 import exceptions

from cloudkittydashboard.api import cloudkitty as api

from openstack_dashboard import api as api_keystone

LOG = logging.getLogger(__name__)


class CreateServiceForm(forms.SelfHandlingForm):
    services_choices = [("service", _("Service")),
                        ("custom_service", _("Custom service"))]
    service_type = forms.ChoiceField(
        label=_("Service type"),
        choices=services_choices,
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'servicetype'}))
    service = forms.DynamicChoiceField(
        label=_("Service"),
        help_text=_("Services are provided by main collector."),
        widget=forms.Select(attrs={
            'class': 'switched',
            'data-switch-on': 'servicetype',
            'data-required-when-shown': 'true',
            'data-servicetype-service': _('Service')}),
        required=False)
    custom_service = forms.CharField(
        label=_("Custom service"),
        help_text=_("Custom services can be defined for any "
                    "additional collector."),
        widget=forms.widgets.TextInput(attrs={
            'class': 'switched',
            'data-switch-on': 'servicetype',
            'data-required-when-shown': 'true',
            'data-servicetype-custom_service': _('Custom service')}),
        required=False)

    def clean_custom_service(self):
        custom_service = self.cleaned_data.get('custom_service').strip()
        service_type = self.cleaned_data.get('service_type')
        if service_type == "custom_service" and not custom_service:
            msg = _('Custom service cannot be empty.')
            self._errors['custom_service'] = self.error_class([msg])
        return custom_service

    def handle(self, request, data):
        if data['service_type'] == 'service':
            service = data['service']
        else:
            service = data['custom_service']
        services_mgr = api.cloudkittyclient(request).rating.hashmap
        LOG.info('Creating service with name %s' % (service))
        try:
            service = services_mgr.create_service(name=service)
            messages.success(
                request,
                _('Service was successfully created'))
            return service
        except Exception:
            horizon_exceptions.handle(request,
                                      _("Unable to create new service."))

    def __init__(self, request, *args, **kwargs):
        super(CreateServiceForm, self).__init__(request, *args, **kwargs)
        metrics = api.cloudkittyclient(request).info.get_metric()['metrics']
        metrics = api.identify(metrics, key='metric_id', name=True)
        choices = sorted([(s.metric_id, s.metric_id) for s in metrics])
        self.fields['service'].choices = choices


class CreateFieldForm(forms.SelfHandlingForm):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    service_name = forms.CharField(label=_("Service Name"),
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        service_id = data['service_id']
        field = data['field']
        LOG.info('Creating field with name %s' % (field))
        fields_mgr = api.cloudkittyclient(request).rating.hashmap
        try:
            field = fields_mgr.create_field(name=field, service_id=service_id)
            messages.success(
                request,
                _('Field was successfully created'))
            return field
        except Exception:
            horizon_exceptions.handle(
                request,
                _("Unable to create field."))

    def __init__(self, request, *args, **kwargs):
        super(CreateFieldForm, self).__init__(request, *args, **kwargs)
        service_id = kwargs['initial']['service_id']
        manager = api.cloudkittyclient(request).rating.hashmap
        service = manager.get_service(service_id=service_id)
        self.fields['service_name'].initial = service['name']

        try:
            fields = manager.get_field(service_id=service['name'])['fields']
        except exceptions.NotFound:
            fields = None
        if fields:
            fields = api.identify(fields)
            choices = sorted([(field, field) for field in fields['metadata']])
            self.fields['field'] = forms.DynamicChoiceField(
                label=_("Field"))
            self.fields['field'].choices = choices
        else:
            self.fields['field'] = forms.CharField(
                label=_("Field"))


class CreateGroupForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))

    def handle(self, request, data):
        name = data['name']
        LOG.info('Creating group with name %s' % (name))
        try:
            group = api.cloudkittyclient(request).rating.hashmap.create_group(
                name=name)
            messages.success(
                request,
                _('Group was successfully created'))
            return group
        except Exception:
            horizon_exceptions.handle(
                request,
                _("Unable to create group."))


class BaseForm(forms.SelfHandlingForm):
    type = forms.ChoiceField(label=_("Type"),
                             choices=(("flat", _("Flat")),
                                      ("rate", _("Rate"))))
    cost = forms.DecimalField(label=_("Cost"))
    url = "horizon:admin:hashmap:group_create"
    group_id = forms.DynamicChoiceField(label=_("Group"),
                                        required=False,
                                        add_item_link=url)
    tenant_id = forms.ChoiceField(label=_("Project"),
                                  required=False)
    fields_order = ['type', 'cost', 'group_id']

    def __init__(self, request, *args, **kwargs):
        super(BaseForm, self).__init__(request, *args, **kwargs)
        # self.order_fields(self.fields_order)
        groups = api.cloudkittyclient(
            request).rating.hashmap.get_group()['groups']
        groups = api.identify(groups, key='group_id', name=True)
        choices = [(group['id'], group['name']) for group in groups]
        choices.insert(0, ('', ' '))
        self.fields['group_id'].choices = choices

        tenants, __ = api_keystone.keystone.tenant_list(request)
        choices_tenants = [(tenant.id, tenant.name) for tenant in tenants]
        choices_tenants.insert(0, (None, ' '))
        self.fields['tenant_id'].choices = choices_tenants


class BaseThresholdForm(BaseForm):
    level = forms.DecimalField(label=_("Level"))
    fields_order = ['level', 'type', 'cost', 'group_id', 'tenant_id']

    def handle(self, request, data):
        thresholds_mgr = api.cloudkittyclient(request).rating.hashmap
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = float(v) if isinstance(v, Decimal) else v
        return thresholds_mgr.create_threshold(**threshold)


class CreateServiceThresholdForm(BaseThresholdForm):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    fields_order = ['service_id', 'level', 'type', 'cost', 'group_id',
                    'tenant_id']


class CreateFieldThresholdForm(BaseThresholdForm):
    field_id = forms.CharField(label=_("Field"),
                               widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}))
    fields_order = ['field_id', 'level', 'type', 'cost', 'group_id',
                    'tenant_id']


class BaseMappingForm(BaseForm):

    def handle(self, request, data):
        mapping_mgr = api.cloudkittyclient(request).rating.hashmap
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = float(v) if isinstance(v, Decimal) else v
        return mapping_mgr.create_mapping(**mapping)


class CreateFieldMappingForm(BaseMappingForm):
    value = forms.CharField(label=_("Value"))
    field_id = forms.CharField(label=_("Field ID"),
                               widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}),
                               required=False)
    fields_order = ['field_id', 'value', 'type', 'cost', 'group_id',
                    'tenant_id']


class CreateServiceMappingForm(BaseMappingForm):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}),
                                 required=False)
    fields_order = ['service_id', 'type', 'cost', 'group_id',
                    'tenant_id']


class BaseEditMappingForm(BaseMappingForm):
    mapping_id = forms.CharField(label=_("Mapping ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    tenant_id = forms.ChoiceField(label=_("Project"),
                                  required=False)

    def handle(self, request, data):
        mapping_mgr = api.cloudkittyclient(request).rating.hashmap
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = float(v) if isinstance(v, Decimal) else v
        mapping['mapping_id'] = self.initial['mapping_id']
        return mapping_mgr.update_mapping(**mapping)


class EditServiceMappingForm(BaseEditMappingForm, CreateServiceMappingForm):
    fields_order = ['service_id', 'mapping_id', 'type', 'cost', 'group_id',
                    'tenant_id']


class EditFieldMappingForm(BaseEditMappingForm, CreateFieldMappingForm):
    fields_order = [
        'field_id',
        'mapping_id',
        'value',
        'type',
        'cost',
        'group_id',
        'tenant_id']


class BaseEditThresholdForm(BaseThresholdForm):
    threshold_id = forms.CharField(label=_("Threshold ID"),
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        threshold_mgr = api.cloudkittyclient(request).rating.hashmap
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = float(v) if isinstance(v, Decimal) else v
        threshold['threshold_id'] = self.initial['threshold_id']
        return threshold_mgr.update_threshold(**threshold)


class EditServiceThresholdForm(BaseEditThresholdForm,
                               CreateServiceThresholdForm):
    fields_order = [
        'service_id',
        'threshold_id',
        'level',
        'type',
        'cost',
        'group_id',
        'tenant_id']


class EditFieldThresholdForm(BaseEditThresholdForm,
                             CreateFieldThresholdForm):
    fields_order = [
        'field_id',
        'threshold_id',
        'level',
        'type',
        'cost',
        'group_id',
        'tenant_id']
