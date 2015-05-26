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

LOG = logging.getLogger(__name__)


class CreateServiceForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))

    def handle(self, request, data):
        name = data['name']
        LOG.info('Creating service with name %s' % (name))
        return api.cloudkittyclient(request).hashmap.services.create(name=name)


class CreateFieldForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                 attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        name = data['name']
        service_id = data['service_id']
        LOG.info('Creating field with name %s' % (name))
        field_client = api.cloudkittyclient(request).hashmap.fields
        return field_client.create(name=name, service_id=service_id)


class CreateGroupForm(forms.SelfHandlingForm):
    name = forms.CharField(label=_("Name"))

    def handle(self, request, data):
        name = data['name']
        LOG.info('Creating group with name %s' % (name))
        return api.cloudkittyclient(request).hashmap.groups.create(name=name)


class CreateServiceThresholdForm(forms.SelfHandlingForm):
    level = forms.DecimalField(label=_("Level"))
    type = forms.ChoiceField(label=_("Type"),
                             choices=(("flat", _("Flat")),
                                      ("rate", _("Rate"))))
    cost = forms.DecimalField(label=_("Cost"))
    group_id = forms.CharField(label=_("Group"), required=False)
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                     attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        client = api.cloudkittyclient(request).hashmap.thresholds
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = v
        return client.create(**threshold)


class CreateFieldThresholdForm(forms.SelfHandlingForm):
    level = forms.DecimalField(label=_("Level"))
    type = forms.ChoiceField(label=_("Type"),
                             choices=(("flat", _("Flat")),
                                      ("rate", _("Rate"))))
    cost = forms.DecimalField(label=_("Cost"))
    group_id = forms.CharField(label=_("Group"), required=False)
    field_id = forms.CharField(label=_("Field"),
                               widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        client = api.cloudkittyclient(request).hashmap.thresholds
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = v
        return client.create(**threshold)


class CreateFieldMappingForm(forms.SelfHandlingForm):
    value = forms.CharField(label=_("Value"))
    type = forms.ChoiceField(label=_("Type"),
                             choices=(("flat", _("Flat")),
                                      ("rate", _("Rate"))))
    cost = forms.DecimalField(label=_("Cost"))
    group_id = forms.CharField(label=_("Group"), required=False)
    field_id = forms.CharField(label=_("Field ID"),
                               widget=forms.TextInput(
                               attrs={'readonly': 'readonly'}),
                               required=False)

    def handle(self, request, data):
        mapping_client = api.cloudkittyclient(request).hashmap.mappings
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = v
        return mapping_client.create(**mapping)


class CreateServiceMappingForm(forms.SelfHandlingForm):
    type = forms.ChoiceField(label=_("Type"),
                             choices=(("flat", _("Flat")),
                                      ("rate", _("Rate"))))
    cost = forms.DecimalField(label=_("Cost"))
    group_id = forms.CharField(label=_("Group"), required=False)
    service_id = forms.CharField(label=_("Service ID"),
                                 widget=forms.TextInput(
                                 attrs={'readonly': 'readonly'}),
                                 required=False)

    def handle(self, request, data):
        mapping_client = api.cloudkittyclient(request).hashmap.mappings
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = v
        return mapping_client.create(**mapping)


class EditServiceMappingForm(CreateServiceMappingForm):
    mapping_id = forms.CharField(label=_("Mapping ID"),
                                 widget=forms.TextInput(
                                 attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        mapping_client = api.cloudkittyclient(request).hashmap.mappings
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = v
        mapping['mapping_id'] = self.initial['mapping_id']
        return mapping_client.update(**mapping)


class EditFieldMappingForm(CreateFieldMappingForm):
    mapping_id = forms.CharField(label=_("Mapping ID"),
                                 widget=forms.TextInput(
                                 attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        mapping_client = api.cloudkittyclient(request).hashmap.mappings
        mapping = {}
        for k, v in data.items():
            if v:
                mapping[k] = v
        mapping['mapping_id'] = self.initial['mapping_id']
        return mapping_client.update(**mapping)


class EditServiceThresholdForm(CreateServiceThresholdForm):
    threshold_id = forms.CharField(label=_("Threshold ID"),
                                   widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        threshold_client = api.cloudkittyclient(request).hashmap.thresholds
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = v
        threshold['threshold_id'] = self.initial['threshold_id']
        return threshold_client.update(**threshold)


class EditFieldThresholdForm(CreateFieldThresholdForm):
    threshold_id = forms.CharField(label=_("Threshold ID"),
                                   widget=forms.TextInput(
                                   attrs={'readonly': 'readonly'}))

    def handle(self, request, data):
        threshold_client = api.cloudkittyclient(request).hashmap.thresholds
        threshold = {}
        for k, v in data.items():
            if v:
                threshold[k] = v
        threshold['threshold_id'] = self.initial['threshold_id']
        return threshold_client.update(**threshold)
