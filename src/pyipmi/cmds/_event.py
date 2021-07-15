#
# Copyright (c) 2020-2021, Hyve Design Solutions Corporation.
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
from .. mesg.ipmi_se import PlatformEvent
from . _common import do_command
from . _sel import print_sel_list

def _event_test(self, argv):
    SOFT_ID = 0x81
    req = []
    flag_kcs = False

    if type(self.intf).__name__ == 'KCS':
        # system interface        
        req = [SOFT_ID]
        flag_kcs = True

    if argv[0] == '1':
        self.print('Sending SAMPLE event: Temperature - Upper Critical - Going High')
        req += [4, 1, 0x30, 1, 9, 0xff, 0xff]
    elif argv[0] == '2':
        self.print('Sending SAMPLE event: Voltage Threshold - Lower Critical - Going Low')
        req += [4, 2, 0x60, 1, 2, 0xff, 0xff]
    elif argv[0] == '3':
        self.print('Sending SAMPLE event: Memory - Correctable ECC')
        req += [4, 0x0c, 0x53, 0x6f, 0, 0xff, 0xff]

    # Issue Platform Event
    self.intf.issue_cmd(PlatformEvent, bytes(req))

    # print SEL entry
    prefix = [0, 2, 0]
    if not flag_kcs: prefix += [SOFT_ID]
    sel1 = prefix + req
    print_sel_list(self, (sel1,))

def help_event(self, argv=None, context=0):
    self.print('Usage: event <num>')
    self.print('    Send generic test events')
    self.print('    1 : Temperature - Upper Critical - Going High')
    self.print('    2 : Voltage Threshold - Lower Critical - Going Low')
    self.print('    3 : Memory - Correctable ECC')
    self.print('Usage: event help')

EVENT_CMDS = {
    '1': _event_test,
    '2': _event_test,
    '3': _event_test,
    'help': help_event, 
}

def do_event(self, argv):
    do_command(self, argv, help_event, EVENT_CMDS)
