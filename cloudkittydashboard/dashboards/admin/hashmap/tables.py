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
from horizon import tabs

from cloudkittydashboard.api import cloudkitty as api


class CreateService(tables.LinkAction):
    name = "createservice"
    verbose_name = _("Create new Service")
    url = 'horizon:admin:hashmap:service_create'
    icon = "create"
    ajax = True
    classes = ("ajax-modal",)


class DeleteService(tables.DeleteAction):
    name = "deleteservice"
    verbose_name = _("Delete Service")
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Service")
    data_type_plural = _("Services")
    icon = "remove"

    def action(self, request, service_id):
        api.cloudkittyclient(request).hashmap.services.delete(
            service_id=service_id)


class ServicesTable(tables.DataTable):
    """This table list the available services.

    Clicking on a service name sends you to a ServiceTabs page.
    """
    name = tables.Column('name', verbose_name=_("Name"),
                         link='horizon:admin:hashmap:service')

    class Meta(object):
        name = "services"
        verbose_name = _("Services")
        table_actions = (CreateService, DeleteService)
        row_actions = (DeleteService,)


class CreateGroup(tables.LinkAction):
    name = "creategroup"
    verbose_name = _("Create new Group")
    icon = "create"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:group_create'
        service_id = self.table.request.service_id
        return reverse(url, args=[service_id])


class DeleteGroup(tables.DeleteAction):
    name = "deletegroup"
    verbose_name = _("Delete Group")
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Group")
    data_type_plural = _("Groups")
    icon = "remove"

    def action(self, request, group_id):
        api.cloudkittyclient(request).hashmap.groups.delete(
            group_id=group_id)


def get_detail_link(datum):
    if datum.group_id:
        url = "horizon:admin:hashmap:group_details"
        return reverse(url, kwargs={'group_id': datum.group_id})


class GroupsTable(tables.DataTable):
    """This table list the available groups.

    Clicking on a group name sends you to a GroupsTab page.
    """
    name = tables.Column('name', verbose_name=_("Name"), link=get_detail_link)
    group_id = tables.Column('group_id', verbose_name=_("Group"))

    class Meta(object):
        name = "groups"
        verbose_name = _("Groups")
        table_actions = (CreateGroup, DeleteGroup)
        row_actions = (DeleteGroup,)


