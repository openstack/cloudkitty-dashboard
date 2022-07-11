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

from django.utils.text import normalize_newlines
from django.utils.translation import gettext_lazy as _
from horizon import exceptions
from horizon import forms
from horizon import messages

from cloudkittydashboard.api import cloudkitty as api

LOG = logging.getLogger(__name__)


class CreateScriptForm(forms.SelfHandlingForm):
    help_text = _('Create a new rating script.')
    name = forms.CharField(label=_("Name"))
    source_choices = [('raw', _('Direct Input')),
                      ('file', _('File'))]
    script_source = forms.ChoiceField(
        label=_('Rating Script Source'),
        choices=source_choices,
        widget=forms.Select(attrs={
            'class': 'switchable',
            'data-slug': 'scriptsource'}))
    script_help = _("A script or set of python commands to modify rating "
                    "calculations.")
    script_upload = forms.FileField(
        label=_('Script File'),
        help_text=script_help,
        widget=forms.FileInput(attrs={
            'class': 'switched',
            'data-required-when-shown': 'true',
            'data-switch-on': 'scriptsource',
            'data-scriptsource-file': _('Script File')}),
        required=False)
    script_data = forms.CharField(
        label=_('Script Data'),
        help_text=script_help,
        widget=forms.widgets.Textarea(attrs={
            'class': 'switched',
            'data-required-when-shown': 'true',
            'data-switch-on': 'scriptsource',
            'data-scriptsource-raw': _('Script Data')}),
        required=False)

    class Meta(object):
        name = _('Create Script')

    def clean(self):
        cleaned = super(CreateScriptForm, self).clean()

        files = self.request.FILES
        script = self.clean_uploaded_files('script', files)

        if script is not None:
            cleaned['script_data'] = script

        return cleaned

    def clean_uploaded_files(self, prefix, files):
        upload_str = prefix + "_upload"

        has_upload = upload_str in files
        if has_upload:
            upload_file = files[upload_str]
            log_script_name = upload_file.name
            LOG.info('got upload %s' % log_script_name)
            script = upload_file.read()
            if script != "":
                try:
                    normalize_newlines(script)
                except Exception as e:
                    msg = _('There was a problem parsing the'
                            ' %(prefix)s: %(error)s')
                    msg = msg % {'prefix': prefix, 'error': e}
                    raise forms.ValidationError(msg)
            return script
        else:
            return None

    def handle(self, request, data):
        name = data['name']
        LOG.info('Creating script with name %s' % (name))
        ck_client = api.cloudkittyclient(request)
        try:
            script = ck_client.rating.pyscripts.create_script(
                name=name,
                data=data['script_data'])
            messages.success(
                request,
                _('Successfully created script'))
            return script
        except Exception:
            exceptions.handle(request,
                              _("Unable to create script."))


class EditScriptForm(CreateScriptForm):
    script_id = forms.CharField(label=_("Script ID"),
                                widget=forms.TextInput(
                                attrs={'readonly': 'readonly'}))
    fields_order = ['script_id', 'name', 'script_source', 'script_upload',
                    'script_data']

    class Meta(object):
        name = _("Update Script")

    def handle(self, request, data):
        script_id = self.initial['script_id']
        LOG.info('Updating script with id %s' % (script_id))
        ck_client = api.cloudkittyclient(request)
        try:
            script = ck_client.rating.pyscripts.update_script(
                script_id=script_id, name=data['name'],
                data=data['script_data'])
            messages.success(
                request,
                _('Successfully updated script'))
            return script
        except Exception:
            exceptions.handle(request,
                              _("Unable to update script."))
