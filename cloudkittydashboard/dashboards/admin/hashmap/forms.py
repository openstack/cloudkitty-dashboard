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

import logging

from django.utils.translation import ugettext_lazy as _
from horizon import forms

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard.dashboards import common

LOG = logging.getLogger(__name__)


class CreateServiceForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))

    def handle(self, request, data):
        name = data['name']
        LOG.info('Creating service with name %s' % (name))
        return api.cloudkittyclient(request).hashmap.services.create(name=name)


class CreateFieldForm(forms.SelfHandlingForm, common.OrderFieldsMixin):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                 attrs={'readonly': 'readonly'}))
    name = forms.CharField(label=_("Name"))

    def handle(self, request, data):
        name = data['name']
        service_id = data['service_id']
        LOG.info('Creating field with name %s' % (name))
        fields_mgr = api.cloudkittyclient(request).hashmap.fields
        return fields_mgr.create(name=name, service_id=service_id)


class CreateGroupForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))

    def handle(self, request, data):
        name = data['name']
        LOG.info('Creating group with name %s' % (name))
        return api.cloudkittyclient(request).hashmap.groups.create(name=name)


class BaseForm(forms.SelfHandlingForm, common.OrderFieldsMixin):
    type = forms.ChoiceField(label=_("Type"),
                             choices=(("flat", _("Flat")),
                                      ("rate", _("Rate"))))
    cost = forms.DecimalField(label=_("Cost"))
    url = "horizon:admin:hashmap:group_create"
    group_id = forms.DynamicChoiceField(label=_("Group"),
                                        required=False,
                                        add_item_link=url)
    fields_order = ['type', 'cost', 'group_id']

    def __init__(self, request, *args, **kwargs):
        super(BaseForm, self).__init__(request, *args, **kwargs)
        self.order_fields()
        groups = api.cloudkittyclient(request).hashmap.groups.list()
        groups = api.identify(groups)
        choices = [(group.id, group.name) for group in groups]
        choices.insert(0, (None, ' '))
        self.fields['group_id'].choices = choices


class BaseThresholdForm(BaseForm):
    level = forms.DecimalField(label=_("Level"))
    fields_order = ['level', 'type', 'cost', 'group_id']

    def handle(self, request, data):
        thresholds_mgr = api.cloudkittyclient(request).hashmap.thresholds
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = v
        return thresholds_mgr.create(**threshold)


class CreateServiceThresholdForm(BaseThresholdForm):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))
    fields_order = ['service_id', 'level', 'type', 'cost', 'group_id']


class CreateFieldThresholdForm(BaseThresholdForm):
    field_id = forms.CharField(label=_("Field"),
                               widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}))
    fields_order = ['field_id', 'level', 'type', 'cost', 'group_id']


class BaseMappingForm(BaseForm):

    def handle(self, request, data):
        mapping_mgr = api.cloudkittyclient(request).hashmap.mappings
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = v
        return mapping_mgr.create(**mapping)


class CreateFieldMappingForm(BaseMappingForm):
    value = forms.CharField(label=_("Value"))
    field_id = forms.CharField(label=_("Field ID"),
                               widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}),
                               required=False)
    fields_order = ['field_id', 'value', 'type', 'cost', 'group_id']


class CreateServiceMappingForm(BaseMappingForm):
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}),
                                 required=False)
    fields_order = ['service_id', 'type', 'cost', 'group_id']


class BaseEditMappingForm(BaseMappingForm):
    mapping_id = forms.CharField(label=_("Mapping ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        mapping_mgr = api.cloudkittyclient(request).hashmap.mappings
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = v
        mapping['mapping_id'] = self.initial['mapping_id']
        return mapping_mgr.update(**mapping)


class EditServiceMappingForm(BaseEditMappingForm, CreateServiceMappingForm):
    fields_order = ['service_id', 'mapping_id', 'type', 'cost', 'group_id']


class EditFieldMappingForm(BaseEditMappingForm, CreateFieldMappingForm):
    fields_order = [
        'field_id',
        'mapping_id',
        'value',
        'type',
        'cost',
        'group_id']


class BaseEditThresholdForm(BaseThresholdForm):
    threshold_id = forms.CharField(label=_("Threshold ID"),
                                   widget=forms.TextInput(
                                       attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        threshold_mgr = api.cloudkittyclient(request).hashmap.thresholds
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = v
        threshold['threshold_id'] = self.initial['threshold_id']
        return threshold_mgr.update(**threshold)


class EditServiceThresholdForm(BaseEditThresholdForm,
                               CreateServiceThresholdForm):
    fields_order = [
        'service_id',
        'threshold_id',
        'level',
        'type',
        'cost',
        'group_id']


class EditFieldThresholdForm(BaseEditThresholdForm,
                             CreateFieldThresholdForm):
    fields_order = [
        'field_id',
        'threshold_id',
        'level',
        'type',
        'cost',
        'group_id']
