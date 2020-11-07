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
from .. mesg.ipmi_app import GetDeviceGUID, GetDeviceID, GetSelfTest, ColdReset, \
                             GetEnables, SetEnables, GetSysInfo, SetSysInfo, \
                             ResetWatchdog, SetWatchdog, GetWatchdog
from . _common import bcd2str, do_command
from . _consts import TupleExt
from .. util.exception import PyCmdsArgsExcept

def _mc_reset(self, argv):
    self.intf.issue_cmd(ColdReset)

def _mc_guid(self, argv):
    guid, = self.intf.issue_cmd(GetDeviceGUID)
    self.print('Device GUID:', guid.hex())

def _mc_info(self, argv):
    t1 = self.intf.issue_cmd(GetDeviceID)
    self.print('Device ID                 : {0}'.format(t1[0]))
    self.print('Device Revision           : {0}'.format(t1[1] & 0x0f))
    self.print('Firmware Revision         : {0}.{1}'.format(t1[2] & 0x7f, bcd2str(t1[3])))
    self.print('IPMI Version              : {0}'.format(bcd2str(t1[4], True)))
    self.print('Manufacturer ID           : 0x{0:06x}'.format(int.from_bytes(t1[6], 'little')))
    self.print('Product ID                : {0}'.format(t1[7]))    

    dev_avail = 'yes' if t1[2] & 0x80 == 0 else 'no'
    self.print('Device Available          : {0}'.format(dev_avail))

    dev_sdr = 'no' if t1[1] & 0x80 == 0 else 'yes'
    self.print('Provides Device SDRs      : {0}'.format(dev_sdr))

    self.print('Additional Device Support :')
    devs = ('Sensor Device', 'SDR Repository Device', 'SEL Device',
            'FRU Inventory Device', 'IPMB Event Receiver',
            'IPMB Event Generator', 'Bridge', 'Chassis Device',)
    dev_sup = t1[5]

    for i in range(8):
        if dev_sup & 1:  self.print('    ' +  devs[i])
        dev_sup >>= 1

    self.print('Aux Firmware Rev Info     :')
    for i in t1[8]:
        self.print('    0x{0:02x}'.format(i))

def _mc_selftest(self, argv):
    rsp, err = self.intf.issue_cmd(GetSelfTest)

    msg = {0x55: 'passed', 0x56: 'not implemented', 
           0x57: 'corrupted or inaccessible data or devices',
           0x58: 'fatal hardware error', 0xff: 'reserved'}

    if rsp in msg.keys():
        self.print('Selftest: {0} ({1:02X}h)'.format(msg[rsp], rsp))
        if rsp == 0x57:
            errs = ('controller operational firmware corrupted',
                    'controller update \'boot block\' firmware corrupted',
                    'Internal Use Area of BMC FRU corrupted',
                    'SDR Repository empty',
                    'IPMB signal lines do not respond',
                    'cannot access BMC FRU device',
                    'cannot access SDR Repository',
                    'cannot access SEL device',)
            for i in range(8):
                if err & 1:  self.print('    ' + errs[i])
                err >>= 1                    
    else:
        self.print('Selftest: {0:02X}h'.format(rsp))

def _mc_getenables(self, argv):
    rsp, = self.intf.issue_cmd(GetEnables)
    enables = ('Receive Message Queue Interrupt', 'Event Message Buffer Full Interrupt',
               'Event Message Buffer', 'System Event Logging', 'reserved', 
               'OEM 0', 'OEM 1', 'OEM 2',)
    for i in range(8):
        if i != 4:  
            self.print('{0:36}'.format(enables[i]), end=' : ')
            if rsp & 1: self.print('enabled')
            else:   self.print('disabled')
        rsp >>= 1

def _mc_setenables(self, argv):
    if len(argv) < 3:
        raise PyCmdsArgsExcept(1, 2)
    if argv[2] not in ('on', 'off'):
        raise PyCmdsArgsExcept(2, 2, argv[2])
        
    cmds = TupleExt(('recv_msg_intr', 'event_msg_intr', 'event_msg', 'system_event_log',
                     'reserved', 'oem0', 'oem1', 'oem2',))
    idx = cmds.get_index(argv[1])
    if idx < 0: 
        raise PyCmdsArgsExcept(2, 2, argv[1])

    enables, = self.intf.issue_cmd(GetEnables)
    val = idx ** 2
    if argv[2] == 'on':  enables |= val
    else:  enables &= ~val

    self.intf.issue_cmd(SetEnables, enables)

def _sysinfo_opts(self, argv, chk):
    idx = 0
    if len(argv) < chk:
        raise PyCmdsArgsExcept(1, 3)

    params = TupleExt(('none', 'system_fw_version', 'system_name', 'primary_os_name', 
                       'os_name',))        
    idx = params.get_index(argv[1], 0)
    if idx == 0:
        raise PyCmdsArgsExcept(2, 3, argv[1])

    return idx

def _mc_getsysinfo(self, argv):
    idx = _sysinfo_opts(self, argv, 2)

    rsp = self.intf.issue_cmd(GetSysInfo, idx, 0, 0)
    if not rsp:
        self.print('Option {0} is not supported by BMC.'.format(argv[1]))
        return

    ret = rsp[2:].decode('latin_1')
    ret_len = rsp[1] - 14
    sel = 1

    while ret_len > 0:
        rsp = self.intf.issue_cmd(GetSysInfo, idx, sel, 0)
        if not rsp: break
        ret += rsp.decode('latin_1')
        ret_len -= 16
        if sel == 255:  break
        sel += 1

    self.print(argv[1] + ': ' + ret.strip())

