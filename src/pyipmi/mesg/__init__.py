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
from .. util.exception import PyMesgExcept, PyMesgCCExcept
import struct

all = [
    'IPMI_Message',
    'IPMI_Raw',
    'ipmi_app',
    'ipmi_chassis',
    'ipmi_se',
    'ipmi_storage',
    'ipmi_transport',
]

class IPMI_Message:
    def __init__(self, netfn, cmd, req_data=None, lun=0):
        self.netfn = netfn
        self.cmd = cmd
        self.req_data = req_data
        self.lun = lun
        self.payload_type = 0

    @staticmethod
    def dump_tuple(t1):
        if type(t1) is not tuple:
            return ''

        data_str = ', '.join(('{0:x}'.format(i) if type(i) is not bytes  
            else (' '.join('{0:02x}'.format(j) for j in i)) for i in t1))

        return '(' + data_str + ')'
    
    def unpack(self, rsp, fmt=None):
        # rsp = (netfn, cmd, cc, rsp_data)
        if rsp[0] != self.netfn + 1:
            raise PyMesgExcept('Invalid NetFn {0:02x}h in the response.'
                               .format(rsp[0]))

        if rsp[1] != self.cmd:
            raise PyMesgExcept('Invalid CMD {0:02x}h in the response.'
                               .format(rsp[1]))

        cc, rsp_data = rsp[2:] 
        if isinstance(self, IPMI_Raw):
            list1 = [cc]
            if rsp_data is not None:
                list1 += list(rsp_data)
            return list1

        if cc != 0:
            raise PyMesgCCExcept(self.netfn, self.cmd, cc)

        if fmt is None: return rsp_data     # do not unpack the response

        if rsp_data is None:    # no response data, but fmt is not None
            raise PyMesgExcept('Unexpected empty response data: NetFn={0:02X}h, CMD={1:02X}h.  Expected {2}.'
                               .format(self.netfn, self.cmd, struct.calcsize(fmt)))

        if struct.calcsize(fmt) != len(rsp_data):
            raise PyMesgExcept('Invalid response data length: NetFn={0:02X}h, CMD={1:02X}h.  Expected {2}, but returned {3}.'
                               .format(self.netfn, self.cmd, struct.calcsize(fmt), len(rsp_data)))

        return struct.unpack(fmt, rsp_data) # has response data

class IPMI_Raw(IPMI_Message):
    def __init__(self, req, lun=0):
        # [netfn, cmd, req_data]
        req_data = None
        if len(req) > 2:
            req_data = bytes(req[2:])            
        super(IPMI_Raw, self).__init__(req[0], req[1], req_data, lun)

    def unpack(self, rsp):
        # rsp = (netfn, cmd, cc, rsp_data)
        return super(IPMI_Raw, self).unpack(rsp)
