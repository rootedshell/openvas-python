#!/usr/bin/env python
# ---------------------------------------------------------------
# rootedshell


import thread
import re
import sys
import subprocess
import time


# colors
RED   = "\033[1;31m"
BLUE  = "\033[1;34m"
CYAN  = "\033[1;36m"
GREEN = "\033[0;32m"
REVERSE = "\033[;7m"
ENDC = '\033[0m'
YELLOW = '\033[93m'


#
def hello():
  print '------------------------------------------------------------------------------'
  print "                               openvas-python"
  print '------------------------------------------------------------------------------'
  

##
# set target host/IP
try:
  hello()

  target = sys.argv[1]

  ##
  # create target for new scan:
  cmd = "omp -u admin -w password --xml='<create_target> <name>"+target+"</name> <hosts>"+target+"</hosts> </create_target>' > tmp.resp"
  runme = subprocess.call([cmd],shell=True)

  readRespForID = open('tmp.resp','r')
  lines = readRespForID.readlines()

  for line in lines:
    # read resp from creating targetID:
    trying = re.compile('create_target_response id="(.*?)"')
    found = re.search(trying, line)

    if found:
      targetID = found.group(1)
      print BLUE + "[+] Found target ID: " + ENDC + RED + str(targetID) + ENDC

  ##
  # prepare scan options (default full scan):
  configID = "daba56c8-73ec-11df-a475-002264764cea" # default mode: full and fast scan ;)
  cmd = "omp -u admin -w password --xml='<create_task> <name>Full and fast scan</name> <comment>Full and fast</comment> <config id=\""+ configID +"\"/> <target id=\""+ targetID +"\"/> </create_task>' > tmp.task"

  print '[+] Preparing options for the scan...'
  runme = subprocess.call([cmd],shell=True)

  getTaskID = open('tmp.task','r')
  lines = getTaskID.readlines()

  for line in lines:
    trying = re.compile('create_task_response id="(.*?)"')
    found = re.search(trying, line)

    if found:
      taskID = found.group(1)
      print GREEN + '[+] Task ID = ' + ENDC +  str(taskID)


  ##
  # run prepared taskID for targetID
  print GREEN + '[+] Running scan for '+ ENDC +  RED + str(target) + ENDC

  # yep, you will be asked for a pass here ;) # 05.01.17; not anymore
  cmd = "omp -u admin -w password --xml='<start_task task_id=\""+ taskID + "\"/>' > tmp.startID"
  runme = subprocess.call([cmd], shell=True)
  print GREEN + '[+] Scan started... ' + ENDC + 'To get current status, see below:\n\t' + ENDC# or type: omp -u admin -G'
  print YELLOW # 01
  # sleep few secs to get -G with our target:
  time.sleep(3)

  cmd2 = "omp -u admin -w password -G | grep %s > tmp.stat" % ( taskID)
  # print cmd2
  runme = subprocess.call([cmd2],shell=True)


  while 'Done' not in open('tmp.stat','r').read():

   
    def work():
      time.sleep( 5 )

    def locked_call( func, lock ):
      lock.acquire()
      func()
      lock.release()

    lock = thread.allocate_lock()
    thread.start_new_thread( locked_call, ( work, lock, ) )

    # This part is icky...
    while( not lock.locked() ):
      time.sleep( 0.1 )

    while( lock.locked() ):
      sys.stdout.write( "#" )
      sys.stdout.flush()
      time.sleep( 1 )
    # --

    runme = subprocess.call([cmd2],shell=True)

  print ENDC # 02 - fin yellow
  

  # target/taskID is scanned. rewriting results to report:
  print GREEN + '[+] Target scanned. Finished taskID : ' + ENDC + RED + str(taskID) + ENDC

  # reports
  print CYAN + '[+] Generating Reports...' + ENDC

  getXml = "omp -u admin -w password -X '<get_reports/> <report id><task id=\""+ str(taskID)  +"\"/>' > get.xml"
  #print getXml

  rungetXml = subprocess.call([getXml],shell=True)
  print '[+] Report ID'

  lookingFor = '<report id="(.*?)" format_id="(.*?)<task id="' + str(taskID) + '"'
#  print lookingFor

  xml = open('get.xml','r')
  xlines = xml.readlines()

  for xline in xlines:
    match = re.compile(lookingFor)
    found = re.search(match, xline)

    if found:
      repID = found.group(1)
      print GREEN + '  [+] Found report ID : ' + repID + ENDC
      print GREEN + '  [+] For taskID      : ' + taskID + ENDC

      print '' + BLUE
      print '[+] Preparing report in CSV for %s ' % target
      print ENDC
      repName = 'Report_for_'+str(target)+'.csv'

      getRep = ("omp -u admin -w password --get-report %s --format 9087b18c-626c-11e3-8892-406186ea4fc5 > %s") % (repID, repName)

      runme = subprocess.call([getRep],shell=True)

      print '[+] Report should be done in : ' + GREEN +  str(repName) + ENDC
    

except NameError, e:
  print RED + '[-] TargetID already exists, try different target host/IP' + ENDC
  print e
  pass



# Reference
# https://github.com/c610
# https://github.com/greenbone/gvmd/blob/master/CMakeLists.txt
# http://stackoverflow.com/a/3160917