def _mc_setsysinfo(self, argv):
    idx = _sysinfo_opts(self, argv, 3)

    val = argv[2].encode('latin_1')
    val_len = len(val)
    if val_len > 255:   
        val = val[:255]
        val_len = 255
    
    data = struct.pack('BBB', 0, 0, val_len) + val[:14]
    val_len -= 14
    if val_len > 0: val = val[14:]
    elif val_len < 0: data += b'\0' * (-val_len)

    cc = self.intf.issue_cmd(SetSysInfo, idx, data)
    if cc != 0:
        if cc == 0x80:
            self.print('Option {0} is not supported by BMC.'.format(argv[1]))
        elif cc == 0x82:
            self.print('Option {0} is read-only.'.format(argv[1]))
        else:
            self.print('Error: completion code = {0:02X}h.'.format(cc))
        return

    sel = 1
    while val_len > 0:
        data = struct.pack('B', sel) + val[:16]
        val_len -= 16
        if val_len > 0: val = val[16:]
        elif val_len < 0: data += b'\0' * (-val_len)
        cc = self.intf.issue_cmd(SetSysInfo, idx, data)
        if cc != 0: return
        sel += 1

def _mc_watchdog(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 1)
        
    if argv[1] not in ('get', 'reset'):
        raise PyCmdsArgsExcept(2, 1, argv[1])

    if argv[1] == 'get':
        (timer, act, pre_int, exp, init_count, 
            present_count) = self.intf.issue_cmd(GetWatchdog)

        timers = TupleExt(('reserved', 'BIOS FRB2', 'BIOS/POST', 'OS Load', 'SMS/OS', 'OEM'))
        timer_str = timers.get(timer & 7, 'reserved')
        timer_stat = ('Stopped', 'Started')[(timer & 0x40) >> 6]
        timer_log = ('On', 'Off')[(timer & 0x80) >> 7]

        acts = TupleExt(('No action', 'Hard Reset', 'Power Down', 'Power Cycle'))
        act_str = acts.get(act, 'reserved')
        ints = TupleExt(('None', 'SMI', 'NMI / Diagnostic Interrupt', 'Messaging Interrupt'))
        int_str = ints.get((act & 0x70) >>  4, 'reserved')

        exp >>= 1
        exp_flags = []
        for i in range(1, 6):
            if exp & 1:  exp_flags.append(timers[i])
            exp >>= 1

        self.print('Watchdog Timer Use       : {0} ({1:02X}h)'.format(timer_str, timer & 7))
        self.print('Watchdog Timer Is        : {0}'.format(timer_stat))
        self.print('Watchdog Timer Logging   : {0}'.format(timer_log))
        self.print('Watchdog Timer Action    : {0} ({1:02X}h)'.format(act_str, act & 7))
        self.print('Pre-timeout Interrupt    : {0}'.format(int_str))
        self.print('Pre-timeout Interval     : {0} seconds'.format(pre_int))
        
        if not exp_flags:
            self.print('Timer Expiration Flags   : none')
        else:
            self.print('Timer Expiration Flags   : [{0}]'.format(exp_flags[0]))
            for i in exp_flags[1:]:
                self.print(' ' * 27 + '[{0}]'.format(i))

        self.print('Initial Countdown        : {0} seconds'.format(init_count / 10))
        self.print('Present Countdown        : {0} seconds'.format(present_count / 10))

    else:   # reset    
        cc = self.intf.issue_cmd(ResetWatchdog)
        if cc == 0:
            self.print('IPMI Watchdog has been successfully reset.')
        elif cc == 0x80:
            self.print('Failed to reset IPMI Watchdog.  Attempted to start un-initialized watchdog.')
        else:
            self.print('Failed to reset IPMI Watchdog.  CC={0:2X}h.'.format(cc))

def help_mc(self, argv=None, context=0):
    if context == 0:
        self.print('MC Commands:')
        self.print('    help')
        self.print('    reset')
        self.print('    guid')
        self.print('    info')
        self.print('    selftest')
    if context in (0, 1):
        self.print('    watchdog <get|reset>')
    if context in (0, 2):
        self.print('    getenables')
        self.print('    setenables <option> <on|off>')
        self.print('     * recv_msg_intr')
        self.print('     * event_msg_intr')
        self.print('     * event_msg')
        self.print('     * system_event_log')
        self.print('     * oem0')
        self.print('     * oem1')
        self.print('     * oem2')
    if context in (0, 3):
        self.print('    getsysinfo <option>')
        self.print('    setsysinfo <option> <value>')
        self.print('     * system_fw_version')
        self.print('     * system_name')
        self.print('     * primary_os_name')
        self.print('     * os_name')

MC_CMDS = {
    'reset': _mc_reset,
    'guid': _mc_guid,
    'info': _mc_info,
    'watchdog': _mc_watchdog, 
    'selftest': _mc_selftest,
    'getenables': _mc_getenables,
    'setenables': _mc_setenables,
    'getsysinfo': _mc_getsysinfo,
    'setsysinfo': _mc_setsysinfo,
    'help': help_mc,  
}

def do_mc(self, argv):
    do_command(self, argv, help_mc, MC_CMDS)
