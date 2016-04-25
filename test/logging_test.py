#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import unittest
import io

from pdml2flow.logging import *
from pdml2flow.conf import Conf

class TestLogging(unittest.TestCase):

    def test_debug(self):
        out = io.StringIO()

        Conf.DEBUG = False
        debug('test', file=out)
        self.assertEqual(out.getvalue(), '')

        Conf.DEBUG = True
        debug('test', file=out)
        self.assertEqual(out.getvalue(), '[Debug: 0]  test\n')

        out.close()

    def test_warning(self):
        out = io.StringIO()

        warning('test', file=out)
        self.assertEqual(out.getvalue(), '[Warning: 0]  test\n')

        out.close()

if __name__ == '__main__':
    unittest.main()
