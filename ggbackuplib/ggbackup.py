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
from builtins import input
from oauth2client import client
from oauth2client.file import Storage

logger = logging.getLogger(__name__)


class GGBackup(object):
    """Object to handle GGBackup operations."""

    def __init__(self):
        """Init with client_secrets file."""
        super(GGBackup, self).__init__()
        self.http_auth = None
        self.credentials = None

    def first_auth(self, client_secrets):
        """Authenticate with Google API."""
        flow = client.flow_from_clientsecrets(
            client_secrets,
            scope=[
                'https://www.googleapis.com/auth/admin.directory.group.readonly',  # noqa
                'https://www.googleapis.com/auth/admin.directory.group.member.readonly'  # noqa
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

    def check_auth(self):
        """Check if a session has authenticated."""
        if self.http_auth is None:
            raise Exception('HTTP Auth not completed.')

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
        """Authenticate with the API using stored creds."""
        self.check_credentials()
        self.http_auth = self.credentials.authorize(httplib2.Http())
