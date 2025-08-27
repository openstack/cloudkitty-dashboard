# Copyright 2018 Objectif Libre
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

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from horizon import tables

from cloudkittydashboard.utils import formatTitle


def get_details_link(datum):
    if datum.tenant_id:
        url = "horizon:admin:rating_summary:project_details"
        return reverse(url, kwargs={'project_id': datum.tenant_id})


class SummaryTable(tables.DataTable):
    project_id = tables.Column(
        'tenant_id', verbose_name=_("Project ID"), link=get_details_link)
    project_name = tables.Column(
        'name', verbose_name=_("Project Name"), link=get_details_link)
    total = tables.Column('rate', verbose_name=_("Project Total"))

    class Meta(object):
        name = "summary"
        verbose_name = _("Summary")


class TenantSummaryTable(tables.DataTable):
    groupby_list = getattr(settings,
                           'OPENSTACK_CLOUDKITTY_GROUPBY_LIST',
                           ['type'])

    # Dynamically create columns based on groupby_list
    for field in groupby_list:
        locals()[field] = tables.Column(
            field, verbose_name=_(formatTitle(field)))

    rate = tables.Column('rate', verbose_name=_("Rate"))

    def __init__(self, request, data=None, needs_form_wrapper=None, **kwargs):
        super().__init__(request, data, needs_form_wrapper, **kwargs)

        #  Hide columns based on checkbox selection
        for field in self.groupby_list:
            if request.GET.get(field) != 'true':
                self.columns[field].classes = ['hidden']

    class Meta(object):
        name = "tenant_summary"
        verbose_name = _("Project Summary")

    def get_object_id(self, datum):
        #  Prevents the table from displaying the same ID for different rows
        id_parts = []
        for field in self.groupby_list:
            if field in datum and datum[field]:
                id_parts.append(str(datum[field]))

        if id_parts:
            return '_'.join(id_parts)
        return _('No IDs found')
