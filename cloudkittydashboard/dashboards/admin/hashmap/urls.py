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

from django.conf.urls import patterns
from django.conf.urls import url

from cloudkittydashboard.dashboards.admin.hashmap import views

urlpatterns = patterns(
    '',
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^service/(?P<service_id>[^/]+)/?$',
        views.ServiceView.as_view(),
        name='service'),
    url(r'^create_service/?$',
        views.ServiceCreateView.as_view(),
        name='service_create'),
    url(r'^field/(?P<field_id>[^/]+)/?$',
        views.FieldView.as_view(),
        name='field'),
    url(r'^create_field/service/(?P<service_id>[^/]+)/?$',
        views.FieldCreateView.as_view(),
        name='field_create'),
    url(r'^create_mapping/service/(?P<service_id>[^/]+)/?$',
        views.ServiceMappingCreateView.as_view(),
        name='service_mapping_create'),
    url(r'^create_mapping/field/(?P<field_id>[^/]+)/?$',
        views.FieldMappingCreateView.as_view(),
        name='field_mapping_create'),
    url(r'^edit_mapping/service/(?P<mapping_id>[^/]+)/?$',
        views.ServiceMappingEditView.as_view(),
        name='service_mapping_edit'),
    url(r'^edit_mapping/field/(?P<mapping_id>[^/]+)/?$',
        views.FieldMappingEditView.as_view(),
        name='field_mapping_edit'),
)
