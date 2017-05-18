# Copyright 2017 The Linde Group, Inc. All Rights Reserved.
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

"""Google Groups CSV Writer."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import csv
import logging
import os

from datetime import date
from six import itervalues

logger = logging.getLogger(__name__)


class GGWriter(object):
    """Write Google Groups data from a GGBackup object."""

    def __init__(self, path, groups, datestamp=False):
        """Initialize and create the directory if needed."""
        super(GGWriter, self).__init__()

        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.isdir(path):
            raise Exception('%s is not a directory.', path)

        self.path = path
        self.groups = groups
        self.datestamp = datestamp

    def append_datestamp(self, filename):
        """Append the datestamp to a file."""
        datestamp = date.today().isoformat()
        (root, ext) = os.path.splitext(filename)
        return root + datestamp + ext

    def write_members(self):
        """Write the members CSV."""
        for group in itervalues(self.groups):
            filename = group['email'] + '-membership.csv'
            if self.datestamp:
                filename = self.append_datestamp(filename)
            path = os.path.join(self.path, filename)

            logger.debug('Writing %s...', path)

            with open(path, 'w') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=[
                    'kind', 'id', 'email', 'role', 'type', 'status', 'etag'])
                writer.writeheader()
                for member in group['members']:
                    writer.writerow(member)

    def write_settings(self):
        """Write the settings."""
        filename = 'settings.csv'
        if self.datestamp:
            filename = self.append_datestamp(filename)
        path = os.path.join(self.path, filename)

        logger.debug('Writing %s...', path)

        # Prep the fields.
        fields = set()
        for group in itervalues(self.groups):
            fields |= set(group.keys())
        fields.remove('members')
        fields.remove('email')

        fields = list(fields)
        fields.sort()
        fields.insert(0, 'email')

        with open(path, 'w') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fields)
            writer.writeheader()
            for group in itervalues(self.groups):
                g = group.copy()
                del g['members']

                if 'aliases' in g:
                    g['aliases'] = ','.join(g['aliases'])

                writer.writerow(g)
