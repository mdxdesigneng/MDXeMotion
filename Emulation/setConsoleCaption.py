import win32console, win32con
import win32gui
from win32console import GetConsoleWindow
import sys

def setConsoleCaption(caption):
       hwnd = win32console.GetConsoleWindow();
       win32gui.SetWindowText(hwnd, caption)    

def identifyConsoleApp():
    setConsoleCaption(sys.argv[0])