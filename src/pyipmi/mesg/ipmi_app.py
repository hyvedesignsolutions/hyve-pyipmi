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
from .. util.exception import PyMesgExcept, PyMesgCCExcept

NETFN_APP = 6

class GetDeviceID(IPMI_Message):
    def __init__(self):
        super(GetDeviceID, self).__init__(NETFN_APP, 0x01)
        self.req_data = None

    def unpack(self, rsp):
        cc, ret = rsp[2:]        
        if cc != 0:
            return super(GetDeviceID, self).unpack(rsp)
        if ret is None:
            raise PyMesgExcept('Get Device ID: unexpected empty response data.') 

        if len(ret) == 11:
            return super(GetDeviceID, self).unpack(rsp, '<BBBBBB3sH')
        elif len(ret) == 15:
            return super(GetDeviceID, self).unpack(rsp, '<BBBBBB3sH4s')
        raise PyMesgExcept('Get Device ID: unexpected response data len = {0}'.format(len(ret)))      

class ColdReset(IPMI_Message):
    def __init__(self):
        super(ColdReset, self).__init__(NETFN_APP, 0x02)
        self.req_data = None

    def unpack(self, rsp):
        return super(ColdReset, self).unpack(rsp)

class GetSelfTest(IPMI_Message):
    def __init__(self):
        super(GetSelfTest, self).__init__(NETFN_APP, 0x04)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSelfTest, self).unpack(rsp, 'BB')

class GetDeviceGUID(IPMI_Message):
    def __init__(self):
        super(GetDeviceGUID, self).__init__(NETFN_APP, 0x08)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetDeviceGUID, self).unpack(rsp, '16s')

class ResetWatchdog(IPMI_Message):
    def __init__(self):
        super(ResetWatchdog, self).__init__(NETFN_APP, 0x22)
        self.req_data = None

    def unpack(self, rsp):
        try:
            super(ResetWatchdog, self).unpack(rsp)
            return 0
        except PyMesgCCExcept:
            return rsp[2]   # CC

class SetWatchdog(IPMI_Message):
    def __init__(self, use, act, pre_timeout, exp, init_count):
        super(SetWatchdog, self).__init__(NETFN_APP, 0x24)
        self.req_data = struct.pack('<BBBBH', use, act, pre_timeout, exp, init_count)

    def unpack(self, rsp):
        return super(SetWatchdog, self).unpack(rsp)

class GetWatchdog(IPMI_Message):
    def __init__(self):
        super(GetWatchdog, self).__init__(NETFN_APP, 0x25)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetWatchdog, self).unpack(rsp, '<BBBBHH')

class SetEnables(IPMI_Message):
    def __init__(self, enables):
        super(SetEnables, self).__init__(NETFN_APP, 0x2E)
        self.req_data = struct.pack('B', enables)

    def unpack(self, rsp):
        return super(SetEnables, self).unpack(rsp)

class GetEnables(IPMI_Message):
    def __init__(self):
        super(GetEnables, self).__init__(NETFN_APP, 0x2F)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetEnables, self).unpack(rsp, 'B')

class IPMI_SendMsg(IPMI_Message):
    def __init__(self, dest, inner):
        super(IPMI_SendMsg, self).__init__(NETFN_APP, 0x34)
        self.req_data = struct.pack('B', 0x40 | dest) + inner

    def unpack(self, rsp):
        # rsp = (netfn, cmd, cc, rsp_data)
        return super(IPMI_SendMsg, self).unpack(rsp)

class GetChnlAuthCap(IPMI_Message):
    def __init__(self, priv, chnl=0x0e):
        super(GetChnlAuthCap, self).__init__(NETFN_APP, 0x38)
        self.req_data = struct.pack('BB', 0x80 | (0x0f & chnl), 
                                    priv & 0x0f)

    def unpack(self, rsp):
        return super(GetChnlAuthCap, self).unpack(rsp, 'BBBB3sB')

