#!/usr/bin/env python3
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.cmds import PyCmds, StrEx
from pyipmi.util.config import PyOpts

def find_line(target, src_str):
    ret = '(not found)'
    list1 = src_str.split('\n')    
    for s in list1:
        if s[:len(target)] == target:
            ret = s
            break

    return ret + '\n'

if __name__ == '__main__':
    pyopts = PyOpts()
    pyopts.add_options()
    opts = pyopts.parse_options('-U hyve -P hyve123')

    # Instead of printing out the results to the console, this sample shows
    # how to record them in a string named 'print_str'.
    print_str = StrEx()
    cmd = PyCmds(opts, print_str)
    
    # The results will be appended in 'print_str' when the next command is called, 
    # just like what you see from the console by running sample4 and sample5.
    # If you don't want this, you need to explictly call 'print_str.reset()'
    # before calling the next cmd.exec_command().

    # In this example, assume we'd like to retrieve specific lines from the outputs
    cmd.exec_command('raw 6 1')
    ret_all = print_str.get_str()
    print_str.reset()

    cmd.exec_command('mc info')
    ret = print_str.get_str()
    ret_all += find_line('Manufacturer ID', ret)
    print_str.reset()

    cmd.exec_command('lan print 1')
    ret = print_str.get_str()
    ret_all += find_line('RMCP+ Cipher Suites', ret)    

    print(ret_all)
