# Ansible Role: Bind9
[![Gitlab pipeline status (self-hosted)](https://git.dubzland.net/dubzland/ansible-role-bind9/badges/main/pipeline.svg)](https://git.dubzland.net/dubzland/ansible-role-bind9/pipelines)
[![Ansible role](https://img.shields.io/ansible/role/45376)](https://galaxy.ansible.com/dubzland/bind9)
[![Ansible role downloads](https://img.shields.io/ansible/role/d/45376)](https://galaxy.ansible.com/dubzland/bind9)
[![Ansible Quality Score](https://img.shields.io/ansible/quality/45376)](https://galaxy.ansible.com/dubzland/bind9)
[![Liberapay patrons](https://img.shields.io/liberapay/patrons/jdubz)](https://liberapay.com/jdubz/donate)
[![Liberapay receiving](https://img.shields.io/liberapay/receives/jdubz)](https://liberapay.com/jdubz/donate)


Installs and configures the Bind9 DNS Server.

## Requirements

Ansible version 2.0 or higher. `jmespath` python module.

## Role Variables

Available variables are listed below, along with their default values (see
    `defaults/main.yml` for more info):

### dubzland_bind9_zone_directory

```yaml
dubzland_bind9_zone_directory: "/var/cache/bind"
```

Directory where zone files will be stored.

### dubzland_bind9_forwarders

```yaml
dubzland_bind9_forwarders:
  - 8.8.8.8
  - 4.4.4.4
```

List of DNS servers to relay queries to.

### dubzland_bind9_keys

```yaml
dubzland_bind9_keys: []
```

List of keys to add to Bind.

### dubzland_bind9_acls

```yaml
dubzland_bind9_acls: []
```

Access Control Lists to setup in Bind.

### dubzland_bind9_zones

```yaml
dubzland_bind9_zones: []
```

List of zones to be configured.

### dubzland_bind9_views

```yaml
dubzland_bind9_views: []
```

Logical views to create in Bind.

## Dependencies

None

## Example Playbook

```yaml
- hosts: dns-servers
  become: yes
  roles:
  - role: dubzland.bind9
    vars:
      dubzland_bind9_zones:
        - name: dubzland.net
          type: master
          hostmaster: admin.dubzland.net
          nameservers:
            - name: ns1.dubzland.net
              ipv4_address: 10.0.0.1
            - name: ns2.dubzland.net
              ipv4_address: 10.0.0.2
          mailservers:
            - mail.dubzland.net
          txt_records:
            - "v=spf1 a mx ~all"
          records:
            - name: dubzland.net.
              value: 10.0.0.1
              type: A
```

## License

MIT

## Author

* [Josh Williams](https://codingprime.com)
