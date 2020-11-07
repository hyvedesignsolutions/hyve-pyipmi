#!/usr/bin/env python3
#
# Copyright (c) 2020, Hyve Design Solutions Corporation.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are 
# met:
#
# 1. Redistributions of source code must retain the above copyright 
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of Hyve Design Solutions Corporation nor the names 
#    of its contributors may be used to endorse or promote products 
#    derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY HYVE DESIGN SOLUTIONS CORPORATION AND 
# CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, 
# BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND 
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL 
# HYVE DESIGN SOLUTIONS CORPORATION OR CONTRIBUTORS BE LIABLE FOR ANY 
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL 
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS 
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) 
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, 
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING 
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE 
# POSSIBILITY OF SUCH DAMAGE.
#
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

