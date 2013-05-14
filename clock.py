#! /usr/bin/python
# An example of how to use the BV4626 with Python and the RPi
# To use type at the command prompt python demo.py <port>
# <port> will be something like "/dev/ttyUSB0" for linux (check with dmesg)
# and something line "COM2" for Windows
#
import sys
from time import sleep
import BV4626   # bv4626 class


# ******************************************************************************
# simple demonstration
# ******************************************************************************
def main():
    # input com port on start
    if len(sys.argv) < 2:
        print "Com port needed as part of input"
        print "for example: python demo.py '/dev/ttyUSB0'"
    else:
        # connect to serial port, this can be done in any maner but the 
        # connect in BV4626 is convenient 
        sp = BV4626.connect(sys.argv[1],115200)
        cl = BV4626.BV4626(sp)
        print "Device id {}".format(cl.ID())
        print "Firmware {}".format(cl.firmware())
        print "Clicking relays"
        for n in range(0,60):
            print n
            cl.relayA(1)
            sleep(1)
            cl.relayA(0)
            sleep(1)

if __name__ == "__main__":
    main()
