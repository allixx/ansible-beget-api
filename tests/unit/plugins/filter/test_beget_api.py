#!/usr/bin/env python

import unittest
import yaml

from collections import defaultdict
from ansible.errors import AnsibleFilterTypeError

from plugins.filter.beget_api import (
    private_dns_to_beget,
    BegetDNSGetToChange,
    FilterModule,
)


class TestDnsGetToChange(unittest.TestCase):
    TESTS = [
        [{}, {}],
        [
            {"CNAME": [{"cname": "domain.com.", "ttl": 600}], "DNS": [], "DNS_IP": []},
            {"CNAME": [{"priority": 0, "value": "domain.com."}]},
        ],
        [
            {
                "A": [{"address": "127.0.0.1", "ttl": 600}],
                "AAAA": [{"address": "::1", "ttl": 600}],
                "CAA": [
                    {"flags": 0, "tag": "issue", "ttl": 600, "value": "letsencrypt.org"}
                ],
                "DNS": [
                    {"value": "ns1.beget.com"},
                    {"value": "ns1.beget.pro"},
                    {"value": "ns2.beget.com"},
                    {"value": "ns2.beget.pro"},
                ],
                "DNS_IP": [{"value": ""}, {"value": ""}, {"value": ""}, {"value": ""}],
                "MX": [{"exchange": "mail.domain.com.", "preference": 10, "ttl": 600}],
                "TXT": [{"ttl": 600, "txtdata": "v=spf1 mx -all"}],
            },
            {
                "A": [{"priority": 0, "value": "127.0.0.1"}],
                "AAAA": [{"priority": 0, "value": "::1"}],
                "CAA": [{"flags": 0, "tag": "issue", "value": "letsencrypt.org"}],
                "MX": [{"priority": 10, "value": "mail.domain.com"}],
                "TXT": [{"priority": 0, "value": "v=spf1 mx -all"}],
                "DNS": [
                    {"value": "ns1.beget.com", "priority": 0},
                    {"value": "ns1.beget.pro", "priority": 0},
                    {"value": "ns2.beget.com", "priority": 0},
                    {"value": "ns2.beget.pro", "priority": 0},
                ],
            },
        ],
    ]

    def setUp(self):
        self.maxDiff = None

    def test_dns_get_to_change_data(self):
        for test in self.TESTS:
            self.assertEqual(BegetDNSGetToChange().process(test[0]), test[1])

    def test_dns_get_to_change_exceptions(self):
        self.assertRaises(AnsibleFilterTypeError, BegetDNSGetToChange().process, [])

        self.assertRaises(
            AnsibleFilterTypeError,
            BegetDNSGetToChange().process,
            {"A": {}},
        )

        self.assertRaises(
            AnsibleFilterTypeError,
            BegetDNSGetToChange().process,
            {"A": [[]]},
        )


class TestFilterModule(unittest.TestCase):
    """Dumb stub for 100% coverage"""

    def test_filters(self):
        self.assertIsInstance(FilterModule().filters(), dict)


class TestPrivateDnsToBeget(unittest.TestCase):
    DATA = """
      domain: domain
      subdomains:
        - subdomain: "@"
          records:
            - type: A
              value: 127.0.0.1
            - type: AAAA
              value: ::1
            - type: CAA
              value: 0 issue "letsencrypt.org"
            - type: MX
              value: 10 mail.domain.
            - type: NS
              value:
                - ns1.beget.com.
                - ns2.beget.com.
                - ns1.beget.pro.
                - ns2.beget.pro.
            - type: TXT
              value: v=spf1 mx -all
        - subdomain: mail
          records:
            - type: A
              value:
                - 127.0.0.1
                - 127.0.0.2
        - subdomain: subdomain
          records:
            - type: CNAME
              value: domain.
        - subdomain: _dmarc
          records:
            - type: TXT
              value: v=DMARC1
    """

    TESTS = [
        (
            "@",
            defaultdict(
                list,
                {
                    "A": [{"value": "127.0.0.1", "priority": 0}],
                    "AAAA": [{"value": "::1", "priority": 0}],
                    "CAA": [{"flags": 0, "tag": "issue", "value": "letsencrypt.org"}],
                    "MX": [{"value": "mail.domain", "priority": 10}],
                    "TXT": [{"value": "v=spf1 mx -all", "priority": 0}],
                    "DNS": [
                        {"value": "ns1.beget.com", "priority": 0},
                        {"value": "ns1.beget.pro", "priority": 0},
                        {"value": "ns2.beget.com", "priority": 0},
                        {"value": "ns2.beget.pro", "priority": 0},
                    ],
                },
            ),
        ),
        ("mail", defaultdict(list, {"A": [{"value": "127.0.0.1", "priority": 0}, {"value": "127.0.0.2", "priority": 0} ]})),
        (
            "subdomain",
            defaultdict(
                list,
                {
                    "CNAME": [{"value": "domain.", "priority": 0}],
                },
            ),
        ),
        (
            "_dmarc",
            defaultdict(list, {"TXT": [{"value": "v=DMARC1", "priority": 0}]}),
        ),
    ]

    def test_private_dns_to_beget_data(self):
        data = yaml.safe_load(self.DATA)

        for test in self.TESTS:
            self.assertEqual(private_dns_to_beget(data["subdomains"], test[0]), test[1])

    def test_private_dns_to_beget_exceptions(self):
        self.assertRaises(AnsibleFilterTypeError, private_dns_to_beget, {}, [])
