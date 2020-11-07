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
import Crypto.Cipher.AES, Crypto.Hash.HMAC, Crypto.Hash.MD2, Crypto.Hash.MD5
import Crypto.Hash.SHA, Crypto.Hash.SHA256

# Common
def checksum(data, fmt=bytes):
    chksum = 0
    for i in data:
        chksum += i
    chksum &= 0xff
    if chksum != 0: chksum = 256 - chksum

    if fmt == bytes:
        return struct.pack('B', chksum)
    else:
        return chksum

def conv_str2bytes(org):
    if type(org) is bytes: return org
    elif type(org) is not str: return None
    if org == '': return None
    return bytes(org, 'latin_1')

# RMCP
AUTH_NONE = 0
AUTH_MD2 = 1
AUTH_MD5 = 2
AUTH_PASSWD = 4
AUTH_OEM = 5
AUTH_RMCPP = 6

RMCP_AUTHS = {
    'none': AUTH_NONE,
    'md2': AUTH_MD2,
    'md5': AUTH_MD5,
    'password': AUTH_PASSWD,
    'oem': AUTH_OEM,
}

def cal_auth_code_15(auth, pwd, sseq=0, sid='\0', data=None):
    auth_code = None
    if pwd is not None:
        pwd_b = struct.pack('16s', pwd)
    else:
        pwd_b = struct.pack('16s', b'\0')
    H = None

    if auth == AUTH_PASSWD:
        return pwd_b
    elif auth == AUTH_MD2:
        H = Crypto.Hash.MD2
    elif auth == AUTH_MD5:
        H = Crypto.Hash.MD5
    else:
        return None

    sid_b = struct.pack('4s', sid)
    sseq_b = struct.pack('<L', sseq)

    data_in = pwd_b + sid_b + data + sseq_b + pwd_b
    h1 = H.new(data_in)
    auth_code = h1.digest()

    return auth_code

# RMCP+
# Authentication
RAKP_NONE = 0
RAKP_HMAC_SHA1 = 1
RAKP_HMAC_MD5 = 2
RAKP_HMAC_SHA256 = 3

# Integrity 
HMAC_SHA1_96 = 1
HMAC_MD5_128 = 2
MD5_128 = 3
HMAC_SHA256_128 = 4

# Confidentiality 
AES_CBC_128 = 1
#XRC4_128 = 2   # not support
#XRC4_40 = 3    # not support

# RMCP+ Cipher Suites
RMCPP_CIPHERS = {
    # ID: (Auth, Inte, Conf)
    0: (RAKP_NONE, RAKP_NONE, RAKP_NONE),
    1: (RAKP_HMAC_SHA1, RAKP_NONE, RAKP_NONE),
    2: (RAKP_HMAC_SHA1, HMAC_SHA1_96, RAKP_NONE),
    3: (RAKP_HMAC_SHA1, HMAC_SHA1_96, AES_CBC_128),
    #4: (RAKP_HMAC_SHA1, HMAC_SHA1_96, XRC4_128),
    #5: (RAKP_HMAC_SHA1, HMAC_SHA1_96, XRC4_40),
    6: (RAKP_HMAC_MD5, RAKP_NONE, RAKP_NONE),
    7: (RAKP_HMAC_MD5, HMAC_MD5_128, RAKP_NONE),
    8: (RAKP_HMAC_MD5, HMAC_MD5_128, AES_CBC_128),
    #9: (RAKP_HMAC_MD5, HMAC_MD5_128, XRC4_128),
    #10: (RAKP_HMAC_MD5, HMAC_MD5_128, XRC4_40),
    11: (RAKP_HMAC_MD5, MD5_128, RAKP_NONE),
    12: (RAKP_HMAC_MD5, MD5_128, AES_CBC_128),
    #13: (RAKP_HMAC_MD5, MD5_128, XRC4_128),
    #14: (RAKP_HMAC_MD5, MD5_128, XRC4_40),
    15: (RAKP_HMAC_SHA256, RAKP_NONE, RAKP_NONE),
    16: (RAKP_HMAC_SHA256, HMAC_SHA256_128, RAKP_NONE),
    17: (RAKP_HMAC_SHA256, HMAC_SHA256_128, AES_CBC_128),
    #18: (RAKP_HMAC_SHA256, HMAC_SHA256_128, XRC4_128),
    #19: (RAKP_HMAC_SHA256, HMAC_SHA256_128, XRC4_40),
}

def get_cipher_tuple(cipher):
    if cipher not in RMCPP_CIPHERS.keys():
        return None
    return RMCPP_CIPHERS[cipher]

def get_cipher(cipher_tuple):
    ret = None
    for c, t in zip(RMCPP_CIPHERS.keys(), RMCPP_CIPHERS.values()):
        if t == cipher_tuple:
            ret = c
            break
    return ret

def cal_auth_code(algo, key, data):
    if algo == RAKP_HMAC_SHA1:
        H = Crypto.Hash.HMAC.new(key, data, Crypto.Hash.SHA)
    elif algo == RAKP_HMAC_MD5:
        H = Crypto.Hash.HMAC.new(key, data, Crypto.Hash.MD5)
    elif algo == RAKP_HMAC_SHA256:
        H = Crypto.Hash.HMAC.new(key, data, Crypto.Hash.SHA256)
    else:
        return None
        
    return H.digest()

def cal_inte_check(algo, key, data):
    trunc = None

    if algo == HMAC_SHA1_96:
        H = Crypto.Hash.HMAC.new(key, data, Crypto.Hash.SHA)
        trunc = 12
    elif algo == HMAC_MD5_128:
        H = Crypto.Hash.HMAC.new(key, data, Crypto.Hash.MD5)
    elif algo == HMAC_SHA256_128:
        H = Crypto.Hash.HMAC.new(key, data, Crypto.Hash.SHA256)
        trunc = 16
    elif algo == MD5_128:
        H = Crypto.Hash.MD5.new(key + data + key)
    else:
        return None
        
    ret = H.digest()
    if trunc is not None: ret = ret[:trunc]

    return ret 
    
def get_inte_len(algo):
    ret = 0

    if algo == HMAC_SHA1_96:
        ret = 12
    elif algo == HMAC_MD5_128:
        ret = 16
    elif algo == HMAC_SHA256_128:
        ret = 16
    elif algo == MD5_128:
        ret = 16

    return ret

def map_auth2inte(auth):
    inte = None

    if auth == RAKP_HMAC_SHA1:
        inte = HMAC_SHA1_96
    elif auth == RAKP_HMAC_MD5:
        inte = HMAC_MD5_128
    elif auth == RAKP_HMAC_SHA256:
        inte = HMAC_SHA256_128

    return inte

def encrypt_aes_128_cbc(key, data):
    iv = os.urandom(16)
    rem = (len(data) + 1) & 0x0f
    if rem != 0:
        # need padding bytes        
        pad_len = 16 - rem
        data += bytes((x for x in range(1, pad_len + 1)))
    else:
        pad_len = 0

    data += struct.pack('B', pad_len)
    E = Crypto.Cipher.AES.new(key[:16], Crypto.Cipher.AES.MODE_CBC, iv)
    
    return iv + E.encrypt(data)

def decrypt_aes_128_cbc(key, data):
    iv = data[:16]
    D = Crypto.Cipher.AES.new(key[:16], Crypto.Cipher.AES.MODE_CBC, iv)
    data = D.decrypt(data[16:])
    pad_len = data[-1]

    return data[:-(pad_len+1)]
