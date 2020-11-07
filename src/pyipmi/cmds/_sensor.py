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
from . _common import str2int, get_sensor_readings, print_sensor_list3, \
                     print_sensor_list4, do_command, print_sensor_type_list
from .. util.exception import PyCmdsArgsExcept

def _sensor_list(self, argv):
    opt = 3
    print_hdl = print_sensor_list3
    filter_sensor_type = 0

    if argv[0] == 'vlist':
        opt = 4
        print_hdl = print_sensor_list4

    if len(argv) > 1:
        if argv[1] == 'type':
            if len(argv) == 2:
                print_sensor_type_list(self)
                return
            else:
                filter_sensor_type = str2int(argv[2])
                if filter_sensor_type < 0:
                    raise PyCmdsArgsExcept(4, 0, argv[2])
        else:
            raise PyCmdsArgsExcept(2, 0, argv[1])

    reading_all = get_sensor_readings(self, opt, 0, filter_sensor_type, True)
    print_hdl(self, reading_all)

def help_sensor(self, argv=None, context=0):
    self.print('Sensor Commands:')
    self.print('    list [type [<sensor_type>]]')
    self.print('    vlist [type [<sensor_type>]]')
    self.print('    help')

SENSOR_CMDS = {
    'list': _sensor_list,
    'vlist': _sensor_list,
    'help': help_sensor,    
}

def do_sensor(self, argv):
    do_command(self, argv, help_sensor, SENSOR_CMDS)
