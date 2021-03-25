#!/usr/bin/env python3
# Copyright (c) 2020, Hyve Design Solutions Corporation.
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are 
# met:
#
# 1. Redistributions of source code must retain the above copyright 
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright 
#    notice, this list of conditions and the following disclaimer in the 
#    documentation and/or other materials provided with the distribution.
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
from bmt import BMT
from bm_conf import *

class BMT3(BMT):
    def __init__(self, opts):
        opts += ' -b {0} -t {1}'.format(bm_b_chnl, bm_b_dest)
        super(BMT3, self).__init__(opts)

    def run_commands(self, argv=None):
        req = ('6 1',                     # Get Device ID
               '0xa 0x48',                # Get SEL Time
               '4 1',                     # Get Event Receiver
               '0x2e 0xe0 0x57 1 0',      # Get Intel ME Factory Presets Signature
               '0x2e 0xe6 0x57 1 0 0',    # Get Exception Data
               '4 0x2d 8',                # Get Sensor Reading 8
               '4 0x2d 197',              # Get Sensor Reading 197      
               )                    

        for i in range(int(bm_times/len(req))+1):
            print('#{0}:'.format(i + 1), end=' ', flush=True)
            for j in req:
                self.exec_command(j)

if __name__ == '__main__':
    opts = '-H {0} -I {1} -U {2} -P {3} -C {4}'.format(bm_host, bm_intf, bm_user, bm_pass, bm_cipher)

    test = BMT3(opts)
    sys.exit(test.run())
