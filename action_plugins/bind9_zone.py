#!/usr/bin/python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible.template import Templar, generate_ansible_template_vars
from datetime import date
from os import path
import hashlib
import json

ZONE_TEMPLATE = """{% macro print_record(name, type, value) %}
{{ "%-15s" | format(name) }} IN      {{ "%-7s" | format(type) }} {{ value }}
{% endmacro %}
; {{ ansible_managed }}
{% if not zone.dynamic | default(False) %}
; Hash:{{ zone.hash}},Serial:{{ zone.serial }}
{% endif %}
$TTL            604800
$ORIGIN {{ zone.name }}.
@               IN      SOA     {{ zone.nameservers | map(attribute='name') | first }}. {{ zone.hostmaster | default("hostmaster." + zone.name) }}. (
                                {{ "%10s" | format(zone.serial | default(zone_serial.stdout)) }}     ; Serial
                                {{ "%10s" | format(zone.refresh | default("604800")) }}     ; Refresh
                                {{ "%10s" | format(zone.retry | default("86400")) }}     ; Retry
                                {{ "%10s" | format(zone.expire | default("2419200")) }}     ; Expire
                                {{ "%10s" | format(zone.ttl | default("604800")) }} )   ; Negative Cache TTL

{% if zone.nameservers is defined and zone.nameservers %}
{%   for ns in zone.nameservers %}
                IN      NS      {{ ns.name }}.
{%   endfor %}
{% endif %}
{% if zone.mailservers is defined and zone.mailservers %}
{%   for mx in zone.mailservers %}
                IN      MX   {{ loop.index * 10 }} {{ mx }}.
{%   endfor %}
{% endif %}
{% if zone.nameservers is defined and zone.nameservers %}
{%   for ns in zone.nameservers -%}
{%     if ns.ipv4_address is defined and ns.ipv4_address %}
{%       if (zone.ptr | default(False)) %}
{{ print_record((ns.ipv4_address.split('.') | last), 'PTR', ns.name + '.') }}
{%       else %}
{{ print_record((ns.name.split('.') | first), 'A', ns.ipv4_address) -}}
{%       endif %}
{%     endif %}
{%-  endfor %}
{% endif %}
{% if not (zone.dynamic | default(False)) %}
{%   if zone.records is defined and zone.records %}
{%     for record in zone.records %}
{%       if (record.state | default('present')) == 'present' %}
{{ print_record(record.name, record.type, record.value) -}}
{%       endif %}
{%-    endfor %}
{%   endif %}
{% endif %}
"""


class ActionModule(ActionBase):

    @property
    def name(self):
        return self._task.args.get('name', None)

    @property
    def admin(self):
        return self._task.args.get('admin', None)

    @property
    def nameservers(self):
        return self._task.args.get('nameservers', None)

    @property
    def mailservers(self):
        return self._task.args.get('mailservers', None)

    @property
    def records(self):
        return self._task.args.get('records', None)

    @property
    def view(self):
        return self._task.args.get('view', None)

    @property
    def zone_directory(self):
        return self._task.args.get('zone_directory', None)

    @property
    def is_dynamic(self):
        return self._task.args.get('dynamic', False)

    @property
    def default_serial(self):
        return date.today().strftime("%Y%0m%0d01")

    @property
    def zone_data(self):
        return {
            "name": self.name,
            "admin": self.admin,
            "nameservers": self.nameservers,
            "mailservers": self.mailservers,
            "refresh": "604800",
            "retry": "86400",
            "expire": "2419200",
            "ttl": "604800",
            "records": self.records
        }

    def fetch_zone_details(self, task_vars):
        module_return = self._execute_module(module_name='bind9_zone_details',
                                        module_args=dict(zone_directory=self.zone_directory),
                                        task_vars=task_vars)
        zone_details = module_return['bind9_zone_details']
        zone_path = self.name
        if self.view != None:
            zone_path = "/".join([self.view, self.name])

        return zone_details.get(zone_path, None)

    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = dict()

        result = super(ActionModule, self).run(tmp, task_vars)

        zone_serial = self.default_serial

        update_zone = False

        force = not self.is_dynamic
        if self.is_dynamic:
            update_zone = True
        else:
            #
            # Retrieve any details already stored for the zone
            #
            zone_details = self.fetch_zone_details(task_vars)

            #
            # Generate a hash of the new zone data
            #
            zone_hash = hashlib.md5(json.dumps(self.zone_data, sort_keys=True).encode('utf-8')).hexdigest()

            if zone_details != None:
                current_hash = zone_details.get('hash', None)
                current_serial = zone_details.get('serial', None)

                if current_hash != zone_hash:
                    update_zone = True
                    if int(current_serial) > int(zone_serial):
                        zone_serial = str(int(current_serial) + 1)
            else:
                update_zone = True

        if update_zone:
            template_args = {
                "zone": {
                    "name": self.name,
                    "serial": zone_serial,
                    "nameservers": self.nameservers,
                    "records": self.records,
                    "dynamic": self.is_dynamic
                },
                "view": self.view
            }

            if not self.is_dynamic:
                template_args['zone'].update(dict(hash=zone_hash))
            template_args.update(generate_ansible_template_vars('/tmp', None))
            templar = Templar(None, variables=template_args)
            templated = templar.template(ZONE_TEMPLATE)

            if self.view != None:
                path_segments = [self.zone_directory, self.view, "db.%s" % self.name]
            else:
                path_segments = [self.zone_directory, "db.%s" % self.name]

            dest_file = path.join(*path_segments)

            new_task = self._task.copy()
            new_task.args.clear()
            new_task.args['content'] = templated
            new_task.args['dest'] = dest_file
            new_task.args['force'] = force
            new_task.args['owner'] = 'bind'
            new_task.args['group'] = 'bind'
            new_task.args['mode'] = '0644'

            copy_action = self._shared_loader_obj.action_loader.get('copy',
                    task=new_task, connection=self._connection,
                    play_context=self._play_context, loader=self._loader,
                    templar=self._templar, shared_loader_obj=self._shared_loader_obj)

            result.update(copy_action.run(task_vars=task_vars))

        return result
