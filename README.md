# Ansible Role: Bind9
[![Gitlab pipeline status (self-hosted)](https://git.dubzland.net/dubzland/ansible-role-bind9/badges/master/pipeline.svg)](https://git.dubzland.net/dubzland/ansible-role-bind9)

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

```
dubzland_bind9_zones: []
```

List of zones to be configured.

### dubzland_bind9_views

```
dubzland_bind9_views: []
```

Logical views to create in Bind.

## Dependencies

None

## Example Playbook

```yaml
- hosts: dhcp-servers
  become: yes
  roles:
  - role: dubzland.dhcpd
    vars:
      dubzland_dhcpd_interfaces:
        - eth1
      dubzland_dhcpd_failovers:
        - name: my-failover
          primary: 192.168.0.1
          secondary: 192.168.0.2
          split: 128
      dubzland_dhcpd_keys:
        - name: my-dynamic-key
          secret: "{{ my_dynamic_key_secret_value }}"
      dubzland_dhcpd_zones:
        - name: example.com
          primary: 192.168.0.1
          key: my-dynamic-key
        - name: 0.168.192.in-addr.arpa
          primary: 192.168.0.1
          key: my-dynamic-key
      dubzland_dhcpd_groups:
        - options: |
            option domain-name example.com;
          subnets:
            - address: 192.168.0.0/24
              pools:
                - range: 192.168.0.101 192.168.0.200
                  options: |
                    failover peer "my-failover";
              options: |
                option routers 192.168.0.1;
                option domain-name-servers 192.168.0.1;
                option domain-search example.com;
                option ntp-servers 192.168.0.1;
          hosts:
            - hostname: myhost
              address: 192.168.0.12
              mac: 00:11:22:aa:bb:cc
```

## License

MIT

## Author

* [Josh Williams](https://codingprime.com)
