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


def _build_reporting_data(client, tenant_id, begin, end):
    """Build reporting data using v2 summary API.

    Returns a dict of services with cumulated totals (for the pie chart)
    and daily breakdown (for the Rickshaw time-series graph).
    """
    services = {}

    # Get cumulated totals by type (single fast API call)
    try:
        summary = client.summary.get_summary(
            tenant_id=tenant_id,
            begin=begin, end=end,
            groupby=['type'],
            response_format='object'
        )
    except Exception:
        return {}

    for item in summary.get('results', []):
        service_id = item.get('type', 'Unknown')
        services[service_id] = {
            'cumulated': decimal.Decimal(str(item.get('rate', 0))),
            'hourly': collections.OrderedDict()
        }

    # Get daily breakdown for time-series chart
    start_dt = datetime.datetime.strptime(begin[:10], "%Y-%m-%d")
    end_dt = datetime.datetime.strptime(end[:10], "%Y-%m-%d")
    current = start_dt
    while current <= end_dt:
        day_begin = current.strftime("%Y-%m-%dT00:00:00")
        day_end = current.strftime("%Y-%m-%dT23:59:59")
        timestamp = int(time.mktime(current.timetuple()))

        # Initialize all services for this timestamp
        for service_id in services:
            services[service_id]['hourly'][timestamp] = 0

        try:
            day_summary = client.summary.get_summary(
                tenant_id=tenant_id,
                begin=day_begin, end=day_end,
                groupby=['type'],
                response_format='object'
            )
            for item in day_summary.get('results', []):
                service_id = item.get('type', 'Unknown')
                if service_id in services:
                    services[service_id]['hourly'][timestamp] = float(
                        item.get('rate', 0))
        except Exception:
            pass

        current += datetime.timedelta(days=1)

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

            begin = "%4d-%02d-01T00:00:00" % (today.year, today.month)
            end = "%4d-%02d-%02dT23:59:59" % (today.year, today.month,
                                              today.day)

        else:  # set default date values (before form is filled in)
            begin = "%4d-%02d-01T00:00:00" % (today.year, today.month)
            end = "%4d-%02d-%02dT23:59:59" % (today.year, today.month,
                                              today.day)

        client = api.cloudkittyclient(request, version='2')
        parsed_data = _build_reporting_data(
            client, request.user.tenant_id, begin, end)
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
