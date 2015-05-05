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

from django.utils.translation import ugettext_lazy as _
import horizon

from cloudkittydashboard.dashboards.admin.hashmap import panel as hashmap_panel
from cloudkittydashboard.dashboards.admin.modules import panel as modules_panel


class CloudkittyPanels(horizon.PanelGroup):
    slug = "cloudkitty"
    name = _("Rating")
    panels = (modules_panel.Modules,
              hashmap_panel.Hashmap)
