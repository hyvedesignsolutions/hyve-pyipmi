import os, struct, threading, time
from . rmcp import RMCP_Ping, RMCP
from . _rmcpp_msg import IPMI20_Message
from . _crypto import RAKP_NONE, MD5_128, get_cipher_tuple, \
                        cal_auth_code, conv_str2bytes
from . _rakp import *
from .. mesg.ipmi_app import GetChnlAuthCap, SetSessPriv, CloseSess
from .. util.exception import PyIntfExcept, PyIntfSeqExcept

class RMCPP(RMCP):
    def __init__(self, opts, keep_alive):
        super(RMCPP, self).__init__(opts, keep_alive)
        self.cipher = (RAKP_NONE, RAKP_NONE, RAKP_NONE)
        self.k1 = None
        self.k2 = None
        self.sid = b'\0'

    def open(self, opts):
        cipher_suite = opts.get('cipher_suite', 3)        
        cipher = get_cipher_tuple(cipher_suite)
        if cipher is None:
            raise PyIntfExcept('Cipher suite {0} is not supported.'.format(cipher))

        # Open socket
        RMCP_Ping.open(self)

        user = conv_str2bytes(opts.get('user', None))
        self.passwd = conv_str2bytes(opts.get('password', None))
        if self.passwd is not None: self.passwd = struct.pack('20s', self.passwd)
        priv = opts.get('priv', 4)        
        self.rcsid = os.urandom(4)

        no_ping = opts.get('no_ping', False)
        if not no_ping:        
            # rmcp ping
            self.ping()

        # Get Channel Authentication Capabilities Command
        self.issue_cmd(GetChnlAuthCap, priv)

        # Open Session Request
        mssid, cipher = self.issue_cmd(RMCPP_OpenSess, self.rcsid, cipher, priv)

        # RAKP 1, 2
        rcrn = os.urandom(16)
        msrn, msguid = self.issue_cmd(RAKP_1_2, self.rcsid, mssid, rcrn, 
                                      priv, user, self.passwd, cipher[0])

        # Calculate SIK        
        # SIK = H(rcrn, msrn, priv, len(user), user)
        # key = KG => user password
        if 'kg' not in opts.keys() or opts['kg'] == '':
            key = self.passwd
        else:
            key = conv_str2bytes(opts['kg'])
            key = struct.pack('20s', key)
        
        if key is not None:
            data = rcrn + msrn
            if user is None:
                data += struct.pack('BB', priv, 0)
            else:
                data += struct.pack('BB', priv, len(user))
                data += user
        
            sik = cal_auth_code(cipher[0], key, data)
        else:
            sik = None

        # RAKP 3, 4
        self.issue_cmd(RAKP_3_4, 
                       self.rcsid, mssid, msrn, rcrn, msguid,
                       priv, user, self.passwd, cipher[0], sik)
        
        self.cipher = cipher
        self.cipher_suite = cipher_suite
        self.sess_act = True
        self.sid = mssid

        # Calculate K1 & K2 by need
        if self.cipher[1] != RAKP_NONE and self.cipher[1] != MD5_128:
            self.k1 = cal_auth_code(cipher[0], sik, b'\x01' * 20)
        if self.cipher[2] != RAKP_NONE:
            self.k2 = cal_auth_code(cipher[0], sik, b'\x02' * 20)

        # Set Session Privilege Level Command
        priv, = self.issue_cmd(SetSessPriv, priv)

        # Create the keep-alive thread
        if self.keep_alive:
            th = threading.Thread(target=self.keep_alive_cb)
            th.daemon = True
            th.start()

    def gen_msg(self, cmd):
        msg = IPMI20_Message(self.cipher, self.sseq, self.sid, self.passwd, 
                             self.k1, self.k2)
                             
        if cmd.payload_type != 0:
            # RMCP Open Session Request & RAKP 1, 3
            payload = cmd.pack()
            data = msg.pack(cmd, payload)
        else:
            # Common IPMI commands
            data = msg.pack(cmd)

        return (msg, data)

    def unpack(self, rsp, msg, cmd):
        if cmd.payload_type != 0:
            payload_type, pkt1 = msg.unpack(rsp)  
            pkt2 = cmd.unpack(payload_type, pkt1)
        else:
            pkt1 = msg.unpack(rsp)  
            pkt2 = cmd.unpack(pkt1)

        return pkt2
