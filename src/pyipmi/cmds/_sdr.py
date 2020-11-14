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
from .. mesg.ipmi_storage import GetSDRRepoInfo, GetSDRRepoAllocInfo
from . _common import get_sensor_readings, print_sensor_list1, print_sensor_list2, \
                    print_sensor_list3, print_sensor_list4, conv_time, do_command, \
                    bcd2str, str2int, get_sdr_repo, conv_sensor_type, conv_entity_id, \
                    print_sensor_type_list
from . _consts import TupleExt, ENTITY_DEVICE_CODES
from .. util.exception import PyCmdsArgsExcept

def _get_event_sdr(self, opt):
    sdr_repo = get_sdr_repo(self)

    for sdr1 in sdr_repo[3]:
        sensor_num = sdr1[2]
        entity_id = sdr1[3]
        entity_inst = sdr1[4] & 0x7f
        sensor_name = sdr1[12:].decode('latin_1')

        if opt in (1, 2, 3):
            yield (sensor_num, entity_id, entity_inst, sensor_name)
        else:
            sensor_type_id = sdr1[5]
            sensor_type = conv_sensor_type(sensor_type_id)
            sensor_type += ' ({0:02X}h)'.format(sensor_type_id)

            entity_str = conv_entity_id(entity_id)
            yield (sensor_num, entity_id, entity_inst, sensor_name, sensor_type, entity_str)


def _get_fru_sdr(self, opt):
    sdr_repo = get_sdr_repo(self)

    for sdr1 in sdr_repo[0x11]:
        if sdr1[2] & 0x80 == 0:
            fru_type = 'Physical FRU'  
            fru_id = '{0}:{1:02x}h'.format(sdr1[2] & 7, sdr1[1])
        else:
            fru_type = 'Logical FRU'
            fru_id = '{0:02x}h'.format(sdr1[1])

        entity_id = sdr1[7]
        entity_inst = sdr1[8] 
        fru_name = sdr1[11:].decode('latin_1')

        if opt in (1, 2, 3):
            yield (fru_name, entity_id, entity_inst, fru_type, fru_id)
        else:
            chnl = sdr1[3]
            dev_type = sdr1[5]
            dev_mod = sdr1[6]
            dev_acc_addr = sdr1[0]
            if dev_type == 0x10:  dev_type_idx = (dev_type << 8) + dev_mod
            else: dev_type_idx = dev_type

            entity_str = conv_entity_id(entity_id)
            dev_type_str = ENTITY_DEVICE_CODES.get(dev_type_idx, '')

            yield (fru_name, entity_id, entity_inst, fru_type, fru_id, chnl,
                   entity_str, dev_type_str, dev_type, dev_mod, dev_acc_addr)

def _get_mcloc_sdr(self, opt):
    sdr_repo = get_sdr_repo(self)

    for sdr1 in sdr_repo[0x12]:
        mc_type = 'Dynamic MC' if sdr1[2] & 0x20 == 0 else 'Static MC'
        mc_id = '{0:02X}h'.format(sdr1[0])

        entity_id = sdr1[7]
        entity_inst = sdr1[8] 
        mc_name = sdr1[11:].decode('latin_1')

        if opt in (1, 2, 3):            
            yield (mc_name, entity_id, entity_inst, mc_type, mc_id)
        else:
            entity_str = conv_entity_id(entity_id)
            chnl = sdr1[1]
            acpi = ('Not Required', 'Required')
            acpi_sys = acpi[(sdr1[2] & 0x80) >> 7]
            acpi_dev = acpi[(sdr1[2] & 0x40) >> 6]
            log_init_agent = ('No', 'Yes')[(sdr1[2] & 8) >> 3]            
            event_gen = ('Enabled', 'Disabled', 'Do Not Init Controller', '')[sdr1[2] & 3]

            caps = sdr1[3]
            list_caps = []
            cap_names = ('Sensor Device', 'SDR Repository Device', 'SEL Device', 
                'FRU Inventory Device', 'IPMB Event Receiver', 'IPMB Event Generator',
                'Bridge', 'Chassis Device')

            idx = 0
            while caps:
                if caps & 1: list_caps.append(cap_names[idx])
                caps >>= 1 
                idx += 1

            yield (mc_name, entity_id, entity_inst, mc_type, mc_id, entity_str, chnl,
                   acpi_sys, acpi_dev, log_init_agent, event_gen, list_caps)

