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

"""Google Groups Backup."""

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import argparse
import logging
import os
import sys

from ggbackuplib import GGBackup, GGWriter

parser = argparse.ArgumentParser(description='Back up Google Groups.')
parser.add_argument('domain',
                    help='The G Suite domain to retrieve groups from.')

group = parser.add_argument_group(title='Logging options')
group.add_argument('-v', action='store_true', help='Verbose logging.')
group.add_argument('--debug', action='store_true', help='Debug logging.')

group = parser.add_argument_group(title='File location options')

group.add_argument('--client_secrets', nargs=1,
                   default=['client_secrets.json'],
                   help='The client_secrets.json file to use.')
group.add_argument('--credentials', nargs=1,
                   default=['credentials.json'],
                   help=('The credentials file to load/save '
                         '(default: credentials.json).'))
group.add_argument('--target', nargs=1, default=['.'],
                   help='The target directory to save CSVs (default: .)')

group = parser.add_argument_group(title='Authentication options')
group.add_argument('--first', action='store_true',
                   help=('First authentication. Will perform full OAuth2 '
                         'request.'))
group.add_argument('-s', '--save', action='store_true',
                   help='Save credentials to file. (implies --first)')
group.add_argument('--setup', action='store_true',
                   help=('Only set up the application, do not request data. '
                         'Implies --first and --save.'))

group = parser.add_argument_group(title='Run options')
group.add_argument('--nosettings', action='store_true',
                   help='Do not retrieve Group Settings.')
group.add_argument('--datestamp', action='store_true',
                   help='Datestamp all CSVs.')

args = parser.parse_args()

# Set up logging
logger = logging.getLogger()
stdout_logger = logging.StreamHandler(sys.stdout)
if args.debug:
    logger.setLevel(logging.DEBUG)
elif args.v:
    logger.setLevel(logging.INFO)
else:
    logger.setLevel(logging.WARNING)
logger.addHandler(stdout_logger)

# Set up error count.
errors = 0

# Start backup process.
ggbackup = GGBackup(args.domain)

# Authenticate
if args.first or args.save or args.setup:
    try:
        ggbackup.first_auth(args.client_secrets[0])
    except Exception as e:
        logger.critical('Error authenticating with Google: %s', e)
        exit(1)

    if args.save or args.setup:
        try:
            ggbackup.save(args.credentials[0])
        except Exception as e:
            logger.error('Error saving credentials: %s', e)
            errors += 1
else:
    # Load saved credentials.
    try:
        ggbackup.load(args.credentials[0])
    except Exception as e:
        logger.error('Error loading credentials: %s', e)
        errors += 1

if args.setup:
    logger.info('Setup complete.')
    exit(errors)

ggbackup.auth()

# Retrieve all groups.
try:
    ggbackup.get_groups()
except Exception as e:
    logger.critical('Error gathering groups: %s', e)
    exit(1)

if args.nosettings is False:
    try:
        ggbackup.get_settings()
        logger.info('Retrieved settings for all groups.')
    except Exception as e:
        logger.error('Error gathering group settings: %s', e)
        errors += 1

try:
    ggbackup.get_members()
    logger.info('Retrieved members for all groups.')
except Exception as e:
    logger.error('Error gathering group members: %s', e)
    errors += 1

# Write the data

ggwriter = GGWriter(os.path.join(args.target[0], args.domain),
                    ggbackup.groups,
                    datestamp=args.datestamp)

try:
    ggwriter.write_members()
    logger.info('Wrote all group membership CSVs.')
except Exception as e:
    logger.error('Error writing group membership: %s', e)
    errors += 1

try:
    ggwriter.write_settings()
    logger.info('Wrote all settings.')
except Exception as e:
    logger.error('Error writing group settings: %s', e)
    errors += 1

exit(errors)
