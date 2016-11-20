import requests
import json
import datetime
import RFIDDataAccess
import SectorAdminSite
import sys
import time 
import datetime 
import RPi.GPIO as io 
import select
from time import gmtime, strftime
import subprocess
import os
import MachineLogic
from datetime import datetime, timedelta

localRFID = ""
rebootTime = time.time() + 86400
free_beer_hours = 8 
machine = MachineLogic.MachineLogic()
machine.Setup()

authService = SectorAdminSite.SectorAdmin()
access = RFIDDataAccess.DataAccess()

try:
   #Pull down the current list of authorized users
   data = authService.GetAuthorizedUsers(machine.machineID)
    
   print('adding users to database')
   #Delete Current Cache of Authorized users
   access.DeleteAllAuthorizedUsers()

   #authService.UpdateMachine(machineID)

   #add the users to the cache
   #for user in data:
   #   access.InsertAuthorizedUser(user[0],user[0],user['display_name']  )

   for user in data["message"]:
   #print (user["rfid"])
      access.InsertAuthorizedUser(int(user["rfid"]),0,user["display_name"]) 

except Exception, e:
   print e

freebeertill = None

#loop forever
while True:
    # read the standard input to see if the RFID has been swiped
    while sys.stdin in select.select([sys.stdin],[],[],0)[0]:
        localRFID = sys.stdin.readline()
        if localRFID:
            localRFID = ''.join(localRFID.splitlines())
            #RFID has been swiped now check if authorized
        print(int(localRFID))
        if access.IsRFIDAuthorized(int(localRFID)):
           print('access.IsRFIDAuthorized was triggred.')
           machine.DoAuthorizedWork()
           machine.rfid = int(localRFID)
           machine.SetBillingAccount(int(localRFID))
           machine.ReportJob()
        else:
           print('User does not have acces')
           print 'localrfid is ' + localRFID 
           machine.LedUnauthroized()
        if str(localRFID) == '0006115262':  #       if str(localRFID) == '463355':0000463355
           print "Time for free info"
           if not freebeertill:
               freebeertill = datetime.now() + timedelta(hours=free_beer_hours)
           else:
               print "No free beer."
               freebeertill = None
               machine.GreenLightOff()
               machine.Closeupthevalues() 
        if freebeertill:     
           now = datetime.now()
           if freebeertill > now:
               print "still free beer"
               machine.GreenLightOn()
               machine.Openupthevalues()
           else:
               print "free beer has gone away :("
               machine.GreenLightOff()
               machine.Closeupthevalues()
    if freebeertill:     
        now = datetime.now()
        if freebeertill > now:
            print "still free beer"
            machine.GreenLightOn()
            machine.Openupthevalues()
        else:
            print "free beer has gone away :("
            machine.GreenLightOff()
            machine.Closeupthevalues()
    time.sleep(machine.sleepTime)

    if  time.time() > rebootTime and not machine.Busy():
        print("rebooting")
        os.system("reboot")
