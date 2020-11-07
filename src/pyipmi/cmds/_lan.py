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
from .. mesg.ipmi_transport import *
from . _common import str2int, get_chnl, do_command
from . _consts import USER_PRIVS, AUTH_TYPES
from .. util.exception import PyCmdsExcept, PyCmdsArgsExcept

def _conv_auth_types(val):
    ret = []
    auths = list(AUTH_TYPES.keys())

    idx = 0
    while val:
        if val & 1: ret.append(auths[idx])
        idx += 1
        val >>= 1
        if idx == 3:  val >>= 1
        if idx >= len(auths):  break

    return ret

def _print_auth_types(self, fmt, title, val):    
    self.print(fmt.format(title), end=' ')
    ret = _conv_auth_types(val)
    if not ret:
        self.print('(all disabled)')
    else:
        self.print(' '.join(ret))

def _print_ip_addr(self, title, val):
    if len(val) < 4:
        raise PyCmdsExcept('Invalid IP Address returned by BMC.', -1)
    self.print('{0} {1}.{2}.{3}.{4}'.format(title, val[0], val[1], val[2], val[3]))

def _print_mac_addr(self, title, val):
    if len(val) < 6:
        raise PyCmdsExcept('Invalid MAC Address returned by BMC.', -1)
    self.print('{0} {1:02x}:{2:02x}:{3:02x}:{4:02x}:{5:02x}:{6:02x}'.format(
         title, val[0], val[1], val[2], val[3], val[4], val[5]))

def _print_ipv6_addr(self, title, val):
    if len(val) < 16:
        raise PyCmdsExcept('Invalid IPv6 Address returned by BMC.', -1)
    self.print(title, end=' ')
    for i in range(7):
        self.print('{0:02x}{1:02x}:'.format(val[i*2], val[i*2+1]), end='')
    self.print('{0:02x}{1:02x}'.format(val[14], val[15]))    

def _lan_print_1(self, rsp):
    # 1 Auth Type Support
    rsp = int.from_bytes(rsp, 'little') 
    _print_auth_types(self, '{0:22}:', 'Auth Type Support', rsp)

def _lan_print_2(self, rsp):
    # 2 Authentication Type Enables
    rsp = list(rsp)
    self.print('Auth Type Enables')
    for i in range(5):
        _print_auth_types(self, '  {0:20}:', USER_PRIVS[i + 1] , rsp[i])

def _lan_print_3(self, rsp):
    # 3 IP Address
    rsp = list(rsp)
    _print_ip_addr(self, 'IP Address            :', rsp)

def _lan_print_4(self, rsp):
    # 4 IP Address Source
    rsp = int.from_bytes(rsp, 'little') 
    src = {0: 'unspecified', 1: 'static address', 2: 'dhcp', 3: 'loaded by host',
           4: 'others'}.get(rsp, '(unknown)')
    self.print('IP Address Source     :', src)

def _lan_print_5(self, rsp):
    # 5 MAC Address
    rsp = list(rsp)
    _print_mac_addr(self, 'MAC Address           :', rsp)

def _lan_print_6(self, rsp):
    # 6 Subnet Mask
    rsp = list(rsp)
    _print_ip_addr(self, 'Subnet Mask           :', rsp)

def _lan_print_7(self, rsp):
    # 7 IPv4 Header Parameters
    rsp = list(rsp)
    ttl = rsp[0]
    flags = (rsp[1] & 0xe0) >> 5
    precedence = (rsp[2] & 0xe0) >> 5
    tos = (rsp[2] & 0x1e) >> 1
    self.print('IPv4 Header           : TTL=0x{0:02x} Flags=0x{1:02x} Precedence=0x{2:02x} TOS=0x{3:02x}'.format(
          ttl, flags, precedence, tos))

def _lan_print_10(self, rsp):
    # 10 BMC-generated ARP control
    rsp = int.from_bytes(rsp, 'little') 
    arp1 = 'Enabled' if rsp & 2 else 'Disabled'
    arp2 = 'Enabled' if rsp & 1 else 'Disabled'

    self.print('BMC ARP Control       : ARP Responses {0}, Gratuitous ARP {1}'.format(arp1, arp2))

