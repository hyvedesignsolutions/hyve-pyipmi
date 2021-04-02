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
from datetime import datetime, timedelta
from pyipmi.util.config import PyOpts
from bm_conf import *
from bmp1 import BMP1
from bmp2 import BMP2
from bmp3 import BMP3
from bmp4 import BMP4
from bmp5 import BMP5
from bmt1 import BMT1
from bmt2 import BMT2
from bmt3 import BMT3
from bmt4 import BMT4
from bmt5 import BMT5

BMP_CLASSES = (BMP1, BMP2, BMP3, BMP4, BMP5)
BMT_CLASSES = (BMT1, BMT2, BMT3, BMT4, BMT5)

def run_testcase(c, opts):
    t1 = datetime.now()
    test = c(opts)
    test.run()
    t2 = datetime.now()
    return (t2 - t1)

def delta2str(d):
    return '{0}m{1}.{2}s'.format(int(d.seconds / 60), d.seconds % 60, int(d.microseconds/1000))

# pyipmi & ipmitool options
pyopts = PyOpts()
pyopts.add_options()

# overwrite bm_intf
if len(sys.argv) > 1:
    if sys.argv[1] in ('lan', 'lanplus', 'kcs'):
        bm_intf = sys.argv[1]

# assign command options
if bm_intf == 'kcs':
    opts_p = pyopts.parse_options('-I kcs')
    opts_t = ''
else:
    opts_p = pyopts.parse_options('-H {0} -I {1} -U {2} -P {3} -C {4}'.format(bm_host, bm_intf, bm_user, bm_pass, bm_cipher))
    opts_t = '-H {0} -I {1} -U {2} -P {3} -C {4}'.format(bm_host, bm_intf, bm_user, bm_pass, bm_cipher)

ret_p = [timedelta(seconds=0)] * len(BMP_CLASSES)
ret_t = [timedelta(seconds=0)] * len(BMT_CLASSES)

for i in range(bm_rounds):
    # pyipmi test cases
    for j in range(len(BMP_CLASSES)):
        d = run_testcase(BMP_CLASSES[j], opts_p)
        ret_p[j] += d

    # ipmitool test cases
    for j in range(len(BMT_CLASSES)):
        d = run_testcase(BMT_CLASSES[j], opts_t)
        ret_t[j] += d

# Output the test results on the console
print('Test Results:')
print('\n--------- pyipmi ----------')
for i in range(len(ret_p)):
    print('#{0}: {1}'.format(i + 1, delta2str(ret_p[i] / bm_rounds)))

print('\n--------- ipmitool ----------')
for i in range(len(ret_t)):
    print('#{0}: {1}'.format(i + 1, delta2str(ret_t[i] / bm_rounds)))

# Write the test results in a log file
fout = open('bm_test_{0}.log'.format(bm_intf), 'w')

fout.write('Test Results:\n')
fout.write('\n--------- pyipmi ----------\n')
for i in range(len(ret_p)):
    fout.write('#{0}: {1}\n'.format(i + 1, delta2str(ret_p[i] / bm_rounds)))

fout.write('\n--------- ipmitool ----------\n')
for i in range(len(ret_t)):
    fout.write('#{0}: {1}\n'.format(i + 1, delta2str(ret_t[i] / bm_rounds)))

fout.close()

