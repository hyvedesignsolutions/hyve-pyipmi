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
class TupleExt(tuple):
    def get(self, idx, default):
        if idx >= len(self):
            return default
        else:
            return self[idx]

    def get_index(self, val, default=-1):
        try:
            idx = super(TupleExt, self).index(val)
        except:
            idx = default
        finally:
            return idx

RATE_UNITS = TupleExt((
    'none', 'per us', 'per ms', 'per s', 'per minute',
    'per hour', 'per day',
))

BASE_UNITS = TupleExt((
    'unspecified', 'degrees C', 'degrees F', 'degrees K', 'Volts',
    'Amps', 'Watts', 'Joules', 'Coulombs', 'VA',
    'Nits', 'lumen', 'lux', 'Candela', 'kPa',
    'PSI', 'Newton', 'CFM', 'RPM', 'Hz',
    'microsecond', 'millisecond', 'second', 'minute', 'hour',
    'day', 'week', 'mil', 'inches', 'feet',
    'cu in', 'cu feet', 'mm', 'cm', 'm',
    'cu cm', 'cu m', 'liters', 'fluid ounce', 'radians',
    'steradians', 'revolutions', 'cycles', 'gravities', 'ounce',
    'pound', 'ft-lb', 'oz-in', 'gauss', 'gilberts',
    'henry', 'millihenry', 'farad', 'microfarad', 'ohms',
    'siemens', 'mole', 'becquerel', 'PPM', 'reserved',
    'Decibels', 'DbA', 'DbC', 'gray', 'sievert',
    'color temp deg K', 'bit', 'kilobit', 'megabit', 'gigabit',
    'byte', 'kilobyte', 'megabyte', 'gigabyte', 'word',
    'dword', 'qword', 'line', 'hit', 'miss', 'retry',
    'reset', 'overflow', 'underrun', 'collision', 'packets',
    'messages', 'characters', 'error', 'correctable error', 'uncorrectable error',
    'fatal error', 'grams',
))

SENSOR_TYPES = TupleExt((
    'reserved', 'Temperature', 'Voltage', 'Current', 'Fan',
    'Physical Security', 'Platform Security', 'Processor', 'Power Supply', 'Power Unit',
    'Cooling Device', 'Other', 'Memory', 'Drive Slot / Bay', 'POST Memory Resize',
    'System Firmwares', 'Event Logging Disabled', 'Watchdog1', 'System Event', 'Critical Interrupt',
    'Button', 'Module / Board', 'Microcontroller', 'Add-in Card', 'Chassis',
    'Chip Set', 'Other FRU', 'Cable / Interconnect', 'Terminator', 'System Boot Initiated',
    'Boot Error', 'OS Boot', 'OS Critical Stop', 'Slot / Connector', 'System ACPI Power State',
    'Watchdog2', 'Platform Alert', 'Entity Presence', 'Monitor ASIC', 'LAN',
    'Management Subsys Health', 'Battery', 'Session Audit', 'Version Change', 'FRU State',
))

ENTITY_ID_CODES = TupleExt((
    'Unspecified',
    'Other',
    'Unknown',
    'Processor',
    'Disk or Disk Bay',
    'Peripheral Bay',
    'System Management Module',
    'System Board',
    'Memory Module',
    'Processor Module',
    'Power Supply',
    'Add-in Card',
    'Front Panel Board',
    'Back Panel Board',
    'Power System Board',
    'Drive Backplane',
    'System Internal Expansion Board',
    'Other System Board',
    'Processor Board',
    'Power Unit',
    'Power Module',
    'Power Management',
    'Chassis Back Panel Board',
    'System Chassis',
    'Sub-Chassis',
    'Other Chassis Board',
    'Disk Drive Bay',
    'Peripheral Bay',
    'Device Bay',
    'Fan Device',
    'Cooling Unit',
    'Cable/Interconnect',
    'Memory Device',
    'System Management Software',
    'BIOS',
    'Operating System',
    'System Bus',
    'Group',
    'Remote Management Device',
    'External Environment',
    'Battery',
    'Processing Blade',
    'Connectivity Switch',
    'Processor/Memory Module',
    'I/O Module',
    'Processor/IO Module',
    'Management Controller Firmware',
    'IPMI Channel',
    'PCI Bus',
    'PCI Express Bus',
    'SCSI Bus (parallel)',
    'SATA/SAS Bus',
    'Processor/Front-Side Bus',
    'Real Time Clock(RTC)',
    'Reserved',
    'Air Inlet',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Reserved',
    'Air Inlet',
    'Processor',
    'Baseboard/Main System Board',
))