def _sdr_list_event(self, opt=1, hdl=None):
    if opt in (1, 3):
        for num, *_, name in _get_event_sdr(self, opt):
            self.print('{0:02X}h | {1:16} | Event-Only'.format(num, name))
    elif opt == 2:
        for num, entity_id, entity_inst, name in _get_event_sdr(self, opt):
            self.print('{0:02X}h | {1:16} | {2:>2}.{3:02} | Event-Only'.format( 
                  num, name, entity_id, entity_inst))
    else:
        for sensor_num, entity_id, entity_inst, sensor_name, sensor_type,\
            entity_str in _get_event_sdr(self, opt):

            self.print('Sensor ID        : {0} ({1:02X}h)'.format(sensor_name, sensor_num))
            self.print('Entity ID        : {0}.{1}'.format(entity_id, entity_inst), end='')

            if entity_str != '': self.print(' (' + entity_str + ')')
            else: self.print('')
            self.print('Sensor Type      : ' + sensor_type)
            self.print('')

def _sdr_list_fru(self, opt=1, hdl=None):
    if opt in (1, 3):
        for fru_name, _, _, fru_type, fru_id in _get_fru_sdr(self, opt):
            self.print('--- | {0:16} | {1} @ {2}'.format( 
                  fru_name, fru_type, fru_id))
    elif opt == 2:
        for fru_name, entity_id, entity_inst, fru_type, fru_id in _get_fru_sdr(self, opt):
            self.print('--- | {0:16} | {1:>2}.{2:02} | {3} @ {4}'.format( 
                  fru_name, entity_id, entity_inst, fru_type, fru_id))
    else:
        for fru_name, entity_id, entity_inst, fru_type, fru_id, chnl, entity_str,\
            dev_type_str, dev_type, dev_mod, dev_acc_addr in _get_fru_sdr(self, opt):

            self.print('Device ID               : ' + fru_name)
            self.print('Entity ID               : {0}.{1}'.format(entity_id, entity_inst), end='')

            if entity_str != '': self.print(' (' + entity_str + ')')
            else: self.print('')

            self.print('Device Access Address   : {0:02X}h'.format(dev_acc_addr))
            self.print(fru_type + ' Device      : ' + fru_id)
            self.print('Channel Number          : {0}'.format(chnl))            
            
            self.print('Device Type             : {0:02X}h.{1:02X}h'.format(dev_type, dev_mod), end='')
            if dev_type != '': self.print(' (' + dev_type_str + ')')
            else: self.print('')

            self.print('')

def _sdr_list_mcloc(self, opt=1, hdl=None):
    if opt in (1, 3):
        for mc_name, _, _, mc_type, mc_id in _get_mcloc_sdr(self, opt):
            self.print('--- | {0:16} | {1} @ {2}'.format(
                  mc_name, mc_type, mc_id))
    elif opt == 2:
        for mc_name, entity_id, entity_inst, mc_type, mc_id in _get_mcloc_sdr(self, opt):
            self.print('--- | {0:16} | {1:>2}.{2:02} | {3} @ {4}'.format(
                  mc_name, entity_id, entity_inst, mc_type, mc_id))
    else:
        for mc_name, entity_id, entity_inst, mc_type, mc_id, entity_str, chnl, acpi_sys,\
            acpi_dev, log_init_agent, event_gen, list_caps in _get_mcloc_sdr(self, opt):

            self.print('Device ID               : ' + mc_name)
            self.print('Entity ID               : {0}.{1}'.format(entity_id, entity_inst), end='')

            if entity_str != '': self.print(' (' + entity_str + ')')
            self.print('Device Slave Address    : ' + mc_id)
            self.print('Channel Number          : {0}'.format(chnl))
            self.print('ACPI System P/S Notif   : ' + acpi_sys)
            self.print('ACPI Device P/S Notif   : ' + acpi_dev)
            self.print('Controller Presence     : ' + mc_type)
            self.print('Logs Init Agent Errors  : ' + log_init_agent)
            self.print('Event Message Gen       : ' + event_gen)

            self.print('Device Capabilities     : ', end='')
            if not list_caps:
                self.print('none')
            else:
                self.print('[{0}]'.format(list_caps[0]))
                for i in list_caps[1:]:
                    self.print(' ' * 26 + '[{0}]'.format(i))            
            self.print('')

