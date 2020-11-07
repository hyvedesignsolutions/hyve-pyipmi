# Hyve PyIPMI

Pure Python-based IPMI client developed by Hyve Design Solutions.

The original purpose of this package is to provide a pure python-based IPMI client library for developing Python test scripts for the IPMI service.  It provides two categories: one is for IPMI raw commands and the other is for PyIPMI commands, which are similar to the famous ipmitool commands like "ipmitool mc info" or "ipmitool sdr list".

By this pure Python library, several console programs are provided for BMC developers' convenience.

Samples are included in the package to show how to write test scripts.  The performance of using this pure Python library is significantly faster than using a hybrid method of shell scripts + system calls to ipmitool to develop your test scripts.

## Features

* Supported IPMI channels
  * RMCP
  * RMCP+
  * Message bridging from LAN to IPMB
* Console programs
  * pyipmi - a Python program similar to ipmitool
  * pyipmr - a Python program supports "ipmitool raw" and has message bridging capability
  * pyping - an RMCP client
* Auto test interface
  * IPMI raw command support
  * PyIPMI command support