class GetSessChallenge(IPMI_Message):
    def __init__(self, auth, user=None):
        super(GetSessChallenge, self).__init__(NETFN_APP, 0x39)
        if user is None:
            self.req_data = struct.pack('B16s', auth, 0)
        else:
            self.req_data = struct.pack('B16s', auth, user)

    def unpack(self, rsp):
        return super(GetSessChallenge, self).unpack(rsp, '4s16s')

class ActivateSess(IPMI_Message):
    def __init__(self, auth, priv, chg_data, ioseq_num):
        super(ActivateSess, self).__init__(NETFN_APP, 0x3A)
        self.req_data = struct.pack('<BB16sL', auth, priv, chg_data, ioseq_num)

    def unpack(self, rsp):
        return super(ActivateSess, self).unpack(rsp, '<B4sLB')

class SetSessPriv(IPMI_Message):
    def __init__(self, priv):
        super(SetSessPriv, self).__init__(NETFN_APP, 0x3B)
        self.req_data = struct.pack('B', priv & 0x0f)

    def unpack(self, rsp):
        return super(SetSessPriv, self).unpack(rsp, 'B')

class CloseSess(IPMI_Message):
    def __init__(self, sid):
        super(CloseSess, self).__init__(NETFN_APP, 0x3C)
        self.req_data = struct.pack('4s', sid)

    def unpack(self, rsp):
        return super(CloseSess, self).unpack(rsp)

class SetUserAccess(IPMI_Message):
    def __init__(self, chnl, user, priv):
        super(SetUserAccess, self).__init__(NETFN_APP, 0x43)
        self.req_data = struct.pack('BBB', chnl, user & 0x3f, priv & 0x0f)

    def unpack(self, rsp):
        return super(SetUserAccess, self).unpack(rsp)

class GetUserAccess(IPMI_Message):
    def __init__(self, chnl, user):
        super(GetUserAccess, self).__init__(NETFN_APP, 0x44)
        self.req_data = struct.pack('BB', chnl & 0x0f, user & 0x3f)

    def unpack(self, rsp):
        return super(GetUserAccess, self).unpack(rsp, 'BBBB')

class SetUserName(IPMI_Message):
    def __init__(self, user, name):
        super(SetUserName, self).__init__(NETFN_APP, 0x45)
        self.req_data = struct.pack('B16s', user & 0x3f, name)

    def unpack(self, rsp):
        return super(SetUserName, self).unpack(rsp)

class GetUserName(IPMI_Message):
    def __init__(self, user):
        super(GetUserName, self).__init__(NETFN_APP, 0x46)
        self.req_data = struct.pack('B', user & 0x3f)

    def unpack(self, rsp):
        return super(GetUserName, self).unpack(rsp, '16s')

class SetUserPass(IPMI_Message):
    def __init__(self, user, op, passwd):
        super(SetUserPass, self).__init__(NETFN_APP, 0x47)
        fmt = 'BB20s' if user & 0x80 else 'BB16s'
        self.req_data = struct.pack(fmt, user & 0xbf, op & 3, passwd)

    def unpack(self, rsp):
        try:
            super(SetUserPass, self).unpack(rsp)
        except PyMesgCCExcept as e:
            if e.cc == 0x80:
                print('Password test failed (CC=80h).')
            elif e.cc == 0x81:
                print('Password test failed (CC=81h).')
            else:
                print(e)
        finally:
            return rsp[2]   # CC

class SetSysInfo(IPMI_Message):
    def __init__(self, param, data):
        super(SetSysInfo, self).__init__(NETFN_APP, 0x58)
        self.req_data = struct.pack('B', param) + data

    def unpack(self, rsp):
        try:
            super(SetSysInfo, self).unpack(rsp)
            return 0
        except PyMesgCCExcept:
            return rsp[2]   # CC

class GetSysInfo(IPMI_Message):
    def __init__(self, param, sel, blk):
        super(GetSysInfo, self).__init__(NETFN_APP, 0x59)
        self.req_data = struct.pack('BBBB', 0, param, sel, blk)

    def unpack(self, rsp):
        try:
            super(GetSysInfo, self).unpack(rsp)
            ret = rsp[3]
            return ret[1:]    
        except PyMesgCCExcept:
            return None
