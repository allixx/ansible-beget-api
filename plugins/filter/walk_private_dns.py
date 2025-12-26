#!/usr/bin/env python

from ansible.errors import AnsibleFilterTypeError


def walk_private_dns(domains):
    """Converts private DNS records data to form consumable by plain loop"""

    result = []

    if not isinstance(domains, list):
        raise AnsibleFilterTypeError(
            f"private_dns requires a list, got {type(domains)} instead."
        )

    for domain in (d for d in domains if "subdomains" in d):
        for subdomain in domain["subdomains"]:
            result += [
                {
                    "domain": domain["domain"],
                    "subdomain": subdomain["subdomain"],
                    "record": record,
                }
                for record in subdomain["records"]
                if "records" in subdomain
            ]

    return result


class FilterModule:
    def filters(self):
        return {
            "walk_private_dns": walk_private_dns,
        }