class GroupsTab(tabs.TableTab):
    name = _("Groups")
    slug = "hashmap_groups"
    table_classes = (GroupsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_groups_data(self):
        client = api.cloudkittyclient(self.request)
        groups = client.hashmap.groups.list()
        return api.identify(groups)


class CreateServiceThreshold(tables.LinkAction):
    name = "createservicethreshold"
    verbose_name = _("Create new Service Threshold")
    icon = "create"
    ajax = False
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:service_threshold_create'
        service_id = self.table.request.service_id
        return reverse(url, args=[service_id])


class CreateFieldThreshold(tables.LinkAction):
    name = "createfieldthreshold"
    verbose_name = _("Create new Field Threshold")
    icon = "create"
    ajax = False
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:field_threshold_create'
        field_id = self.table.request.field_id
        return reverse(url, args=[field_id])


class DeleteServiceThreshold(tables.DeleteAction):
    name = "deletetservicehreshold"
    verbose_name = _("Delete Service Threshold")
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Service Threshold")
    data_type_plural = _("Service Thresholds")
    icon = "remove"

    def action(self, request, threshold_id):
        api.cloudkittyclient(request).hashmap.thresholds.delete(
            threshold_id=threshold_id)


class DeleteFieldThreshold(tables.DeleteAction):
    name = "deletefieldthreshold"
    verbose_name = _("Delete Field Threshold")
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Field Threshold")
    data_type_plural = _("Field Thresholds")
    icon = "remove"

    def action(self, request, threshold_id):
        api.cloudkittyclient(request).hashmap.thresholds.delete(
            threshold_id=threshold_id)


class EditServiceThreshold(tables.LinkAction):
    name = "editservicethreshold"
    verbose_name = _("Edit Service Threshold")
    icon = "edit"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:service_threshold_edit'
        return reverse(url, args=[datum.threshold_id])


class BaseThresholdsTable(tables.DataTable):
    level = tables.Column('level', verbose_name=_("Level"))
    type = tables.Column('type', verbose_name=_("Type"))
    cost = tables.Column('cost', verbose_name=_("Cost"))
    group_id = tables.Column('group_id', verbose_name=_("Group"))


class ServiceThresholdsTable(BaseThresholdsTable):
    """This table list the available service thresholds.

    Clicking on a group name sends you to a GroupsTab page.
    """

    class Meta(object):
        name = "service_thresholds"
        verbose_name = _("Service Threshold")
        table_actions = (CreateServiceThreshold, DeleteServiceThreshold)
        row_actions = (EditServiceThreshold, DeleteServiceThreshold)


class ServiceThresholdsTab(tabs.TableTab):
    name = _("Service Thresholds")
    slug = "hashmap_service_thresholds"
    table_classes = (ServiceThresholdsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_service_thresholds_data(self):
        client = api.cloudkittyclient(self.request)
        thresholds = client.hashmap.thresholds.list(
            service_id=self.request.service_id)
        return api.identify(thresholds)


class EditFieldThreshold(tables.LinkAction):
    name = "editfieldthreshold"
    verbose_name = _("Edit Field Threshold")
    icon = "edit"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:field_threshold_edit'
        return reverse(url, args=[datum.threshold_id])


class FieldThresholdsTable(BaseThresholdsTable):
    """This table list the available field thresholds.

    Clicking on a group name sends you to a GroupsTab page.
    """

    class Meta(object):
        name = "field_thresholds"
        verbose_name = _("Field Threshold")
        table_actions = (CreateFieldThreshold, DeleteFieldThreshold)
        row_actions = (EditFieldThreshold, DeleteFieldThreshold)


class FieldThresholdsTab(tabs.TableTab):
    name = _("Field Thresholds")
    slug = "hashmap_field_thresholds"
    table_classes = (FieldThresholdsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_field_thresholds_data(self):
        client = api.cloudkittyclient(self.request)
        thresholds = client.hashmap.thresholds.list(
            field_id=self.request.field_id)
        return api.identify(thresholds)


class DeleteField(tables.DeleteAction):
    name = "deletefield"
    verbose_name = _("Delete Field")
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Field")
    data_type_plural = _("Fields")
    icon = "remove"

    def action(self, request, field_id):
        api.cloudkittyclient(request).hashmap.fields.delete(
            field_id=field_id)


class CreateField(tables.LinkAction):
    name = "createfield"
    verbose_name = _("Create new Field")
    icon = "create"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:field_create'
        service_id = self.table.request.service_id
        return reverse(url, args=[service_id])


class FieldsTable(tables.DataTable):
    """This table lists the available fields for a given service.

    Clicking on a fields sends you to a MappingsTable.
    """
    name = tables.Column(
        'name',
        verbose_name=_("Name"),
        link='horizon:admin:hashmap:field')

    class Meta(object):
        name = "fields"
        verbose_name = _("Fields")
        multi_select = False
        row_actions = (DeleteField,)
        table_actions = (CreateField, DeleteField)


class FieldsTab(tabs.TableTab):
    name = _("Fields")
    slug = "hashmap_fields"
    table_classes = (FieldsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_fields_data(self):
        client = api.cloudkittyclient(self.request)
        fields = client.hashmap.fields.list(service_id=self.request.service_id)
        return api.identify(fields)


class DeleteMapping(tables.DeleteAction):
    name = "deletemapping"
    verbose_name = _("Delete Mapping")
    action_present = _("Delete")
    action_past = _("Deleted")
    data_type_singular = _("Mapping")
    data_type_plural = _("Mappings")
    icon = "remove"

    def action(self, request, mapping_id):
        api.cloudkittyclient(request).hashmap.mappings.delete(
            mapping_id=mapping_id)


class CreateServiceMapping(tables.LinkAction):
    name = "createiservicemapping"
    verbose_name = _("Create new Mapping")
    icon = "create"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:service_mapping_create'
        service_id = self.table.request.service_id
        return reverse(url, args=[service_id])


class EditServiceMapping(tables.LinkAction):
    name = "editservicemapping"
    verbose_name = _("Edit Mapping")
    icon = "edit"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:service_mapping_edit'
        return reverse(url, args=[datum.mapping_id])


class BaseMappingsTable(tables.DataTable):
    type = tables.Column('type', verbose_name=_("Type"))
    cost = tables.Column('cost', verbose_name=_("Cost"))
    group_id = tables.Column('group_id', verbose_name=_("Group"))


class ServiceMappingsTable(BaseMappingsTable):

    class Meta(object):
        name = "mappings"
        verbose_name = _("Mappings")
        row_actions = (EditServiceMapping, DeleteMapping)
        table_actions = (CreateServiceMapping, DeleteMapping)


class CreateFieldMapping(tables.LinkAction):
    name = "createfieldmapping"
    verbose_name = _("Create new Mapping")
    icon = "create"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:field_mapping_create'
        field_id = self.table.request.field_id
        return reverse(url, args=[field_id])


class EditFieldMapping(tables.LinkAction):
    name = "editfieldmapping"
    verbose_name = _("Edit Mapping")
    icon = "edit"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:field_mapping_edit'
        return reverse(url, args=[datum.mapping_id])


class FieldMappingsTable(BaseMappingsTable):
    value = tables.Column('value', verbose_name=_("Value"))

    class Meta(object):
        name = "mappings"
        verbose_name = _("Mappings")
        row_actions = (EditFieldMapping, DeleteMapping)
        table_actions = (CreateFieldMapping, DeleteMapping)


class FieldMappingsTab(tabs.TableTab):
    name = _("Field Mappings")
    slug = "hashmap_field_mappings"
    table_classes = (FieldMappingsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_mappings_data(self):
        client = api.cloudkittyclient(self.request)
        mappings = client.hashmap.mappings.list(
            field_id=self.request.field_id)
        return api.identify(mappings)


class MappingsTab(tabs.TableTab):
    name = _("Service Mappings")
    slug = "hashmap_mappings"
    table_classes = (ServiceMappingsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_mappings_data(self):
        client = api.cloudkittyclient(self.request)
        mappings = client.hashmap.mappings.list(
            service_id=self.request.service_id)
        return api.identify(mappings)


class FieldTabs(tabs.TabGroup):
    slug = "field_tabs"
    tabs = (FieldMappingsTab, FieldThresholdsTab)
    sticky = True


class ServiceTabs(tabs.TabGroup):
    slug = "services_tabs"
    tabs = (FieldsTab, MappingsTab, ServiceThresholdsTab, GroupsTab)
    sticky = True