def _lan_print_12(self, rsp):
    # 12 Default Gateway Address
    rsp = list(rsp)
    _print_ip_addr(self, 'Default Gateway IP    :', rsp)

def _lan_print_13(self, rsp):
    # 13 Default Gateway MAC Address
    rsp = list(rsp)
    _print_mac_addr(self, 'Default Gateway MAC   :', rsp)

def _lan_print_14(self, rsp):
    # 14 Default Gateway Address
    rsp = list(rsp)
    _print_ip_addr(self, 'Backup Gateway IP     :', rsp)

def _lan_print_15(self, rsp):
    # 15 Backup Gateway MAC Address
    rsp = list(rsp)
    _print_mac_addr(self, 'Backup Gateway MAC    :', rsp)

def _lan_print_20(self, rsp):
    # 20 802.1q VLAN ID
    rsp = list(rsp)
    if rsp[1] & 0x80 == 0:
        ret = 'disabled'
    else:
        ret = ((rsp[1] & 0x0f) << 8) + rsp[0]
        ret = '{0:03x}'.format(ret)

    self.print('802.1q VLAN ID        : {0}'.format(ret))

def _lan_print_21(self, rsp):
    # 21 802.1q VLAN Priority
    rsp = int.from_bytes(rsp, 'little') 
    self.print('802.1q VLAN Priority  : {0}'.format(rsp & 7))

def _lan_get_ciphers(self, chnl):
    # 22 RMCP+ Messaging Cipher Suite Entry Support
    rsp = self.intf.issue_cmd(GetLanConfig, chnl, 22, 0, 0)
    if not rsp: 
        raise PyCmdsExcept('Failed to get the number of suppported RMCP+ Cipher Suites.', -1)

    num = int.from_bytes(rsp, 'little') 
    if not num:
        raise PyCmdsExcept('The number of supported RMCP+ Cipher Suites is zero.', -1)

    # 23 RMCP+ Messaging Cipher Suite Entries
    entries = self.intf.issue_cmd(GetLanConfig, chnl, 23, 0, 0)
    if not entries:    
        raise PyCmdsExcept('Failed to get any supported RMCP+ Cipher Suites.', -1)

    entries = list(entries)

    # 24 RMCP+ Messaging Cipher Suite Privilege Levels
    privs = self.intf.issue_cmd(GetLanConfig, chnl, 24, 0, 0)
    if not privs:
        raise PyCmdsExcept('Failed to get any privilege levels of the supported RMCP+ Cipher Suites.', -1)

    privs = list(privs)

    return (num, entries, privs)

def _lan_print_ciphers(self, num, entries, privs):
    self.print('RMCP+ Cipher Suites   : ', end='')
    self.print(','.join((str(x) for x in entries[1:])))

    try:
        count = (num + 1) / 2 if num & 1 else num / 2
        count = int(count)
        self.print('Cipher Suite Priv Max : ', end='')
        for i in range(1, count):
            self.print('{0},{1},'.format(privs[i] & 0x0f, (privs[i] & 0xf0) >> 4), end='')
    
        if num & 1:
            self.print(privs[count] & 0x0f)
        else:
            self.print('{0},{1}'.format(privs[count] & 0x0f, (privs[count] & 0xf0) >> 4))
    except:
        raise PyCmdsExcept('Unexpected privilege levels of the supported RMCP+ Cipher Suites returned.', -1)

    finally:
        self.print(' ' * 23 + '* 0h = Unused')
        for i in range(1, 6):
            self.print(' ' * 23 + '* {0}h = {1}'.format(i, USER_PRIVS[i]))

LAN_PRINT_HDL = {
    1: (_lan_print_1, 1),
    2: (_lan_print_2, 5),
    3: (_lan_print_3, 4),
    4: (_lan_print_4, 1),
    5: (_lan_print_5, 6),
    6: (_lan_print_6, 4),
    7: (_lan_print_7, 3),
    10: (_lan_print_10, 1),
    12: (_lan_print_12, 4),
    13: (_lan_print_13, 6),
    14: (_lan_print_14, 4),
    15: (_lan_print_15, 6),
    20: (_lan_print_20, 2),
    21: (_lan_print_21, 1),
}

