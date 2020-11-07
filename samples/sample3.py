#!/usr/bin/env python3
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
