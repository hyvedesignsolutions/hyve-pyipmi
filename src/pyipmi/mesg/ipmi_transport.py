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
