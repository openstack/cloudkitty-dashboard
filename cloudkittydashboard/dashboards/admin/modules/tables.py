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
from django.utils.translation import ugettext_lazy as _
from horizon import tables

from cloudkittydashboard.api import cloudkitty as api

ENABLE = 0
DISABLE = 1


class ToggleEnabledModule(tables.BatchAction):
    name = "toggle_module"
    action_present = (_("Enable"), _("Disable"))
    action_past = (_("Enabled"), _("Disabled"))
    data_type_singular = _("Module")
    data_type_plural = _("Modules")
    classes = ("btn-toggle",)

    def allowed(self, request, module=None):
        self.enabled = module.enabled
        if self.enabled:
            self.current_present_action = DISABLE
        else:
            self.current_present_action = ENABLE
        return True

    def action(self, request, obj_id):
        module = api.cloudkittyclient(request).modules.get(module_id=obj_id)
        self.enabled = module.enabled
        if self.enabled:
            self.current_past_action = DISABLE
            module.disable()
        else:
            module.enable()
            self.current_past_action = ENABLE


def get_details_link(datum):
    if datum.module_id:
        url = "horizon:admin:rating_modules:module_details"
        return reverse(url, kwargs={'module_id': datum.module_id})


class ModulesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_("Name"), link=get_details_link)
    description = tables.Column('description', verbose_name=_("Description"))
    hot_config = tables.Column('hot-config', verbose_name=_("Configurable"))
    enabled = tables.Column('enabled', verbose_name=_("Enabled"))

    class Meta(object):
        name = "modules"
        verbose_name = _("Modules")
        row_actions = (ToggleEnabledModule,)
