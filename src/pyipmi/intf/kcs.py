#
# Copyright (c) 2021, Hyve Design Solutions Corporation.
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
import ctypes, fcntl, os, select, struct, sys
from . ioctl import IOR, IOWR
from . _crypto import checksum
from . import Intf
from .. mesg import IPMI_Raw
from .. mesg.ipmi_app import IPMI_SendMsg
from .. util.exception import PyIntfExcept, PyIntfSeqExcept

class ipmi_addr(ctypes.Structure):
    _fields_ = [
            ('addr_type', ctypes.c_int),
            ('channel', ctypes.c_short),
            ('data', ctypes.c_char_p),
    ]

class ipmi_si_addr(ctypes.Structure):
    _fields_ = [
            ('addr_type', ctypes.c_int),
            ('channel', ctypes.c_short),
            ('lun', ctypes.c_ubyte),
    ]

class ipmi_ipmb_addr(ctypes.Structure):
    _fields_ = [
            ('addr_type', ctypes.c_int),
            ('channel', ctypes.c_short),
            ('slave_addr', ctypes.c_ubyte),
            ('lun', ctypes.c_ubyte),
    ]

class ipmi_msg(ctypes.Structure):
    _fields_ = [
            ('netfn', ctypes.c_ubyte),
            ('cmd', ctypes.c_ubyte),
            ('data_len', ctypes.c_ushort),
            ('data', ctypes.c_char_p),
    ]

class ipmi_req(ctypes.Structure):
    _fields_ = [
            ('addr', ctypes.c_void_p),
            ('addr_len', ctypes.c_uint),
            ('msgid', ctypes.c_long),
            ('msg', ipmi_msg),
    ]

class ipmi_recv(ctypes.Structure):
    _fields_ = [
            ('recv_type', ctypes.c_int),
            ('addr', ctypes.c_void_p),
            ('addr_len', ctypes.c_uint),
            ('msgid', ctypes.c_long),
            ('msg', ipmi_msg),
    ]

class KCS(Intf):
    def __init__(self, opts):
        self.fd = None
        self.msgid = 1
        self.my_addr = opts.get('bmc_addr', 0x20)
        self.dev_num = opts.get('dev_num', 0)

    def __del__(self):
        try:
            if self.fd is not None:
                os.close(self.fd)
        except:
            pass

    def open(self):
        IPMICTL_SET_GETS_EVENTS_CMD = IOR('i', 16, ctypes.c_int)
        IPMICTL_SET_MY_ADDRESS_CMD = IOR('i', 17, ctypes.c_uint)

        DEV_STRS = ('/dev/ipmi', '/dev/ipmi/', '/dev/ipmidev/')
        ipmi_devs = ['{0}{1}'.format(dev, self.dev_num) for dev in DEV_STRS]

        for dev in ipmi_devs:
            try:
                self.fd = os.open(dev, os.O_RDWR)
                break
            except:
                continue

        if self.fd is None:
            # Couldn't open the IPMI driver
            print('Could not open device at ' + ' or '.join(ipmi_devs) + ': ', end='')
            print('No such file or directory')
            return -1

        receive_events = ctypes.c_int(1)
        try:
            fcntl.ioctl(self.fd, IPMICTL_SET_GETS_EVENTS_CMD, receive_events)
        except:
            print('Could not enable event receiver')
            return -1

        if self.my_addr != 0:
            my_addr = ctypes.c_uint(self.my_addr)
            try:
                fcntl.ioctl(self.fd, IPMICTL_SET_MY_ADDRESS_CMD, my_addr)
            except:                
                print('Could not set IPMB address')
                return -1

        return 0

    def close(self):
        pass

    def sendrecv(self, req):
        IPMICTL_SEND_COMMAND = IOR('i', 13, ctypes.sizeof(ipmi_req))
        IPMICTL_RECEIVE_MSG_TRUNC = IOWR('i', 11, ctypes.sizeof(ipmi_recv))

        # send command request
        fcntl.ioctl(self.fd, IPMICTL_SEND_COMMAND, req)

        # wait for response
        while True:
            r, _, x = select.select([self.fd], [], [], 3)
            if x: raise PyIntfExcept('select() exception occurred.')
            if r: 
                # receive response
                IPMI_MAX_ADDR_SIZE = 0x20
                IPMI_BUF_SIZE = 1024

                addr = ipmi_addr(0, 0, ctypes.addressof(ctypes.create_string_buffer(IPMI_MAX_ADDR_SIZE)))
                addr_len = ctypes.sizeof(addr) + IPMI_MAX_ADDR_SIZE - ctypes.sizeof(ctypes.c_char_p)
                data = ctypes.create_string_buffer(IPMI_BUF_SIZE)
                recv = ipmi_recv(0, ctypes.addressof(addr), addr_len, 0, 
                                 ipmi_msg(0, 0, IPMI_BUF_SIZE, ctypes.addressof(data)))

                # receive command response
                fcntl.ioctl(self.fd, IPMICTL_RECEIVE_MSG_TRUNC, recv)

                # check message ID
                if recv.msgid != req.msgid:
                    continue

                # compose the response message
                cc = data.raw[0]
                if recv.msg.data_len > 0:
                    rsp_data = data.raw[1:recv.msg.data_len]
                    rsp = [recv.msg.netfn, recv.msg.cmd, cc, rsp_data]
                else:
                    rsp = [recv.msg.netfn, recv.msg.cmd, cc]

                return rsp

            else:
                # select() times out
                raise PyIntfExcept('Times out.  Host has no response.')

    def gen_msg(self, cmd, bridging=False, dest=0, target=0):        
        IPMI_SYSTEM_INTERFACE_ADDR_TYPE = 0x0c
        IPMI_IPMB_ADDR_TYPE	= 0x01
        IPMI_BMC_CHANNEL = 0x0f

        if not bridging:
            bmc_addr = ipmi_si_addr(IPMI_SYSTEM_INTERFACE_ADDR_TYPE, IPMI_BMC_CHANNEL, cmd.lun)
        else:
            bmc_addr = ipmi_ipmb_addr(IPMI_IPMB_ADDR_TYPE, dest, target, cmd.lun)

        if cmd.req_data:
            req_len = len(cmd.req_data)
            req_data = cmd.req_data
        else:
            req_len = 0
            req_data = bytes([])

        msg = ipmi_msg(cmd.netfn, cmd.cmd, req_len, req_data)
        req = ipmi_req(ctypes.addressof(bmc_addr), ctypes.sizeof(bmc_addr), self.msgid, msg)
        self.msgid += 1
        if self.msgid == 0xffff:    self.msgid = 1

        return req

    def issue_bridging_cmd(self, dest, target, req, lun=0):
        cmd = IPMI_Raw(req, lun)
        msg = self.gen_msg(cmd, True, dest, target)
        rsp = self.sendrecv(msg)

        return cmd.unpack(rsp)

    def issue_cmd(self, cmd_cls, *args):
        cmd = cmd_cls(*args)
        msg = self.gen_msg(cmd)
        rsp = self.sendrecv(msg)

        return cmd.unpack(rsp)

    def issue_raw_cmd(self, req, lun=0):        
        return self.issue_cmd(IPMI_Raw, req, lun)


