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
import os, struct, socket, select
from . import rmcp
from . rmcp import RMCP_Ping
from . _rmcp_msg import IPMI15_Message, RMCP_Message
from . _crypto import *
from .. util.exception import PyIntfExcept

class IPMI20_Message(IPMI15_Message):
    seq_num = 1

    def __init__(self, cipher, sseq=0, sid=0, pwd='', k1=None, k2=None):
        self.cipher = cipher
        self.k1 = k1
        self.k2 = k2
        
        # Get this seq_num
        if isinstance(self, IPMI20_Message):
            self.seq_num = IPMI20_Message.seq_num
            IPMI20_Message.seq_num += 1
            if IPMI20_Message.seq_num == 64: IPMI20_Message.seq_num = 0

        super(IPMI20_Message, self).__init__(AUTH_RMCPP, sseq, sid, pwd)

    def _pack_lan_header(self, payload, payload_type):
        payload_len = len(payload)

        # Auth Type (1) | Payload Type (1) | Sess ID (4) | Seq # (4) | Payload Len (2)
        hdr = struct.pack('<BB4sLH', self.auth, payload_type, self.sid, self.sseq, 
                          payload_len)

        return hdr

    def _unpack_lan_header(self, rsp):
        # unpack payload
        try:
            # Auth Type (1) = 06h | Payload Type (1) | Sess ID (4) | Seq # (4) | Payload Len (2)
            t1 = struct.unpack('<BBLLH', rsp[:12])
            payload = rsp[12:]
        except:
            raise PyIntfExcept('Invalid RMCP+ header in response.')        

        # unpack IPMI LAN package
        if len(payload) != t1[-1] or len(payload) < 7:
            raise PyIntfExcept('Invalid RMCP+ payload length in response.')        

        if t1[0] != self.auth:
            raise PyIntfExcept('Invalid RMCP+ header in response.')        
        
        return t1, payload

    def pack(self, cmd, payload=None):
        # Pack IPMI Payload
        if payload is None:
            payload = self._pack_lan_payload(cmd)
        if len(payload) > 65535:
            raise PyIntfExcept('Request data exceeds max length.')

        # pack the IPMI LAN 2.0 header
        payload_type = cmd.payload_type
        if self.cipher[2] != RAKP_NONE:
            # bit 7 = 1b: payload is encrypted
            payload_type = 0x80
        if self.cipher[1] != RAKP_NONE:
            # bit 6 = 1b: payload is unauthenticated
            payload_type |= 0x40

        # Encrypt the payload if necessary
        if self.cipher[2] == AES_CBC_128:
            payload = encrypt_aes_128_cbc(self.k2, payload)

        msg = self._pack_lan_header(payload, payload_type) + payload

        # Add Integrity Check if necessary
        if self.cipher[1] != RAKP_NONE:
            rem = (len(msg) + 2) & 3
            if rem != 0: 
                pad_len = 4 - rem
                pad = struct.pack('B', 0xff) * pad_len
            else: 
                pad_len = 0

            tail = struct.pack('BB', pad_len, 7)    # Pad Length, Next Header
            if pad_len != 0:    tail = pad + tail   
            msg += tail         

            if self.cipher[1] != MD5_128:
                msg += cal_inte_check(self.cipher[1], self.k1, msg)
            else:
                msg += cal_inte_check(self.cipher[1], self.pwd, msg)
        
        # pack RMCP header
        return RMCP_Message.pack(self) + msg

    def unpack(self, rsp):
        # unpack RMCP header
        rsp = RMCP_Message.unpack(self, rsp)

        # Integrity Check if necessary
        if self.cipher[1] != RAKP_NONE:
            auth_code_len = get_inte_len(self.cipher[1])
            auth_code = rsp[-auth_code_len:]
            rsp = rsp[:-auth_code_len]
            if self.cipher[1] != MD5_128:
                auth_code_expected = cal_inte_check(self.cipher[1], self.k1, rsp)
            else:
                auth_code_expected = cal_inte_check(self.cipher[1], self.pwd, rsp)

            if auth_code != auth_code_expected:
                raise PyIntfExcept('Integrity Check failed.')

            pad_len = rsp[-2]
            rsp = rsp[:-(pad_len+2)]

        # unpack IPMI 2.0 header
        t1, payload = self._unpack_lan_header(rsp)

        # Decrypt if necessary
        if self.cipher[2] == AES_CBC_128:
            payload = decrypt_aes_128_cbc(self.k2, payload)
                    
        # unpack IPMI LAN package
        if t1[1] & 0x3f == 0:
            return self._unpack_lan_payload(payload)
        else:
            return (t1[1], payload)
