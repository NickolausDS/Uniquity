import sys
import os
import wx


if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    BASEPATH = sys._MEIPASS
else:
    # we are running in a normal Python environment
    BASEPATH = os.path.dirname(__file__)

# IMAGE_DIR=os.path.join(BASEPATH, "assets" + os.path.sep)
#NOTE: This adds the path of the current working directory instead of this file. BUG!!!
sys.path.insert(0, os.path.abspath(BASEPATH))
# IMAGE_DIR=os.path.join(BASEPATH, "assets")
# sys.path.insert(0, IMAGE_DIR)


import data.config
import models.logger
import models.uniquity
import views.mainView


app = wx.App(False)
frame = views.mainView.MainWindow(None, "Uniquity -- The Unique File Analyzer")
app.MainLoop()
exit(0)