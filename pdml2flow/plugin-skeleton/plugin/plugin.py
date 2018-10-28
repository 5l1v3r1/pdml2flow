# vim: set fenc=utf8 ts=4 sw=4 et :
from pdml2flow.plugin import Plugin2
from argparse import ArgumentParser

argparser = ArgumentParser('A new plugin')

class Plugin(Plugin2):
    """Version 2 plugin interface."""

    @classmethod
    def help(cls):
        """Return a help string."""
        return argparser.format_help()

    def __init__(self, *args):
        """Called once during startup."""
        argparser.parse_args(args)

    def __deinit__(self):
        """Called once during shutdown."""
        pass

    def flow_new(self, flow, frame):
        """Called every time a new flow is opened."""
        pass

    def flow_expired(self, flow):
        """Called every time a flow expired, before printing the flow."""
        pass

    def flow_end(self, flow):
        """Called every time a flow ends, before printing the flow."""
        pass

    def frame_new(self, frame, flow):
        """Called for every new frame."""
        pass

if __name__ == '__main__':
    print(Plugin.help())