def _lan_print(self, argv):
    chnl = get_chnl(argv[1:])
    flag = False
    for key in LAN_PRINT_HDL.keys():
        rsp = self.intf.issue_cmd(GetLanConfig, chnl, key, 0, 0)
        if not rsp:  continue

        print_func = LAN_PRINT_HDL[key][0]
        rsp_len = LAN_PRINT_HDL[key][1]
        if len(rsp) != rsp_len:
            continue
        
        flag = True
        print_func(self, rsp)

    num, entries, privs = _lan_get_ciphers(self, chnl)
    flag = True
    _lan_print_ciphers(self, num, entries, privs)

    if not flag:
        raise PyCmdsExcept('Failed to get any LAN configuration parameters.', -1)

def _lan_alert(self, argv):
    chnl = get_chnl(argv[1:])

    # 17 Number of Destinations
    rsp = self.intf.issue_cmd(GetLanConfig, chnl, 17, 0, 0)
    if not rsp: 
        raise PyCmdsExcept('Failed to get the number of alert destinations.', -1)
    
    num = int.from_bytes(rsp, 'little') 
    if not num:
        raise PyCmdsExcept('The number of alert destinations is zero.', -1)

    flag = False
    for i in range(0, num + 1):
        # 18 Destination Type
        rsp = self.intf.issue_cmd(GetLanConfig, chnl, 18, i, 0)
        if not rsp: continue
        
        # 19 Destination Addresses
        rsp2 = self.intf.issue_cmd(GetLanConfig, chnl, 19, i, 0)
        if not rsp2: continue
        
        flag = True
        rsp = list(rsp)
        rsp2 = list(rsp2)

        # Output results
        ack = 'Acknowledged' if rsp[1] & 0x80 else 'Unacknowledged'
        dest_type = {0: 'PET Trap', 6: 'OEM 1', 7: 'OEM 2'}.get(rsp[1] & 7, 'Unknown')

        self.print('Alert Destination      : {0}'.format(rsp[0]))
        self.print('Alert Acknowledge      : {0}'.format(ack))
        self.print('Destination Type       : {0}'.format(dest_type))
        if rsp[1] & 0x80:
            self.print('Acknowledge Timeout    : {0} seconds'.format(rsp[2]))
        self.print('Number of Retries      : {0}'.format(rsp[3] & 7))

        if rsp2[1] & 0x10:   # IPv6
            _print_ipv6_addr(self, 'Alert IPv6 Address     :', rsp2[2:])
        else:
            gateway = 'default' if rsp2[2] & 1 == 0 else 'backup'

            self.print('Alert Gateway          : {0}'.format(gateway))
            _print_ip_addr(self, 'Alert IP Address       :', rsp2[3:7])
            _print_mac_addr(self, 'Alert MAC Address      :', rsp2[7:])
            
        self.print('')

    if not flag:
        raise PyCmdsExcept('Failed to get any alert destinations.', -1)

def _lan_enable_cipher(self, argv, op=1):
    # op = 0: disable a cipher suite
    # op = 1: enable a cipher suite

    chk = 1 if op == 0 else 2
    if len(argv) < chk:
        raise PyCmdsArgsExcept(1, 1)

    cipher = str2int(argv[0])
    if cipher < 0:
        raise PyCmdsExcept('Invalid cipher suite: ' + argv[0], 1)

    if op == 1:  # enable
        priv = str2int(argv[1])
        if priv < 1 or priv > 5:
            raise PyCmdsExcept('Invalid privilege level: ' + argv[1], 1)
    else:  # disable
        # prohibit to disable the in-use cipher suite
        if cipher == self.intf.cipher_suite:
            raise PyCmdsExcept('Error: Cipher Suite {0} is in use.'.format(cipher), -1)

    chk = 2 if op == 0 else 3
    chnl = get_chnl(argv[(chk - 1):])

    num, entries, privs = _lan_get_ciphers(self, chnl)

    valid_entries = entries[1:num+1]
    if cipher not in valid_entries:
        raise PyCmdsExcept('Cipher Suite ' + argv[0] + ' is not supported by BMC.')

    idx = valid_entries.index(cipher) + 1

    if idx & 1:
        x = int((idx + 1) / 2)    
        if op == 1:     # enable
            privs[x] = (privs[x] & 0xf0) + priv   # change lower nibble
        else:   # disable
            privs[x] &= 0xf0
    else:
        x = int(idx / 2)
        if op == 1:     # enable
            privs[x] = (priv << 4) + (privs[x] & 0x0f)  # change upper nibble
        else:   # disable
            privs[x] &= 0x0f

    # Set LAN Config, parameter #24
    self.intf.issue_cmd(SetLanConfig, chnl, 24, bytes(privs))

