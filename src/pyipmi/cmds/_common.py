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
import time, sys, builtins
from collections import defaultdict
from . _consts import *
from .. mesg.ipmi_se import *
from .. mesg.ipmi_storage import GetSDRRepoInfo, GetSDR
from .. util.exception import PyExcept, PyCmdsExcept

g_add_ts = 0
g_erase_ts = 0
g_sdr_repo = defaultdict(list)
g_sensor_map = {}

conv_time = lambda ts: time.asctime(time.localtime(ts))

def bcd2str(bcd, rev=False):
    # for 1 byte only
    s1 = bcd & 0x0f
    s2 = (bcd & 0xf0) >> 4
    
    if not rev:
        ret = '{0}{1}'.format(s2, s1)        
    else: 
        ret = '{0}.{1}'.format(s1, s2)        

    return ret

def str2int(org, default=-1):
    if type(org) is not str: return default
    org = org.strip()

    try:
        if org[:2] in ('0x', '0X'):
            ret = int(org, 16)
        else:
            ret = int(org)
    except:
        ret = default
    finally:
        return ret

def get_chnl(argv):
    chnl = -1    
    if argv: chnl = str2int(argv[0])
    if chnl < 0:  chnl = 0x0e    

    return chnl

def _cal_twos_complement(val, bits):
    ret = val
    if val & (1 << (bits - 1)):  # minus        
        ret = val - (1 << bits)

    return ret

def _cal_threshold_sensor_reading(x, sdr):
    # y = L[(Mx + (B * 10^K1)) * 10^K2] units
    M = _cal_twos_complement(((sdr[20] & 0xc0) << 2) + sdr[19], 10)
    B = _cal_twos_complement(((sdr[22] & 0xc0) << 2) + sdr[21], 10)
    K1 = _cal_twos_complement(sdr[24] & 0x0f, 4)
    K2 = _cal_twos_complement(sdr[24] >> 4, 4)

    y = (M * x + (B * (10 ** K1))) * (10 ** K2)

    return y

def _cal_discrete_sensor_reading(t1):
    reading = 0
    if len(t1) >= 4:
        reading = (t1[3] << 8) + t1[2]

    return reading

def _conv_units(sdr):
    unit = sdr[15]
    base = sdr[16]
    mod = sdr[17]
    ret = ''

    if unit & 1:
        ret = 'percent'
    else:
        if base > 0 and base < len(BASE_UNITS):
            ret = BASE_UNITS[base]

        if mod > 0 and mod < len(BASE_UNITS):
            mod_str = BASE_UNITS[mod]
            unit_mod = (unit >> 1) & 3
            if unit_mod == 2:
                ret += ' / ' + mod_str
            elif unit_mod == 3:
                ret += ' * ' + mod_str

    unit_rate = (unit & 0x3f) >> 3
    if unit_rate > 0 and unit_rate < len(RATE_UNITS):
        ret += ' ' + RATE_UNITS[unit_rate]

    return ret

def _conv_sensor_name(sdr_type, sdr):
    start = (0, 43, 27, 12)[sdr_type]
    return sdr[start:].decode('latin_1')

def _conv_sensor_reading(t1, sdr_type, sdr1, with_units=True, with_raw_reading=False):
    event_reading_type = sdr1[8]
    reading_str = '0'

    if sdr_type == 1:
        if event_reading_type == 1:  # threshold-based
            reading = _cal_threshold_sensor_reading(t1[0], sdr1)                    
            if type(reading) is float:
                reading_str = '{0:.03f}'.format(reading)
            else:
                reading_str = str(reading)

            if with_units: reading_str += ' ' + _conv_units(sdr1)
        else:   # discrete
            reading = _cal_discrete_sensor_reading(t1)
            reading_str = '0x{0:04x}'.format(reading)
    else:   # sdr_type == 2
        if event_reading_type == 1:  # threshold-based
            reading_str = str(t1[0])  # couldn't calculate y = Mx + B  
            if with_units: reading_str += ' ' + _conv_units(sdr1)
        else:   # discrete
            reading = _cal_discrete_sensor_reading(t1)
            reading_str = '0x{0:04x}'.format(reading)

    if with_raw_reading:
        return (reading, reading_str)
    else:
        return reading_str

def conv_entity_id(eid):
    if eid >= 0x90 and eid <= 0xaf:
        ret = 'Chassis-Specific'
    elif eid >= 0xb0 and eid <= 0xcf:
        ret = 'Board-Set Specific'
    elif eid >= 0xd0 and eid <= 0xff:
        ret = 'OEM'
    else:
        ret = ENTITY_ID_CODES.get(eid, 'Reserved')
    
    return ret

