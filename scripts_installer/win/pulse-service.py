#!/usr/bin/env python
# -*- coding: utf-8; -*-
#
# (c) 2016 siveo, http://www.siveo.net
#
# This file is part of Pulse 2, http://www.siveo.net
#
# Pulse 2 is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Pulse 2 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pulse 2; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
# MA 02110-1301, USA.

# generation bach file 'C:\\Program Files\\Pulse\\bin\\pulse-service-process.bat' pour lancer les service.
# usage pulse-service-process.bat nomservicepython programme args
# ce fichier bat est généré automatiquement.

import socket

import win32serviceutil

import servicemanager
import win32event
import win32service
import win32evtlog
import time
import re
import subprocess
import os
import sys
import logging
import logging.handlers
import urllib2
from shutil import copyfile
from subprocess import call
import psutil

log_file = os.path.join("c:\\", "Program Files", "Pulse", "var", "log", "service.log")
agent_dir = os.path.join("C:\\", "Python27","Lib", "site-packages", "pulse_xmpp_agent")

logger = logging.getLogger("pulseagentservice")

logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler(log_file, maxBytes=10485760, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(module)-10s - %(levelname)-8s %(message)s', '%d-%m-%Y %H:%M:%S')
handler.setFormatter(formatter)
logger.addHandler(handler)

pythondir = "c:\\Python27\\"
processname = "agent-pulse-service"

class SMWinservice(win32serviceutil.ServiceFramework):
    '''Base class to create winservice in Python'''

    _svc_name_ = 'pythonService'
    _svc_display_name_ = 'pythonservice'
    _svc_description_ = 'Python Service Description'

    @classmethod
    def parse_command_line(cls):
        '''
        ClassMethod to parse the command line
        '''
        win32serviceutil.HandleCommandLine(cls)

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        '''
        Called when the service is asked to stop
        '''
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        '''
        Called when the service is asked to start
        '''
        self.start()
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_, ''))
        self.main()

    def start(self):
        '''
        Override to add logic before the start
        eg. running condition
        '''
        pass

    def stop(self):
        '''
        Override to add logic before the stop
        eg. invalidating running condition
        '''
        pass

    def main(self):
        '''
        Main class to be ovverridden to add logic
        '''
        pass

def path_excec_script():
    name_bat_file = "pulse-service-process.bat"
    #creation du fichier bat pour windows
    directory_launcher = os.path.dirname(os.path.realpath(__file__))
    pythonexec = os.path.join( directory_launcher, name_bat_file)
    return pythonexec

def creation_excec_script():
    contentfile="""set PYTHON_HOME="%s"
set PYTHON_NAME=%%1.exe
copy "%%PYTHON_HOME%%python.exe" "%%PYTHON_HOME%%%%PYTHON_NAME%%"
set args=%%*
set args=%%args:* =%%
"%%PYTHON_HOME%%%%PYTHON_NAME%%" %%args%% """ % pythondir
    file_put_contents(path_excec_script(), contentfile)

def file_put_contents(filename, data):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    f = open(filename, 'w')
    f.write(data)
    f.close()

def file_get_contents(filename, use_include_path=0,
                      context=None, offset=-1, maxlen=-1):
    if (filename.find('://') > 0):
        ret = urllib2.urlopen(filename).read()
        if (offset > 0):
            ret = ret[offset:]
        if (maxlen > 0):
            ret = ret[:maxlen]
        return ret
    else:
        fp = open(filename, 'rb')
        try:
            if (offset > 0):
                fp.seek(offset)
            ret = fp.read(maxlen)
            return ret
        finally:
            fp.close()

class PulseAgentService(SMWinservice):
    _svc_name_ = "pulseagent"
    _svc_display_name_ = "Pulse agent"
    _svc_description_ = "Workstation management agent"
    isrunning = False
    isdebug = False
    listnamefilepid=["pidlauncher","pidconnection","pidagent"]

    def __init__(self, args):
        '''
        Constructor of the winservice
        '''
        # self.my_service_name = "processpulse.exe"
        # self.mame_exec = "python.exe"

        # self.executable = os.path.join("c:\\", "Python27", self.mame_exec)
        # batfile="""set PYTHON_HOME="c:\\Python27\\"
         # set PYTHON_NAME=%1.exe
         # copy "%PYTHON_HOME%python.exe" "%PYTHON_HOME%%PYTHON_NAME%"
         # set args=%*
         # set args=%args:* =%
         # "%PYTHON_HOME%%PYTHON_NAME%" %args%"""


        # if sys.executable not in [None, ""]:
            # self.executable = os.path.realpath(sys.executable)
            # logger.info("My executable  %s"% self.executable)

            # logger.info("sys executable  %s"% sys.executable)

            # pathexecutable =  os.path.dirname(self.executable)
            # self.executable = os.path.join(pathexecutable, self.mame_exec)

            # logger.info("My executable  %s"% self.executable)


        # pathexecutable =  os.path.dirname(self.executable)

        # self.file_path = os.path.dirname(os.path.realpath(__file__))

        # self.my_program = os.path.join( pathexecutable,
                                        # self.my_service_name)

        # logger.info("My programm  %s"%self.my_program)
        # if os.path.exists(self.my_program):
            # os.remove(self.my_program)


        # logger.info("My executable  %s"% self.executable)
        # copyfile( self.executable, self.my_program)

        SMWinservice.__init__(self, args)

    def start(self):
        if "-debug" in sys.argv:
            self.isdebug = True
            logger.info("Service %s launched in debug mode"%self._svc_display_name_)
        else:
            logger.info("Service %s launched in normal mode"%self._svc_display_name_)
        creation_excec_script()
        self.isrunning = True

    def kill_proc_tree(self,  including_parent=True):
        parent = psutil.Process(self.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()
        gone, still_alive = psutil.wait_procs(children, timeout=5)
        if including_parent:
            parent.kill()
            parent.wait(5)

    def stop(self):
        self.isrunning = False
        logger.info("Service %s stopped" %self._svc_display_name_)
        cmd =""
        self.kill_proc_tree()

    def main(self):
        i = 0
        while self.isrunning:
            batcmd ="NET START"
            result = subprocess.check_output(batcmd, shell=True)
            filter = "pulseagent"
            if not re.search(filter, result):
                if not self.isdebug:

                    args = [path_excec_script(),
                            "agent_pulse",
                            "%s"%os.path.join(agent_dir, "launcher.py"),
                            "-t",
                            "machine"]
                    # args = [self.my_program, "%s"%os.path.join(agent_dir, "launcher.py"), "-t", "machine"]
                    logger.info("agent_dir %s"%agent_dir)
                    logger.info("args %s"%args)

                    self.ProcessObj = subprocess.Popen( args,
                                                    stdout=None,
                                                    stderr=None,
                                                    stdin=None,
                                                    close_fds=True)
                    logger.info("yes %s"%args)
                    logger.info("yes %s"%str(self.ProcessObj.pid))
                    time.sleep(1)
                    self.pid = self.ProcessObj.pid

                    logger.info("pid %s"%self.pid)
                    self.ProcessObj.wait()
                else:
                    args = [path_excec_script(),
                            "launcher_pulse_debug",
                            "%s"%os.path.join(agent_dir, "launcher.py"),
                            "-c",
                            "-t",
                            "machine"]
                    logger.info("args %s"%args)
                    p = call(args)
                    p.wait()
            else:
                time.sleep(5)

if __name__ == '__main__':
    PulseAgentService.parse_command_line()
