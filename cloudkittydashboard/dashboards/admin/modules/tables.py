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
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from horizon import tables

from cloudkittydashboard.api import cloudkitty as api

ENABLE = 0
DISABLE = 1


class EditModulePriority(tables.LinkAction):
    name = "editmodulepriority"
    verbose_name = _("Edit module priority")
    icon = "edit"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum):
        if datum.module_id:
            url = "horizon:admin:rating_modules:edit_priority"
            return reverse(url, kwargs={'module_id': datum.module_id})


class ToggleEnabledModule(tables.BatchAction):
    name = "toggle_module"
    data_type_singular = _("Module")
    data_type_plural = _("Modules")
    classes = ("btn-toggle",)

    @staticmethod
    def action_present(count):
        return (
            ngettext_lazy(
                u"Enable Module",
                u"Enable Modules",
                count
            ),
            ngettext_lazy(
                u"Disable Module",
                u"Disable Modules",
                count
            ),
        )

    @staticmethod
    def action_past(count):
        return (
            ngettext_lazy(
                u"Enabled Module",
                u"Enabled Modules",
                count
            ),
            ngettext_lazy(
                u"Disabled Module",
                u"Disabled Modules",
                count
            ),
        )

    def allowed(self, request, module=None):
        self.enabled = module.get('enabled')
        if self.enabled:
            self.current_present_action = DISABLE
        else:
            self.current_present_action = ENABLE
        return True

    def action(self, request, obj_id):
        client = api.cloudkittyclient(request)
        module = client.rating.get_module(module_id=obj_id)
        self.enabled = module.get('enabled', False)
        self.current_past_action = DISABLE if self.enabled else ENABLE
        client.rating.update_module(module_id=obj_id,
                                    enabled=(not self.enabled))


def get_details_link(datum):
    if datum.module_id:
        url = "horizon:admin:rating_modules:module_details"
        return reverse(url, kwargs={'module_id': datum.module_id})


class ModulesTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_("Name"), link=get_details_link)
    description = tables.Column('description', verbose_name=_("Description"))
    hot_config = tables.Column('hot-config', verbose_name=_("Configurable"))
    priority = tables.Column('priority', verbose_name=_("Priority"))
    enabled = tables.Column('enabled', verbose_name=_("Enabled"))

    class Meta(object):
        name = "modules"
        verbose_name = _("Modules")
        row_actions = (ToggleEnabledModule, EditModulePriority)
