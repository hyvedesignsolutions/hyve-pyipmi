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
import cmd, sys
from .. util import PyTest

class PyShell(cmd.Cmd, PyTest):
    intro = 'Welcome to the PyIPMI shell.  Type help or ? to list commands.\n'
    prompt = 'pysh> '
    doc_header = 'PyIPMI shell commands (type help <topic>):'
    file = None

    def __init__(self, print_file=sys.stdout):
        PyTest.__init__(self, None, False, True)
        cmd.Cmd.__init__(self)
        self.print_file = print_file

    from ._lan import do_lan, help_lan
    from ._mc import do_mc, help_mc
    from ._chassis import do_chassis, help_chassis
    from ._power import do_power, help_power
    from ._sdr import do_sdr, help_sdr
    from ._sel import do_sel, help_sel
    from ._sensor import do_sensor, help_sensor
    from ._user import do_user, help_user
    from ._raw import do_raw, help_raw

    from ._common import print
    from ._common import print_rsp
    
    def do_exit(self, arg):
        self.intf.__del__()
        return True
    
    def help_exit(self):
        print('Type \'exit\' to leave the PyIPMI Shell.')

    def do_selftest(self, argv):
        print('Calling raw 6 1...')
        self.do_raw(['6', '1'])
        print('\nCalling mc info...')
        self.do_mc(['info'])
        print('\nCalling chassis status...')
        self.do_chassis(['status'])
        print('\nCalling power status...')
        self.do_power(['status'])
        print('\nCalling sdr list...')
        self.do_sdr(['list'])
        print('\nCalling sel list...')
        self.do_sel(['list'])
        print('\nCalling sensor list...')
        self.do_sensor(['list'])
        print('\nCalling lan list...')
        self.do_lan(['print', '1'])
        print('\nCalling user list...')
        self.do_user(['list'])
        print('\nselftest done.')
    
    def help_selftest(self):
        print('Type \'selftest\' to perform a self test.')

    def precmd(self, line):
        text = line.lower()
        if len(text) > 1 and text[0] == '[' and text[-1] == ']':
            # raw command
            text = 'raw ' + text[1:-1]

        return text

    def get_pos(self, text, line, begidx, endidx):
        count = 0
        c_prev = ''
        for c in line:
            if c == begidx:  break
            if c == ' ' and c_prev != ' ':
                count += 1

            c_prev = c

        args = line.split(' ')

        if count > 1:  ret = (count, args[count-1], args[count-2])
        elif count == 1:  ret = (count, args[count-1], None)
        else:  ret = (0, None)

        return ret
        
    def match_words(self, text, words):
        ret = []
        for word in words:
            if text == word[:len(text)]:
                ret.append(word)

        return ret if ret else None

    def complete_chassis(self, text, line, begidx, endidx):
        pos, arg_prev, arg_1st = self.get_pos(text, line, begidx, endidx)
        words_d = {
            'power': ('status', 'on', 'off', 'cycle', 'reset', 'diag', 'soft',),
            'policy': ('list', 'always-on', 'previous', 'always-off',),
            'identify': ('on', 'off',),
            'bootdev': ('none', 'pxe', 'safe', 'diag', 'cdrom', 'bios', 'floppy',),
        }

        if pos == 1:
            words = ('bootdev', 'identify', 'restart_cause', 'status', 
                     'power', 'policy', 'poh',)
            
            return self.match_words(text, words)
        
        if pos == 2:
            words = words_d.get(arg_prev, None)

            if words is None:   return None
            return self.match_words(text, words)

        if pos == 3:
            words = ('clear-cmos', )
            if arg_1st == 'bootdev':
                return self.match_words(text, words)
            else:  
                return None
        
        return None

    def complete_power(self, text, line, begidx, endidx):
        pos, *_ = self.get_pos(text, line, begidx, endidx)
        if pos == 1:
            words = ('status', 'on', 'off', 'cycle', 'reset', 'diag', 'soft',)
            return self.match_words(text, words)

        return None

    def complete_mc(self, text, line, begidx, endidx):
        pos, arg_prev, arg_1st = self.get_pos(text, line, begidx, endidx)

        if pos == 1:
            words = ('help', 'reset', 'guid', 'info', 'selftest', 'watchdog',
                     'getenables', 'setenables', 'getsysinfo', 'setsysinfo',)
            return self.match_words(text, words)

        if pos == 2:
            if arg_prev == 'watchdog':
                words = ('get', 'reset')
                return self.match_words(text, words)
            elif arg_prev == 'setenables':
                words = ('recv_msg_intr', 'event_msg_intr', 'event_msg', 'system_event_log',
                         'oem0', 'oem1', 'oem2',)
                return self.match_words(text, words)
            elif arg_prev in ('getsysinfo', 'setsysinfo'):
                words = ('system_fw_version', 'system_name', 'primary_os_name', 'os_name',)
                return self.match_words(text, words)
            else:
                return None

        if pos == 3:
            if arg_1st == 'setenables':
                words = ('on', 'off')
                return self.match_words(text, words)
            else:
                return None

        return None

    def complete_sdr(self, text, line, begidx, endidx):
        pos, arg_prev, _ = self.get_pos(text, line, begidx, endidx)
        words_list = ['list', 'elist', 'slist', 'vlist',]

        if pos == 1:
            words = words_list + ['info', 'help']
            return self.match_words(text, words)

        if pos == 2:
            if arg_prev in words_list:
                words = ('all', 'full', 'compact', 'event', 'fru', 'mcloc', 'type',)
                return self.match_words(text, words)
            else:
                return None

        return None

    def complete_sel(self, text, line, begidx, endidx):
        pos, *_ = self.get_pos(text, line, begidx, endidx)

        if pos == 1:
            words = ('info', 'list', 'elist', 'vlist', 'clear', 'time', 'help',)
            return self.match_words(text, words)

        return None
    
    def complete_sensor(self, text, line, begidx, endidx):
        pos, arg_prev, _ = self.get_pos(text, line, begidx, endidx)
        words_list = ['list', 'vlist',]

        if pos == 1:
            words = words_list + ['help',]
            return self.match_words(text, words)

        if pos == 2:
            if arg_prev in words_list:
                words = ('type',)
                return self.match_words(text, words)
            else:
                return None

        return None

    def complete_user(self, text, line, begidx, endidx):
        pos, arg_prev, _ = self.get_pos(text, line, begidx, endidx)

        if pos == 1:
            words = ('info', 'list', 'set', 'test', 'enable', 'disable',)
            return self.match_words(text, words)

        if pos == 2:
            if arg_prev == 'set':
                words = ('name', 'password', 'priv',)
                return self.match_words(text, words)
            else:
                return None

        return None

    def complete_lan(self, text, line, begidx, endidx):
        pos, arg_prev, _ = self.get_pos(text, line, begidx, endidx)

        if pos == 1:
            words = ('help', 'print', 'enable', 'disable', 'alert',)
            return self.match_words(text, words)
        if pos == 2:
            words = ('auth', 'cipher',)
            if arg_prev in ('enable', 'disable'):
                return self.match_words(text, words)
            else:
                return None

        return None
