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

from horizon import messages
from horizon import tabs

from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard import forms


def _do_this_month(data):
    services = {}

    # these variables will keep track of the time span to fill the dicts with
    # empty values after the parsing. This is needed by rickshaw to display
    # stacked graphs
    start_timestamp = None
    end_timestamp = None
    for dataframe in data.get('dataframes', []):
        begin = dataframe['begin']
        timestamp = int(
            time.mktime(
                datetime.datetime.strptime(
                    begin[:16], "%Y-%m-%dT%H:%M").timetuple()
            )
        )
        if start_timestamp is None or timestamp < start_timestamp:
            start_timestamp = timestamp
        if end_timestamp is None or timestamp > end_timestamp:
            end_timestamp = timestamp

        for resource in dataframe['resources']:
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
    name = _("This month")
    slug = "this_month"
    template_name = 'project/reporting/this_month.html'

    def get_context_data(self, request, **kwargs):
        today = datetime.datetime.today()
        day_start, day_end = calendar.monthrange(today.year, today.month)

        form = self.get_form()

        if form.is_valid():
            # set values to be from datepicker form
            start = form.cleaned_data['start']
            end = form.cleaned_data['end']
            begin = "%4d-%02d-%02dT00:00:00" % (start.year,
                                                start.month, start.day)
            end = "%4d-%02d-%02dT23:59:59" % (end.year, end.month, end.day)

            if end < begin:
                messages.error(
                    self.request,
                    _("Invalid time period. The end date should be "
                        "more recent than the start date."
                        " Setting the end as today."))

                end = "%4d-%02d-%02dT23:59:59" % (today.year,
                                                  today.month, day_end)

            elif start > today.date():
                messages.error(
                    self.request,
                    _("Invalid time period. You are requesting "
                      "data from the future which may not exist."))

        elif form.is_bound:
            messages.error(
                self.request, _(
                    "Invalid date format: Using this month as default.")
                )

            begin = "%4d-%02d-%02dT00:00:00" % (today.year,
                                                today.month, day_start)
            end = "%4d-%02d-%02dT23:59:59" % (today.year, today.month, day_end)

        else:  # set default date values (before form is filled in)
            begin = "%4d-%02d-%02dT00:00:00" % (today.year,
                                                today.month, day_start)
            end = "%4d-%02d-%02dT23:59:59" % (today.year, today.month, day_end)

        client = api.cloudkittyclient(request)
        data = client.storage.get_dataframes(
            begin=begin, end=end, tenant_id=request.user.tenant_id)
        parsed_data = _do_this_month(data)
        return {'repartition_data': parsed_data, 'form': form}

    @property
    def today(self):
        return timezone.now()

    @property
    def first_day(self):
        days_range = settings.OVERVIEW_DAYS_RANGE
        if days_range:
            return self.today.date() - datetime.timedelta(days=days_range)
        return datetime.date(self.today.year, self.today.month, 1)

    def init_form(self):
        self.start = self.first_day
        self.end = self.today.date()

        return self.start, self.end

    def get_form(self):
        if not hasattr(self, "form"):
            req = self.request
            start = req.GET.get('start', req.session.get('usage_start'))
            end = req.GET.get('end', req.session.get('usage_end'))
            if start and end:
                # bound form
                self.form = forms.DateForm({'start': start, 'end': end})

            else:
                # non-bound form
                init = self.init_form()
                start = init[0].isoformat()
                end = init[1].isoformat()
                self.form = forms.DateForm(
                    initial={'start': start, 'end': end})
            req.session['usage_start'] = start
            req.session['usage_end'] = end
        return self.form


class ReportingTabs(tabs.TabGroup):
    slug = "reporting_tabs"
    tabs = (CostRepartitionTab,)
    sticky = True


class IndexView(tabs.TabbedTableView):
    tab_group_class = ReportingTabs
    template_name = 'project/reporting/index.html'
