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

from collections import OrderedDict
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext_lazy

from horizon import tables
from horizon import tabs

from cloudkittydashboard.api import cloudkitty as api


class CreateService(tables.LinkAction):
    name = "createservice"
    verbose_name = _("Create new Service")
    url = 'horizon:admin:hashmap:service_create'
    icon = "plus"
    ajax = True
    classes = ("ajax-modal",)


class DeleteService(tables.DeleteAction):
    name = "deleteservice"
    verbose_name = _("Delete Service")
    data_type_singular = _("Service")
    data_type_plural = _("Services")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Service",
            u"Delete Services",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Service",
            u"Deleted Services",
            count
        )

    def action(self, request, service_id):
        api.cloudkittyclient(request).rating.hashmap.delete_service(
            service_id=service_id)


class ServicesTable(tables.DataTable):
    """This table list the available services.

    Clicking on a service name sends you to a ServiceTabs page.
    """
    name = tables.Column('name', verbose_name=_("Name"),
                         link='horizon:admin:hashmap:service')
    unit = tables.Column("unit", verbose_name=_("Unit"))

    def get_object_id(self, datum):
        return datum['id']

    def get_object_display(self, datum):
        return datum['name']

    class Meta(object):
        name = "services"
        verbose_name = _("Services")
        table_actions = (CreateService, DeleteService)
        row_actions = (DeleteService,)


class CreateGroup(tables.LinkAction):
    name = "creategroup"
    verbose_name = _("Create new Group")
    icon = "plus"
    ajax = True
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:group_create'
        service_id = self.table.request.service_id
        return reverse(url, args=[service_id])


class DeleteGroup(tables.DeleteAction):
    name = "deletegroup"
    verbose_name = _("Delete Group")
    data_type_singular = _("Group")
    data_type_plural = _("Groups")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Group",
            u"Delete Groups",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Group",
            u"Deleted Groups",
            count
        )

    def action(self, request, group_id):
        api.cloudkittyclient(request).rating.hashmap.delete_group(
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
        groups = client.rating.hashmap.get_group().get('groups', [])
        return api.identify(groups, key='group_id')


class CreateServiceThreshold(tables.LinkAction):
    name = "createservicethreshold"
    verbose_name = _("Create new Service Threshold")
    icon = "plus"
    ajax = False
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:service_threshold_create'
        service_id = self.table.request.service_id
        return reverse(url, args=[service_id])


class CreateFieldThreshold(tables.LinkAction):
    name = "createfieldthreshold"
    verbose_name = _("Create new Field Threshold")
    icon = "plus"
    ajax = False
    classes = ("ajax-modal",)

    def get_link_url(self, datum=None):
        url = 'horizon:admin:hashmap:field_threshold_create'
        field_id = self.table.request.field_id
        return reverse(url, args=[field_id])


class DeleteServiceThreshold(tables.DeleteAction):
    name = "deletetservicethreshold"
    verbose_name = _("Delete Service Threshold")
    data_type_singular = _("Service Threshold")
    data_type_plural = _("Service Thresholds")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Service Threshold",
            u"Delete Service Thresholds",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Service Threshold",
            u"Deleted Service Thresholds",
            count
        )

    def action(self, request, threshold_id):
        api.cloudkittyclient(request).rating.hashmap.delete_threshold(
            threshold_id=threshold_id)


