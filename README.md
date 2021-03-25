# Hyve PyIPMI

Pure Python-based IPMI client developed by Hyve Design Solutions.

The original purpose of this package is to provide a pure python-based IPMI client library for developing Python test scripts for the IPMI service.  It provides two categories: one is for IPMI raw commands and the other is for PyIPMI commands, which are similar to the famous ipmitool commands like "ipmitool mc info" or "ipmitool sdr list".

By this pure Python library, several console programs are provided for BMC developers' convenience.

Samples are included in the package to show how to write test scripts.  The performance of using this pure Python library is significantly faster than using a hybrid method of shell scripts + system calls to ipmitool to develop your test scripts.

## Features

* Supported IPMI channels
  * RMCP
  * RMCP+
  * KCS
  * Message bridging from LAN/KCS to IPMB
* Console programs
  * pyipmi - a Python program similar to ipmitool
  * pyipmr - a Python program supports "ipmitool raw" and has message bridging capability
  * pyping - an RMCP client
  * pysh - an interactive shell for the PyIPMI commands, with auto completion and up/down keys to show previous commands
* Auto test interface
  * IPMI raw command support (see samples 1-3 below)
  * PyIPMI command support (see samples 4-6 below)

## Installation
The following steps were tested on Ubuntu desktop 16.04 LTS, 18.04 LTS, and 20.04 LTS.

### 1) Prerequisite
```
$ sudo apt -y install git python3-pip
```

### 2) Download the source
```
$ git clone https://github.com/hyvedesignsolutions/hyve-pyipmi
$ cd hyve-pyipmi
```

### 3) Install the Hyve PyIPMI package and the console programs
```
$ pip3 install .
```

## Test Hyve PyIPMI
By default, pip3 will install the Hyve PyIPMI package in $HOME/.local/lib/python3.x/site-packages and its console programs in $HOME/.local/bin.  Generally speaking, the site-packages directory has been included in sys.path and you need to add the bin directory in PATH by yourself.  For example, execute
```
$ export PATH=~/.local/bin:$PATH
```
Then, you are able to execute your first PyIPMI command.  For example, we execute something very similar to ipmitool as follows:
```
$ pyipmi -H 192.168.0.169 -I lanplus -U root -P root123 raw 6 1
```

Note that by default, if you choose to use "-I kcs" that goes through the Linux OpenIPMI driver, you will need root privilege to execute the program.

During the first time when the package is used, it automatically generates a user config file in $HOME/.config/pyipmi/pyipmi.conf with default settings.  Then, the options supported will overwrite some of the settings.  In the above example, it specifies four options and issues a raw IPMI command.

After the config file is created, you can choose to either use all the settings in the config file or continue to overwrite some of the options as the previous example.  The program will automatically record the latest overwritten values in the config file.
```
$ pyipmi sdr list   # Just use the settings in the config file
$ pyipmi -C 2 user list  # Use RMCP+ Cipher Suite 2
$ pyipmi -U hyve -P hyve456 lan print 1  # User credential hyve/hyve456
```
Type -h to show all the command options and use "help" command to list the available commands.
```
$ pyipmi -h
$ pyipmi help
```

## Advanced Usage
The program pyipmr is equal to "pyipmi raw" + additional features.  It supports
* IPMI response LUN other than 0
* IPMI message bridging from LAN to IPMB
```
$ pyipmr 6 1   # Get Device ID (NetFn=App, CMD=01h)
$ pyipmr -L 1 6 1  # LUN = 1
$ pyipmr -b 6 -t 0x2c raw 6 1  # Bridge Get Device ID to destination 0x2c via channel 6
```

## Test scripts examples
**Sample 1**
```
#!/usr/bin/env python3
import sys
from pyipmi.util import PyTest

# Just overwrite the run_commands() method and you can issue
# IPMI commands like this example
class Sample1(PyTest):
    def __init__(self):
        super(Sample1, self).__init__()

    def run_commands(self, argv=None):
        # issue_raw_cmd(req, lun):
        #     req (list): [NetFn, CMD, Req_Data]
        #     lun (int): default is 0
        print('Get Device ID:')
        rsp = self.intf.issue_raw_cmd([6, 1])
        self.print_rsp(rsp)

        print('\nGet User Name 2:')
        rsp = self.intf.issue_raw_cmd([6, 0x46, 2])
        self.print_rsp(rsp)

        print('\nGet LAN Config 1:')
        rsp = self.intf.issue_raw_cmd([0x0c, 2, 1, 1, 0, 0])
        self.print_rsp(rsp)

if __name__ == '__main__':
    test = Sample1()
    sys.exit(test.run())
```

