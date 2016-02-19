# Copyright 2016, A10 Networks
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

import mock
import requests

import test_base

import a10_neutron_lbaas.acos_client_extensions as target

import acos_client.client
import errno
import socket

import httplib

class TestACOSClientExtensions(test_base.UnitTestBase):

    def test_patient_client_replaces_http(self, client_version="3.0"):

        c = acos_client.client.Client(host="ax", username="admin", 
                                      password="password", version=client_version)
        unexpected = c.http
        actual = target.patient_client(c)
        self.assertIsNot(unexpected, actual.http)

    def test_patient_client_replaces_http_21(self):
        return self.test_patient_client_replaces_http("2.1")

    def test_patient_client_replaces_http_request_21(self):
        return self.test_patient_client_replaces_http_request("2.1")

    def test_patient_client_replaces_http_request(self, client_version="3.0"):

        c = acos_client.client.Client(host="ax", username="admin", 
                                      password="password", version=client_version)
        unexpected = c.http.request
        actual = target.patient_client(c)
        self.assertIsNot(unexpected, actual.http.request)

    def test_patient_client_21(self):
        c = acos_client.client.Client(host="ax", username="admin", 
                                      password="password", version="2.1")
        actual = target.patient_client(c)

        with mock.patch('httplib.HTTPConnection') as http_mock:
            with mock.patch('httplib.HTTPSConnection') as https_mock:
                connection_mock = mock.MagicMock()

                http_mock.return_value = connection_mock
                https_mock.return_value = connection_mock

                request_mock = mock.MagicMock()
                connection_mock.request = request_mock

                response_mock = mock.MagicMock()
                response_mock.read.return_value = "Stuff"
                connection_mock.getresponse.return_value = response_mock

                actual.http.get("/stuff")
                self.assertTrue(request_mock.called)
    
    def test_patient_client(self, client_version="3.0"):

        c = acos_client.client.Client(host="ax", username="admin", 
                                      password="password", version=client_version)
        actual = target.patient_client(c)

        with mock.patch('requests.request') as request_mock:
            request_mock.return_value = mock.MagicMock()
            request_mock.return_value.json.return_value = "Stuff!"

            actual.http.get("/stuff")
            self.assertTrue(request_mock.called)

    def test_patient_client_handles_host_unreachable(self, client_version="3.0"):

        c = acos_client.client.Client(host="ax", username="admin", 
                                      password="password", version=client_version)
        actual = target.patient_client(c)

        with mock.patch('requests.request') as request_mock:
            result_mock = mock.MagicMock()
            result_mock.json.return_value = "asdf"
            request_mock.side_effect = [socket.error(errno.EHOSTUNREACH, "Host unreachable"), result_mock]
            
            actual.http.get("/stuff")
            self.assertEqual(2, request_mock.call_count)

    def test_patient_client_handles_host_unreachable_21(self):
        c = acos_client.client.Client(host="ax", username="admin", 
                                      password="password", version="2.1")
        actual = target.patient_client(c)

        with mock.patch('httplib.HTTPConnection') as http_mock:
            with mock.patch('httplib.HTTPSConnection') as https_mock:
                connection_mock = mock.MagicMock()

                http_mock.return_value = connection_mock
                https_mock.return_value = connection_mock

                request_mock = mock.MagicMock()
                request_mock.side_effect = [socket.error(errno.EHOSTUNREACH, "Host unreachable"), mock.MagicMock()]
                connection_mock.request = request_mock           

                response_mock = mock.MagicMock()
                response_mock.read.return_value = "Stuff"
                connection_mock.getresponse.return_value = response_mock

                actual.http.get("/stuff")
                self.assertEqual(2, request_mock.call_count)