def _conv_entity(sdr):
    entity = sdr[3]
    entity_inst = sdr[4] & 0x7f
    entity_str = '{0}.{1:02}'.format(entity, entity_inst)

    entity_name = conv_entity_id(entity)

    return (entity_str, entity_name)

def _conv_threshold(sdr, reading, opt=0):
    # opt = 0: reading
    # opt = 1: event mask
    ret = []
    events = ('lnc', 'lcr', 'lnr', 'unc', 'ucr', 'unr')
    
    if opt == 0:
        mask = (((sdr[12] >> 4) & 7) << 3) + ((sdr[10] >> 4) & 7)
    else:
        mask = 0xff

    for i in range(5):
        if mask & 1 and reading & 1:
            ret.append(events[i])
        mask >>= 1
        reading >>= 1

    return ret

def _conv_discrete(sdr, val, opt=0, output=list):
    # opt = 0: reading
    # opt = 1: event mask
    ret = []
    sensor_type = sdr[7]
    event_reading_type = sdr[8]    

    if opt == 0:
        mask = (sdr[14] << 8) + sdr[13]
    else:
        mask = 0xffff

    if event_reading_type >= 2 and event_reading_type <= 0x0c:
        # generic
        events = GENERIC_EVENT_TYPES[event_reading_type]
    elif event_reading_type == 0x6f:
        # sensor-specific
        if sensor_type in SPECIFIC_EVENT_TYPES.keys():
            events = SPECIFIC_EVENT_TYPES[sensor_type]
        else:
            return '' if output is str else []
    else:
        return '' if output is str else []

    for i in range(14):
        if mask & 1 and val & 1:
            ret.append(events[i])
        mask >>= 1
        val >>= 1

    if output is str:
        ret_str = ''
        for i in ret:
            if ret_str:  ret_str += ', ' + i
            else:  ret_str = i
                
        return ret_str
    else:
        return ret

def _conv_event_mask(sdr, opt=0):
    # opt = 0: assertion event mask
    # opt = 1: deassertion event mask
    event_reading_type = sdr[8]
    ret = []

    if event_reading_type == 1:     # threshold-based
        events = ('lnc-', 'lnc+', 'lcr-', 'lcr+', 'lnr-', 'lnr+',
                  'unc-', 'unc+', 'ucr-', 'ucr+', 'unr-', 'unr+')
        
        if opt == 0:    # assertion
            mask = ((sdr[10] & 0x3f) << 8) + sdr[9]
        else:   # deassertion
            mask = ((sdr[12] & 0x3f) << 8) + sdr[11]

        for i in range(11):
            if mask & 1: ret.append(events[i])
            mask >>= 1

    else:   # discrete
        if opt == 0:    # assertion
            mask = ((sdr[10] & 0x7f) << 8) + sdr[9]
        else:   # deassertion
            mask = ((sdr[12] & 0x7f) << 8) + sdr[11]

        ret = _conv_discrete(sdr, mask, 1)

    return ret

def conv_sensor_type(sensor_type):
    if sensor_type > 0 and sensor_type < len(SENSOR_TYPES):
        ret = SENSOR_TYPES[sensor_type]
    elif sensor_type >= 0xc0 and sensor_type <= 0xff:
        ret = 'OEM'
    else:
        ret = 'Reserved'

    return ret

def conv_event_reading(event_reading, ext=False):
    if event_reading == 1:
        ret = 'threshold' if not ext else 'Threshold'
    elif event_reading >= 2 or event_reading <= 0xc:
        ret = 'discrete' if not ext else 'Generic Discrete'
    elif event_reading == 0x6f:
        ret = 'discrete' if not ext else 'Sensor-Specific Discrete'
    elif event_reading >= 0x70 or event_reading <= 0x7f:
        ret = 'OEM'
    else:
        ret = 'n/a'

    return ret

def _conv_sensor_type_and_er(sdr):
    sensor_type = sdr[7]
    event_reading = sdr[8]

    ret = conv_sensor_type(sensor_type) + ' ('
    ret +=  conv_event_reading(event_reading) + ')'

    return ret

