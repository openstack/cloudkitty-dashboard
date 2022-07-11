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

from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from horizon import tables


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
    res_type = tables.Column('res_type', verbose_name=_("Res Type"))
    rate = tables.Column('rate', verbose_name=_("Rate"))

    class Meta(object):
        name = "tenant_summary"
        verbose_name = _("Tenant Summary")
