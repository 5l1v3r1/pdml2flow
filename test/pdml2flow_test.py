#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import os
import io
import json
from .testcase import TestCase

from pdml2flow.conf import Conf
import pdml2flow

TEST_DIR="test/data/"

class TestPdml2Flow(TestCase):

    def test_pdml2flow(self):
        for test in os.listdir(TEST_DIR):
            with self.subTest(test=test):
                with    open('{}/{}/stdin'.format(TEST_DIR, test)) as f_stdin, \
                        io.StringIO() as f_stdout, \
                        io.StringIO() as f_stderr:
                    # set stdin & stdout
                    Conf.IN = f_stdin
                    Conf.OUT = f_stdout
                    try:
                        # try to load arguments
                        with open('{}/{}/args'.format(TEST_DIR, test)) as f:
                            Conf.ARGS = f.read()
                    except FileNotFoundError:
                        Conf.ARGS = ''
                    # run
                    pdml2flow.pdml2flow()
                    # compare stdout
                    with open('{}/{}/stdout'.format(TEST_DIR, test)) as f:
                        expected = json.loads(f.read())
                    self.assertEqual(expected, json.loads(f_stdout.getvalue()))
                    try:
                        # try compare stderr
                        with open('{}/{}/stderr'.format(TEST_DIR, test)) as f:
                            expected = c_stdout.read()
                        self.assertEqual(expected, f_stderr.getvalue())
                    except FileNotFoundError:
                        pass

if __name__ == '__main__':
    unittest.main()
