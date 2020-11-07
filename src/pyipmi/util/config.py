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
import os, configparser
from optparse import OptionParser
from . exception import PyConfExcept

class PyConfig:
    valid_opts = {
        'global': {
            'interface': (('lan', 'lanplus'), 'lanplus'),
            'host': (str, 'localhost'),
            'port': (int, 623),
        },

        'lan': {
            'user': (str, 'root'),
            'password': (str,  'root123'),
            'auth': (('none', 'md2', 'md5', 'password', 'oem'), 'md5'),
            'no_ping': (bool, True),
        },

        'lanplus': {
            'user': (str, 'admin'),
            'password': (str,  'admin123'),
            'cipher_suite': (int, 3),
            'priv': (int, 4),
            'kg': (str, ''),
            'no_ping': (bool, True),
        }
    }

    def __init__(self):
        self.config = configparser.ConfigParser()

    def write_config(self, config_file, opts=None):
        if opts:
            for key in opts.keys():
                self.config[key] = opts[key]

        with open(config_file, 'w') as configfile:
            configfile.write('###### Generic Configuration File for PyIPMI ######\n')
            self.config.write(configfile)
            configfile.flush()
            configfile.close()

    def write_default_config(self, config_file):
        # check if the file path exists
        path = os.path.dirname(config_file)
        if not os.path.exists(path):
            os.mkdir(path, 0o755)

        # load default values
        for k1 in PyConfig.valid_opts.keys():
            d1 = {}
            for k2 in PyConfig.valid_opts[k1].keys():
                if PyConfig.valid_opts[k1][k2][0] is bytes:
                    d1[k2] = PyConfig.valid_opts[k1][k2][1].decode()
                else:
                    d1[k2] = str(PyConfig.valid_opts[k1][k2][1])
            
            self.config[k1] = d1

        # write to the config file
        self.write_config(config_file)

    def parse_config(self, config_file):
        # assign default values
        d1 = {}
        for k1 in PyConfig.valid_opts.keys():
            d2 = {}
            for k2 in PyConfig.valid_opts[k1].keys():
                d2[k2] = PyConfig.valid_opts[k1][k2][1]
            d1[k1] = d2

        flag = False

        # check if the config file is valid
        if not os.path.isfile(config_file):
            # config file not exist, create it
            self.write_default_config(config_file)
            flag = True
        else:
            # read the config file
            self.config.read(config_file)

            # assign values from the config file
            for s in self.config.sections():
                if not s in PyConfig.valid_opts.keys(): continue
                for key in self.config[s]:
                    if not key in PyConfig.valid_opts[s].keys(): continue

                    if isinstance(PyConfig.valid_opts[s][key][0], tuple):
                        if self.config[s][key] in PyConfig.valid_opts[s][key][0]:
                            d1[s][key] = self.config[s][key]
                    elif PyConfig.valid_opts[s][key][0] is bool:
                        d1[s][key] = self.config.getboolean(s, key)
                    elif PyConfig.valid_opts[s][key][0] is int:
                        d1[s][key] = self.config.getint(s, key)
                    elif PyConfig.valid_opts[s][key][0] is bytes:
                        d1[s][key] = bytes(self.config[s][key], 'latin_1')
                    else:
                        d1[s][key] = self.config[s][key]

        return (d1, flag)

    def overwrite_config(self, opts, opts_overwrite):
        opts_ow = opts_overwrite.__dict__

        def conv_config_type(key, opt, vopts):
            if isinstance(vopts[key][0], tuple):
                if opt not in vopts[key][0]:
                    PyConfExcept('Unknown option value: ' + opt)
            elif vopts[key][0] is bool:
                opt = bool(opt)
            elif vopts[key][0] is int:                
                opt = int(opt)
            elif vopts[key][0] is bytes:
                opt = bytes(opt, 'latin_1')

            return opt

        def do_overwrite(sec, vopts):
            for key in sec.keys():
                opt = opts_ow.get(key, None)
                if opt:  sec[key] = conv_config_type(key, opt, vopts)

        # section global
        sec = opts['global']
        vopts = PyConfig.valid_opts['global']
        do_overwrite(sec, vopts)

        # validate the specified interface
        intf = opts['global']['interface']
        if intf not in vopts['interface'][0]:
            raise PyConfExcept('Interface ' + intf + ' is not supported.')

        # section of the interface
        sec = opts.get(intf, None)
        vopts = PyConfig.valid_opts[intf]
        if not sec:
            raise PyConfExcept('Config file does not have section ' + intf + '.  Stopped.')
        else:  do_overwrite(sec, vopts)

        return opts

class PyOpts:
    def __init__(self):
        self.parser = OptionParser()

    def add_options(self):
        self.parser.add_option('-H', '--host', dest='host',
                  help='Remote server address.')
        self.parser.add_option('-I', '--interface', dest='interface', 
                  help='Select the IPMI interface.  Supported interfaces are lan and lanplus (default).')
        self.parser.add_option('-p', '--port', dest='port', 
                  help='Remote server UDP port to connect to.  Default is 623.')
        self.parser.add_option('-U', '--user', dest='user', 
                  help='Remote server username.')
        self.parser.add_option('-P', '--password', dest='password', 
                  help='Remote server password.')
        self.parser.add_option('-C', '--cipher_suite', dest='cipher_suite', 
                  help='''The remote server authentication, integrity, and encryption algorithms 
to use for IPMI v2.0 RMCP+ connections.  The default value is 3.''')
        self.parser.add_option('-A', '--auth', dest='auth', 
                  help='''Specify an authentication type to use for IPMI 1.5 RMCP connections. 
Supported types are none, md2, md5 (default), password, and oem.''')
        self.parser.add_option('-L', '--priv', dest='priv', 
                  help='Force session privilege level.  The default level is 4 (=Administrator).')
        self.parser.add_option('-f', '--force', action='store_true', dest='force',
                  help='Force to overwrite the config file with the options given from the command line.')

    def add_more_options(self):
        self.parser.add_option('-l', '--lun', dest='lun', 
                  help='Set destination lun for raw commands.')
        self.parser.add_option('-b', '--dest_chnl', dest='dest_chnl', 
                  help='Set destination channel for bridged request.')
        self.parser.add_option('-t', '--target_addr', dest='target_addr', 
                  help='Bridge IPMI requests to the remote target address.')

    def parse_options(self, opt_str):
        args = opt_str.split(' ')
        args = [x.strip() for x in args]

        options, _ = self.parser.parse_args(args)

        return options
