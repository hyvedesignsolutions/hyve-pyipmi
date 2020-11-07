#!/usr/bin/env python3
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.cmds import PyCmds
            
if __name__ == '__main__':
    # This example shows how to use PyIPMI commands in a script
    cmd = PyCmds()
    cmd.exec_command('raw 6 1')
    cmd.exec_command('mc info')
    cmd.exec_command('chassis status')
    cmd.exec_command('power status')
    cmd.exec_command('sdr list')
    cmd.exec_command('sel list')
    cmd.exec_command('sensor list')
    cmd.exec_command('lan print 1')
    cmd.exec_command('user list')
