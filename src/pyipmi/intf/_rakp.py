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
import os, struct
from .. util.exception import PyIntfExcept, PyIntfCCExcept
from . _rmcpp_msg import IPMI20_Message
from . _crypto import RAKP_NONE, cal_auth_code, map_auth2inte, cal_inte_check

class RAKP_Message:
    def __init__(self, rcsid):
        self.rcsid = rcsid
        self.payload_type = 0
        self.msg_tag = os.urandom(1)

    def pack(self):
        pass

    def unpack(self, payload_type, rsp, exp_len=8):
        if len(rsp) < 8:
            raise PyIntfExcept('Wrong response payload length.')

        tag, cc, _, sid = struct.unpack('<1sBH4s', rsp[:8])

        if payload_type != self.payload_type + 1:
            raise PyIntfExcept('Payload Type is 0x{0:02x}, but expected to be 0x{1:02x}.'.format(
                                                                payload_type, self.payload_type + 1))
        if tag != self.msg_tag:  # Message Tag
            raise PyIntfExcept('Message Tag does not match.')
        if cc != 0:  # RMCP+ Status Code
            raise PyIntfCCExcept(rsp[1])
        if sid != self.rcsid:
            raise PyIntfExcept('Remote console session ID does not match.')

        if len(rsp) < exp_len:
            raise PyIntfExcept('Wrong response payload length.')

        return rsp[8:]

class RMCPP_OpenSess(RAKP_Message):
    def __init__(self, rcsid, cipher, priv):
        super(RMCPP_OpenSess, self).__init__(rcsid)
        self.cipher = cipher  # (auth, inte, conf)
        self.priv = priv
        self.payload_type = 0x10

    def pack(self):
        # RMCP+ Open Session Request, payload_type = 0x10
        # console -> BMC
        
        auth = struct.pack('<BHBB3s', 0, 0, 8, self.cipher[0], b'\0')
        inte = struct.pack('<BHBB3s', 1, 0, 8, self.cipher[1], b'\0')
        conf = struct.pack('<BHBB3s', 2, 0, 8, self.cipher[2], b'\0')

        payload = struct.pack('<1sBH4s', self.msg_tag, self.priv, 0, self.rcsid)
        payload += auth + inte + conf

        return payload

    def unpack(self, payload_type, rsp):
        # RMCP+ Open Session Response
        # BMC -> console, payload_type = 0x11
        payload = super(RMCPP_OpenSess, self).unpack(payload_type, rsp, 36)
        mssid, auth, inte, conf = struct.unpack('<4s8s8s8s', payload)
        algo = lambda x: x[4] & 0x3f

        return (mssid, (algo(auth), algo(inte), algo(conf)))

class RAKP_1_2(RAKP_Message):
    def __init__(self, rcsid, mssid, rcrn, priv, user=None, passwd=None, auth=RAKP_NONE):
        super(RAKP_1_2, self).__init__(rcsid)
        self.mssid = mssid
        self.rcrn = rcrn
        self.priv = priv
        self.user = user
        self.passwd = passwd
        self.auth = auth
        self.payload_type = 0x12

    def pack(self):
        # RAKP 1: console -> BMC
        if self.user is not None:
            payload = struct.pack('<1s3s4s16sBHB16s', self.msg_tag, b'\0', self.mssid,
                                  self.rcrn, self.priv, 0, len(self.user), self.user)
        else:
            payload = struct.pack('<1s3s4s16sBHB', self.msg_tag, b'\0', self.mssid,
                                  self.rcrn, self.priv, 0, 0)

        return payload

    def unpack(self, payload_type, rsp):
        # RAKP 2 : BMC -> console
        payload = super(RAKP_1_2, self).unpack(payload_type, rsp, 40)

        msrn = payload[:16]
        msguid = payload[16:32]
        auth_code = payload[32:]

        # verify auth code
        # auth_code = H(rcsid, mssid, rcrn, msrn, msguid, priv, len(user), user)
        # key = user password
        if self.auth != RAKP_NONE and self.passwd is not None:
            if len(auth_code) == 0:
                raise PyIntfExcept('Key Exchange Authentication Code is not valid in RAKP 2.')           

            if self.user is not None:
                data = struct.pack('<4s4s16s16s16sBB', self.rcsid, self.mssid, self.rcrn, msrn, msguid,
                                   self.priv, len(self.user))
                data += self.user
            else:
                data = struct.pack('<4s4s16s16s16sBB', self.rcsid, self.mssid, self.rcrn, msrn, msguid,
                                   self.priv, 0)

            auth_code_expected = cal_auth_code(self.auth, self.passwd, data)

            if auth_code != auth_code_expected:
                raise PyIntfExcept('Key Exchange Authentication Code is not valid in RAKP 2.')           

        return (msrn, msguid)

class RAKP_3_4(RAKP_Message):
    def __init__(self, rcsid, mssid, msrn, rcrn, msguid, 
                 priv, user=None, passwd=None, auth=RAKP_NONE, sik=None):
        super(RAKP_3_4, self).__init__(rcsid)        
        self.mssid = mssid
        self.msrn = msrn
        self.rcrn = rcrn
        self.msguid = msguid
        self.priv = priv
        self.user = user
        self.passwd = passwd
        self.auth = auth
        self.sik = sik
        self.payload_type = 0x14

    def pack(self):
        # RAKP 3: console -> BMC
        payload = struct.pack('<1s3s4s', self.msg_tag, b'\0', self.mssid)

        # calculate auth code
        # auth_code = H(msrn, rcsid, priv, len(user), user)
        # key = user password
        if self.auth != RAKP_NONE and self.passwd is not None:
            if self.user != None:
                data = struct.pack('<16s4sBB', self.msrn, self.rcsid, 
                                   self.priv, len(self.user))
                data += self.user
            else:
                data = struct.pack('<16s4sBB', self.msrn, self.rcsid, 
                                   self.priv, 0)
        
            auth_code = cal_auth_code(self.auth, self.passwd, data)
            payload += auth_code

        return payload

    def unpack(self, payload_type, rsp):
        # RAKP 4: BMC -> console
        auth_code = super(RAKP_3_4, self).unpack(payload_type, rsp, 8)

        # verify auth code
        # auth_code = H(rcrn, mssid, msguid)
        # key = SIK
        if self.auth != RAKP_NONE and self.sik is not None:
            if len(auth_code) == 0:
                raise PyIntfExcept('Key Exchange Authentication Code is not valid in RAKP 4.')           

            data = struct.pack('16s4s16s', self.rcrn, self.mssid, self.msguid)
            inte = map_auth2inte(self.auth)
            auth_code_expected = cal_inte_check(inte, self.sik, data)

            if auth_code != auth_code_expected:
                raise PyIntfExcept('Key Exchange Authentication Code is not valid in RAKP 4.')           
