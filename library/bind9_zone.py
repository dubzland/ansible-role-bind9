#!/usr/bin/python

# Copyright: (c) 2019, Josh Williams <vmizzle@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: bind9_zone

short_description: Creates a Bind9 compatible zone file

version_added: "2.2"

description:
    - "Creates/updates a Bind9 zone file, updating the serial if necessary"

options:
    name:
        description:
            - Name of the zone being created
        required: true
    dynamic:
        description:
            - Whether or not this zone will receive dynamic updates
        required: false
    admin:
        description:
            - Administrator for the zone in Bind format (ie.  hostmaster.example.com)
        required: false
    nameservers:
        description:
            - List of nameservers authoritative for this zone
        required: false
    mailservers:
        description:
            - List of mailservers (MX records) for this zone
        required: false
    view:
        description:
            - Logical view to which this zone belongs
        required: false
    zone_directory:
        description:
            - Root directory for storing zone files
        required: true
    records:
        description:
            - List of records to be added to the zone file (only applicable for static zones.
        required: false
'''

from __future__ import absolute_import, division, print_function
__metaclass__ = type
