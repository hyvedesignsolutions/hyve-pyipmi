#!/usr/bin/env python3
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.cmds import PyCmds
from pyipmi.util.config import PyOpts
            
if __name__ == '__main__':
    # Same as sample4,
    # with overwriting some of the options in the user config
    pyopts = PyOpts()
    pyopts.add_options()
    opts = pyopts.parse_options('-U hyve -P hyve123')

    cmd = PyCmds(opts)
    cmd.exec_command('raw 6 1')
    cmd.exec_command('mc info')
    cmd.exec_command('chassis status')
    cmd.exec_command('power status')
    cmd.exec_command('sdr list')
    cmd.exec_command('sel list')
    cmd.exec_command('sensor list')
    cmd.exec_command('lan print 1')
    cmd.exec_command('user list')
