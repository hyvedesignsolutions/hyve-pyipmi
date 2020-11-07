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
from .. util.exception import PyMesgCCExcept

NETFN_TRANS = 0xc

class SetLanConfig(IPMI_Message):
    def __init__(self, chnl, param, data):
        super(SetLanConfig, self).__init__(NETFN_TRANS, 0x01)
        self.req_data = struct.pack('BB', chnl, param) + data

    def unpack(self, rsp):
        return super(SetLanConfig, self).unpack(rsp)

class GetLanConfig(IPMI_Message):
    def __init__(self, chnl, param, s_sel, b_sel):
        super(GetLanConfig, self).__init__(NETFN_TRANS, 0x02)
        self.req_data = struct.pack('BBBB', chnl, param, s_sel, b_sel)

    def unpack(self, rsp):
        try:
            super(GetLanConfig, self).unpack(rsp)
            ret = rsp[3]
            return ret[1:]    
        except PyMesgCCExcept:
            return None
