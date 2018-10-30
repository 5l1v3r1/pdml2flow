# vim: set fenc=utf8 ts=4 sw=4 et :

class Plugin2(object): # pragma: no cover
    """Version 2 plugin interface."""

    @staticmethod
    def help():
        """Return a help string."""
        pass

    def __init__(self, *args):
        """Called once during startup."""
        pass

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

