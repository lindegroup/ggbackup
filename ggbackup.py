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
import sys

from ggbackuplib import GGBackup

parser = argparse.ArgumentParser(description='Back up Google Groups.')
parser.add_argument('--setup', action='store_true', help='Setup ggbackup.')
parser.add_argument('-v', action='store_true', help='Verbose logging.')
parser.add_argument('--debug', action='store_true', help='Debug logging.')
parser.add_argument('--client_secrets', nargs=1,
                    default=['client_secrets.json'],
                    help='The client_secrets.json file to use.')
parser.add_argument('--credentials', nargs=1,
                    default=['credentials.json'],
                    help=('The credentials file to load/save '
                          '(default: credentials.json).'))
parser.add_argument('-s', '--save', action='store_true',
                    help='Save credentials to file. (implies --first)')
parser.add_argument('--first', action='store_true',
                    help=('First authentication. Will perform full OAuth2 '
                          'request. Will save result with the --save flag '
                          'at --credentials.'))
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

# Start backup process.
ggbackup = GGBackup()

# Authenticate
if args.first or args.save:
    try:
        ggbackup.first_auth(args.client_secrets[0])
    except Exception as e:
        logger.critical('Error authenticating with Google: %s', e)
        exit(1)

    if args.save:
        try:
            ggbackup.save(args.credentials[0])
        except Exception as e:
            logger.error('Error saving credentials: %s', e)
else:
    # Load saved credentials.
    try:
        ggbackup.load(args.credentials[0])
    except Exception as e:
        logger.error('Error loading credentials: %s', e)

ggbackup.auth()

