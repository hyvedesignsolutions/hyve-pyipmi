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
from . _crypto import *
from .. util.exception import PyIntfExcept, PyIntfSeqExcept

class RMCP_Message:
    SOFT_ID = 0x81
    BMC_ADDR = 0x20

    def __init__(self, msg_cls=6, seq_num=0xff):
        self.msg_cls = msg_cls
        self.rmcp_seq_num = seq_num

    def pack(self):
        msg = struct.pack('BBBB', 6, 0, self.rmcp_seq_num, self.msg_cls)
        return msg

    def unpack(self, rsp):
        if rsp[:4] != struct.pack('BBBB', 6, 0, 0xff, self.msg_cls):
            raise PyIntfExcept('Invalid RMCP package.')

        return rsp[4:]

class ASF_Ping(RMCP_Message):
    seq_num = 1
    def __init__(self):
        # Generate the RMCP header
        self.seq_num = ASF_Ping.seq_num        
        super(ASF_Ping, self).__init__(seq_num=self.seq_num)
        
        seq_num = self.seq_num
        seq_num += 1
        if seq_num == 0xff: seq_num = 0
        RMCP_Message.seq_num = seq_num

    def pack(self):
        msg = super(ASF_Ping, self).pack()
        msg_ping = struct.pack('>LBBBB', 4542, 0x80, self.seq_num, 0, 0)
        msg += msg_ping

        return msg

    def unpack(self, rsp):
        pass

class IPMI15_Message(RMCP_Message):
    seq_num = 1

    def __init__(self, auth=AUTH_NONE, sseq=0, sid=b'\0', pwd=''):
        # Get this seq_num
        if isinstance(self, IPMI15_Message):
            self.seq_num = IPMI15_Message.seq_num
            IPMI15_Message.seq_num += 1
            if IPMI15_Message.seq_num == 64: IPMI15_Message.seq_num = 0

        self.auth = auth
        self.sseq = sseq
        self.sid = sid
        self.pwd = pwd
        self.rs_addr = RMCP_Message.BMC_ADDR
        
        # Generate the RMCP header
        super(IPMI15_Message, self).__init__(msg_cls=7)

    def _pack_lan_payload(self, req, rs_addr=RMCP_Message.BMC_ADDR):
        # rsAddr (SA or SW ID) | NetFn (even) / rsLUN | checksum
        p1 = struct.pack('<BB', rs_addr, (req.netfn << 2) + req.lun)                     
        p1 += checksum(p1)

        # rqAddr (SA or SW ID)  | rqSeq / rqLUN | cmd | req data (0..N) | checksum
        p2 = struct.pack('<BBB', RMCP_Message.SOFT_ID, self.seq_num << 2, req.cmd)
        if req.req_data != None: p2 += req.req_data
        p2 += checksum(p2)

        return p1 + p2

    def _pack_lan_header(self, payload):
        payload_len = len(payload)
        if self.auth == AUTH_NONE:
            # Auth Type (1) | Seq # (4) | Sess ID (4) | Payload Len (1)
            hdr = struct.pack('<BL4sB', self.auth, self.sseq, self.sid, payload_len)
        else:
            # Auth Type (1) | Seq # (4) | Sess ID (4) |  AuthCode (16) | Payload Len (1)
            auth_code = cal_auth_code_15(self.auth, self.pwd, self.sseq, self.sid, payload)

            hdr = struct.pack('<BL4s16sB', self.auth, self.sseq, self.sid, auth_code, 
                              payload_len)   

        return hdr

    def pack(self, req):
        # Pack IPMI Payload
        payload = self._pack_lan_payload(req)
        if len(payload) > 255:
            raise PyIntfExcept('Request data exceeds max length.')

        # pack the IPMI LAN 1.5 header
        hdr = self._pack_lan_header(payload)
        
        # pack RMCP header
        msg = super(IPMI15_Message, self).pack()
        msg += hdr + payload

        return msg
    
    def _unpack_lan_payload(self, payload):
        # verify checksum        
        if (checksum(payload[:2], int) != payload[2] or
            checksum(payload[3:len(payload)-1], int) != payload[-1]):
            raise PyIntfExcept('Invalid RMCP checksum in response.')        

        # unpack data fields
        rq_addr, netfn = struct.unpack('BB', payload[:2])
        netfn >>= 2
        rs_addr, rq_seq, cmd, cc = struct.unpack('BBBB', payload[3:7])
        rq_seq >>= 2
        rsp_data = payload[7:len(payload)-1]

        if rq_addr != RMCP_Message.SOFT_ID:
            raise PyIntfExcept('Invalid rq_addr: {0:02X}h in response.  Expected {1:02X}h.'.format(
                               rq_addr, RMCP_Message.SOFT_ID)) 

        if rs_addr != self.rs_addr:
            raise PyIntfExcept('Invalid rs_addr: {0:02X}h in response.  Expected {1:02X}h.'.format(
                               rs_addr, self.rs_addr)) 

        if rq_seq != self.seq_num:
            raise PyIntfSeqExcept('RMCP sequence number mismatches in response.')  

        return (netfn, cmd, cc, rsp_data)

    def _unpack_lan_header(self, rsp):
        # unpack payload
        try:
            if self.auth == AUTH_NONE:
                # Auth Type (1) | Seq # (4) | Sess ID (4) | Payload Len (1)
                t1 = struct.unpack('<BL4sB', rsp[:10])
                payload = rsp[10:]
            else:
                # Auth Type (1) | Seq # (4) | Sess ID (4) |  AuthCode (16) | Payload Len (1)
                t1 = struct.unpack('<BL4s16sB', rsp[:26])
                payload = rsp[26:]
        except:
            raise PyIntfExcept('Invalid RMCP header in response.')        

        # unpack IPMI LAN package
        if len(payload) != t1[-1] or len(payload) < 7:
            raise PyIntfExcept('Invalid RMCP payload length in response.')        

        if t1[0] != self.auth:
            raise PyIntfExcept('Invalid RMCP header in response.')        

        # verify AuthCode
        if t1[0] != AUTH_NONE:
            auth_code = cal_auth_code_15(t1[0], self.pwd, t1[1], t1[2], payload)
            if auth_code != t1[3]:
                raise PyIntfExcept('Invalid RMCP AuthCode in response.')  
        
        return payload

    def unpack(self, rsp):
        # unpack RMCP header
        rsp = super(IPMI15_Message, self).unpack(rsp)

        # unpack IPMI 1.5 header
        payload = self._unpack_lan_header(rsp)
                    
        # unpack IPMI LAN package
        return self._unpack_lan_payload(payload)
