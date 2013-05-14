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
from time import sleep
CR = '\015'
ESC = '\033'

# ------------------------------------------------------------------------------
# returns the comport connector for use with class
# ------------------------------------------------------------------------------
def Connect(port,baud):
    return serial.Serial(port, baud, timeout=.5, stopbits=1, parity='N' )

class bv4626:
    """BV4626 Multi I/O"""
    sp = None   # sp is set to communication device by Init()
    def __init__(self,com,ack='\006'):
        self.sp = com # communication instance
        self.ack = ack 

    # --------------------------------------------------------------------------
    # Initialise device, sets the Baud rate and ACK char
    # --------------------------------------------------------------------------
    def Init(self):
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
        print 'DEBUG',j 

    # --------------------------------------------------------------------------
    # sends command, starts with ESC and waits for ACK
    # --------------------------------------------------------------------------
    def Csi(self,str):
        self.sp.flushInput()
        self.sp.write(ESC+str)
        self.Wack()

    # --------------------------------------------------------------------------
    # for commands that just return ACK,
    # Does not return anything but will wait for the ACK char
    # --------------------------------------------------------------------------
    def Wack(self):
        k = 0
        j = 10 # time out after this
        while k != self.ack:
            k = self.sp.read(1)
            j = j - 1
            if j <= 0: break
        # DEBUG
        if j < 5: 
            print "Possible command problem"
             
    # --------------------------------------------------------------------------
    # reads characters up to ACK and returns them
    # note will return a string
    # --------------------------------------------------------------------------
    def CsiRead(self,str):
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
        return self.CsiRead('[?31d')

    # ------------------------------------------------------------------------------
    # firmware version
    # ------------------------------------------------------------------------------
    def Firmware(self):
        return self.CsiRead('[?31f')
    
    # ******************************************************************************
    # RELAYS
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # truns realy on or off action = 0 for off
    # ------------------------------------------------------------------------------
    def RelayA(self,action):
        if action == 0:
            self.Csi('[0A')
        else:
            self.Csi('[1A')
    
    def RelayB(self,action):
        if action == 0:
            self.Csi('[0B')
        else:
            self.Csi('[1B')
    
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
        self.Csi('['+str(action)+'s')
    
    # ------------------------------------------------------------------------------
    # return port value
    # ------------------------------------------------------------------------------
    def Ioval(self):
        return self.CsiRead('[r')
    
    # ------------------------------------------------------------------------------
    # sets a PWM value for a given channel
    # chanal should be a value from 'a' to 'h' as text
    # value should also be an integer '0' to '255'
    # ------------------------------------------------------------------------------
    def Ioout(self,chan,val):
        self.Csi('['+str(val)+chan)
        
    # ******************************************************************************
    # ADC, Analogue to Digital
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # gets value of specified channel
    # Range 0 to 3
    # ------------------------------------------------------------------------------
    def Adcin(self,chan):
        return self.CsiRead('['+str(chan)+'D')

    # ------------------------------------------------------------------------------
    # Sets voltage refrence
    # value is 0 to 3
    # 0 = 1.02V
    # 1 = 2.048V
    # 3 = 4.096V
    # ------------------------------------------------------------------------------
    def Adcvoltage(self,value):
        self.Csi('['+str(value)+'V')
        
    # ******************************************************************************
    # DAC, Digital to Analogue
    # ******************************************************************************
    # ------------------------------------------------------------------------------
    # outputs a value to a channel X
    # Range
    # value = 0 to 63
    # ------------------------------------------------------------------------------
    def DacX(self,value):
        self.Csi('['+str(value)+'X')
           
    # ------------------------------------------------------------------------------
    # outputs a value to a channel Y
    # Range
    # value = 0 to 63
    # ------------------------------------------------------------------------------
    def DacY(self,value):
        self.Csi('['+str(value)+'Y')

