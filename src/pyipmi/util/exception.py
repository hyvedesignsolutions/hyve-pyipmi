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
# The base class of all the exceptions defined in PyIPMI
class PyExcept(Exception):
    def __str__(self):
        return type(self).__name__ + ': ' + Exception.__str__(self)

# The exceptions in RMCP or RMCP+ protocols
class PyIntfExcept(PyExcept):
    pass 

# The exceptions when the response doesn't match the request
# by the sequence number
class PyIntfSeqExcept(PyIntfExcept):
    pass 

# The exceptions of reading config
class PyConfExcept(PyExcept):
    pass

# The exceptions for RMCP+ and RAKP Messages
class PyIntfCCExcept(PyIntfExcept):
    def __init__(self, cc):
        self.cc = cc

    def __str__(self):
        ERR_CCS = (
            'No errors',
            'Insufficient resources to create a session',
            'Invalid Session ID',
            'Invalid payload type',
            'Invalid authentication algorithm',
            'Invalid integrity algorithm',
            'No matching authentication payload',
            'No matching integrity payload',
            'Inactive Session ID',
            'Invalid role',
            'Unauthorized role or privilege level requested',
            'Insufficient resources to create a session at the requested role',
            'Invalid name length',
            'Unauthorized name',
            'Unauthorized GUID (RAKP2 BMC to remote console)',
            'Invalid integrity check value',
            'Invalid confidentiality algorithm',
            'No Cipher Suite match with propsed security algorithms',
            'Illegal or unrecognized parameter',
        )

        if self.cc <= 0x12:  msg = ERR_CCS[self.cc]
        else:  msg = 'Reserved'

        return 'Failed to establish an RMCP+ session.  RMCP+ Status Code = {0:02x}h ({1}.)'.format(self.cc, msg)

# The exceptions in IPMI commands
class PyMesgExcept(PyExcept):
    pass 

# The exceptions in IPMI responses when 
# the completion code is non-zero
class PyMesgCCExcept(PyMesgExcept):
    def __init__(self, netfn, cmd, cc):
        self.netfn = netfn
        self.cmd = cmd
        self.cc = cc

    def __str__(self):
        ERR_CCS = {
            0xc0: 'Node Busy.', 
            0xc1: 'Invalid Command.',
            0xc2: 'Invalid LUN.',
            0xc3: 'Timeout while processing command.',
            0xc4: 'Out of space.',
            0xc5: 'Invalid Reservation ID.',
            0xc6: 'Request data truncated.',
            0xc7: 'Request data length invalid.',
            0xc8: 'Request data field length limit exceeded.',
            0xc9: 'Parameter out of range.',
            0xca: 'Cannot return number of requested data bytes.',
            0xcb: 'Requested Sensor, data, or record not present.',
            0xcc: 'Invalid data field in Request.',
            0xcd: 'Command illegal for specified sensor or record type.',
            0xce: 'Command response could not be provided.',
            0xcf: 'Cannot execute duplicated request.',
            0xd0: 'Command response could not be provided. SDR Repository in update mode.',
            0xd1: 'Command response could not be provided. Device in firmware update mode.',
            0xd2: 'Command response could not be provided. BMC init or init agent in progress.',
            0xd3: 'Destination unavailable',
            0xd4: 'Cannot execute command due to insufficient privilege level or other security-based restriction.',
            0xd5: 'Cannot execute command. Command or request parameters not supported in present state.',
            0xd6: 'Cannot execute command. Parameter is illegal because command sub-functions has been disabled or is unavailable.',
            0xff: 'Unspecified error.',
        }

        return ('Command failed: NetFn={0:02X}h, CMD={1:02X}h, CC={2:02X}h ({3})'
                .format(self.netfn, self.cmd, self.cc, 
                        ERR_CCS.get(self.cc, 'Unknown Completion Code.')))

# The exceptions in PyIPMI commands
class PyCmdsExcept(PyExcept):
    def __init__(self, msg, context=0):
        self.context = context
        super(PyCmdsExcept, self).__init__(msg)

    def __str__(self):
        return Exception.__str__(self)

class PyCmdsArgsExcept(PyCmdsExcept):
    def __init__(self, opt, context=0, arg=None):
        if opt == 1:
            super(PyCmdsArgsExcept, self).__init__('Insufficient arguments.', context)
        elif opt == 2:
            super(PyCmdsArgsExcept, self).__init__('Unknown argument: {0}.'.format(arg), context)
        elif opt == 3:
            super(PyCmdsArgsExcept, self).__init__('Invalid input argument: {0}.'.format(arg), context)
        elif opt == 4:
            msg = 'Unexpected sensor type: {0}'.format(arg)
            msg += '. Please specify the sensor type by an integer.\n'
            msg += 'Use \'list type\' to get the full list of all the sensor types.'
            super(PyCmdsArgsExcept, self).__init__(msg, context)
        else:
            super(PyCmdsArgsExcept, self).__init__('Unspecified error occurred.', context)
