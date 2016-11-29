# vim: set fenc=utf8 ts=4 sw=4 et :
from pdml2flow.logging import *
from pdml2flow.plugin import *

class MyPlugin(Plugin1):
    def flow_expired(self, flow):
        macs = []
        try:
            macs += flow.get_frames()['eth']['src']['raw']
        except AttributeError:
            pass
        ips = []
        try:
            ips += flow.get_frames()['ip']['src']['raw']
        except AttributeError:
            pass
        try:
            ips += flow.get_frames()['ipv6']['src']['raw']
        except AttributeError:
            pass
        warning(ips)
        warning(macs)

