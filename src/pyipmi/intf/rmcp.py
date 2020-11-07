import os, struct, socket, select, threading, time
from .. util.exception import PyIntfExcept, PyIntfSeqExcept

from . import Intf

from . _rmcp_msg import ASF_Ping, IPMI15_Message
from . _crypto import RMCP_AUTHS, AUTH_NONE, conv_str2bytes

from .. mesg import IPMI_Raw
from .. mesg.ipmi_app import GetChnlAuthCap,\
        GetSessChallenge, ActivateSess, SetSessPriv, CloseSess

class RMCP_Ping(Intf):
    def __init__(self, opts):
        self.socket = None
        self.host = opts.get('host', 'localhost')
        self.port = opts.get('port', 623)

    def __del__(self):
        if self.socket is not None:
            self.socket.close()

    def open(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            self.socket.connect((self.host, self.port))
        except:
            raise PyIntfExcept("Failed to connect to host.")

    def close(self):
        pass

    def sendrecv(self, data):
        retries = 3
        while retries:
            self.socket.send(data)
            r, _, x = select.select([self.socket], [], [], 1.5)
            if x:  raise PyIntfExcept('Socket exception occurred.  Stopped.')
            if r:  return self.socket.recv(4096)
            retries -= 1

        raise PyIntfExcept('Times out.  Host has no response.')

    def ping(self):
        ping = ASF_Ping()
        msg = ping.pack()
        rsp = self.sendrecv(msg)
        if len(rsp) != 28:
            raise PyIntfExcept('Host responded improperly.')

class RMCP(RMCP_Ping):
    KEEP_ALIVE_PERIOD = 55

    def __init__(self, opts, keep_alive):
        self.auth = AUTH_NONE
        self.sseq = 0
        self.sid = b'\0'
        self.sess_act = False

        self.keep_alive = keep_alive
        self.wd_count = RMCP.KEEP_ALIVE_PERIOD
        self.lock = threading.Lock()
        
        super(RMCP, self).__init__(opts)

    def __del__(self):
        try:
            if self.sess_act:
                self.close()    # close session
        except:
            pass
        finally:
            super(RMCP, self).__del__() # close socket

    def open(self, opts):
        if 'auth' in opts.keys() and opts['auth'] not in RMCP_AUTHS.keys():
            raise PyIntfExcept('Authentication algorithm {0} is not supported.'
                                 .format(opts['auth']))

        super(RMCP, self).open()

        user = conv_str2bytes(opts.get('user', None))
        self.passwd = conv_str2bytes(opts.get('password', None))
        priv = opts.get('priv', 4)        
        self.ioseq = 0

        no_ping = opts.get('no_ping', False)
        if not no_ping:        
            # rmcp ping
            self.ping()

        # open session
        # Get Channel Authentication Capabilities Command
        self.issue_cmd(GetChnlAuthCap, priv)

        # Get Session Challenge Command
        auth = RMCP_AUTHS[opts.get('auth', 'md5')]
        self.sid, chg_data = self.issue_cmd(GetSessChallenge, auth, user)

        # Activate Session Command
        self.auth = auth
        while self.ioseq == 0:
            self.ioseq, = struct.unpack('<L', os.urandom(4))
        self.auth, self.sid, self.sseq, priv = self.issue_cmd(
                                     ActivateSess, auth, priv, chg_data, self.ioseq)

        self.sess_act = True  # Mark the session as activated

        # Set Session Privilege Level Command
        priv, = self.issue_cmd(SetSessPriv, priv)

        # Create the keep-alive thread
        if self.keep_alive:
            th = threading.Thread(target=self.keep_alive_cb)
            th.daemon = True
            th.start()

    def close(self):
        # Close Session Command
        self.issue_cmd(CloseSess, self.sid)
        self.sess_act = False

    def recv(self):
        r, _, x = select.select([self.socket], [], [], 1.5)
        if x:   raise PyIntfExcept('Socket exception occurred.  Stopped.')
        if r:   return self.socket.recv(4096)
        return None

    def gen_msg(self, cmd):
        msg = IPMI15_Message(self.auth, self.sseq, self.sid, self.passwd)
        data = msg.pack(cmd)
        return (msg, data)

    def unpack(self, rsp, msg, cmd):
        pkt1 = msg.unpack(rsp)  
        pkt2 = cmd.unpack(pkt1)
        return pkt2

    def issue_cmd_imp(self, cmd_cls, *args):
        if self.keep_alive: self.wd_count = RMCP.KEEP_ALIVE_PERIOD
        cmd = cmd_cls(*args)

        if self.sess_act:
            self.sseq += 1
            if self.sseq > 0xffffffff:
                self.sseq = 1

        msg, data = self.gen_msg(cmd)
        rsp = self.sendrecv(data)

        try:
            return self.unpack(rsp, msg, cmd)   

        except PyIntfSeqExcept:
            # The response mismatches the request
            # Check the next response message
            retries = 2
            while retries:
                try:
                    rsp = self.recv()
                    if rsp: return self.unpack(rsp, msg, cmd)

                except PyIntfSeqExcept:
                    pass

                finally:
                    retries -= 1

        raise PyIntfExcept('Could not match the request with the response message.')        

    def issue_cmd(self, cmd_cls, *args):
        with self.lock:
            rsp = self.issue_cmd_imp(cmd_cls, *args)
        return rsp

    def issue_raw_cmd(self, req, lun=0):
        with self.lock:
            rsp = self.issue_cmd_imp(IPMI_Raw, req, lun)
        return rsp

    def keep_alive_cb(self):
        while True:
            if self.wd_count == 0 and self.sess_act:
                self.issue_raw_cmd([6, 1])
            self.wd_count -= 1
            time.sleep(1)
            