**Sample 2**
```
#!/usr/bin/env python3
import sys
from pyipmi.util import PyTest
from pyipmi.util.config import PyOpts

# Same as sample1, with simple checks on the response data
# and overwrite some values of the user config
class Sample2(PyTest):
    def __init__(self, opts):
        super(Sample2, self).__init__(opts)

    def run_commands(self, argv=None):
        req = ([[6, 1],                     # Get Device ID
                [6, 0x46, 2],               # Get User Name 2
                [0x0c, 2, 1, 1, 0, 0]])     # Get LAN Config 1
            
        rsp = ([[0, 0x22, 1, 1, 2, 2, 0x9f, 0x55, 0xda, 0, 1, 0, 0x59, 1, 0, 0],
                [0, 0x72, 0x6f, 0x6f, 0x74, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
                [0, 0x11, 0x15]])

        # run the commands
        count_p = 0
        count_f = 0
        for i in range(len(req)):
            rsp_one = self.intf.issue_raw_cmd(req[i])
            if rsp_one == rsp[i]:
                print('test case {0}: PASSED!'.format(i + 1))
                count_p += 1
            else:            
                print('test case {0}: FAILED!'.format(i + 1))
                count_f += 1

        # output the results            
        print('Total {0} cases executed: PASSED {1}, FAILED {2}.'
                .format(count_p + count_f, count_p, count_f))

if __name__ == '__main__':
    pyopts = PyOpts()
    pyopts.add_options()
    opts = pyopts.parse_options('-U hyve -P hyve123')

    test = Sample2(opts)
    sys.exit(test.run())
```

**Sample 3**
```
#!/usr/bin/env python3
import sys
from pyipmi.util import PyTest
from pyipmi.util.config import PyOpts

# Message bridging example
# Support the following configuration
# [PyIPMI] <-- LAN (RMCP/RMCP+) --> [BMC] <-- IPMB --> [ME]
class Sample3(PyTest):
    def __init__(self, opts, chnl, target):
        self.chnl = chnl
        self.target = target

        super(Sample3, self).__init__(opts)

    def bridge_cmd(self, req):
        # issue_bridging_cmd(chnl, target, req, lun):
        #     chnl (int): IPMI channel number to bridge the message
        #     target (int): I2C slave address of the bridging destination
        #     req (list): [NetFn, CMD, Req_Data]
        #     lun (int): default is 0
        return self.intf.issue_bridging_cmd(self.chnl, self.target, req) 

    def run_commands(self, argv=None):       
        print('Get Device ID:')
        rsp = self.bridge_cmd([6, 1])
        self.print_rsp(rsp)

        print('\nGet SEL Time:')
        rsp = self.bridge_cmd([0xa, 0x48])
        self.print_rsp(rsp)

        print('\nGet Event Receiver:')
        rsp = self.bridge_cmd([4, 1])
        self.print_rsp(rsp)

        print('\nGet Intel ME FW Capabilities:')
        rsp = self.bridge_cmd([0x2e, 0xde, 0x57, 1, 0, 0, 0, 0, 0, 2, 0xff, 0])
        self.print_rsp(rsp)

        print('\nGet Intel ME Factory Presets Signature:')
        rsp = self.bridge_cmd([0x2e, 0xe0, 0x57, 1, 0])
        self.print_rsp(rsp)

        print('\nGet Exception Data:')
        rsp = self.bridge_cmd([0x2e, 0xe6, 0x57, 1, 0, 0])
        self.print_rsp(rsp)

        print('\nGet Sensor Reading:')
        sensor_num = (8, 197)
        for num in sensor_num:
            rsp = self.bridge_cmd([4, 0x2d, num])
            self.print_rsp(rsp)

        print('\nGet SEL Entry:')
        req = [0xa, 0x43, 0, 0, 0, 0, 0, 0xff]
        rsp = self.bridge_cmd(req)
        id1, id2 = rsp[1:3]        
        while not (id1 == 0xff and id2 == 0xff):
            req[4], req[5] = id1, id2
            rsp = self.bridge_cmd(req)
            id1, id2 = rsp[1:3]        
            self.print_rsp(rsp)

if __name__ == '__main__':
    pyopts = PyOpts()
    pyopts.add_options()
    opts = pyopts.parse_options('-H 10.19.84.90 -I lanplus -U admin -P admin')

    test = Sample3(opts, 6, 0x2c)
    sys.exit(test.run())
```

**Sample 4**
```
#!/usr/bin/env python3
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
```

**sample 5**
```
#!/usr/bin/env python3
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
```

**Sample 6**
```
#!/usr/bin/env python3
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
```

## Contact
You may like to contact Janny Au, the main developer of this program, if you have any questions or suggestions.
* Janny Au: <jannya@hyvedesignsolutions.com>

