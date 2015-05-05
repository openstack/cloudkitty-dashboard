# -*- coding: utf-8 -*-
# Copyright 2015 Objectif Libre
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

from django.conf.urls import patterns  # noqa
from django.conf.urls import url  # noqa
from django.utils.translation import ugettext_lazy as _
from openstack_dashboard.dashboards.project.instances.workflows \
    import create_instance


# Instances Panel
class InstancePredictivePricing(create_instance.SetInstanceDetailsAction):
    class Meta(object):
        name = _("Details")
        help_text_template = ("project/rating/"
                              "_launch_details_price.html")

    def get_help_text(self, extra_context=None):
        extra = extra_context or {}
        extra['price'] = 0
        extra = super(InstancePredictivePricing,
                      self).get_help_text(extra_context=extra)
        return extra

create_instance.SetInstanceDetails.action_class = InstancePredictivePricing
