# Copyright (c) 2008, Comat Technologies Pvt Ltd
# Author: Kiran Jonnalagadda <kiran.j@comat.com>

"""
RBC Windows Boot Script Service executes maintenance scripts at boot time.

Usage:

  Installation

    The RBC service should be installed by the RBC Windows
    installer. You can manually install, uninstall the service from
    the commandline.

      rbcservice.py [options] install|update|remove|start [...]
           |stop|restart [...]|debug [...]

    Options for 'install' and 'update' commands only:

     --username domain\username : The Username the service is to run
                                  under

     --password password : The password for the username

     --startup [manual|auto|disabled] : How the service starts,
                                        default = manual

    Commands

      install : Installs the service

      update : Updates the service.  Use this if you change any
               configuration settings and need the service to be
               re-registered.

      remove : Removes the service

      start : Starts the service, this can also be done from the
              services control panel

      stop : Stops the service, this can also be done from the
             services control panel

      restart : Restarts the service

    You can view the usage options by running this module without any
    arguments.
"""

import sys, os

import pywintypes
import winerror, win32con
import win32api, win32event, win32file, win32pipe, win32process, win32security
import win32service, win32serviceutil
import servicemanager
import _winreg as wreg


import traceback

def ApplyIgnoreError(fn, args):
    try:
        return apply(fn, args)
    except error: # Ignore win32api errors.
        return None

class WindowsRegistry:

    def __init__(self, company="Comat", project="TCConfig", write=1):
        """
        handle registry access
        """
        self.write = write
        self.company = company
        self.project = project
        self.keyname = "Software\\%s\\%s" % (self.company, self.project)

        try:
            self.key = wreg.OpenKey(wreg.HKEY_LOCAL_MACHINE, self.keyname)
        except:
            if self.write:
                self.key = wreg.CreateKey(wreg.HKEY_LOCAL_MACHINE, self.keyname)

    def set(self, name, value):
        " set value in registry "
        if not self.write:
            raise Exception, "registry is read only"
        wreg.SetValue(self.key, name, wreg.REG_SZ,str(value))

    def pset(self, name, value):
        " set using pickle "
        self.set(name, pickle.dumps(value))

    def get(self, name):
        " get value out of registry "
        return wreg.QueryValue(self.key, name)

    def pget(self, name):
        " get using pickle "
        return pickle.loads(self.get(name))

    def close(self):
        " close the key finally "
        self.key.Close()

    def __del__(self):
        self.close()


class RBCService(win32serviceutil.ServiceFramework):
    """Windows service to execute a set of startup scripts."""
    _svc_name_ = "RBC-Service"
    _svc_display_name_ = "RBC Windows Boot Service"
    _svc_description_ = "Executes Python scripts at boot time."

    evtlog_name = 'ComatRBC'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)

        try:
            servicemanager.SetEventSourceName(self.evtlog_name)
        except AttributeError:
            # old pywin32 - that's ok.
            pass
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        # Before we do anything, tell the SCM we are starting the stop process.
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.onStop()
        # Set the stop event - the main loop takes care of termination.
        win32event.SetEvent(self.hWaitStop)

    # SvcStop only gets triggered when the user explictly stops (or restarts)
    # the service.  To shut the service down cleanly when Windows is shutting
    # down, we also need to hook SvcShutdown.
    SvcShutdown = SvcStop

    def logmsg(self, event):
        # log a service event using servicemanager.LogMsg
        try:
            servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                                  event,
                                  (self._svc_name_,
                                   " (%s)" % self._svc_display_name_))
        except win32api.error, details:
            # Failed to write a log entry - most likely problem is
            # that the event log is full.  We don't want this to kill us
            try:
                print "FAILED to write INFO event", event, ":", details
            except IOError:
                pass

    def _dolog(self, func, msg):
        try:
            fullmsg = "%s (%s): %s" % \
                      (self._svc_name_, self._svc_display_name_, msg)
            func(fullmsg)
        except win32api.error, details:
            # Failed to write a log entry - most likely problem is
            # that the event log is full.  We don't want this to kill us
            try:
                print "FAILED to write event log entry:", details
                print msg
            except IOError:
                # And if running as a service, its likely our sys.stdout
                # is invalid
                pass

    def info(self, s):
        self._dolog(servicemanager.LogInfoMsg, s)

    def warning(self, s):
        self._dolog(servicemanager.LogWarningMsg, s)

    def error(self, s):
        self._dolog(servicemanager.LogErrorMsg, s)

    def SvcDoRun(self):
        self.logmsg(servicemanager.PYS_SERVICE_STARTED)
        win32api.Sleep(1000)
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.logmsg(servicemanager.PYS_SERVICE_STOPPED)

    def onStop(self):
        pass

if __name__=='__main__':
    win32serviceutil.HandleCommandLine(RBCService)
