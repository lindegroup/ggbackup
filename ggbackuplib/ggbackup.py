# Copyright 2017 The Linde Group. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Main Google Groups Backup Class."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import httplib2
import webbrowser

from math import ceil

from builtins import input

from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage

logger = logging.getLogger(__name__)


class GGBackup(object):
    """Object to handle GGBackup operations."""

    def __init__(self, domain):
        """Init with target domain, set initial values."""
        super(GGBackup, self).__init__()
        self.domain = domain
        self.http_auth = None
        self.credentials = None
        self.service = None
        self.gsetservice = None
        self.groups = {}

    def first_auth(self, client_secrets):
        """Authenticate with Google API."""
        flow = client.flow_from_clientsecrets(
            client_secrets,
            scope=[
                'https://www.googleapis.com/auth/admin.directory.group.readonly',  # noqa
                'https://www.googleapis.com/auth/admin.directory.group.member.readonly',  # noqa
                'https://www.googleapis.com/auth/apps.groups.settings'
            ],
            redirect_uri='urn:ietf:wg:oauth:2.0:oob')

        logger.debug('Generating authorization URL.')
        auth_uri = flow.step1_get_authorize_url()
        webbrowser.open(auth_uri)

        auth_code = input('Enter the auth code: ')

        logger.debug('Generating credentials.')
        self.credentials = flow.step2_exchange(auth_code)

    def check_credentials(self):
        """Check if credentials have been gathered."""
        if self.credentials is None:
            raise Exception('Credentials not found.')
        if self.credentials.invalid:
            raise Exception('Credentials are invalid.')

    def check_auth(self):
        """Check if a session has authenticated."""
        if self.http_auth is None:
            raise Exception('HTTP Auth not completed.')
        if self.service is None:
            raise Exception('Admin SDK service is not available.')
        if self.gsetservice is None:
            raise Exception('Groups Settings service is not available.')

    def save(self, cred_file):
        """Save credentials to an external file."""
        self.check_credentials()
        storage = Storage(cred_file)
        storage.put(self.credentials)
        logger.info('Saved credentials to %s', cred_file)

    def load(self, cred_file):
        """Load pre-saved credentials."""
        storage = Storage(cred_file)
        self.credentials = storage.get()

    def auth(self):
        """Authenticate with the API and create the service."""
        self.check_credentials()
        self.http_auth = self.credentials.authorize(httplib2.Http())
        self.service = discovery.build('admin', 'directory_v1',
                                       http=self.http_auth,
                                       cache_discovery=False)
        self.gsetservice = discovery.build('groupssettings', 'v1',
                                           http=self.http_auth,
                                           cache_discovery=False)

    def get_groups(self):
        """Retrieve google groups."""
        self.check_auth()
        request = self.service.groups().list(domain=self.domain)
        while request is not None:
            groups = request.execute()
            for group in groups['groups']:
                self.groups[group['email']] = group
            request = self.service.groups().list_next(request, groups)

    def batch(self, items):
        """Return a list of lists that contain 1000 items or less."""
        count = ceil(float(len(items)) / 1000.)
        batches = []
        i = 0
        while i < count:
            low = i * 1000
            high = (i + 1) * 1000
            batches.append(items[low:high])
            i += 1
        return batches

    def get_settings(self):
        """Retrieve all group settings."""
        self.check_auth()

        groups = list(self.groups.keys())
        batches = self.batch(groups)

        def add_settings(request_id, response, exception):
            if exception is not None:
                logger.warning(
                    'Exception encountered while gathering settings: %s',
                    exception)
                return
            logger.debug('Settings for group %s retrieved.',
                         response['email'])
            email = self.groups[response['email']]
            email.update(response)

        for batch in batches:
            batchreq = self.gsetservice.new_batch_http_request(
                callback=add_settings)
            for group in batch:
                batchreq.add(self.gsetservice.groups().get(groupUniqueId=group,
                                                           alt='json'))
                logger.debug('Executing batch.')
            batchreq.execute()
