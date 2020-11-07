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
