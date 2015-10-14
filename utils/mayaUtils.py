__author__ = 'Natasha'

import subprocess
import signal

mayapyLocation = 'C:\\Program Files\\Autodesk\\Maya2016\\bin\\mayapy.exe'
outputStr = ''

def getSceneData(sceneFile):
    mayaCameraScript = 'P:\\dev\\shot_submit\\maya_scripts\\getSceneData.py'
    cmd = '"%s" %s %s' % (mayapyLocation, mayaCameraScript, sceneFile)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    outputStr = process.stdout.read()