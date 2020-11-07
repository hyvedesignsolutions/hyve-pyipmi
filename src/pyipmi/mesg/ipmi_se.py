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
