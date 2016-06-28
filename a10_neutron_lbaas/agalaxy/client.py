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

import json
import logging
import requests
from six.moves import http_client
import sys

import endpoints.device as device_endpoint
import errors

# Initialize logging
LOG = logging.getLogger(__name__)

out_hdlr = logging.StreamHandler(sys.stdout)
out_hdlr.setLevel(logging.DEBUG)
LOG.addHandler(out_hdlr)

LOG.setLevel(logging.DEBUG)

http_client.HTTPConnection.debuglevel = logging.INFO


class HttpVerbsMixin(object):
    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def put(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def delete(self, *args, **kwargs):
        return self.request('DELETE', *args, **kwargs)


class HttpClient(HttpVerbsMixin, object):
    HEADERS = {
        'Content-type': 'application/json',
        'Accept': 'application/json',
    }

    def __init__(self, host, protocol='https', port=None, verify=False):
        self.host = host
        self.protocol = protocol
        self.port = port
        self.verify = verify
        self._session = None

    def _get_session(self):
        self._session = self._session or self._create_session()
        return self._session

    def _create_session(self):
        session = requests.session()
        session.verify = self.verify
        return session

    def request(self, method, api_url, data=None, headers={}):
        base_url = "%s://%s" % (self.protocol, self.host)
        if self.port is not None:
            base_url = "%s:%s" % (base_url, self.port)
        url = base_url + api_url

        client = self._get_session()

        all_headers = self.HEADERS.copy()
        csrf_token = client.cookies.get('csrftoken')
        if csrf_token is not None:
            all_headers['X-CSRFToken'] = csrf_token
        all_headers.update(headers)

        if data is not None:
            body = json.dumps(data)
        else:
            body = None

        http_response = client.request(method, url, data=body, headers=all_headers)

        if http_response.status_code == 204:
            return None

        if http_response.status_code == 404:
            raise errors.NotFound(404)

        return http_response.json()

    def close(self):
        if self._session is not None:
            self._session.close()
        self._session = None


class Session(HttpVerbsMixin, object):
    def __init__(self, username, password, http):
        self.username = username
        self.password = password
        self.http = http
        self.authenticated = False

    def request(self, method, api_url, data=None, headers={}):
        if not self.authenticated:
            self.authenticate(self.username, self.password)

        return self.http.request(method, api_url, data=data, headers=headers)

    def authenticate(self, username, password):
        url = '/agapi/auth/login/'
        data = {"credentials": {
            'username': 'admin',
            'password': 'a10'
        }}

        response = self.http.post(url, data)
        self.authenticated = True
        return response

    def close(self):
        if not self.authenticated:
            self.http.close()
            return

        url = '/agapi/auth/logout/'

        result = self.http.post(url)
        self.http.close()
        return result


class Client(object):

    def __init__(self, host=None, username=None, password=None,
                 port=None, protocol='https', verify=False,
                 session=None):
        self.session = session or Session(
            username, password,
            HttpClient(host, protocol=protocol, port=port, verify=verify))

        self.device = device_endpoint.Device(self)
