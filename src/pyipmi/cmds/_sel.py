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
from .. mesg.ipmi_storage import GetSELInfo, GetSELAllocInfo, GetSELTime, \
                                ClearSEL, GetSELEntry, RevSEL
from .. util.exception import PyCmdsArgsExcept
from . _common import conv_time, bcd2str, conv_sensor_type, get_sensor_map, \
                    conv_event_reading, do_command, str2int
from . _consts import GENERIC_EVENT_TYPES, SPECIFIC_EVENT_TYPES

def _sel_info(self, argv):
    ver, rec, free, add_ts, erase_ts, op = self.intf.issue_cmd(GetSELInfo)
    self.print('SEL Version               : ' + bcd2str(ver, True))
    self.print('Record Count              : {0}'.format(rec))
    self.print('Free Space                : {0} bytes'.format(free))
    self.print('Most Recent Addition      : ' + conv_time(add_ts))
    self.print('Most Recent Erase         : ' + conv_time(erase_ts))

    get_op_support = lambda mask: 'yes' if op & mask else 'no'

    self.print('SEL Overflow              : ' + get_op_support(0x80))
    self.print('Delete SEL Supported      : ' + get_op_support(8))
    self.print('Partial Add SEL Supported : ' + get_op_support(4))
    self.print('Reserve SEL Supported     : ' + get_op_support(2))
    self.print('SEL Alloc Info Supported  : ' + get_op_support(1))    

    if op & 1:
        t1 = self.intf.issue_cmd(GetSELAllocInfo)
        UC = 'unspecified'

        alloc_units = '{0}'.format(t1[0]) if t1[0] != 0 else UC
        alloc_unit_size = '{0} bytes'.format(t1[1]) if t1[0] != 0 else UC

        self.print('# of Alloc Units          : ' + alloc_units)
        self.print('Alloc Unit Size           : ' + alloc_unit_size)
        self.print('# Free Units              : {0}'.format(t1[2]))
        self.print('Largest Free Blk          : {0}'.format(t1[3]))
        self.print('Max Record Size           : {0}'.format(t1[4]))    

def get_sel_entries(self):
    _, rec, *_  = self.intf.issue_cmd(GetSELInfo)
    if rec == 0:  yield None

    # Get SEL Entry
    next_id, *sel1 = self.intf.issue_cmd(GetSELEntry, b'\0')
    yield sel1
    sel_count = 1

    while next_id != b'\xff\xff':
        if sel_count > rec: break   # already got more SELs than the total # 
        next_id, *sel1 = self.intf.issue_cmd(GetSELEntry, next_id)
        yield sel1
        sel_count += 1

def _conv_sel_event(event, event_reading_type, sensor_type):
    ret = '(unknown)'

    if event_reading_type >= 1 and event_reading_type <= 0x0c:
        # generic
        events = GENERIC_EVENT_TYPES[event_reading_type]
    elif event_reading_type == 0x6f:
        # sensor-specific
        if sensor_type in SPECIFIC_EVENT_TYPES.keys():
            events = SPECIFIC_EVENT_TYPES[sensor_type]
        else:
            return ret
    else:
        return ret

    if event < len(events):
        ret = events[event]

    return ret

def print_sel_list(self, sel_all, opt=1, sensor_map=None):
    if not sel_all:
        self.print('No SEL entries.')
        return

    for sel1 in sel_all:
        rec_id = sel1[0]
        rec_type = sel1[1]
        if rec_type >= 0xe0:  ts = '(OEM Non-Timestamped)'
        else:  ts = conv_time(sel1[2])

        sensor_type = sel1[5]
        sensor_num = sel1[6]
        event_dir = 'Deassertion' if (sel1[7] & 0x80) >> 7 else 'Assertion'
        event_type = sel1[7] & 0x7f
        event = sel1[8] & 0x0f

        sensor_type_str = conv_sensor_type(sel1[5])
        event_str = _conv_sel_event(event, event_type, sensor_type)

        if opt == 1:
            self.print('{0:>4x} | {1} | {2} #{3:02X}h | {4} | {5}'.format(
                  rec_id, ts, sensor_type_str, sensor_num, event_str, event_dir))
        else:
            sdr_entries = sensor_map.get(sensor_num, None)
            if sdr_entries:
                sensor_name, *_ = sdr_entries[0]
            else:
                sensor_name = '#{0:02X}h'.format(sensor_num)

            if opt == 2:
                self.print('{0:>4x} | {1} | {2}: {3} | {4} | {5}'.format(
                      rec_id, ts, sensor_type_str, sensor_name, event_str, event_dir))
            else:
                gen_id = sel1[3]
                evm_rev = sel1[4]
                event_data = '{0:02x}{1:02x}{2:02x}'.format(sel1[8], sel1[9], sel1[10])
                if rec_type == 2:
                    rec_type_str = 'System Event Record (02h)'
                elif rec_type >= 0xc0 and rec_type <= 0xdf:
                    rec_type_str = 'OEM Timestamped ({0:02X}h)'.format(rec_type)
                elif rec_type >= 0xe0:
                    rec_type_str = 'OEM Non-Timestamped ({0:02X}h)'.format(rec_type)
                else:
                    rec_type_str = 'Unknown ({0:02X}h)'.format(rec_type)

                self.print('SEL Record ID              : {0:04x}'.format(rec_id))
                self.print('    Record Type            : ' + rec_type_str)
                self.print('    Timestamp              : ' + ts)
                self.print('    Generator ID           : {0:04x}'.format(gen_id))
                self.print('    EvM Revision           : {0:02x}'.format(evm_rev))
                self.print('    Sensor Type            : ' + sensor_type_str)
                self.print('    Sensor                 : {0} ({1:02X}h)'.format(sensor_name, sensor_num))
                self.print('    Event Type             : ' + conv_event_reading(event_type, True))
                self.print('    Event Direction        : ' + event_dir)
                self.print('    Event Data             : ' + event_data)
                self.print('    Description            : ' + event_str)
                self.print('')

