# vim: set fenc=utf8 ts=4 sw=4 et :
from pdml2flow.logging import *
from pdml2flow.plugin import *

import dns.resolver
import dns.reversename
import dns.tsigkeyring
import dns.update
import sys


class Links(object):

    def __init__(self):
        self.__macs = set()
        self.__hosts = set()
        self.__ipv4s = set()
        self.__ipv6s = set()

    def __repr__(self):
        return str(vars(self))

    def reverse_lookup(self, ip):
        try:
            for resolved_host in dns.resolver.query(
                dns.reversename.from_address(ip),
                'PTR'
            ):
                self.add_host(resolved_host)
        except dns.resolver.NoAnswer:
            pass
        
    def add_host(self, host):
        if host in self.__hosts:
            return
        self.__hosts.add(host)
        try: 
            for a_record in dns.resolver.query(str(host), 'A'):
                self.add_ipv4(a_record)
        except dns.resolver.NoAnswer:
            pass
        try: 
            for aaaa_record in dns.resolver.query(str(host), 'AAAA'):
                self.add_ipv6(aaaa_record)
        except dns.resolver.NoAnswer:
            pass

    def add_mac(self, mac):
        if mac in self.__macs:
            return
        self.__macs.add(mac)

    def add_ipv4(self, ipv4):
        if ipv4 in self.__ipv4s:
            return
        self.__ipv4s.add(ipv4) 
        self.reverse_lookup(ipv4)

    def add_ipv6(self, ipv6):
        if ipv6 in self.__ipv6s:
            return 
        self.__ipv6s.add(ipv6)
        self.reverse_lookup(ipv6)

    def update(self):
        keyring = dns.tsigkeyring.from_text({
            'update-key' : 'z6j0p5oBXiewrxB7NVb8sg=='
        })
        for host in self.__hosts:
            update = dns.update.Update('pond.', keyring=keyring, keyname='update-key')
            for ipv4 in self.__ipv4s:
                update.replace('test.pond.', 300, 'A', str(ipv4))
            for ipv6 in self.__ipv6s:
                update.replace('test.pond.', 300, 'AAAA', str(ipv6))
        response = dns.query.tcp(update, '192.168.2.11') 

class DNSLink(Plugin1):
    def __init__(self):
        self.__flow_links = {}

    def flow_new(self, flow, frame):
        debug('flow start: {}'.format(flow))
        self.__flow_links[flow] = Links()

    def frame_new(self, frame, flow):
        links = self.__flow_links[flow]
        try:
            for mac in flow.get_frames()['eth']['src']['raw']:
                links.add_mac(mac)
        except AttributeError:
            pass
        try:
            for ipv4 in flow.get_frames()['ip']['src']['raw']:
                links.add_ipv4(ipv4)
        except AttributeError:
            pass
        try:
            for ipv6 in flow.get_frames()['ipv6']['src']['raw']:
                links.add_ipv6(ipv6)
        except AttributeError:
            pass

        links.update()

    def flow_end(self, flow):
        links = self.__flow_links[flow]
        warning(links)
        del self.__flow_links[flow]