ENTITY_DEVICE_CODES = {
    0x01: 'Reserved',
    0x02: 'DS1624 temperature sensor',
    0x03: 'DS1621 temperature sensor',
    0x04: 'LM75 Temperature Sensor',
    0x05: 'Heceta ASIC',
    0x06: 'Reserved',
    0x07: 'Reserved',
    0x08: 'EEPROM, 24C01',
    0x09: 'EEPROM, 24C02',
    0x0a: 'EEPROM, 24C04',
    0x0b: 'EEPROM, 24C08',
    0x0c: 'EEPROM, 24C16',
    0x0d: 'EEPROM, 24C17',
    0x0e: 'EEPROM, 24C32',
    0x0f: 'EEPROM, 24C64',
    0x1000: 'IPMI FRU Inventory',
    0x1001: 'DIMM Memory ID',
    0x1002: 'IPMI FRU Inventory',
    0x1003: 'System Processor Cartridge FRU',
    0x11: 'Reserved',
    0x12: 'Reserved',
    0x13: 'Reserved',
    0x14: 'PCF 8570 256 byte RAM',
    0x15: 'PCF 8573 clock/calendar',
    0x16: 'PCF 8574A I/O Port',
    0x17: 'PCF 8583 clock/calendar',
    0x18: 'PCF 8593 clock/calendar',
    0x19: 'Clock calendar',
    0x1a: 'PCF 8591 A/D, D/A Converter',
    0x1b: 'I/O Port',
    0x1c: 'A/D Converter',
    0x1d: 'D/A Converter',
    0x1e: 'A/D, D/A Converter',
    0x1f: 'LCD Controller/Driver',
    0x20: 'Core Logic (Chip set) Device',
    0x21: 'LMC6874 Intelligent Battery controller',
    0x22: 'Intelligent Batter controller',
    0x23: 'Combo Management ASIC',
    0x24: 'Maxim 1617 Temperature Sensor',
    0xbf: 'Other/Unspecified',
}

