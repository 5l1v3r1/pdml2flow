# vim: set fenc=utf8 ts=4 sw=4 et :
from abc import ABC, abstractmethod

class Plugin2(ABC):
    """Version 2 plugin interface."""

    @staticmethod
    @abstractmethod
    def help():
        """Return a help string."""
        pass

    @abstractmethod
    def __init__(self, *args):
        """Called once during startup."""
        pass

    @abstractmethod
    def __deinit__(self):
        """Called once during shutdown."""
        pass

    @abstractmethod
    def flow_new(self, flow, frame):
        """Called every time a new flow is opened."""
        pass

    @abstractmethod
    def flow_expired(self, flow):
        """Called every time a flow expired, before printing the flow."""
        pass

    @abstractmethod
    def flow_end(self, flow):
        """Called every time a flow ends, before printing the flow."""
        pass

    @abstractmethod
    def frame_new(self, frame, flow):
        """Called for every new frame."""
        pass

