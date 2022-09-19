#!/usr/bin/python3
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

import time
import sys
import os
import re
import subprocess
import win32serviceutil  # ServiceFramework and commandline helper
import win32service  # Events
import servicemanager  # Simple setup and logging
from pathlib import Path
import logging
import logging.handlers


log_file = r'C:\Program Files\Pulse\var\log\service.log'
agent_dir = Path(r'"%PROGRAMFILES%"\Python37\Lib\site-packages\pulse_xmpp_agent')
launcher = agent_dir / "launcher.py"
python = Path(r'C:\"Program Files"\Python37\python.exe')



class MyService:
    """Silly little application stub"""
    def stop(self):
        """Stop the service"""
        self.running = False

    def run(self):
        """Main service loop. This is where work is done!"""
        self.isdebug = False
        self.command = "%s %s -t machine"%(python, launcher)


        if "-debug" in sys.argv:
            self.command = "%s %s -c -t machine"%(python, launcher)
            self.isdebug = True

        self.running = True
        while self.running:
            time.sleep(5)
            os.system(self.command)


class MyServiceFramework(win32serviceutil.ServiceFramework):

    _svc_name_ = 'pulseagent'
    _svc_display_name_ = 'Pulse Agent'

    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.service_impl.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def SvcDoRun(self):
        """Start the service; does not return until stopped"""
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        self.service_impl = MyService()
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        # Run the service
        self.service_impl.run()


def init():
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(MyServiceFramework)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(MyServiceFramework)

if __name__ == '__main__':
    init()