GENERIC_EVENT_TYPES = TupleExt((
    TupleExt((
        # 0x00 - Nothing
    )),
    TupleExt((
        # 0x01 - Threshold Based States
        'Lower Non-critical going low',
        'Lower Non-critical going high',
        'Lower Critical going low',
        'Lower Critical going high',
        'Lower Non-recoverable going low',
        'Lower Non-recoverable going high',
        'Upper Non-critical going low',
        'Upper Non-critical going high',
        'Upper Critical going low',
        'Upper Critical going high',
        'Upper Non-recoverable going low',
        'Upper Non-recoverable going high',
    )),
    TupleExt((
        # 0x02 - DMI-based "usage state" States
        'Transition to Idle',
        'Transition to Active',
        'Transition to Busy',
    )),
    TupleExt((
        # 0x03 - DMI-based "usage state" States
        'State Deasserted',
        'State Asserted',
    )),
    TupleExt((
        # 0x04 - DMI-based "usage state" States
        'Predictive Failure Deasserted',
        'Predictive Failure Asserted',
    )),
    TupleExt((
        # 0x05 - DMI-based "usage state" States
        'Limit Not Exceeded',
        'Limit Exceeded',
    )),
    TupleExt((
        # 0x06 - Digital-Discrete Event States
        'Performance Met',
        'Performance Lags',
    )),
    TupleExt((
        # 0x07 - Severity Event States
        'Transition to OK',
        'Transition to Non-critical from OK',
        'Transition to Critical from less severe',
        'Transition to Non-recoverable from less severe',
        'Transition to Non-critical from more severe',
        'Transition to Critical from Non-recoverable',
        'Transition to Non-recoverable',
        'Monitor',
        'Informational',
    )),
    TupleExt((
        # 0x08 - Severity Event States
        'Device Absent',
        'Device Present',
    )),
    TupleExt((
        # 0x09 - Severity Event States
        'Device Disabled',
        'Device Enabled',
    )),
    TupleExt((
        # 0x0a - Availability Status States
        'Transition to Running',
        'Transition to In Test',
        'Transition to Power Off',
        'Transition to On Line',
        'Transition to Off Line',
        'Transition to Off Duty',
        'Transition to Degraded',
        'Transition to Power Save',
        'Install Error',
    )),
    TupleExt((
        # 0x0b - Redundancy States
        'Fully Redundant',
        'Redundancy Lost',
        'Redundancy Degraded',
        'Non-Redundant: Sufficient from Redundant',
        'Non-Redundant: Sufficient from Insufficient',
        'Non-Redundant: Insufficient Resources',
        'Redundancy Degraded from Fully Redundant',
        'Redundancy Degraded from Non-Redundant',
    )),
    TupleExt((
        # 0x0c - ACPI Device Power States
        'D0 Power State',
        'D1 Power State',
        'D2 Power State',
        'D3 Power State',
    )),
))

