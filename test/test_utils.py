# vim: set fenc=utf8 ts=4 sw=4 et :
from unittest.mock import MagicMock

from .testcase import TestCase

from pdml2flow.utils import *

class TestUtils(TestCase):

    def test_boolify(self):
        self.assertEqual(True, boolify('True'))
        self.assertEqual(False, boolify('False'))
        self.assertRaises(ValueError, boolify, 'Something but not a bool')

    def test_autoconvert(self):
        self.assertEqual(True, autoconvert('True'))
        self.assertEqual(False, autoconvert('False'))
        self.assertEqual(0, autoconvert('0'))
        self.assertEqual(123, autoconvert('123'))
        self.assertEqual(-123, autoconvert('-123'))
        self.assertEqual(0.5, autoconvert('0.5'))
        self.assertEqual(-0.5, autoconvert('-0.5'))
        self.assertEqual('Can not convert', autoconvert('Can not convert'))

    def test_call_plugin(self):
        from pdml2flow.plugin import Plugin2
        plugin = Plugin2()
        plugin.interface_function = MagicMock(return_value = 1)
        self.assertEqual(
            call_plugin(
                plugin,
                'interface_function'
            ),
            1
        )
        try:
            # This does not work in python < 3.6
            plugin.interface_function.assert_called_once()
        except AttributeError:
            pass

    def test_call_plugin_function_not_implemented(self):
        from pdml2flow.plugin import Plugin2
        plugin = Plugin2()
        self.assertEqual(
            call_plugin(
                plugin,
                'interface_function'
            ),
            None
        )
