import sys
from .. util import PyTest
from ._raw import do_raw
from ._lan import do_lan
from ._mc import do_mc
from ._chassis import do_chassis
from ._power import do_power
from ._sdr import do_sdr
from ._sel import do_sel
from ._sensor import do_sensor
from ._user import do_user

__all__ = [
    'PyCmds',
]

PY_CMDS = {
    'mc': do_mc,
    'chassis': do_chassis,
    'power': do_power,
    'sdr': do_sdr,
    'sel': do_sel,
    'sensor': do_sensor,
    'user': do_user,
    'lan': do_lan,
    'raw': do_raw,
}

class StrEx(str):
    def __init__(self):
        self.print_str = ''

    def __str__(self):
        return self.print_str

    def write(self, text):        
        self.print_str += text

    def get_str(self):
        return self.print_str

    def reset(self):
        self.print_str = '' 

class PyCmds(PyTest):
    def __init__(self, opts_overwrite=None, print_file=sys.stdout):
        super(PyCmds, self).__init__(opts_overwrite)
        self.print_file = print_file

    @staticmethod
    def print_usage(prg=None):
        if prg is not None:
            print('Usage: {0} <command> [<options>]'.format(prg))
        print('Commands:')
        print('    ping')
        for i in PY_CMDS.keys():
            print('    {0}'.format(i))
        print('    help')

    from ._common import print
    from ._common import print_rsp

    def exec_command(self, cmd):
        if type(cmd) is str:
            args = cmd.split(' ')
            args = [x.strip() for x in args]
        else:
            args = cmd
        
        command = args[0]
        args = args[1:]

        if command == 'help':
            PyCmds.print_usage()
        elif command == 'ping':
            try:
                self.intf.ping()
                print('Success')
            except BaseException as e:
                print(e)
        elif command not in PY_CMDS.keys():
            print('Invalid command:', command)
        else:
            PY_CMDS[command](self, args)
