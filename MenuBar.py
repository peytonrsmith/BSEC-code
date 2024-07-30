#!/usr/bin/env python

# Copyright (c) 2014 Johns Hopkins University
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# - Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the
#   distribution.
# - Neither the name of the copyright holders nor the names of
#   its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL
# THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.


import Tkinter
import subprocess
import tkMessageBox
import webbrowser
import os
from Tkinter import *

from tools.serial.tools.list_ports import *
from tools.labeler.Handler import Handler
from tools.labeler.GraphFrame import GraphFrame
import tools.labeler.ttk as ttk


class MenuBar(Frame):

    BASESTATION_SIZE = 3326
    ROUTER_SIZE = 3326
    LEAF_SIZE = 3326
    TOASTER_SIZE = 20136

    comDict = {}
    DEFAULT_STRING = "<no device detected>"

    def __init__(self, parent, handler, **args):
        Frame.__init__(self, parent, **args)
#        Menu.__init__(parent, **args)
        
        # parent frame - for centering pop-up boxes
        self.parent = parent

        # handler for UI actions
        self.handler = handler
        
        # connection status
        self.connected = False
        
        # variable to track programming status 
        self.programVar = BooleanVar()
        self.programVar.trace("w", self.programDone)
        #
        self.basestation_file = os.path.join('tools', 'firmware', 'basestation.ihex')
        self.leaf_file = os.path.join('tools', 'firmware', 'leaf.ihex')
        self.router_file = os.path.join('tools', 'firmware', 'router.ihex')
        self.toaster_file = os.path.join('tools', 'firmware', 'toaster.ihex')
        
        #        
        self.initUI()
        self.pack()

    def donothing():
        filewin = Toplevel(root)
        button = Button(filewin, text="Do nothing button")
        button.pack()


    def initUI(self):
        """Create a MENUBAR 
        """
        self.fileMenu = Menu(self, tearoff=0)
        self.fileMenu.add_command(label="Options", command=self.donothing)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Exit", command=self.quit)
        self.parent.add_cascade(label="File", menu=self.fileMenu)
                
        self.connectMenu = Menu(self, tearoff=0)
        self.connectMenu.add_command(label="Connect", command=self.connect)
        self.connectMenu.add_separator()
        self.parent.add_cascade(label="Connection", menu=self.connectMenu)
        self.portsMenu = Menu(self.connectMenu,tearoff=0)
        self.connectMenu.add_cascade(label="Ports", menu=self.portsMenu)
        
        self.progMenu = Menu(self, tearoff=0)
        self.progMenu.add_command(label="Worker node", command=self.programLeaf)
        self.progMenu.add_command(label="Router node", command=self.programRouter)
        self.progMenu.add_command(label="Basestation", command=self.programBasestation)
        self.parent.add_cascade(label="Programming", menu=self.progMenu)
        
        self.dbMenu = Menu(self, tearoff=0)
        self.dbMenu.add_command(label="Export metadata", command=self.donothing)
        self.parent.add_cascade(label="Database", menu=self.dbMenu)
        
        self.helpmenu = Menu(self, tearoff=0)
        self.helpmenu.add_command(label="Help document", command=self.show_help)
        self.helpmenu.add_command(label="LUYF website", command=self.show_luyf)
        self.helpmenu.add_command(label="Device barcodes", command=self.donothing)
        self.helpmenu.add_command(label="Sensor barcodes", command=self.donothing)
        self.helpmenu.add_command(label="About...", command=self.donothing)
        self.parent.add_cascade(label="Help", menu=self.helpmenu)
        
        # column 2, option menu for COM port
        # populated by the deviceDetection function
        self.comVar = StringVar()        
        self.comVar.set(self.DEFAULT_STRING)
        self.portsMenu.add_radiobutton(label=self.comVar)
        #
        self.comOption = self.portsMenu
            
        # column 10, progress bar
        self.progressVar = IntVar()
        self.progressVar.set(0)

#         self.progressBar = ttk.Progressbar(self, orient='horizontal', variable=self.progressVar, length=104, mode='determinate')
#         self.progressBar.grid(column=10, row=1)
        
        # send message
        self.handler.debugMsg("No USB device detected, plase insert one")
        
#         # detect devices. this function calls itself every second.
        self.deviceDetection()

    def donothing(self):
        return
            
    def noUSB(self):
        self.handler.debugMsg("No USB device detected, please connect one")
        

    def deviceDetection(self):
        """ Detect serial devices by using the built-in comports command in pyserial.
        """

        # make dictionary with (description, comport)
        newDict = {}
        ports = sorted(comports())
        for port, desc, hwid in ports:
            newDict[desc] = port

        if not newDict:
            self.noUSB()

        # call disconnect function if the current device disappears
        if self.connected and self.comVar.get() not in newDict:
            self.noUSB()
            self.disconnect()
            
        # update menu when not currently connected
        if newDict != self.comDict or not newDict:
            self.noUSB()

            # reset menu
            self.comOption.delete(0)
