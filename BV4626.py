#! /usr/bin/python
# BV4626 is a a muti I/O board with ADC, DCA and relays. To use with RPi
# it is necessary to connect to the USB to obtain a serial port as it operates
# at 5V.
# For linux the poer will be something like: "/dev/ttyUSB0"
# for windows it will be something line "COM5" 
#
# Version 1 27 Feb 2013
#
import serial
import logging
from time import sleep
CR = '\015'
ESC = '\033'

logging.basicConfig()
log = logging.getLogger(__name__)

# ------------------------------------------------------------------------------
# returns the comport connector for use with class
# ------------------------------------------------------------------------------
def connect(port,baud):
    return serial.Serial(port, baud, timeout=.5, rtscts=1, stopbits=1, parity='N' )

class BV4626(object):
    """BV4626 Multi I/O"""
    sp = None   # sp is set to communication device by Init()
    def __init__(self,com,ack='\006',do_connect=True):
        self.sp = com # communication instance
        self.ack = ack 
        if do_connect:
            self.connect()
    # --------------------------------------------------------------------------
    # Initialise device, sets the Baud rate and ACK char
    # --------------------------------------------------------------------------
    def connect(self):
        j = 10
        k = ''
        self.sp.write(CR) # establish Baud rate
        sleep(0.05)
        # now wait for '*'
        while k != '*':
            k = self.sp.read()
            j = j - 1
            if j <= 0: break
        # requires text to be sent
        self.sp.write("Clearing buffer\r") # clears buffer
        self.sp.write("\r")
        self.sp.write(ESC+'['+str(ord(self.ack))+'E') # set ACK
        log.debug(j)
        
    # --------------------------------------------------------------------------
    # sends command, starts with ESC and waits for ACK
    # --------------------------------------------------------------------------
    def csi(self,str):
        self.sp.flushInput()
        self.sp.write(ESC+str)
        self.wack()

    # --------------------------------------------------------------------------
    # for commands that just return ACK,
    # Does not return anything but will wait for the ACK char
    # --------------------------------------------------------------------------
    def wack(self):
        k = 0
        j = 10 # time out after this
        while k != self.ack:
            k = self.sp.read(1)
            j = j - 1
            if j <= 0: break
        # DEBUG
        if j < 5: 
            log.error("Possible command problem")
             
    # --------------------------------------------------------------------------
    # reads characters up to ACK and returns them
    # note will return a string
    # --------------------------------------------------------------------------
    def csiRead(self,str):
        k = ''
        v = ''
        self.sp.flushInput()
        self.sp.write(ESC+str)
        while k != self.ack:
            k = self.sp.read(1)
            if len(k) == 0: # timeout
                break
            if k != self.ack:
                v = v + k
        return v


    # ******************************************************************************
    # SYSTEM
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # device id
    # ------------------------------------------------------------------------------
    def ID(self):
        return self.csiRead('[?31d')

    # ------------------------------------------------------------------------------
    # firmware version
    # ------------------------------------------------------------------------------
    def firmware(self):
        return self.csiRead('[?31f')
    
    # ******************************************************************************
    # RELAYS
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # truns realy on or off action = 0 for off
    # ------------------------------------------------------------------------------
    def relayA(self,action):
        if action == 0:
            self.csi('[0A')
        else:
            self.csi('[1A')
    
    def relayB(self,action):
        if action == 0:
            self.csi('[0B')
        else:
            self.csi('[1B')
    
    # ******************************************************************************
    # digital I/O
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # Sets individual line on port to be either input or output
    # Example: To set channels 1-4 (a,b,c,d) as input and the other channels 
    # as output, the value in binary is 00001111, this is 0x0f in hex and 15 
    # in decimal, thus: Ioset(15). or Ioset(0x0f) 
    # ------------------------------------------------------------------------------
    def Ioset(self,action):
        self.csi('['+str(action)+'s')
    
    # ------------------------------------------------------------------------------
    # return port value
    # ------------------------------------------------------------------------------
    def Ioval(self):
        return self.csiRead('[r')
    
    # ------------------------------------------------------------------------------
    # sets a PWM value for a given channel
    # chanal should be a value from 'a' to 'h' as text
    # value should also be an integer '0' to '255'
    # ------------------------------------------------------------------------------
    def Ioout(self,chan,val):
        self.csi('['+str(val)+chan)
        
    # ******************************************************************************
    # ADC, Analogue to Digital
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # gets value of specified channel
    # Range 0 to 3
    # ------------------------------------------------------------------------------
    def Adcin(self,chan):
        return self.csiRead('['+str(chan)+'D')

    # ------------------------------------------------------------------------------
    # Sets voltage refrence
    # value is 0 to 3
    # 0 = 1.02V
    # 1 = 2.048V
    # 3 = 4.096V
    # ------------------------------------------------------------------------------
    def Adcvoltage(self,value):
        self.csi('['+str(value)+'V')
        
    # ******************************************************************************
    # DAC, Digital to Analogue
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # outputs a value to a channel X
    # Range
    # value = 0 to 63
    # ------------------------------------------------------------------------------
    def DacX(self,value):
        self.csi('['+str(value)+'X')
           
    # ------------------------------------------------------------------------------
    # outputs a value to a channel Y
    # Range
    # value = 0 to 63
    # ------------------------------------------------------------------------------
    def DacY(self,value):
        self.csi('['+str(value)+'Y')


