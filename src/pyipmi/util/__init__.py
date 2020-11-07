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
