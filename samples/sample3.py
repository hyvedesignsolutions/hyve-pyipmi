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

# Message bridging example
# Support the following configuration
# [PyIPMI] <-- LAN (RMCP/RMCP+) --> [BMC] <-- IPMB --> [ME]
class Sample3(PyTest):
    def __init__(self):
        pyopts = PyOpts()
        pyopts.add_options()
        opts = pyopts.parse_options('-H 10.19.84.90 -I lanplus -U admin -P admin')
        self.chnl = 6
        self.target = 0x2c

        super(Sample3, self).__init__(opts)

    def bridge_cmd(self, req):
        # issue_bridging_cmd(chnl, target, req, lun):
        #     chnl (int): IPMI channel number to bridge the message
        #     target (int): I2C slave address of the bridging destination
        #     req (list): [NetFn, CMD, Req_Data]
        #     lun (int): default is 0
        return self.intf.issue_bridging_cmd(self.chnl, self.target, req) 

    def run_commands(self, argv=None):       
        print('Get Device ID:')
        rsp = self.bridge_cmd([6, 1])
        self.print_rsp(rsp)

        print('\nGet SEL Time:')
        rsp = self.bridge_cmd([0xa, 0x48])
        self.print_rsp(rsp)

        print('\nGet Event Receiver:')
        rsp = self.bridge_cmd([4, 1])
        self.print_rsp(rsp)

        print('\nGet Intel ME FW Capabilities:')
        rsp = self.bridge_cmd([0x2e, 0xde, 0x57, 1, 0, 0, 0, 0, 0, 2, 0xff, 0])
        self.print_rsp(rsp)

        print('\nGet Intel ME Factory Presets Signature:')
        rsp = self.bridge_cmd([0x2e, 0xe0, 0x57, 1, 0])
        self.print_rsp(rsp)

        print('\nGet Exception Data:')
        rsp = self.bridge_cmd([0x2e, 0xe6, 0x57, 1, 0, 0])
        self.print_rsp(rsp)

        print('\nGet Sensor Reading:')
        sensor_num = (8, 197)
        for num in sensor_num:
            rsp = self.bridge_cmd([4, 0x2d, num])
            self.print_rsp(rsp)

        print('\nGet SEL Entry:')
        req = [0xa, 0x43, 0, 0, 0, 0, 0, 0xff]
        rsp = self.bridge_cmd(req)
        id1, id2 = rsp[1:3]        
        while not (id1 == 0xff and id2 == 0xff):
            req[4], req[5] = id1, id2
            rsp = self.bridge_cmd(req)
            id1, id2 = rsp[1:3]        
            self.print_rsp(rsp)

if __name__ == '__main__':
    test = Sample3()
    sys.exit(test.run())
