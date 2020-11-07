#!/usr/bin/env python3
import sys
from os.path import dirname, join

mylib = join(dirname(__file__), '../src')
if not mylib in sys.path:
    sys.path.insert(0, mylib)

from pyipmi.intf.rmcpp import RMCPP
from pyipmi.mesg import IPMI_Message
from pyipmi.mesg.ipmi_app import GetDeviceID

def print_rsp(rsp):
    for i in rsp:
        print('{0:02x}'.format(i), end=' ')
    print()

if __name__ == '__main__':
    user = 'root'
    passwd = 'root123'
    priv = 4
    cipher = 3
    
    r1 = RMCPP({'host': 'localhost', 'port': 623, }, False)
    r1.open({'user': user, 'password': passwd, 'priv': priv, 
        'cipher_suite': cipher, 'kg': '', 'no_ping': True,})

    rsp = r1.issue_cmd(GetDeviceID)
    print(IPMI_Message.dump_tuple(rsp))

    rsp = r1.issue_raw_cmd([6, 1])
    print_rsp(rsp)
    rsp = r1.issue_raw_cmd([6, 0x46, 2])
    print_rsp(rsp)
    rsp = r1.issue_raw_cmd([0x0c, 2, 1, 1, 0, 0])
    print_rsp(rsp)
    rsp = r1.issue_raw_cmd([6, 1], 1)   # LUN = 1
    print_rsp(rsp)

