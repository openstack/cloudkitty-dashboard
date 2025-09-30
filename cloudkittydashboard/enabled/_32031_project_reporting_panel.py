# Copyright 2019 Objectif Libre
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#

PANEL_GROUP = 'rating'
PANEL_DASHBOARD = 'project'
PANEL = 'reporting'

ADD_XSTATIC_MODULES = [
    ('xstatic.pkg.d3', ['d3.js']),
    ('xstatic.pkg.rickshaw', ['rickshaw.js'])
]

ADD_PANEL = \
    'cloudkittydashboard.dashboards.project.reporting.panel.Project_reporting'
