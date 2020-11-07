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

NETFN_SE = 4

class GetSensorReading(IPMI_Message):
    def __init__(self, sensor_num):
        super(GetSensorReading, self).__init__(NETFN_SE, 0x2d)
        self.req_data = struct.pack('B', sensor_num)

    def unpack(self, rsp):
        cc, ret = rsp[2:]        
        if cc != 0:
            return super(GetSensorReading, self).unpack(rsp)
        if ret is None:
            raise PyMesgExcept('Get Sensor Reading: unexpected empty response data.') 

        rsp_data_len = len(ret)
        if  rsp_data_len >= 2 or rsp_data_len <= 4:
            return super(GetSensorReading, self).unpack(rsp, 'B' * rsp_data_len)
        raise PyMesgExcept('Get Sensor Reading: unexpected response data len = {0}'.format(len(ret)))      

class GetSensorHys(IPMI_Message):
    def __init__(self, sensor_num):
        super(GetSensorHys, self).__init__(NETFN_SE, 0x25)
        self.req_data = struct.pack('BB', sensor_num, 0xff)

    def unpack(self, rsp):
        return super(GetSensorHys, self).unpack(rsp, 'BB')

class GetSensorThres(IPMI_Message):
    def __init__(self, sensor_num):
        super(GetSensorThres, self).__init__(NETFN_SE, 0x27)
        self.req_data = struct.pack('B', sensor_num)

    def unpack(self, rsp):
        return super(GetSensorThres, self).unpack(rsp, 'B' * 7)