def _lan_enable_auth(self, argv, op=1):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 2)

    auth = AUTH_TYPES.get(argv[0], -1)
    if auth < 0:
        raise PyCmdsExcept('Invalid auth type: ' + argv[0], 2)

    priv = str2int(argv[1])
    if priv < 1 or priv > 5:
        raise PyCmdsExcept('Invalid privilege level: ' + argv[1], 2)

    chnl = get_chnl(argv[2:])

    # Get LAN Config, parameter #1
    rsp = self.intf.issue_cmd(GetLanConfig, chnl, 1, 0, 0)
    if not rsp:
        raise PyCmdsExcept('Failed to get the supported auth types.', -1)
    auths = int.from_bytes(rsp, 'little') 
    auth_types = _conv_auth_types(auths)

    if argv[0] not in auth_types:
        raise PyCmdsExcept('Auth type: ' + argv[0] + ' is not supported by BMC.')

    # Get LAN Config, parameter #2
    rsp = self.intf.issue_cmd(GetLanConfig, chnl, 2, 0, 0)
    if not rsp:
        raise PyCmdsExcept('Failed to get the current enabled auth types.', -1)

    rsp = list(rsp)
    rsp = [x & auths for x in rsp]
    
    # Set LAN Config, parameter #2
    if op == 1:
        rsp[priv - 1] |= auth
    else:
        rsp[priv - 1] &= ~auth

    self.intf.issue_cmd(SetLanConfig, chnl, 2, bytes(rsp))

def _lan_enable_imp(self, argv, op=1):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1)

    if argv[1] == 'cipher':
        _lan_enable_cipher(self, argv[2:], op)
    elif argv[1] == 'auth':
        _lan_enable_auth(self, argv[2:], op)
    else:
        raise PyCmdsArgsExcept(2, 1, argv[1])

def _lan_enable(self, argv):
    _lan_enable_imp(self, argv)

def _lan_disable(self, argv):
    _lan_enable_imp(self, argv, 0)

def help_lan(self, argv=None, context=0):
    if context == 0:
        self.print('LAN Commands:')
        self.print('    help')
        self.print('    print [<channel number>]')
        self.print('    alert [<channel number>]')
    if context in (0, 1):
        self.print('    enable cipher <cipher suite> <priv> [<channel number>]')
        self.print('    disable cipher <cipher suite> [<channel number>]')
        self.print('        e.g. enable cipher 2 4')
        self.print('        e.g. disable cipher 2')
    if context in (0, 2):    
        self.print('    enable auth <auth type> <priv> [<channel number>]')
        self.print('    disable auth <auth type> <priv> [<channel number>]')
        self.print('        e.g. enable auth md5 4')
        self.print('        e.g. disable auth md5 4')
        self.print('        Auth Types:')
        for i in AUTH_TYPES.keys():
            self.print(' ' * 9 + '* {0}'.format(i))
        self.print('        Privilege Levels:')
        for i in range(1, 6):
            self.print(' ' * 9 + '* {0}h = {1}'.format(i, USER_PRIVS[i]))

LAN_CMDS = {
    'print': _lan_print,
    'alert': _lan_alert,
    'enable': _lan_enable,
    'disable': _lan_disable,
    'help': help_lan,
}

def do_lan(self, argv):
    do_command(self, argv, help_lan, LAN_CMDS)
