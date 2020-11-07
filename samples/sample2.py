#!/usr/bin/env python3
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.util import PyTest
from pyipmi.util.config import PyOpts

# Same as sample1, with simple checks on the response data
# and overwrite some values of the user config
class Sample2(PyTest):
    def __init__(self):
        pyopts = PyOpts()
        pyopts.add_options()
        opts = pyopts.parse_options('-U hyve -P hyve123')

        super(Sample2, self).__init__(opts)

    def run_commands(self, argv=None):
        req = ([[6, 1],                     # Get Device ID
                [6, 0x46, 2],               # Get User Name 2
                [0x0c, 2, 1, 1, 0, 0]])     # Get LAN Config 1
            
        rsp = ([[0, 0x22, 1, 1, 2, 2, 0x9f, 0x55, 0xda, 0, 1, 0, 0x59, 1, 0, 0],
                [0, 0x72, 0x6f, 0x6f, 0x74, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0x11, 0x15]])

        # run the commands
        count_p = 0
        count_f = 0
        for i in range(len(req)):
            rsp_one = self.intf.issue_raw_cmd(req[i])
            if rsp_one == rsp[i]:
                print('test case {0}: PASSED!'.format(i + 1))
                count_p += 1
            else:            
                print('test case {0}: FAILED!'.format(i + 1))
                count_f += 1

        # output the results            
        print('Total {0} cases executed: PASSED {1}, FAILED {2}.'
                .format(count_p + count_f, count_p, count_f))

if __name__ == '__main__':
    test = Sample2()
    sys.exit(test.run())

