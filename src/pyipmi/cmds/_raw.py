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
import builtins
from .. util.exception import PyExcept, PyCmdsExcept, PyCmdsArgsExcept

def help_raw(self, from_shell=True):
    print('Issue raw commands:')
    print('    raw <NetFn> <CMD> <Req Data>')

    if from_shell:
        print('    [<NetFn> <CMD> <Req Data>]')
        print('    [<NetFn>, <CMD>, <Req_b1, Req_b2, ...>]')

def _do_raw_imp(self, raw, from_shell):
    # At least 2 arguments for NetFn and CMD
    # unless it's asking for help
    if raw[0] == 'help':
        help_raw(self, from_shell)
        return
    elif len(raw) < 2:
        raise PyCmdsArgsExcept(1)

    # convert arguments to int from str
    req = []
    for i in raw:  # Drop the program name
        try:
            if not i: continue
            if i[:2] == '0x' or i[:2] == '0X':
                req.append(int(i, base=16))
            else:
                req.append(int(i))
        except:
            raise PyCmdsArgsExcept(3, 0, i) 

    rsp = self.intf.issue_raw_cmd(req)
    self.print_rsp(rsp)

def do_raw(self, text):
    from_shell = True

    # process input to a list
    if type(text) is str:
        # arguments separated by , or space
        raw = text.split(sep=',')
        if len(raw) < 2:
            raw = text.split(sep=' ')
    else:
        from_shell = False
        raw = text

    raw = [x.strip() for x in raw]

    try:
        _do_raw_imp(self, raw, from_shell)
        
    except PyCmdsExcept as e:
        builtins.print(e, '\n')
        if e.context >= 0:  help_raw(self, from_shell)

    except PyExcept as e:
        builtins.print(e)