def _sdr_list_all(self, opt=1, print_hdl=None):
    # SDR type 1h, 2h
    reading_all = get_sensor_readings(self, opt)
    print_hdl(self, reading_all)

    # Other SDR types
    for key in SDR_PRINT_HDL.keys():
        if key == 'all':    continue
        SDR_PRINT_HDL[key](self, opt, print_hdl)

def _sdr_list(self, argv):
    filter_sdr = 0
    filter_sensor_type = 0
    opt, print_hdl = SENSOR_PRINT_HDL[argv[0]]    

    if len(argv) > 1:
        if argv[1] == 'full':
            filter_sdr = 1
        elif argv[1] == 'compact':
            filter_sdr = 2
        elif argv[1] == 'type':
            if len(argv) > 2:
                filter_sensor_type = str2int(argv[2])
                if filter_sensor_type < 0:
                    raise PyCmdsArgsExcept(4, 0, argv[2])
            else:
                print_sensor_type_list(self)
                return
        else:
            if argv[1] in SDR_PRINT_HDL.keys():
                return SDR_PRINT_HDL[argv[1]](self, opt, print_hdl)
            else:
                raise PyCmdsArgsExcept(2, 0, argv[1])

    reading_all = get_sensor_readings(self, opt, filter_sdr, filter_sensor_type)
    print_hdl(self, reading_all)

def _sdr_info(self, argv):
    ver, rec, free, add_ts, erase_ts, op = self.intf.issue_cmd(GetSDRRepoInfo)
    self.print('SDR Version                         : ' + bcd2str(ver, True))
    self.print('Record Count                        : {0}'.format(rec))
    self.print('Free Space                          : {0} bytes'.format(free))
    self.print('Most Recent Addition                : ' + conv_time(add_ts))
    self.print('Most Recent Erase                   : ' + conv_time(erase_ts))

    UC = 'unspecified'
    update = (op & 0x60) >> 5
    sdr_update_support = (UC, 'non-modal', 'modal', 'both')[update]

    get_op_support = lambda mask: 'yes' if op & mask else 'no'

    self.print('SDR Overflow                        : ' + get_op_support(0x80))
    self.print('SDR Repository Update Supported     : ' + sdr_update_support)
    self.print('Delete SDR Supported                : ' + get_op_support(8))
    self.print('Partial Add SDR Supported           : ' + get_op_support(4))
    self.print('Reserve SDR Repository Supported    : ' + get_op_support(2))
    self.print('SDR Repository Alloc Info Supported : ' + get_op_support(1))    

    if op & 1:
        t1 = self.intf.issue_cmd(GetSDRRepoAllocInfo)

        alloc_units = '{0}'.format(t1[0]) if t1[0] != 0 else UC
        alloc_unit_size = '{0} bytes'.format(t1[1]) if t1[1] != 0 else UC

        self.print('# of Alloc Units                    : ' + alloc_units)
        self.print('Alloc Unit Size                     : ' + alloc_unit_size)
        self.print('# Free Units                        : {0}'.format(t1[2]))
        self.print('Largest Free Blk                    : {0}'.format(t1[3]))
        self.print('Max Record Size                     : {0}'.format(t1[4]))    

def help_sdr(self, argv=None, context=0):
    self.print('SDR Commands:')
    self.print('    list | elist | slist | vlist [options]')
    self.print('        all')
    self.print('        full')
    self.print('        compact')
    self.print('        event')
    self.print('        fru')
    self.print('        mcloc')
    self.print('        type [<sensor_type>]')
    self.print('    info')
    self.print('    help')

SDR_CMDS = {
    'list': _sdr_list,
    'elist': _sdr_list,
    'slist': _sdr_list,
    'vlist': _sdr_list,
    'info': _sdr_info,
    'help': help_sdr,
}

SENSOR_PRINT_HDL = {
    'list': (1, print_sensor_list1),
    'elist': (2, print_sensor_list2),
    'slist': (3, print_sensor_list3),
    'vlist': (4, print_sensor_list4),
}

SDR_PRINT_HDL = {
    'event': _sdr_list_event,
    'fru': _sdr_list_fru,
    'mcloc': _sdr_list_mcloc,
    'all': _sdr_list_all,
}

def do_sdr(self, argv):
    do_command(self, argv, help_sdr, SDR_CMDS)    