#            menu = self.comOption["menu"]
            
            # keep current selection
            oldIndex = self.comVar.get()
            
            # if devices were found
            if newDict:
                
                # populate menu
                for key in sorted(newDict.keys()):    
#                    menu.add_command(label=key, command=Tkinter._setit(self.comVar, key))
                    self.portsMenu.add_radiobutton(label=key, command=Tkinter._setit(self.comVar, key))
                
                # choose first port if no port was previously selected
                if oldIndex not in newDict:
                    self.comVar.set(ports[0][1])
                
                # enable menu and connect/programming buttons
                self.enableUI()
                self.handler.debugMsg("USB device detected, press any menu button to start")
                
            else:
                # no devices found. disable menu and all buttons.
                self.portsMenu.add_radiobutton(label=self.DEFAULT_STRING, command=Tkinter._setit(self.comVar, self.DEFAULT_STRING))
                self.comVar.set(self.DEFAULT_STRING)
                self.disableUI()
                self.noUSB()
                
            # update
            self.comDict = newDict
            
        # run detection again after 1000 ms
        self.comOption.after(1000, self.deviceDetection)


    def connect(self):
        """ Event handler for changing connection status.
        """        
        self.handler.debugMsg("Connecting to Bacon...")
        
        self.handler.busy()
        self.connected = True
        
        self.disableUI()
        self.connectMenu.entryconfig(0,label="Disconnect", command=self.disconnect, state=NORMAL)
        self.handler.connect(self.comDict[self.comVar.get()])

    def disconnect(self):
        """ Event handler for changing connection status.
        """        
        self.handler.busy()
        self.connected = False
        
        self.enableUI()
        self.connectMenu.entryconfig(0,label="Connect", state=NORMAL, command=self.connect)
        self.handler.disconnect()
        self.handler.notbusy()

    def disableUI(self):
        self.connectMenu.entryconfig(0,state=DISABLED)
        self.progMenu.entryconfig(0,state=DISABLED)
        self.progMenu.entryconfig(1,state=DISABLED)
        self.progMenu.entryconfig(2,state=DISABLED)
        self.dbMenu.entryconfig(0,state=DISABLED)        

    def enableUI(self):
        self.connectMenu.entryconfig(0,state=NORMAL)
        self.progMenu.entryconfig(0,state=NORMAL)
        self.progMenu.entryconfig(1,state=NORMAL)
        self.progMenu.entryconfig(2,state=NORMAL)        
        self.dbMenu.entryconfig(0,state=NORMAL)

#------ programming functions -------------------------------------------------------------------------
    
    def programLeaf(self):
        self.handler.busy()
        self.disableUI()

        self.progressVar.set(0)
        self.programming = True
        self.programSize = self.LEAF_SIZE
        self.handler.program(self.leaf_file, self.comDict[self.comVar.get()], self.programDone)
        self.programProgress()

    def programRouter(self):
        self.handler.busy()
        self.disableUI()

        self.progressVar.set(0)
        self.programming = True
        self.programSize = self.ROUTER_SIZE
        self.handler.program(self.router_file, self.comDict[self.comVar.get()], self.programDone)
        self.programProgress()

    def programBasestation(self):
        self.handler.busy()
        self.disableUI()

        self.progressVar.set(0)
        self.programming = True
        self.programSize = self.BASESTATION_SIZE
        self.handler.program(self.basestation_file, self.comDict[self.comVar.get()], self.programDone)
        self.programProgress()

    def programProgress(self):
        progress = self.handler.programProgress() * 100.0 / self.programSize
        
        if progress > self.progressVar.get():
            self.progressVar.set(progress)

        if self.programming:
            return
#            self.progressBar.after(200, self.programProgress)
        else:
            # reset progress bar
            self.progressVar.set(0)                        
            self.enableUI()
            self.handler.notbusy()

            if self.programmingStatus:
                tkMessageBox.showinfo("Labeler", "Programming done", parent=self.parent)
            else:
                tkMessageBox.showerror("Error", "Programming failed", parent=self.parent)

    def programDone(self, status):
        self.programming = False
        self.programmingStatus = status

#------ database related functions ---------------------------------------------------

    def exportCSV(self):
        try:
            self.handler.exportCSV()
        except:
            tkMessageBox.showerror("Error", "CSV export failed", parent=self.parent)
        else:
            tkMessageBox.showinfo("Labeler", "CSV export done", parent=self.parent)

#------ help related functions ----------------------------------------------------

    def show_help(self):
        webbrowser.open("file://"+os.path.realpath("LabelerGuide.pdf"))

    def show_luyf(self):
        webbrowser.open("http://lifeunderyourfeet.org")

    def show_about(self):
        return
    


if __name__ == '__main__':
    root = Tk()
    
    handler = Handler()    
    menuBar = MenuBar(root, handler)
    
    root.mainloop()