def _sel_list(self, argv):
    if argv[0] == 'elist' or argv[0] == 'vlist':
        sensor_map = get_sensor_map(self)
    else:
        sensor_map = None

    sel_all = get_sel_entries(self)
    opt, print_hdl = SEL_PRINT_HDL[argv[0]]
    print_hdl(self, sel_all, opt, sensor_map)

def _sel_get(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1)

    rec_id = str2int(argv[1])
    if rec_id == -1:
        raise PyCmdsArgsExcept(3, 0, argv[1])
    rec_id = rec_id.to_bytes(2, 'little')

    # Get SEL Entry
    _, *sel1 = self.intf.issue_cmd(GetSELEntry, rec_id)
    sensor_map = get_sensor_map(self)
    opt, print_hdl = SEL_PRINT_HDL[argv[0]]
    print_hdl(self, (sel1,), opt, sensor_map)

def _sel_clear(self, argv):
    rev, = self.intf.issue_cmd(RevSEL)
    prog, = self.intf.issue_cmd(ClearSEL, rev, 0xaa)

    prog_str = 'unknown'
    if prog == 0:  prog_str = 'in progress'
    elif prog == 1: prog_str = 'completed'
    self.print('SEL Erasure Progress: {0}'.format(prog_str))

def _sel_time(self, argv):
    curr, = self.intf.issue_cmd(GetSELTime)
    self.print('Present Timestamp: {0}'.format(conv_time(curr)))

def _sel_writeraw(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1)

    fout = open(argv[1], 'wb')
    sel_all = get_sel_entries(self)
    for sel1 in sel_all:
        data = struct.pack('<HBLH', sel1[0], sel1[1], sel1[2], sel1[3])
        data += bytes(sel1[4:])
        fout.write(data)

    fout.close()
    self.print('All SEL entries have been written in {0}.'.format(argv[1]))

def _sel_readraw(self, argv):
    # process arguments
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1)

    if len(argv) >= 3:
        view = argv[2]
        if view not in ('list', 'elist', 'vlist'):
            raise PyCmdsArgsExcept(3, 0, view)
    else:
        view = 'list'

    if view in ('elist', 'vlist'):
        sensor_map = get_sensor_map(self)
    else:
        sensor_map = None

    # read SEL entries
    fin = open(argv[1], 'rb')
    data = fin.read(16)
    sel_all = []
    while data:
        sel1 = struct.unpack('<HBLHBBBBBBB', data)
        sel_all.append(sel1)
        data = fin.read(16)

    fin.close()

    # print SEL entries
    opt, print_hdl = SEL_PRINT_HDL[view]
    print_hdl(self, sel_all, opt, sensor_map)    

def help_sel(self, argv=None, context=0):
    self.print('SEL Commands:')
    self.print('    list | elist | vlist')
    self.print('    get <record_id>')
    self.print('    clear')
    self.print('    time')
    self.print('    info')
    self.print('    writeraw <output file>')
    self.print('    readraw <input file> [list | elist | vlist]')
    self.print('    help')

SEL_CMDS = {
    'info': _sel_info,
    'list': _sel_list,
    'elist': _sel_list,
    'vlist': _sel_list,
    'get': _sel_get,
    'clear': _sel_clear,
    'time': _sel_time,
    'writeraw': _sel_writeraw,
    'readraw': _sel_readraw,
    'help': help_sel,    
}

SEL_PRINT_HDL = {
    'list': (1, print_sel_list),
    'elist': (2, print_sel_list),
    'vlist': (4, print_sel_list),
    'get': (4, print_sel_list),
}

def do_sel(self, argv):
    do_command(self, argv, help_sel, SEL_CMDS)