def _conv_threshold_values(sdr1, opt=0, argv=None):
    # opt = 0: get everything from SDR
    # opt = 1: convert thresholds from input
    # opt = 2: convert hystersis from input
    thres = []

    if opt in (0, 1):
        # lnc, lc, lnr, unc, uc, unr        
        thres_sdr = (36, 35, 34, 33, 32, 31)
        m = sdr1[13] & 0x3f

        for i in range(0, 6):
            s = thres_sdr[i]
            raw = sdr1[s] if opt == 0 else argv[i]
            if m & 1: thres.append(_conv_sensor_reading((raw,), 1, sdr1, False))
            else:  thres.append('na')
            m >>= 1

    if opt == 0:
        # n_reading, n_max, n_min, pos_hys, neg_hys
        thres_sdr2 = (26, 27, 28, 37, 38)
        m2 = (1, 1, 1, sdr1[37], sdr1[38])

        for i in range(0, 5):
            s = thres_sdr2[i]
            if m2[i]: thres.append(_conv_sensor_reading((sdr1[s],), 1, sdr1, False))
            else:  thres.append('na')

    if opt == 2:
        for x in argv:
            if x: thres.append(_conv_sensor_reading((x,), 1, sdr1, False))
            else:  thres.append('na')

    return thres

def load_sdr_repo(self):
    next_id = b'\0'
    sdr_count = 0

    def load_one_sdr():
        nonlocal next_id, sdr_count

        # Get SDR: Resv ID (2) | Rec ID (2) | offset (1) | bytes_to_read (1)
        sdr1 = self.intf.issue_cmd(GetSDR, b'\0', next_id, 0, 0xff)
        next_id = sdr1[:2]
        rec_type = sdr1[5]
        g_sdr_repo[rec_type].append(sdr1[7:])
        sdr_count += 1

        # Handle sensor map
        if rec_type in (1, 2, 3):
            sdr2 = sdr1[7:]
            sensor_num = sdr2[2]    # Sensor number
            sensor_name = _conv_sensor_name(rec_type, sdr2)  # Sensor name

            entity_str, entity_name, units, sensor_type = '', '', '', ''
            thres = ['na'] * 11
            mask_r, mask_s, asserts, deasserts = [], [], [], []
            mask = sdr2[13] & 0x3f

            if rec_type in (1, 2):
                event_reading_type = sdr2[8]
                entity_str, entity_name = _conv_entity(sdr2)
                units = _conv_units(sdr2)
                sensor_type = _conv_sensor_type_and_er(sdr2)
                asserts = _conv_event_mask(sdr2, 0)
                deasserts = _conv_event_mask(sdr2, 1)

                if event_reading_type == 1:
                    mask_r = _conv_threshold(sdr2, mask, 1)
                    mask_s = _conv_threshold(sdr2, sdr2[14] & 0x3f, 1)

                    if rec_type == 1:
                        thres = _conv_threshold_values(sdr2)
                else:
                    mask_r = _conv_discrete(sdr2, ((sdr2[14] & 0x7f) << 8) + sdr2[13], 1)

            g_sensor_map[sensor_num] = (sensor_name, rec_type, len(g_sdr_repo[rec_type]) - 1, 
                entity_str, entity_name, units, thres, mask_r, mask_s,
                sensor_type, asserts, deasserts)

    global g_add_ts, g_erase_ts, g_sensor_map
    _, rec, _, add_ts, erase_ts, _ = self.intf.issue_cmd(GetSDRRepoInfo)
    if rec == 0:  
        raise PyCmdsExcept('SDR repository is empty.', False)

    if g_sdr_repo:
        if add_ts == g_add_ts and erase_ts == g_erase_ts:
            # no change on the SDR repository
            return False
        else:
            # SDR has changes and it's not empty
            # clear the previous SDRs before getting the new ones
            g_sdr_repo.clear()
            g_sensor_map.clear()

    #self.print('Loading {0} SDRs...\n'.format(rec))

    load_one_sdr()
    while next_id != b'\xff\xff':
        if sdr_count > rec: break   # already got more SDRs than the total # 
        load_one_sdr()

    g_add_ts = add_ts
    g_erase_ts = erase_ts
    g_sensor_map = dict(sorted(g_sensor_map.items()))

    return True

def get_sdr_repo(self):
    load_sdr_repo(self)
    return g_sdr_repo

def get_sensor_map(self):
    load_sdr_repo(self)
    return g_sensor_map    