SPECIFIC_EVENT_TYPES = {
    0x05: TupleExt((
        #  Physical Security
        'General Chassis intrusion',
        'Drive Bay intrusion',
        'I/O Card area intrusion',
        'Processor area intrusion',
        'System unplugged from LAN',
        'Unauthorized dock',
        'FAN area intrusion',
    )),
    0x06: TupleExt((
        #  Platform Security
        'Front Panel Lockout violation attempted',
        'Pre-boot password violation - user password',
        'Pre-boot password violation - setup password',
        'Pre-boot password violation - network boot password',
        'Other pre-boot password violation',
        'Out-of-band access password violation',
    )),
    0x07: TupleExt((
        #  Processor
        'IERR',
        'Thermal Trip',
        'FRB1/BIST failure',
        'FRB2/Hang in POST failure',
        'FRB3/Processor startup/init failure',
        'Configuration Error',
        'SM BIOS Uncorrectable CPU-complex Error',
        'Presence detected',
        'Disabled',
        'Terminator presence detected',
        'Throttled',
        'Uncorrectable machine check exception',
        'Correctable machine check error',
    )),
    0x08: TupleExt((
        #  Power Supply
        'Presence detected',
        'Failure detected',
        'Predictive failure',
        'Power Supply AC lost',
        'AC lost or out-of-range',
        'AC out-of-range, but present',
        'Config Error: Vendor Mismatch',
        'Config Error: Revision Mismatch',
        'Config Error: Processor Missing',
        'Config Error: Power Supply Rating Mismatch',
        'Config Error: Voltage Rating Mismatch',
        'Config Error',
        'Power Supply Inactive',
    )),
    0x09: TupleExt((
        #  Power Unit
        'Power off/down',
        'Power cycle',
        '240VA power down',
        'Interlock power down',
        'AC lost',
        'Soft-power control failure',
        'Failure detected',
        'Predictive failure',
    )),
    0x0c: TupleExt((
        #  Memory
        'Correctable ECC',
        'Uncorrectable ECC',
        'Parity',
        'Memory Scrub Failed',
        'Memory Device Disabled',
        'Correctable ECC logging limit reached',
        'Presence Detected',
        'Configuration Error',
        'Spare',
        'Throttled',
        'Critical Overtemperature',
    )),
    0x0d: TupleExt((
        #  Drive Slot
        'Drive Present',
        'Drive Fault',
        'Predictive Failure',
        'Hot Spare',
        'Parity Check In Progress',
        'In Critical Array',
        'In Failed Array',
        'Rebuild In Progress',
        'Rebuild Aborted',
    )),
    0x0f: TupleExt((
        #  System Firmware Progress
        'Unspecified',
        'No system memory installed',
        'No usable system memory',
        'Unrecoverable IDE device failure',
        'Unrecoverable system-board failure',
        'Unrecoverable diskette failure',
        'Unrecoverable hard-disk controller failure',
        'Unrecoverable PS/2 or USB keyboard failure',
        'Removable boot media not found',
        'Unrecoverable video controller failure',
        'No video device selected',
        'BIOS corruption detected',
        'CPU voltage mismatch',
        'CPU speed mismatch failure',
        'Unknown Error',
        'Unspecified',
        'Memory initialization',
        'Hard-disk initialization',
        'Secondary CPU Initialization',
        'User authentication',
        'User-initiated system setup',
        'USB resource configuration',
        'PCI resource configuration',
        'Option ROM initialization',
        'Video initialization',
        'Cache initialization',
        'SMBus initialization',
        'Keyboard controller initialization',
        'Management controller initialization',
        'Docking station attachment',
        'Enabling docking station',
        'Docking station ejection',
        'Disabling docking station',
        'Calling operating system wake-up vector',
        'System boot initiated',
        'Motherboard initialization',
        'reserved',
        'Floppy initialization',
        'Keyboard test',
        'Pointing device test',
        'Primary CPU initialization',
        'Unknown Hang',
        'Unspecified',
        'Memory initialization',
        'Hard-disk initialization',
        'Secondary CPU Initialization',
        'User authentication',
        'User-initiated system setup',
        'USB resource configuration',
        'PCI resource configuration',
        'Option ROM initialization',
        'Video initialization',
        'Cache initialization',
        'SMBus initialization',
        'Keyboard controller initialization',
        'Management controller initialization',
        'Docking station attachment',
        'Enabling docking station',
        'Docking station ejection',
        'Disabling docking station',
        'Calling operating system wake-up vector',
        'System boot initiated',
        'Motherboard initialization',
        'reserved',
        'Floppy initialization',
        'Keyboard test',
        'Pointing device test',
        'Primary CPU initialization',
        'Unknown Progress',
    )),
    0x10: TupleExt((
        #  Event Logging Disabled
        'Correctable memory error logging disabled',
        'Event logging disabled',
        'Log area reset/cleared',
        'All event logging disabled',
        'Log full',
        'Log almost full',
    )),
    0x11: TupleExt((
        #  Watchdog 1
        'BIOS Reset',
        'OS Reset',
        'OS Shut Down',
        'OS Power Down',
        'OS Power Cycle',
        'OS NMI/Diag Interrupt',
        'OS Expired',
        'OS pre-timeout Interrupt',
    )),
    0x12: TupleExt((
        #  System Event
        'System Reconfigured',
        'OEM System boot event',
        'Undetermined system hardware failure',
        'Entry added to auxiliary log',
        'PEF Action',
        'Timestamp Clock Sync',
    )),
    0x13: TupleExt((
        #  Critical Interrupt
        'NMI/Diag Interrupt',
        'Bus Timeout',
        'I/O Channel check NMI',
        'Software NMI',
        'PCI PERR',
        'PCI SERR',
        'EISA failsafe timeout',
        'Bus Correctable error',
        'Bus Uncorrectable error',
        'Fatal NMI',
        'Bus Fatal Error',
        'Bus Degraded',
    )),
    0x14: TupleExt((
        #  Button
        'Power Button pressed',
        'Sleep Button pressed',
        'Reset Button pressed',
        'FRU Latch',
        'FRU Service',
    )),
    0x19: TupleExt((
        #  Chip Set
        'Soft Power Control Failure',
        'Thermal Trip',
    )),
    0x1b: TupleExt((
        #  Cable/Interconnect
        'Connected',
        'Config Error',
    )),
    0x1d: TupleExt((
        #  System Boot Initiated
        'Initiated by power up',
        'Initiated by hard reset',
        'Initiated by warm reset',
        'User requested PXE boot',
        'Automatic boot to diagnostic',
        'OS initiated hard reset',
        'OS initiated warm reset',
        'System Restart',
    )),
    0x1e: TupleExt((
        #  Boot Error
        'No bootable media',
        'Non-bootable disk in drive',
        'PXE server not found',
        'Invalid boot sector',
        'Timeout waiting for selection',
    )),
    0x1f: TupleExt((
        #  OS Boot
        'A: boot completed',
        'C: boot completed',
        'PXE boot completed',
        'Diagnostic boot completed',
        'CD-ROM boot completed',
        'ROM boot completed',
        'boot completed - device not specified',
        'Installation started',
        'Installation completed',
        'Installation aborted',
        'Installation failed',
    )),
    0x20: TupleExt((
        #  OS Stop/Shutdown
        'Error during system startup',
        'Run-time critical stop',
        'OS graceful stop',
        'OS graceful shutdown',
        'PEF initiated soft shutdown',
        'Agent not responding',
    )),
    0x21: TupleExt((
        #  Slot/Connector
        'Fault Status',
        'Identify Status',
        'Device Installed',
        'Ready for Device Installation',
        'Ready for Device Removal',
        'Slot Power is Off',
        'Device Removal Request',
        'Interlock',
        'Slot is Disabled',
        'Spare Device',
    )),
    0x22: TupleExt((
        #  System ACPI Power State
        'S0/G0: working',
        'S1: sleeping with system hw & processor context maintained',
        'S2: sleeping, processor context lost',
        'S3: sleeping, processor & hw context l',
        'S4: non-volatile sleep/suspend-to-disk',
        'S5/G2: soft-off',
        'S4/S5: soft-off',
        'G3: mechanical off',
        'Sleeping in S1/S2/S3 state',
        'G1: sleeping',
        'S5: entered by override',
        'Legacy ON state',
        'Legacy OFF state',
        'Unknown',
    )),
    0x23: TupleExt((
        #  Watchdog 2
        'Timer expired',
        'Hard reset',
        'Power down',
        'Power cycle',
        'reserved',
        'reserved',
        'reserved',
        'reserved',
        'Timer interrupt',
    )),
    0x24: TupleExt((
        #  Platform Alert
        'Platform generated page',
        'Platform generated LAN alert',
        'Platform Event Trap generated',
        'Platform generated SNMP trap, OEM format',
    )),
    0x25: TupleExt((
        #  Entity Presence
        'Present',
        'Absent',
        'Disabled',
    )),
    0x27: TupleExt((
        #  LAN
        'Heartbeat Lost',
        'Heartbeat',
    )),
    0x28: TupleExt((
        #  Management Subsystem Health
        'Sensor access degraded or unavailable',
        'Controller access degraded or unavailable',
        'Management controller off-line',
        'Management controller unavailable',
        'Sensor failure',
        'FRU failure',
    )),
    0x29: TupleExt((
        #  Battery
        'Low',
        'Failed',
        'Presence Detected',
    )),
    0x2b: TupleExt((
        #  Version Change
        'Hardware change detected',
        'Firmware or software change detected',
        'Firmware or software change detected, Mngmt Ctrl Dev Id',
        'Firmware or software change detected, Mngmt Ctrl Firm Rev',
        'Firmware or software change detected, Mngmt Ctrl Dev Rev',
        'Firmware or software change detected, Mngmt Ctrl Manuf Id',
        'Firmware or software change detected, Mngmt Ctrl IPMI Vers',
        'Firmware or software change detected, Mngmt Ctrl Aux Firm Id',
        'Firmware or software change detected, Mngmt Ctrl Firm Boot Block',
        'Firmware or software change detected, Mngmt Ctrl Other',
        'Firmware or software change detected, BIOS/EFI change',
        'Firmware or software change detected, SMBIOS change',
        'Firmware or software change detected, O/S change',
        'Firmware or software change detected, O/S loader change',
        'Firmware or software change detected, Service Diag change',
        'Firmware or software change detected, Mngmt SW agent change',
        'Firmware or software change detected, Mngmt SW App change',
        'Firmware or software change detected, Mngmt SW Middle',
        'Firmware or software change detected, Prog HW Change (FPGA)',
        'Firmware or software change detected, board/FRU module change',
        'Firmware or software change detected, board/FRU component change',
        'Firmware or software change detected, board/FRU replace equ ver',
        'Firmware or software change detected, board/FRU replace new ver',
        'Firmware or software change detected, board/FRU replace old ver',
        'Firmware or software change detected, board/FRU HW conf change',
        'Hardware incompatibility detected',
        'Firmware or software incompatibility detected',
        'Invalid or unsupported hardware version',
        'Invalid or unsupported firmware or software version',
        'Hardware change success',
        'Firmware or software change success',
        'Firmware or software change success, Mngmt Ctrl Dev Id',
        'Firmware or software change success, Mngmt Ctrl Firm Rev',
        'Firmware or software change success, Mngmt Ctrl Dev Rev',
        'Firmware or software change success, Mngmt Ctrl Manuf Id',
        'Firmware or software change success, Mngmt Ctrl IPMI Vers',
        'Firmware or software change success, Mngmt Ctrl Aux Firm Id',
        'Firmware or software change success, Mngmt Ctrl Firm Boot Block',
        'Firmware or software change success, Mngmt Ctrl Other',
        'Firmware or software change success, BIOS/EFI change',
        'Firmware or software change success, SMBIOS change',
        'Firmware or software change success, O/S change',
        'Firmware or software change success, O/S loader change',
        'Firmware or software change success, Service Diag change',
        'Firmware or software change success, Mngmt SW agent change',
        'Firmware or software change success, Mngmt SW App change',
        'Firmware or software change success, Mngmt SW Middle',
        'Firmware or software change success, Prog HW Change (FPGA)',
        'Firmware or software change success, board/FRU module change',
        'Firmware or software change success, board/FRU component change',
        'Firmware or software change success, board/FRU replace equ ver',
        'Firmware or software change success, board/FRU replace new ver',
        'Firmware or software change success, board/FRU replace old ver',
        'Firmware or software change success, board/FRU HW conf change',
    )),
    0x2c: TupleExt((
        #  FRU State
        'Not Installed',
        'Inactive',
        'Activation Requested',
        'Activation in Progress',
        'Active',
        'Deactivation Requested',
        'Deactivation in Progress',
        'Communication lost',
    )),
    0xF0: TupleExt((
        #  PICMG FRU Hot Swap
        'Transition to M0',
        'Transition to M1',
        'Transition to M2',
        'Transition to M3',
        'Transition to M4',
        'Transition to M5',
        'Transition to M6',
        'Transition to M7',
    )),
    0xF1: TupleExt((
        #  PICMG IPMB Physical Link
        'IPMB-A disabled, IPMB-B disabled',
        'IPMB-A enabled, IPMB-B disabled',
        'IPMB-A disabled, IPMB-B enabled',
        'IPMB-A enabled, IPMB-B enabled',
    )),
    0xF2: TupleExt((
        #  PICMG IPMB Physical Link
        'Module Handle Closed',
        'Module Handle Opened',
        'Quiesced',
    )),
}

USER_PRIVS = {0: 'reserved', 1: 'Callback', 2: 'User', 3: 'Operator', 4: 'Administrator',
              5: 'OEM', 0x0f: 'No Access'}

AUTH_TYPES = {'none': 1, 'md2': 2, 'md5': 4, 'password': 16, 'oem': 32}
