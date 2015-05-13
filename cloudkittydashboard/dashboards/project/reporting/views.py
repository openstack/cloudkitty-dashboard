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

import calendar
import collections
import datetime
import decimal
import time

from horizon import tabs

from cloudkittydashboard.api import cloudkitty as api


def _do_this_month(data):
    services = {}

    # these variables will keep track of the time span to fill the dicts with
    # empty values after the parsing. This is needed by rickshaw to display
    # stacked graphs
    start_timestamp = None
    end_timestamp = None
    for dataframe in data:
        begin = dataframe.begin
        timestamp = int(time.mktime(
            datetime.datetime.strptime(begin[:16],
                                       "%Y-%m-%dT%H:%M").timetuple()))
        if start_timestamp is None or timestamp < start_timestamp:
            start_timestamp = timestamp
        if end_timestamp is None or timestamp > end_timestamp:
            end_timestamp = timestamp

        for resource in dataframe.resources:
            service_id = resource['service']
            service_data = services.setdefault(
                service_id, {'cumulated': 0, 'hourly': {}})
            service_data['cumulated'] += decimal.Decimal(resource['rating'])
            hourly_data = service_data['hourly']
            hourly_data.setdefault(timestamp, 0)
            hourly_data[timestamp] += float(resource['rating'])

    service_names = services.keys()
    t = start_timestamp
    if end_timestamp:
        while t <= end_timestamp:
            for service in service_names:
                hourly_d = services[service]['hourly']
                hourly_d.setdefault(t, 0)
            t += 3600

    # now sort the dicts
    for service in service_names:
        d = services[service]['hourly']
        services[service]['hourly'] = collections.OrderedDict(
            sorted(d.items(), key=lambda t: t[0]))

    return services


class CostRepartitionTab(tabs.Tab):
    name = "This month"
    slug = "this_month"
    template_name = 'project/reporting/this_month.html'

    def get_context_data(self, request, **kwargs):
        today = datetime.datetime.today()
        day_start, day_end = calendar.monthrange(today.year, today.month)
        begin = "%4d-%02d-01T00:00:00" % (today.year, today.month)
        end = "%4d-%02d-%02dT23:59:59" % (today.year, today.month, day_end)
        client = api.cloudkittyclient(request)
        data = client.storage.dataframes.list(
            begin=begin, end=end, tenant_id=request.user.tenant_id)
        parsed_data = _do_this_month(data)
        return {'repartition_data': parsed_data}


class ReportingTabs(tabs.TabGroup):
    slug = "reporting_tabs"
    tabs = (CostRepartitionTab, )
    sticky = True


class IndexView(tabs.TabbedTableView):
    tab_group_class = ReportingTabs
    template_name = 'project/reporting/index.html'
