#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
from inspect import getmembers, ismethod, isfunction, signature

from .testcase import TestCase
from pdml2flow.conf import Plugin2

class TestPlugin(TestCase):
    """Test the current version of the Plugin interface.

    As a rule of thumb: If you need to change these
    Tests you probably want to bump the Plugin interface
    version.
    """

    def test_methods(self):
        self.assertEqual(
            sorted([
                (name, str(signature(method)))
                for name, method in
                getmembers(
                    Plugin2,
                    predicate=ismethod
                )
            ]),
            sorted([
                ('help', '()')
            ])
        )

    def test_functions(self):
        self.assertEqual(
            sorted([
                (name, str(signature(method)))
                for name, method in
                getmembers(
                    Plugin2,
                    predicate=isfunction
                )
            ]),
            sorted([
                ('__init__', '(self, *args)'),
                ('__deinit__', '(self)'),
                ('flow_end', '(self, flow)'),
                ('flow_expired', '(self, flow)'),
                ('flow_new', '(self, flow, frame)'),
                ('frame_new', '(self, frame, flow)'),
            ])
        )

if __name__ == '__main__':
    unittest.main()
