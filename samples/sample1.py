#!/usr/bin/env python3
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.util import PyTest

# Just overwrite the run_commands() method and you can issue
# IPMI commands like this example
class Sample1(PyTest):
    def __init__(self):
        super(Sample1, self).__init__()

    def run_commands(self, argv=None):
        # issue_raw_cmd(req, lun):
        #     req (list): [NetFn, CMD, Req_Data]
        #     lun (int): default is 0
        print('Get Device ID:')
        rsp = self.intf.issue_raw_cmd([6, 1])
        self.print_rsp(rsp)

        print('\nGet User Name 2:')
        rsp = self.intf.issue_raw_cmd([6, 0x46, 2])
        self.print_rsp(rsp)

        print('\nGet LAN Config 1:')
        rsp = self.intf.issue_raw_cmd([0x0c, 2, 1, 1, 0, 0])
        self.print_rsp(rsp)

if __name__ == '__main__':
    test = Sample1()
    sys.exit(test.run())

