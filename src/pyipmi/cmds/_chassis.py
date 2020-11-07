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
from collections import OrderedDict
from .. mesg.ipmi_chassis import *
from . _consts import TupleExt
from . _common import str2int, do_command
from .. util.exception import PyCmdsExcept, PyCmdsArgsExcept

def _chassis_status(self, argv):
    t1 = self.intf.issue_cmd(GetChsStat)
    d1 = OrderedDict()

    get_on = lambda val, mask: 'on' if val & mask else 'off'
    get_true = lambda val, mask: 'true' if val & mask else 'false'
    get_act = lambda val, mask: 'active' if val & mask else 'inactive'

    # Current Power State
    d1['System Power'] = get_on(t1[0], 1)
    d1['Power Overload'] = get_true(t1[0], 2)
    d1['Power Interlock'] = get_act(t1[0], 4)
    d1['Main Power Fault'] = get_true(t1[0], 8)
    d1['Power Control Fault'] = get_true(t1[0], 16)
    d1['Power Restore Policy'] = ('always-off', 'last state', 'always-on', 'unknown')[(t1[0] & 0x60) >> 5]

    # Last Power Event
    events = []
    event_names = ('AC failed', 'Power overload', 'Power interlock', 'Power fault', 'Power on by IPMI')
    e = t1[1] & 0x1f

    idx = 0
    while e:
        if e & 1: events.append(event_names[idx])
        e >>= 1
        idx += 1

    d1['Last Power Event'] = ', '.join(events) if events else ''

    # Misc Chassis Status
    d1['Chassis Intrusion'] = get_act(t1[2], 1)
    d1['Front-Panel Lockout'] = get_act(t1[2], 2)
    d1['Drive Fault'] = get_true(t1[2], 4)
    d1['Cooling/Fan Fault'] = get_true(t1[2], 8)
    if t1[2] & 64:
        d1['Chassis Identify'] = ('off', 'temporary on', 'indefinite on', 'reserved')[(t1[2] & 0x30) >> 4]

    # FP Button Cap and status
    if len(t1) >= 4:
        d1['Power Button Disabled'] = get_true(t1[3], 1)
        d1['Reset Button Disabled'] = get_true(t1[3], 2)
        d1['Diag Button Disabled'] = get_true(t1[3], 4)
        d1['Sleep Button Disabled'] = get_true(t1[3], 8)

        get_allow = lambda mask: 'allowed' if t1[3] & mask else 'not allowed'
        d1['Power Button Disable'] = get_allow(16)
        d1['Reset Button Disable'] = get_allow(32)
        d1['Diag Button Disable'] = get_allow(64)
        d1['Sleep Button Disable'] = get_allow(128)

    # Output
    for key, val in d1.items():
        self.print('{0:24}: {1}'.format(key, val))

def _chassis_power(self, argv):
    from . _power import do_power
    do_power(self, argv[1:])

def _chassis_policy(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 1)

    opts = TupleExt(('always-off', 'previous', 'always-on', 'list'))
    opt = opts.get_index(argv[1])
    if opt < 0:
        raise PyCmdsArgsExcept(2, 1, argv[1])

    poc, = self.intf.issue_cmd(PowerRestore, opt)

    if opt == 3:    # list (no change)
        poc_support = []
        poc &= 7
        idx = 0
        while poc:
            if poc & 1: poc_support.append(opts[idx])
            poc >>= 1
            idx += 1
        ret = ' '.join(poc_support) if poc_support else '(none)'
        self.print('Supported chassis power policy: ' + ret)
    else:        
        self.print('Set chassis power restore policy to ' + opts[opt])

def _chassis_restart_cause(self, argv):
    cause, _ = self.intf.issue_cmd(GetSysRestartCause)
    rcs = ('unknown', 'Chassis Control command', 'reset via pushbutton',
           'power-up via power pushbutton', 'Watchdog expiration', 'OEM',
           'automatic power-up on AC being applied due to \'always restore\' power restore policy',
           'automatic power-up on AC being applied due to \'restore previous power state\' power restore policy',
           'reset via PEF', 'power-cycle via PEF', 'soft reset', 'power-up via RTC wakeup')
    
    if cause >= len(rcs):  cause = 0
    self.print('System restart cause: ' + rcs[cause])

def _chassis_poh(self, argv):
    mins, counter = self.intf.issue_cmd(GetPoh)
    mins_all = mins * counter
    
    h = int(mins_all / 60)
    m = mins_all - h * 60 

    d = int(h / 24)
    h -= d * 24

    self.print('POH Counter: {0} days, {1} hours, {2} minutes'.format(d, h, m))

def _chassis_identify(self, argv):
    interval = 15
    force = 0    

    if len(argv) >= 2:
        if argv[1] == 'on':
            force = 1
            ret = 'indefinitely on'
        elif argv[1] == 'off':
            interval = 0
        else:
            int_req = str2int(argv[1])
            if int_req > 0 and int_req < 256:
                interval = int_req
            ret = '{0} seconds'.format(interval)
    else:
        ret = 'default ({0} seconds)'.format(interval)

    self.intf.issue_cmd(ChsIdentify, interval, force)

    CI = 'Chassis identify'
    if interval == 0:
        self.print(CI + ' is off')
    else:
        self.print(CI + ' interval: ' + ret)

def _chassis_bootdev(self, argv):
    if len(argv) < 2: 
        raise PyCmdsArgsExcept(1, 2)
    
    devs = TupleExt(('none', 'pxe', 'disk', 'safe', 'diag', 'cdrom', 'bios'))
    if argv[1] == 'floppy':
        dev = 15
    else:
        dev = devs.get_index(argv[1])

    if dev == -1:
        raise PyCmdsArgsExcept(2, 2, argv[1])

    if len(argv) >= 3:
        if argv[2] == 'clear-cmos':
            dev |= 0x80
        else:
            raise PyCmdsArgsExcept(2, 2, argv[2])

    # data1 = 1010 0000b, this will change the config to EFI
    data = struct.pack('BBBBB', 0xa0, dev, 0, 0, 0)
    
    self.intf.issue_cmd(SetBootOpts, 5, data)

def help_chassis(self, argv=None, context=0):
    if context == 0:
        self.print('Chassis Commands:')
        self.print('    status')        
        self.print('    power <status|on|off|cycle|reset|diag|soft>')
    if context in (0, 1):
        self.print('    policy <list|always-on|previous|always-off>')
    if context == 0:
        self.print('    restart_cause')
        self.print('    poh')
        self.print('    identify [<on|off|1-255>]')
    if context in (0, 2):
        self.print('    bootdev <none|pxe|disk|safe|diag|cdrom|bios|floppy> [clear-cmos]')

CHASSIS_CMDS = {
    'status': _chassis_status,
    'power': _chassis_power,
    'policy': _chassis_policy,
    'restart_cause': _chassis_restart_cause,
    'poh': _chassis_poh,
    'identify': _chassis_identify,
    'bootdev': _chassis_bootdev,
    'help': help_chassis,
}

def do_chassis(self, argv):
    do_command(self, argv, help_chassis, CHASSIS_CMDS)