def get_sensor_readings(self, opt=1, filter_sdr=0, filter_sensor_type=0, ext=False):
    load_sdr_repo(self)
    
    for sensor_num in g_sensor_map.keys():
        (sensor_name, sdr_type, idx, entity_str, entity_name, units, 
         thres, mask_r, mask_s, sensor_type, asserts, deasserts) = g_sensor_map[sensor_num]

        if sdr_type == 3:   continue    # Do not handle Event-Only SDRs here

        sdr1 = g_sdr_repo[sdr_type][idx]
        event_reading_type = sdr1[8]

        # filter SDR type
        if filter_sdr != 0 and filter_sdr != sdr_type:
            continue

        # filter sensor type
        if filter_sensor_type != 0 and filter_sensor_type != sdr1[7]:
            continue

        # IPMI: Get sensor reading 
        try:
            t1 = self.intf.issue_cmd(GetSensorReading, sensor_num)
        except:
            continue

        # Sensor status
        stat = (t1[1] & 0x7f) >> 5
        stat_str = ('ns', 'na', 'ok', 'ns')[stat]

        # Convert the sensor reading to human readable format
        if stat == 2:
            if opt == 3:
                reading_str = _conv_sensor_reading(t1, sdr_type, sdr1, False)
            else:
                reading, reading_str = _conv_sensor_reading(t1, sdr_type, sdr1, True, True)                    
        elif stat & 2 == 0:
            reading_str = 'disabled'
        else:
            reading_str = 'not available'

        if opt in (1, 2):    # sdr list, sdr elist
            if opt == 2:
                if event_reading_type != 1:     
                    reading_str = _conv_discrete(sdr1, reading, 0, str)

            yield (sensor_num, sensor_name, reading_str, stat_str, entity_str)
            continue

        # The remaining is for opt == 3 or 4, i.e. sdr slist/vlist or sensor list/vlist        
        if ext:  # In ext mode, overwrite the thresholds from SDR with the ones from command
            try:
                # Get Sensor Thresholds command
                argv = self.intf.issue_cmd(GetSensorThres, sensor_num)
                thres[:6] = _conv_threshold_values(sdr1, 1, argv[1:])
            except:
                pass

        if opt == 3:  # sdr slist or sensor list
            ret = [sensor_num, sensor_name, reading_str, units, stat_str,] + thres[:6]
            yield ret
            continue

        # The remaining is all for opt == 4, i.e. sdr vlist or sensor vlist
        if ext:  # In ext mode, overwrite the hysteresis from SDR with the ones from command
            try:
                # Get Sensor Hysteresis command
                argv = self.intf.issue_cmd(GetSensorHys, sensor_num)
                thres[9:] = _conv_threshold_values(sdr1, 2, argv)
            except:
                pass

        # Get absolute values of Hysteresis
        thres[9:] = [x[1:] if x[0] == '-' else x for x in thres[9:]]

        if event_reading_type != 1:
            asserted_events = _conv_discrete(sdr1, reading)
        else:
            if len(t1) >= 3:
                asserted_events = _conv_threshold(sdr1, t1[2] & 0x3f)   
            else:
                asserted_events = []
                
        ret = [sensor_num, sensor_name, entity_str, entity_name, sensor_type, reading_str, stat_str,]
        ret += thres
        ret += [asserts, deasserts, event_reading_type, asserted_events, mask_r, mask_s,]
                            
        yield ret

def print_sensor_list1(self, reading_all):
    for sensor_num, sensor_name, reading, stat, _ in reading_all:
        fmt = '{0:02X}h | {1:16} | {2:16} | {3}' 
        self.print(fmt.format(sensor_num, sensor_name, reading, stat))

def print_sensor_list2(self, reading_all):
    for num, name, reading, stat, entity in reading_all:
        fmt = '{0:02X}h | {1:16} | {3:>5} | {2} | {4}' 
        self.print(fmt.format(num, name, stat, entity, reading))

def print_sensor_list3(self, reading_all):
    for (sensor_num, sensor_name, reading, unit, stat, 
         lnc, lc, lnr, unc, uc, unr) in reading_all:
        if reading == 'not available':  reading = 'na'
        if reading == 'disabled':  reading = 'ns'

        fmt = '{0:02X}h | {1:16} | {2:8} | {3:10} | {4}' 
        fmt += ' | {7:7} | {6:7} | {5:7} | {8:7} | {9:7} | {10:7}'

        self.print(fmt.format(sensor_num, sensor_name, reading, unit, stat,
                         lnc, lc, lnr, unc, uc, unr))

