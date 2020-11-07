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
