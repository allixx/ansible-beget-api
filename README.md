# Manage (sub)domains and DNS records using [Beget API](https://beget.com/)[^1][^2] with Ansible.

## `allixx.beget.beget_api` role

Automates management of (sub)domains and DNS records. It was created as a thought experiment, but ended up being useful.
Tested on ansible-core<2.19.

`beget_api_login` and `beget_api_password` variables must contain valid API credentials with suitable domains/DNS rights 

Main input variable is `beget_api_domains_and_dns`. It contains a list of domains, subdomains and DNS records. Variable
structure is illustrated in [Example playbook](#example-splaybook) section.

The role iterates over domains first to create missing and remove obsolete subdomains.

Annoying magic `www` subdomains are removed: see `beget_api_ignore_subdomains` variable - someone at Beget
decided it would be a good idea to automatically slap `www` subdomain on each created subdomain.

Then the role goes over DNS records and rewrites records only if the change is due.

NB: the role does not handle domain(s) creation: they must already be present in Beget system! Also, no input validation
whatsoever is performed, so handle with care.

## `allixx.beget.verify_dns` role

Helper to validate (sub)domains and DNS records by performing actual DNS queries.

Role's input variable `verify_dns` is expected to have the same structure as `allixx.beget.beget_api`'s `beget_api_domains_and_dns`.

## Example playbook ##

```yaml
---

- hosts: localhost
  gather_facts: false
  vars:
    input_data:
      - domain: domain.com
        subdomains:
          - subdomain: "@"                 # @ is a shortcut: domain.com is used here
            records:
              - type: A                    # anything supported by Beget AND community.general.dig
                value: 1.2.3.4             # it's possible to pass a single value
              - type: AAAA
                value:
                  - ::1                    # or pass a list (where applicable by Beget/DNS rules)
                  - ::2
              - type: CAA
                value: 0 issue "letsencrypt.org"
              - type: TXT
                value: v=spf1 mx -all
              - type: MX
                value: 10 mail.domain.com. # trailing dot is required
          - subdomain: mail
            records:
              - type: A
                value: 1.2.3.4
          - subdomain: test
            records:
              - type: CNAME
                value: domain.com.
        # etc...

    beget_api_login: api_login
    beget_api_password: api_password

  roles:
    - role: allixx.beget.beget_api
      beget_api_domains_and_dns: "{{ input_data }}"
    - role: allixx.beget.verify_dns
      verify_dns: "{{ input_data }}"
```

## Sidenotes ##

Beget API is somewhat "special". At least in domains and DNS API, it's impossible to directly use data
received with `get*` endpoints by `change*` endpoints without transformation.

DNS part of this transformation is handled internally by `allixx.beget.beget_dns_get_to_change` filter.

Transformation of internal DNS variable to data digestable by beget is handled by `allixx.beget.beget.private_dns_to_beget` filter.

[^1]: https://beget.com/en/kb/api/dns-administration-functions
[^2]: https://beget.com/en/kb/api/functions-for-work-with-domains
