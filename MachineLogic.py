#!/usr/bin/python
import sys
import time 
import datetime 
import RPi.GPIO as io 
import select
import SectorAdminSite
import RFIDDataAccess
import subprocess
import glob
import os
#import Adafruit_CharLCDPlate
#from Adafruit_I2C import Adafruit_I2C
import locale
import math
import Adafruit_PCA9685

class MachineLogic:
    rfid =0
    prevRFID = 0
    billingRFID = 0
    cashRFID = 7898934
    machineID = 4
    Led0 = 0
    Led1 = 1
    Led2 = 2
    Led3 = 3
    Led4 = 4
    led5 = 5
    Led6 = 6
    Led7 = 7
    Led8 = 8
    Led9 = 9
    Led10 = 10
    Led11 = 11
    greenLed = 12
    redLed =13
    valve = 14
    valve2 = 15   
    isbusy = False
    DebugMode = False
    fullname= ''
    accruingDue = 0.0
    sleepTime = 1
    state = [ "DISABLED",  "VERIFYING",  "ENABLED",  "ENROLLING"]
    currentstate = "DISABLED"
    authService = SectorAdminSite.SectorAdmin()
    access = RFIDDataAccess.DataAccess()
    locale.setlocale(locale.LC_ALL,'')
    pwm = 0
    pca = 0


    def Busy(self):
        return self.isbusy

    def Setup(self):
        i = 0
        print("setup")
        self.pwm = Adafruit_PCA9685.PCA9685()
        lights = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13,]
        for light in sorted(lights):
            self.pwm.set_pwm(light,0x1000, 0)
            print "Turn off the lights. "
        #Closing the valves.
        valves = [self.valve, self.valve2]
        for valve in valves:
            self.pwm.set_pwm(valve, 0x1000, 0)
        time.sleep(1)
        print "sleeping"

    def LedUnauthroized(self):
        print "LedAunthorzied triggered"
        redLed = 13
        self.pwm.set_pwm(redLed,0, 0x1000)
        time.sleep(3)
        print "turned off the red led for 3 seconds." 
        self.pwm.set_pwm(redLed,0x1000,0)

    def LedFadeOff(self):
        print "AuthenticationLed triggered"
        valves = [self.valve, self.valve2]
        #Opening up the valves.
        for valve in valves:
            self.pwm.set_pwm(valve,0, 0x1000)
        #Setting the green leds. 
        greenLed = 12        
        self.pwm.set_pwm(greenLed, 0, 0x1000)
        lights = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
        for light in sorted(lights):
            self.pwm.set_pwm(light,0, 0x1000)
        for light in sorted(lights):
            print "diming light" + str(light)
            for i in xrange(0, 4095, 10):
                self.pwm.set_pwm(light, 0, i)
                time.sleep(0.001)
            self.pwm.set_pwm(light,0x1000, 0)
        #Closing the valves.
        for valve in valves:
            self.pwm.set_pwm(valve, 0x1000, 0)
        print "Turning off the green light"
        self.pwm.set_pwm(greenLed, 0x1000, 0)

    def SetRFID(self, inRFID):
        self.prevRFID = self.rfid
        self.rfid = inRFID

    #// If a job has recently ended, report it
    def ReportJob(self):        
        #newest = max(glob.iglob('/home/pi/ImageLog/*.jpg'), key=os.path.getctime)
        #print(newest)
       #jpgfile = open(newest).read()
        amount = 1
        try:
            amount = self.authService.AddMachinePayment(int(self.billingRFID),1,self.machineID, 'Kegerator purchase 1.00 unit')
        except:
            print('internet connection failed')

    def CaptureImage(self):

        subprocess.call("/home/pi/grabPic.sh")


    def DoUnAuthorizedContinuousWork(self):
        i = 0


    def DoAuthorizedWork(self):
        self.LedFadeOff();
        i = 0

    def SetBillingAccount(self, rfid):
        if self.currentstate == "ENABLED" and self.laseron <> True:
              self.fullname = ''
        try:
              data = self.authService.GetUserByRFID(rfid)            
              self.fullname = data
              print(self.fullname)
              self.billingRFID = rfid
        except:
              print('cannot add billing user')
        self.LCDRefresh = True

    def CheckButton(self):
        for self.b in self.btn:
            if self.lcd.buttonPressed(self.b[0]):
                if self.b is not self.prev:
                    print(self.b[1])
            if self.b[1] == "Down":
               self.DebugMode = True
            if self.b[1] == "Up":                  
               self.DebugMode = False
               self.LCDRefresh = True
            self.prev = self.b
