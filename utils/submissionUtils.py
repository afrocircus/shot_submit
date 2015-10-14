__author__ = 'Natasha'

import subprocess
import re


def submitCmd(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    outputStr = process.stdout.read()
    return outputStr

def getJobID(outputStr):
    m = re.search(r'\[(\w+)\=(?P<id>\d+)\]', outputStr)
    return m.group('id')