def print_sensor_list4(self, reading_all):
    def print_threshold_events(title, events):
        if events:
            self.print(title, end=' ')
            for i in events:
                self.print(i, end=' ')
            self.print('')

    def print_discrete_events(title, events):
        if events:
            self.print(title + ' [' + events[0] + ']')
            for i in events[1:]:
                self.print(' ' * 25 + '[' + i + ']')

    for (sensor_num, sensor_name, entity_str, entity_name, sensor_type, 
         reading_str, stat_str, lnc, lc, lnr, unc, uc, unr, n_reading, n_max, n_min,
         pos_hys, neg_hys, asserts, deasserts, er_type, asserted_events, 
         mask_r, mask_s) in reading_all:

        self.print('Sensor ID              : {0} ({1:02X}h)'.format(sensor_name, sensor_num))
        self.print('  Entity ID            : ' + entity_str + ' (' + entity_name + ')')        
        self.print('  Sensor Type          : ' + sensor_type)
        self.print('  Sensor Reading       : ' + reading_str)
        self.print('  Status               : ' + stat_str)

        if er_type == 1:    # threshold
            self.print('  Nominal Reading      : ' + n_reading)
            self.print('  Normal Minimum       : ' + n_min)
            self.print('  Normal Maximum       : ' + n_max)
            if unr != 'na': self.print('  Upper Non-Recoverable: ' + unr)
            if uc != 'na':  self.print('  Upper Critical       : ' + uc)
            if unc != 'na': self.print('  Upper Non-Critical   : ' + unc)
            if lnc != 'na': self.print('  Lower Non-Critical   : ' + lnc)
            if lc != 'na':  self.print('  Lower Critical       : ' + lc)
            if lnr != 'na': self.print('  Lower Non-recoverable: ' + lnr)
            if pos_hys != 'na': self.print('  Positive Hysteresis  : ' + pos_hys)
            if neg_hys != 'na': self.print('  Negative Hysteresis  : ' + neg_hys)
            
            print_func = print_threshold_events
            print_func('  Readable Thresholds  :', mask_r)
            print_func('  Settable Thresholds  :', mask_s)

        else:   # discrete
            print_func = print_discrete_events
            print_func('  Reading Mask         :', mask_r)

        print_func('  Asserted Events      :', asserted_events)
        print_func('  Assertions Enabled   :', asserts)
        print_func('  Deassertions Enabled :', deasserts)

        self.print(' ')

def print_sensor_type_list(self):
    self.print('Sensor Types:')
    self.print('    Temperature               (0x01)   Voltage                   (0x02)')
    self.print('    Current                   (0x03)   Fan                       (0x04)')
    self.print('    Physical Security         (0x05)   Platform Security         (0x06)')
    self.print('    Processor                 (0x07)   Power Supply              (0x08)')
    self.print('    Power Unit                (0x09)   Cooling Device            (0x0a)')
    self.print('    Other                     (0x0b)   Memory                    (0x0c)')
    self.print('    Drive Slot / Bay          (0x0d)   POST Memory Resize        (0x0e)')
    self.print('    System Firmwares          (0x0f)   Event Logging Disabled    (0x10)')
    self.print('    Watchdog1                 (0x11)   System Event              (0x12)')
    self.print('    Critical Interrupt        (0x13)   Button                    (0x14)')
    self.print('    Module / Board            (0x15)   Microcontroller           (0x16)')
    self.print('    Add-in Card               (0x17)   Chassis                   (0x18)')
    self.print('    Chip Set                  (0x19)   Other FRU                 (0x1a)')
    self.print('    Cable / Interconnect      (0x1b)   Terminator                (0x1c)')
    self.print('    System Boot Initiated     (0x1d)   Boot Error                (0x1e)')
    self.print('    OS Boot                   (0x1f)   OS Critical Stop          (0x20)')
    self.print('    Slot / Connector          (0x21)   System ACPI Power State   (0x22)')
    self.print('    Watchdog2                 (0x23)   Platform Alert            (0x24)')
    self.print('    Entity Presence           (0x25)   Monitor ASIC              (0x26)')
    self.print('    LAN                       (0x27)   Management Subsys Health  (0x28)')
    self.print('    Battery                   (0x29)   Session Audit             (0x2a)')
    self.print('    Version Change            (0x2b)   FRU State                 (0x2c)')

def do_command(self, argv, help_func, cmd_map):
    if type(argv) is str:
        argv = argv.split(' ')
        argv = [x.strip() for x in argv if x.strip() != '']

    try:
        if len(argv) == 0:
            raise PyCmdsExcept('No input command.')

        if argv[0] not in cmd_map.keys():
            raise PyCmdsExcept('Command ' + argv[0] + ' is not supported.')

        # Pass the arguments to the corresponding command handler
        cmd_map[argv[0]](self, argv)    

    except PyCmdsExcept as e:
        builtins.print(e, '\n')
        if e.context >= 0:  help_func(self, argv, e.context)

    except BaseException as e:
        builtins.print(e)

def print(self, *objects, sep=' ', end='\n', flush=False):
    builtins.print(*objects, sep=sep, end=end, file=self.print_file, flush=flush)

def print_rsp(self, rsp):
    self.print(' '.join(('{0:02x}'.format(i) for i in rsp)))
