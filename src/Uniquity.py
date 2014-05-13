import sys
import os
import wx


if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    BASEPATH = sys._MEIPASS
else:
    # we are running in a normal Python environment
    BASEPATH = os.path.dirname(__file__)

#Add the path
sys.path.insert(0, os.path.abspath(BASEPATH))

#With path setup, we can finally import what we need from the project
import views.controller

#Start the main Uniquity GUI
uniquity = views.controller.Controller()
