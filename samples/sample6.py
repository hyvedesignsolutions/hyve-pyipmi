#!/usr/bin/env python3
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
