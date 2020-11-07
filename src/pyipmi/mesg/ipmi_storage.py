import struct
from . import IPMI_Message
from .. util.exception import PyMesgExcept

NETFN_STORAGE = 0x0a

class GetSDRRepoInfo(IPMI_Message):
    def __init__(self):
        super(GetSDRRepoInfo, self).__init__(NETFN_STORAGE, 0x20)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSDRRepoInfo, self).unpack(rsp, '<BHHLLB')

class GetSDRRepoAllocInfo(IPMI_Message):
    def __init__(self):
        super(GetSDRRepoAllocInfo, self).__init__(NETFN_STORAGE, 0x21)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSDRRepoAllocInfo, self).unpack(rsp, '<HHHHB')

class RevSDR(IPMI_Message):
    def __init__(self):
        super(RevSDR, self).__init__(NETFN_STORAGE, 0x22)
        self.req_data = None

    def unpack(self, rsp):
        return super(RevSDR, self).unpack(rsp, '<2s')

class GetSDR(IPMI_Message):
    def __init__(self, rev_id, rec_id, offset, bytes_to_read):
        super(GetSDR, self).__init__(NETFN_STORAGE, 0x23)
        self.req_data = struct.pack('<2s2sBB', rev_id, rec_id, offset, bytes_to_read)

    def unpack(self, rsp):
        return super(GetSDR, self).unpack(rsp)

class GetSELInfo(IPMI_Message):
    def __init__(self):
        super(GetSELInfo, self).__init__(NETFN_STORAGE, 0x40)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSELInfo, self).unpack(rsp, '<BHHLLB')

class GetSELAllocInfo(IPMI_Message):
    def __init__(self):
        super(GetSELAllocInfo, self).__init__(NETFN_STORAGE, 0x41)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSELAllocInfo, self).unpack(rsp, '<HHHHB')

class RevSEL(IPMI_Message):
    def __init__(self):
        super(RevSEL, self).__init__(NETFN_STORAGE, 0x42)
        self.req_data = None

    def unpack(self, rsp):
        return super(RevSEL, self).unpack(rsp, '<2s')

class GetSELEntry(IPMI_Message):
    def __init__(self, rec_id):
        super(GetSELEntry, self).__init__(NETFN_STORAGE, 0x43)
        self.req_data = struct.pack('<2s2sBB', b'\0', rec_id, 0, 0xff)

    def unpack(self, rsp):
        return super(GetSELEntry, self).unpack(rsp, '<2sHBLHBBBBBBB')

class ClearSEL(IPMI_Message):
    def __init__(self, rev, stat):
        super(ClearSEL, self).__init__(NETFN_STORAGE, 0x47)
        self.req_data = struct.pack('2sBBBB', rev, 0x43, 0x4c, 0x52, stat)

    def unpack(self, rsp):
        return super(ClearSEL, self).unpack(rsp, 'B')

class GetSELTime(IPMI_Message):
    def __init__(self):
        super(GetSELTime, self).__init__(NETFN_STORAGE, 0x48)
        self.req_data = None

    def unpack(self, rsp):
        return super(GetSELTime, self).unpack(rsp, '<L')

