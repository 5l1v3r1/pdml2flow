#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import unittest
import io

from pdml2flow.conf import Conf

class TestConf(unittest.TestCase):
    
    def test_get_real_paths(self):
        p = Conf.get_real_paths([
            'this{}is{}a{}path'.format(*[Conf.FLOW_DEF_NESTCHAR]*3)
        ], Conf.FLOW_DEF_NESTCHAR)
        self.assertEqual(p , [['this', 'is', 'a', 'path', 'raw']])

    def test_set(self):
        pass

if __name__ == '__main__':
    unittest.main()
