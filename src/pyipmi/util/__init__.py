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
import os, sys
from optparse import OptionParser
from . config import PyConfig
from .. import intf

__all__ = [
    'PyTest',
    'config',
    'exception',
]

class PyTest:
    def __init__(self, opts_overwrite=None, ping_only=False, keep_alive=False):
        self.ping_only = ping_only

        try:
            # read the config file
            config_file = os.path.join(os.getenv('HOME'), '.config', 'pyipmi', 'pyipmi.conf')
            self.conf = PyConfig()
            opts, w_flag = self.conf.parse_config(config_file)  

            # command line option to overwrite the settings in the config file
            if opts_overwrite:
                opts = self.conf.overwrite_config(opts, opts_overwrite)
                if w_flag or opts_overwrite.force:  
                    self.conf.write_config(config_file, opts)

            # create the interface object
            self.intf = intf.init(opts, ping_only, keep_alive)

        except BaseException as e:
            print(e)
            exit(1)

    def print_rsp(self, rsp):
        print(' '.join(('{0:02x}'.format(i) for i in rsp)))

    def run_commands(self, argv=None):
        if self.ping_only:
            # RMCP Ping
            self.intf.ping()
            print('Success')
        else:
            # IPMI command: Get Device ID (NetFn=App, CMD=1)
            req = [6, 1]
            rsp = self.intf.issue_raw_cmd(req)
            self.print_rsp(rsp)

    def run(self):
        ret = 1
        try:
            self.run_commands()
            ret = 0
        except BaseException as e:
            print(e)
        finally:
            return ret
