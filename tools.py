import time
import os
from sys import platform

def wait(secs):
    time.sleep(secs)
    pass

def clearScreen():
    if platform == "win32":
        os.system('cls')
    elif platform in ["linux", "linux2", "darwin"]:
        os.system('clear')
