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
from calendar import monthrange
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import json

from django.conf import settings
from django import http
from django.utils.translation import gettext_lazy as _
from django.views import generic
from horizon import exceptions

from cloudkittydashboard.api import cloudkitty as api
from cloudkittydashboard import utils

rate_prefix = getattr(settings,
                      'OPENSTACK_CLOUDKITTY_RATE_PREFIX', None)
rate_postfix = getattr(settings,
                       'OPENSTACK_CLOUDKITTY_RATE_POSTFIX', None)


class IndexView(generic.TemplateView):
    template_name = 'project/rating/index.html'

    def _get_month_dates(self, year, month):
        """Get start and end dates for a given month."""
        start = datetime(year, month, 1)
        _, last_day = monthrange(year, month)
        end = datetime(year, month, last_day, 23, 59, 59)
        return start, end

    def _get_summary_for_period(self, client, tenant_id, begin, end,
                                groupby=None):
        """Fetch summary data for a specific period."""
        try:
            kwargs = {
                'tenant_id': tenant_id,
                'begin': begin.isoformat(),
                'end': end.isoformat(),
                'response_format': 'object'
            }
            if groupby:
                kwargs['groupby'] = groupby
            return client.summary.get_summary(**kwargs)
        except Exception:
            return {'results': [], 'total': 0}

    def _calculate_forecast(self, current_total, days_elapsed, days_in_month):
        """Calculate forecasted month-end total based on current spending."""
        if days_elapsed <= 0:
            return current_total
        daily_rate = current_total / days_elapsed
        return daily_rate * days_in_month

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client = api.cloudkittyclient(self.request, version='2')
        tenant_id = self.request.user.tenant_id

        now = datetime.now(timezone.utc)
        _, days_in_month = monthrange(now.year, now.month)
        days_elapsed = now.day

        # Current month dates
        current_month_start, current_month_end = self._get_month_dates(
            now.year, now.month)

        # Last month dates
        last_month = now.replace(day=1) - timedelta(days=1)
        last_month_start, last_month_end = self._get_month_dates(
            last_month.year, last_month.month)

        # Fetch current month summary by type
        current_month_by_type = self._get_summary_for_period(
            client, tenant_id, current_month_start, now, groupby=['type'])
        current_month_data = current_month_by_type.get('results', [])
        current_month_total = sum(
            r.get('rate', 0) for r in current_month_data)

        # Fetch last month summary
        last_month_summary = self._get_summary_for_period(
            client, tenant_id, last_month_start, last_month_end)
        last_month_total = sum(
            r.get('rate', 0) for r in last_month_summary.get('results', []))

        # Calculate forecast
        forecast_total = self._calculate_forecast(
            current_month_total, days_elapsed, days_in_month)

        # Fetch top cost generators (group by resource_id)
        top_resources = self._get_summary_for_period(
            client, tenant_id, current_month_start, now,
            groupby=['type', 'resource_id'])
        top_resources_data = sorted(
            top_resources.get('results', []),
            key=lambda x: x.get('rate', 0),
            reverse=True
        )[:10]

        # Format rates for display
        for item in current_month_data:
            item['rate_display'] = utils.formatRate(
                item['rate'], rate_prefix, rate_postfix)

        for item in top_resources_data:
            item['rate_display'] = utils.formatRate(
                item.get('rate', 0), rate_prefix, rate_postfix)

        # Prepare breakdown data for chart (percentages)
        breakdown_data = []
        for item in current_month_data:
            percentage = (item['rate'] / current_month_total * 100
                          if current_month_total > 0 else 0)
            percentage_rounded = round(percentage, 1)
            breakdown_data.append({
                'type': item.get('type', 'Unknown'),
                'rate': item.get('rate', 0),
                'rate_display': item['rate_display'],
                'percentage': percentage_rounded,
                'percentage_css': str(percentage_rounded).replace(',', '.')
            })

        context.update({
            'current_month_total': utils.formatRate(
                current_month_total, rate_prefix, rate_postfix),
            'current_month_total_raw': current_month_total,
            'last_month_total': utils.formatRate(
                last_month_total, rate_prefix, rate_postfix),
            'last_month_total_raw': last_month_total,
            'forecast_total': utils.formatRate(
                forecast_total, rate_prefix, rate_postfix),
            'forecast_total_raw': forecast_total,
            'breakdown_data': breakdown_data,
            'breakdown_data_json': json.dumps(breakdown_data),
            'top_resources': top_resources_data,
            'current_month_name': now.strftime('%B %Y'),
            'last_month_name': last_month.strftime('%B %Y'),
            'days_elapsed': days_elapsed,
            'days_in_month': days_in_month,
        })

        return context


def quote(request):
    pricing = 0.0
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.method == 'POST':
            json_data = json.loads(request.body)

            def __update_quotation_data(element, service):
                if isinstance(element, dict):
                    element['service'] = service
                else:
                    for elem in element:
                        __update_quotation_data(elem, service)

            try:
                service = getattr(
                    settings, 'CLOUDKITTY_QUOTATION_SERVICE', 'instance')
                __update_quotation_data(json_data, service)
                pricing = float(api.cloudkittyclient(request)
                                .rating.get_quotation(res_data=json_data))
            except Exception:
                exceptions.handle(request,
                                  _('Unable to retrieve price.'))

    return http.HttpResponse(json.dumps(pricing),
                             content_type='application/json')
