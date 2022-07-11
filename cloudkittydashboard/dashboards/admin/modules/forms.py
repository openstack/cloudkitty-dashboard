# Copyright 2017 Objectif Libre
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
from horizon import exceptions
from horizon import forms
from horizon import messages

from cloudkittydashboard.api import cloudkitty as api


class EditPriorityForm(forms.SelfHandlingForm):
    priority = forms.IntegerField(label=_("Priority"))

    def handle(self, request, data):
        ck_client = api.cloudkittyclient(request)
        try:
            priority = ck_client.rating.update_module(
                module_id=self.initial["module_id"], priority=data["priority"])
            messages.success(
                request,
                _('Successfully updated priority'))
            return priority
        except Exception:
            exceptions.handle(request,
                              _("Unable to update priority."))
