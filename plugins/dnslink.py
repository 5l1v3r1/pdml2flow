# vim: set fenc=utf8 ts=4 sw=4 et :
from pdml2flow.logging import *
from pdml2flow.plugin import *

import socket

class DNSLink(Plugin1):
    def flow_expired(self, flow):
        # mac
        macs = set()
        try:
            macs = macs.union(set(flow.get_frames()['eth']['src']['raw']))
        except AttributeError:
            pass
        # ipv4
        ips = set()
        try:
            ips = ips.union(set(flow.get_frames()['ip']['src']['raw']))
        except AttributeError:
            pass
        # ipv6
        try:
            ips = ips.union(set(flow.get_frames()['ipv6']['src']['raw']))
        except AttributeError:
            pass
        hostnames = set()
        new_ips = ips
        while len(new_ips):
            new_ips_cpy = set(new_ips)
            new_ips = set()
            for ip in new_ips_cpy:
                try:
                    resolve = socket.gethostbyaddr(ip)
                    hostnames.add(resolve[0])
                    # got a new ip?
                    for ip in resolve[2]:
                        if ip not in ips:
                            new_ips.add(ip)
                        ips.add(ip)
                except socket.herror:
                    pass
        warning(ips)

