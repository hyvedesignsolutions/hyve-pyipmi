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
import struct
from . import IPMI_Message
from .. util.exception import PyMesgExcept

NETFN_CHASSIS = 0

class GetChsStat(IPMI_Message):
    def __init__(self):
        super(GetChsStat, self).__init__(NETFN_CHASSIS, 0x01)
        self.req_data = None

    def unpack(self, rsp):
        cc, ret = rsp[2:]        
        if cc != 0:
            return super(GetChsStat, self).unpack(rsp)
        if ret is None:
            raise PyMesgExcept('Get Chassis Status: unexpected empty response data.') 

        if len(ret) == 3:
            return super(GetChsStat, self).unpack(rsp, 'BBB')
        elif len(ret) == 4:
            return super(GetChsStat, self).unpack(rsp, 'BBBB')
        raise PyMesgExcept('Get Chassis Status: unexpected response data len = {0}'.format(len(ret)))      

class ChsCtrl(IPMI_Message):
    def __init__(self, ctrl):
        super(ChsCtrl, self).__init__(NETFN_CHASSIS, 0x02)
        self.req_data = struct.pack('B', ctrl)

    def unpack(self, rsp):
        return super(ChsCtrl, self).unpack(rsp)

class PowerRestore(IPMI_Message):
    def __init__(self, ctrl):
        super(PowerRestore, self).__init__(NETFN_CHASSIS, 0x06)
        self.req_data = struct.pack('B', ctrl)

    def unpack(self, rsp):
        return super(PowerRestore, self).unpack(rsp, 'B')

class GetSysRestartCause(IPMI_Message):
    def __init__(self):
        super(GetSysRestartCause, self).__init__(NETFN_CHASSIS, 0x07)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSysRestartCause, self).unpack(rsp, 'BB')

class GetPoh(IPMI_Message):
    def __init__(self):
        super(GetPoh, self).__init__(NETFN_CHASSIS, 0x0F)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetPoh, self).unpack(rsp, '<BL')

class ChsIdentify(IPMI_Message):
    def __init__(self, interval, force):
        super(ChsIdentify, self).__init__(NETFN_CHASSIS, 0x04)
        self.req_data = struct.pack('BB', interval, force)

    def unpack(self, rsp):
        return super(ChsIdentify, self).unpack(rsp)

class SetBootOpts(IPMI_Message):
    def __init__(self, param, data):
        super(SetBootOpts, self).__init__(NETFN_CHASSIS, 0x08)
        self.req_data = struct.pack('B', param) + data

    def unpack(self, rsp):
        return super(SetBootOpts, self).unpack(rsp)
