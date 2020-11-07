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
from .. mesg.ipmi_app import SetUserAccess, GetUserAccess, SetUserName, \
                            GetUserName, SetUserPass
from . _common import str2int, get_chnl, do_command
from . _consts import USER_PRIVS
from .. util.exception import PyCmdsArgsExcept

def _user_info(self, argv):
    chnl = get_chnl(argv[1:])
    max_user, enabled_user, fixed_user, _  = self.intf.issue_cmd(GetUserAccess, chnl, 1)

    self.print('Maximum IDs         : {0}'.format(max_user & 0x3f))
    self.print('Enabled User Count  : {0}'.format(enabled_user & 0x3f))
    self.print('Fixed Name Count    : {0}'.format(fixed_user & 0x3f))

def _user_list(self, argv):
    user_enabled = []
    user_acc = []
    user_name = []

    chnl = get_chnl(argv[1:])
    max_user, enabled, _, acc = self.intf.issue_cmd(GetUserAccess, chnl, 1)
    user_enabled.append((enabled & 0xc0) >> 6)
    user_acc.append(acc)
    
    for i in range(2, max_user + 1):
        try:
            _, enabled, _, acc = self.intf.issue_cmd(GetUserAccess, chnl, i)
        except:
            enabled = 0
            acc = 0x0f
        finally:
            user_enabled.append((enabled & 0xc0) >> 6)
            user_acc.append(acc)

    for i in range(1, max_user + 1):
        try:
            name, = self.intf.issue_cmd(GetUserName, i)
            name = name.decode('latin_1')
            name = name.replace('\x00', '\x20')
        except:
            name = ' ' * 16
        finally:
            user_name.append(name)

    self.print('ID | Name             | Enabling | Callin | Link  | IPMI  | Chnl Priv')
    self.print('-' * 73)
    for i in range(1, max_user + 1):
        enabled = ('unspecified', 'enabled', 'disabled', 'reserved')[user_enabled[i - 1]]
        name = user_name[i - 1]
        acc = user_acc[i - 1]
        callin = 'true' if acc & 0x40 == 0 else 'false'
        link = 'true' if acc & 0x20 else 'false'
        msg = 'true' if acc & 0x10 else 'false'
        priv = USER_PRIVS.get(acc & 0x0f, '(Unknown)')
        fmt = '{0:>2} | {1} | {2:8} | {3:6} | {4:5} | {5:5} | {6} '
        self.print(fmt.format(i, name, enabled, callin, link, msg, priv))

def _user_set_name(self, argv):
    user_id = str2int(argv[0])
    if user_id < 0:
        raise PyCmdsArgsExcept(3, 1, argv[0])

    user_name = b'\0' if len(argv) < 2 else argv[1].encode()
    
    self.intf.issue_cmd(SetUserName, user_id, user_name)

def _user_set_password_imp(self, argv, op):    
    user_id = str2int(argv[0])
    if user_id < 0:
        raise PyCmdsArgsExcept(3, 1, argv[0])
    
    passwd = b'\0' if len(argv) < 2 else argv[1].encode()

    pass_len = '20'
    if len(argv) >= 3:
        if argv[2] in ('20', '16'):
            pass_len = argv[2]
        else:
            raise PyCmdsArgsExcept(3, 1, argv[2])
    if pass_len == '20':    user_id |= 0x80

    return self.intf.issue_cmd(SetUserPass, user_id, op, passwd)

def _user_set_password(self, argv):    
    _user_set_password_imp(self, argv, 2)

def _user_test(self, argv):    
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 1)

    cc = _user_set_password_imp(self, argv[1:], 3)
    if cc == 0: self.print('Password test OK.')

def _user_set(self, argv):
    if len(argv) < 3:
        raise PyCmdsArgsExcept(1, 1)
    if argv[1] == 'name':
        _user_set_name(self, argv[2:])
    elif argv[1] == 'password':
        _user_set_password(self, argv[2:])
    elif argv[1] == 'priv':
        _user_set_priv(self, argv[2:])
    else: 
        raise PyCmdsArgsExcept(2, 1, argv[1])

def _user_disable(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 2)
    _user_set_password_imp(self, argv[1:], 0)

def _user_enable(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 2)
    _user_set_password_imp(self, argv[1:], 1)

def _user_set_priv(self, argv):
    if len(argv) < 2:
        raise PyCmdsArgsExcept(1, 2)

    user_id = str2int(argv[0])
    if user_id < 0:
        raise PyCmdsArgsExcept(3, 2, argv[0])

    priv = str2int(argv[1])
    if priv < 1 or (priv > 5 and priv != 0xf):
        raise PyCmdsArgsExcept(3, 2, argv[1])

    chnl = get_chnl(argv[2:])
    if priv != 0x0f:  chnl |= 0x90
    else:  chnl |= 0x80

    self.intf.issue_cmd(SetUserAccess, chnl, user_id, priv)

def help_user(self, argv=None, context=0):
    if context == 0:
        self.print('User Commands:')
        self.print('    info         [<channel number]')
        self.print('    list         [<channel number]')
    if context in (0, 1):
        self.print('    set name     <user id> <username>')
        self.print('    set password <user id> [<password> [<16|20>]]')
        self.print('    test         <user id> [<password> [<16|20>]]')
        self.print('    set priv     <user id> <privilege level> [<channel number>]')
        self.print('        Privilege levels:')
        self.print('         * 0x1 - Callback')
        self.print('         * 0x2 - User')
        self.print('         * 0x3 - Operator')
        self.print('         * 0x4 - Administrator')
        self.print('         * 0x5 - OEM Proprietary')
        self.print('         * 0xF - No Access')
    if context in (0, 2):
        self.print('    enable       <user id>')
        self.print('    disable      <user id>')

USER_CMDS = {
    'info': _user_info,
    'list': _user_list,
    'set': _user_set,
    'test': _user_test,
    'disable': _user_disable,
    'enable': _user_enable,
    'help': help_user, 
}

def do_user(self, argv):
    do_command(self, argv, help_user, USER_CMDS)
