from .. mesg.ipmi_chassis import GetChsStat, ChsCtrl
from . _common import do_command

def _power_status(self, argv):
    t1 = self.intf.issue_cmd(GetChsStat)
    pstat = 'on' if t1[0] & 1 else 'off'
    self.print('Chassis Power is', pstat)

def _power_on(self, argv):
    self.intf.issue_cmd(ChsCtrl, 1)
    self.print('Chassis Power Control: Up/On')

def _power_off(self, argv):
    self.intf.issue_cmd(ChsCtrl, 0)
    self.print('Chassis Power Control: Down/Off')

def _power_cycle(self, argv):
    self.intf.issue_cmd(ChsCtrl, 2)
    self.print('Chassis Power Control: Cycle')

def _power_reset(self, argv):
    self.intf.issue_cmd(ChsCtrl, 3)
    self.print('Chassis Power Control: Hard Reset')

def _power_diag(self, argv):
    self.intf.issue_cmd(ChsCtrl, 4)
    self.print('Chassis Power Control: Pulse Diagnostic Interrupt')

def _power_soft(self, argv):
    self.intf.issue_cmd(ChsCtrl, 5)
    self.print('Chassis Power Control: Soft Shutdown')

def help_power(self, argv=None, context=0):
    self.print('Power Commands:')
    for cmd in POWER_CMDS.keys():
        self.print('    {0}'.format(cmd))

POWER_CMDS = {
    'status': _power_status,
    'on': _power_on,
    'off': _power_off,
    'cycle': _power_cycle,
    'reset': _power_reset,
    'diag': _power_diag,
    'soft': _power_soft,
    'help': help_power,
}

def do_power(self, argv):
    do_command(self, argv, help_power, POWER_CMDS)
