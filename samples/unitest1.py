#!/usr/bin/env python3
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
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.intf.rmcp import RMCP
from pyipmi.mesg import IPMI_Message
from pyipmi.mesg.ipmi_app import GetDeviceID

def print_rsp(rsp):
    for i in rsp:
        print('{0:02x}'.format(i), end=' ')
    print()

if __name__ == '__main__':
    user = 'root'
    passwd = 'root123'
    priv = 4
    auth = 'md5'

    r1 = RMCP({'host': 'localhost', 'port': 623, }, False)
    r1.open({'user': user, 'password': passwd, 'priv': priv, 'auth': auth, 
             'no_ping': True,})
    rsp = r1.issue_cmd(GetDeviceID)
    print(IPMI_Message.dump_tuple(rsp))

    rsp = r1.issue_raw_cmd([6, 1])
    print_rsp(rsp)
    rsp = r1.issue_raw_cmd([6, 0x46, 2])
    print_rsp(rsp)
    rsp = r1.issue_raw_cmd([0x0c, 2, 1, 1, 0, 0])
    print_rsp(rsp)
    rsp = r1.issue_raw_cmd([6, 1], 1)   # LUN = 1
    print_rsp(rsp)