class DeleteFieldThreshold(tables.DeleteAction):
    name = "deletefieldthreshold"
    verbose_name = _("Delete Field Threshold")
    data_type_singular = _("Field Threshold")
    data_type_plural = _("Field Thresholds")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Field Threshold",
            u"Delete Field Thresholds",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Field Threshold",
            u"Deleted Field Thresholds",
            count
        )

    def action(self, request, threshold_id):
        api.cloudkittyclient(request).rating.hashmap.delete_threshold(
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


def get_groupname(datum):
    if hasattr(datum, "group_name"):
        groupname = datum.group_name
        return groupname
    return _("Not available")


def add_groupname(request, datums):
    client = api.cloudkittyclient(request)
    groups = client.rating.hashmap.get_group().get('groups', [])
    full_groups = OrderedDict([(str(group['group_id']), group['name'])
                               for group in groups])

    for datum in datums:
        if datum.get('group_id'):
            if datum['group_id'] in full_groups:
                datum['group_name'] = full_groups[datum['group_id']]
            else:
                group = client.rating.hashmap.get_group(
                    group_id=datum['group_id'])
                datum['group_name'] = group['name']


class BaseThresholdsTable(tables.DataTable):
    level = tables.Column('level', verbose_name=_("Level"))
    type = tables.Column('type', verbose_name=_("Type"))
    cost = tables.Column('cost', verbose_name=_("Cost"))
    group_name = tables.Column(get_groupname,
                               verbose_name=_("Group Name"),
                               link=get_detail_link)
    tenant_id = tables.Column('tenant_id', verbose_name=_("Project"))


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
        thresholds = client.rating.hashmap.get_threshold(
            service_id=self.request.service_id).get('thresholds', [])
        add_groupname(self.request, thresholds)
        return api.identify(thresholds, key='threshold_id', name=True)


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
        thresholds = client.rating.hashmap.get_threshold(
            field_id=self.request.field_id).get('thresholds', [])
        add_groupname(self.request, thresholds)
        return api.identify(thresholds, key='threshold_id', name=True)


class DeleteField(tables.DeleteAction):
    name = "deletefield"
    verbose_name = _("Delete Field")
    data_type_singular = _("Field")
    data_type_plural = _("Fields")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Field",
            u"Delete Fields",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Field",
            u"Deleted Fields",
            count
        )

    def action(self, request, field_id):
        api.cloudkittyclient(request).rating.hashmap.delete_field(
            field_id=field_id)


class CreateField(tables.LinkAction):
    name = "createfield"
    verbose_name = _("Create new Field")
    icon = "plus"
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
        fields = client.rating.hashmap.get_field(
            service_id=self.request.service_id)['fields']
        return api.identify(fields, key='field_id')


class DeleteMapping(tables.DeleteAction):
    name = "deletemapping"
    verbose_name = _("Delete Mapping")
    data_type_singular = _("Mapping")
    data_type_plural = _("Mappings")

    @staticmethod
    def action_present(count):
        return ngettext_lazy(
            u"Delete Mapping",
            u"Delete Mappings",
            count
        )

    @staticmethod
    def action_past(count):
        return ngettext_lazy(
            u"Deleted Mapping",
            u"Deleted Mappings",
            count
        )

    def action(self, request, mapping_id):
        api.cloudkittyclient(request).rating.hashmap.delete_mapping(
            mapping_id=mapping_id)


class CreateServiceMapping(tables.LinkAction):
    name = "createiservicemapping"
    verbose_name = _("Create new Mapping")
    icon = "plus"
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
    group_name = tables.Column(get_groupname,
                               verbose_name=_("Group Name"),
                               link=get_detail_link)
    tenant_id = tables.Column('tenant_id', verbose_name=_("Project"))


class ServiceMappingsTable(BaseMappingsTable):

    class Meta(object):
        name = "mappings"
        verbose_name = _("Mappings")
        row_actions = (EditServiceMapping, DeleteMapping)
        table_actions = (CreateServiceMapping, DeleteMapping)


class CreateFieldMapping(tables.LinkAction):
    name = "createfieldmapping"
    verbose_name = _("Create new Mapping")
    icon = "plus"
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
        mappings = client.rating.hashmap.get_mapping(
            field_id=self.request.field_id).get('mappings', [])
        add_groupname(self.request, mappings)
        return api.identify(mappings, key='mapping_id', name=True)


class MappingsTab(tabs.TableTab):
    name = _("Service Mappings")
    slug = "hashmap_mappings"
    table_classes = (ServiceMappingsTable,)
    template_name = "horizon/common/_detail_table.html"
    preload = True

    def get_mappings_data(self):
        client = api.cloudkittyclient(self.request)
        mappings = client.rating.hashmap.get_mapping(
            service_id=self.request.service_id).get('mappings', [])
        add_groupname(self.request, mappings)
        return api.identify(mappings, key='mapping_id', name=True)


class FieldTabs(tabs.TabGroup):
    slug = "field_tabs"
    tabs = (FieldMappingsTab, FieldThresholdsTab)
    sticky = True


class ServiceTabs(tabs.TabGroup):
    slug = "services_tabs"
    tabs = (FieldsTab, MappingsTab, ServiceThresholdsTab, GroupsTab)
    sticky = True
