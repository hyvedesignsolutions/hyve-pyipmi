from .. util.exception import PyIntfExcept

__all__ = [
    'kcs',
    'rmcp',
    'rmcpp',
    'init',    
]

def init(opts, ping_only, keep_alive):
    if ping_only:
        from . rmcp import RMCP_Ping
        intf = RMCP_Ping(opts['global'])
        intf.open()
        return intf

    if 'interface' not in opts['global']:
        intf_name = 'lanplus'
    else:
        intf_name = opts['global']['interface']

    if intf_name == 'lan':
        from . rmcp import RMCP
        intf = RMCP(opts['global'], keep_alive)
        intf.open(opts['lan'])
        return intf

    if intf_name == 'lanplus':
        from . rmcpp import RMCPP
        intf = RMCPP(opts['global'], keep_alive)
        intf.open(opts['lanplus'])
        return intf

    raise PyIntfExcept('Invalid interface specified: ' + intf_name)

class Intf:
    def __init__(self):
        pass

    def __del__(self):
        pass

    def open(self):
        pass

    def close(self):
        pass

    def sendrecv(self, data):
        pass
