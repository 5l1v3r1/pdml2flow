# vim: set fenc=utf8 ts=4 sw=4 et :
import os
import io
import json
import unittest
from shlex import split

from .testcase import TestCase

from pdml2flow.conf import Conf
import pdml2flow

TEST_DIR_PDML2FLOW="test/pdml2flow_tests/"
TEST_DIR_PDML2FRAME="test/pdml2frame_tests/"

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

def get_test(run, directory, test):
    def system_test(self):
        if os.path.isfile('{}/{}/skip'.format(directory, test)):
            self.skipTest('Skipfile found')
        with open('{}/{}/stdin'.format(directory, test)) as f_stdin, \
            io.StringIO() as f_stdout, \
            io.StringIO() as f_stderr:

            # wire up io
            Conf.IN = f_stdin
            Conf.OUT = f_stdout
            Conf.OUT_DEBUG = f_stderr
            Conf.OUT_WARNING = f_stderr
            Conf.OUT_ERROR = f_stderr

            try:
                # try to load arguments
                with open('{}/{}/args'.format(directory, test)) as f:
                    Conf.ARGS = split(f.read())
            except FileNotFoundError:
                Conf.ARGS = ''

            # run
            run()

            # compare stdout
            stdout_raw = f_stdout.getvalue()
            stderr_raw = f_stderr.getvalue()

            with open('{}/{}/stdout'.format(directory, test)) as f:
                expected_raw = f.read()

            # Try parsing as json, and compare objects
            run_objs = self.read_json(stdout_raw)
            expected_objs = self.read_json(expected_raw)
            self.assertEqual(
                len(run_objs),
                len(expected_objs)
            )
            for e in expected_objs:
                self.assertIn(
                    e,
                    expected_objs
                )
            for o in run_objs:
                self.assertIn(
                    o,
                    expected_objs
                )

            # if no object loaded: do a raw comparison, line by line
            if len(run_objs) == 0 or len(expected_objs) == 0:
                self.assertEqual(
                    sorted(
                        stdout_raw.splitlines()
                    ),
                    sorted(
                         expected_raw.splitlines()
                    )
                )

            try:
                # try compare stderr
                with open('{}/{}/stderr'.format(directory, test)) as f:
                    expected_raw = f.read()
                self.assertEqual(
                    expected_raw,
                    stderr_raw
                )
            except FileNotFoundError:
                self.assertEqual(
                    '',
                    stderr_raw
                )

    return system_test

def add_tests(run, directory):
    for test in os.listdir(directory):
        # append test
        setattr(
            TestSystem,
            'test_{}_{}'.format(run.__name__, test),
            get_test(run, directory, test)
        )

# Add tests
add_tests(pdml2flow.pdml2flow, TEST_DIR_PDML2FLOW)
add_tests(pdml2flow.pdml2frame, TEST_DIR_PDML2FRAME)
