#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import os
import io
import json
from .testcase import TestCase

from pdml2flow.conf import Conf
import pdml2flow

TEST_DIR_PDML2FLOW="test/pdml2flow_tests/"
TEST_DIR_PDML2JSON="test/pdml2json_tests/"

class TestSystem(TestCase):

    def read_json(self, f):
        objs = []
        data = ''
        for line in f:
            data += line
            try:
                objs.append(json.loads(data))
                data = ''
            except ValueError:
                # Not yet a complete JSON value
                pass
        return objs

    def system_test(self, run, directory):
        for test in os.listdir(directory):
            with self.subTest(test=test):
                with    open('{}/{}/stdin'.format(directory, test)) as f_stdin, \
                        io.StringIO() as f_stdout, \
                        io.StringIO() as f_stderr:
                    # set stdin & stdout
                    Conf.IN = f_stdin
                    Conf.OUT = f_stdout
                    try:
                        # try to load arguments
                        with open('{}/{}/args'.format(directory, test)) as f:
                            Conf.ARGS = f.read().split()
                        print(Conf.ARGS)
                    except FileNotFoundError:
                        Conf.ARGS = ''
                    # run
                    run()
                    # compare stdout
                    objs = self.read_json(f_stdout.getvalue())
                    with open('{}/{}/stdout'.format(directory, test)) as f:
                        expected = self.read_json(f.read())
                    for e in expected:
                        self.assertIn(e, objs)
                    for o in objs:
                        self.assertIn(o, expected)
                    try:
                        # try compare stderr
                        with open('{}/{}/stderr'.format(directory, test)) as f:
                            expected = c_stdout.read()
                        self.assertEqual(expected, f_stderr.getvalue())
                    except FileNotFoundError:
                        pass

    def test_pdml2flow(self):
        self.system_test(pdml2flow.pdml2flow, TEST_DIR_PDML2FLOW)

    def test_pdml2json(self):
        self.system_test(pdml2flow.pdml2json, TEST_DIR_PDML2JSON)
if __name__ == '__main__':
    unittest.main()
