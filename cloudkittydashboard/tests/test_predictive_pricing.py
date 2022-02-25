# Copyright 2019 Objectif Libre
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
import json
import os
from unittest import mock

from django import http

from cloudkittydashboard.tests import base


class PredictivePricingTest(base.TestCase):

    def setUp(self):
        super(PredictivePricingTest, self).setUp()

        os.environ['DJANGO_SETTINGS_MODULE'] = 'openstack_dashboard.settings'
        import horizon.tables  # noqa
        with mock.patch('horizon.tables'):
            from cloudkittydashboard.dashboards.project.rating.views \
                import quote
        os.environ.pop('DJANGO_SETTINGS_MODULE')
        self.quote = quote

    def _test_quote_request_not_ajax_post(self, arg):
        request = mock.MagicMock()
        if arg == 'ajax':
            request.is_ajax.return_value = False
        elif arg == 'method':
            request.method == 'POST'
        resp = self.quote(request)
        self.assertIsInstance(resp, http.HttpResponse)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), '0.0')

    def test_quote_request_not_ajax(self):
        self._test_quote_request_not_ajax_post('ajax')

    def test_quote_request_wrong_method(self):
        self._test_quote_request_not_ajax_post('method')

    @mock.patch('cloudkittydashboard.dashboards.project.rating.views.api')
    def test_quote_does_update_request_dict(self, api_mock):
        body = [{'service': 'nope'}, {'other_key': None}]
        expected_body = [{'service': 'test_service'},
                         {'other_key': None, 'service': 'test_service'}]

        request = mock.MagicMock()
        request.is_ajax.return_value = True
        request.method = 'POST'
        request.body = json.dumps(body)

        client_mock = mock.MagicMock()
        client_mock.rating.get_quotation.return_value = 42.0
        api_mock.cloudkittyclient.return_value = client_mock

        settings = mock.MagicMock()
        settings.CLOUDKITTY_QUOTATION_SERVICE = 'test_service'
        with mock.patch(
                'cloudkittydashboard.dashboards.project.rating.views.settings',
                settings):
            resp = self.quote(request)

        api_mock.cloudkittyclient.assert_called_with(request)
        client_mock.rating.get_quotation.assert_called_with(
            res_data=expected_body)
        self.assertIsInstance(resp, http.HttpResponse)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.content.decode(), '42.0')
