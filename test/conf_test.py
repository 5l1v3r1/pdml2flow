#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import io

from .testcase import TestCase
from pdml2flow.conf import Conf

class TestConf(TestCase):

    def test_get_real_paths(self):
        p = Conf.get_real_paths([
            'this{}is{}a{}path'.format(*[Conf.FLOW_DEF_NESTCHAR]*3)
        ], Conf.FLOW_DEF_NESTCHAR)
        self.assertEqual(p , [['this', 'is', 'a', 'path', 'raw']])

    def test_set(self):
        d = Conf.DEBUG
        m = Conf.DATA_MAXLEN
        e = Conf.EXTRACT_SHOW
        newConf = dict()
        newConf['debug'] = not d
        newConf['DATA_MAXLEN'] = m + 1
        Conf.set(newConf)
        self.assertEqual(Conf.DEBUG, not d)
        self.assertEqual(Conf.DATA_MAXLEN, m + 1)
        self.assertEqual(Conf.EXTRACT_SHOW, e)

if __name__ == '__main__':
    unittest.main()
