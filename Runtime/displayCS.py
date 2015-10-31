#!/usr/bin/python
#displayCS.py
#
# Copyright (C) 2011 Michael Schurpf
# E-mail: michaelschuerpf AT gmail DOT com 
#
# Simple module to convert coordinates in between screens
#
# Scripts maintained at http://www.swisstard.com
# Comments, suggestions and bug reports welcome.
#
# Released subject to the GNU Public License
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# In addition to the permissions in the GNU General Public License, the
# authors give you unlimited permission to link or embed the compiled
# version of this file into combinations with other programs, and to
# distribute those combinations without any restriction coming from the
# use of this file. (The General Public License restrictions do apply in
# other respects; for example, they cover modification of the file, and
# distribution when not linked into a combine executable.)
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA



import win32api,win32gui

try:
    #only needed to show screen numbers
    import wx, time

    class wxSimple(wx.Frame):

        def __init__(self, text, pos=(10,10), parent=None, id=-1, title=""):
            wx.Frame.__init__(self, parent, id, title,size=(40,60))

            self.panel = wx.Panel(self)

            wx.StaticText(self.panel, -1, text)

            self.Move(pos)

            self.Show()
            
except:
    pass
    

class AllDisplay:
    def __init__(self):
    
        self.monitorInfo = {}        

        monitorList = win32api.EnumDisplayMonitors()

        #get monitor data
        for mon in monitorList:
            monitorInfoTemp = win32api.GetMonitorInfo(mon[0])
            deviceNbr = int(monitorInfoTemp['Device'].split('DISPLAY')[-1])
            ltrb =  monitorInfoTemp['Monitor'] #left, top, right, bottom

            self.monitorInfo[deviceNbr] = ltrb

    def DispV2DispW(self,pos,dispV, dispW):
        """transfer a pos in display V coordinates to coordinates in display W.
    Diplays are given as  integers. 1: default display, 2: secondary display, ..."""
        vdata = self.monitorInfo[dispV]
        wdata = self.monitorInfo[dispW]

        V0 = [vdata[0],vdata[1]]
        W0 = [wdata[0],wdata[1]]

        return self.addVec(self.addVec(self.multVec(-1,W0),V0),pos)

    def showDisplayNumbers(self):
        """show all display and according display numbers.
Wxpython needed for this!"""
        try:
            app = wx.App()
            frameList = []
            for dispNbr in self.monitorInfo.keys():
                pos = self.DispV2DispW((10,10),dispNbr,1)
                frameList.append(wxSimple(str(dispNbr),pos))

##            time.sleep(5)
##            for f in frameList:
##                f.Close()
            
            app.MainLoop()
        except:
            win32gui.MessageBox(0, "Wxpython is needed to show screen numbers.", "Wxpython missing", 0)

    def hitTest(self, currPos = -1):
        """Return display number where currPos is currently on.
no argument passed => current cursor position is used."""
        if currPos == -1:
            currPos = win32gui.GetCursorPos()

        for dispNbr in self.monitorInfo.keys():
            ltrb = self.monitorInfo[dispNbr]
            monitorRect = wx.Rect(ltrb[0],ltrb[1],abs(ltrb[0]-ltrb[2]),abs(ltrb[1]-ltrb[3]))
            if monitorRect.InsideXY(currPos[0],currPos[1]):
                print dispNbr, currPos[0],currPos[1]
                return dispNbr
        return 0

        
#-------
#helper fun

    def addVec(self,a,b):
        return map(lambda x,y: x+y, a, b)

    def multVec(self,k,a):
        return [k*x for x in a]

    def __str__(self):
        printStr = 'Display \tleft top right bottom\n'
        for dispNbr in self.monitorInfo.keys():
            ltrb = self.monitorInfo[dispNbr]
            printStr += str(dispNbr)+': \t'+str(ltrb)+'\n'
        return printStr
        
        
if __name__ == "__main__" :    
##    import sys
##    sys.stdout = open('stdout.txt','w')
    
    #test with 2 displays
    p=(100,100)
    d = AllDisplay()
    print d.DispV2DispW(p,1,1)
    print d.DispV2DispW(p,1,2)
    print d.DispV2DispW(p,2,1) #convert p given in display 2 cs into display 1 cs

    print d

    ###d.showDisplayNumbers() #need wxpython to run

    #close number display frames to have demo continue

    #test hittest
    print "hit test"
    for i in range(5):
        print d.hitTest()
        time.sleep(1)

