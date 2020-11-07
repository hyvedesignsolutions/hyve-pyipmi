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
from .. util.exception import PyIntfExcept

__all__ = [
    'kcs',
    'rmcp',
    'rmcpp',
    'init',    
]

def init(opts, ping_only, keep_alive):
    if ping_only:
        from . rmcp import RMCP_Ping
        intf = RMCP_Ping(opts['global'])
        intf.open()
        return intf

    if 'interface' not in opts['global']:
        intf_name = 'lanplus'
    else:
        intf_name = opts['global']['interface']

    if intf_name == 'lan':
        from . rmcp import RMCP
        intf = RMCP(opts['global'], keep_alive)
        intf.open(opts['lan'])
        return intf

    if intf_name == 'lanplus':
        from . rmcpp import RMCPP
        intf = RMCPP(opts['global'], keep_alive)
        intf.open(opts['lanplus'])
        return intf

    raise PyIntfExcept('Invalid interface specified: ' + intf_name)

class Intf:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def sendrecv(self, data):
        pass
