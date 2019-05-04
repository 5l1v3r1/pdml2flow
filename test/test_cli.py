# vim: set fenc=utf8 ts=4 sw=4 et :
from os import path

from .testcase import TestCaseWithTestDir

from pdml2flow.cli import *
from pdml2flow.conf import Conf

class TestCli(TestCaseWithTestDir):

    def test_pdml2flow_new_plugin(self):
        Conf.ARGS = [
            path.join(
                self.test_dir,
                'new-plugin'
            )
        ]
        pdml2flow_new_plugin()
