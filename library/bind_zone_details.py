#!/usr/bin/python

from ansible.module_utils.basic import AnsibleModule
from os import path

def run_module():
    module_args = dict(
        zone_directory=dict(type='str', required=True)
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )


    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    rc, stdout, stderr = module.run_command('grep -ir --include "db.*" "; Hash" %s' % module.params['zone_directory'], use_unsafe_shell=True)
    details = {}
    for line in stdout.split("\n"):
        if len(line) > 0:
            zone_file, zone_details = line.split(":", 1)
            _, filename = path.split(zone_file)
            zone_name = filename.split(".", 1)[-1]
            hash_chunk, serial_chunk = zone_details.split(",")
            _, hash_str = hash_chunk.split(":")
            _, serial_str = serial_chunk.split(":")
            details[zone_name] = { "hash": hash_str, "serial": serial_str }
    result['ansible_facts'] = dict(bind_zone_details=details)
    result['bind_zone_details'] = details

    # use whatever logic you need to determine whether or not this module
    # made any modifications to your target
    # if module.params['new']:
    #     result['changed'] = True

    # during the execution of the module, if there is an exception or a
    # conditional state that effectively causes a failure, run
    # AnsibleModule.fail_json() to pass in the message and the result
    # if module.params['name'] == 'fail me':
    #     module.fail_json(msg='You requested this to fail', **result)

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(**result)

def main():
    run_module()

if __name__ == '__main__':
    main()
