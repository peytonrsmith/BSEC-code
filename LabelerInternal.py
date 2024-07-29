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


from Tkinter import *

#from tools.labeler.MenuFrame  import MenuFrame
from tools.labeler.MenuBar  import MenuBar
from tools.labeler.BaconFrame import BaconFrame
from tools.labeler.ToastFrame import ToastFrame
from tools.labeler.Handler    import Handler
from tools.labeler.GraphFrame import GraphFrame
from tools.labeler.AdcFrame   import AdcFrame
from tools.labeler.TextFrame  import TextFrame
from tools.SimPy.SimPlot      import SimPlot 


def selectall(event):
    event.widget.select_range(0, END)

def quit(key=None):
    handler.menuFrame.disconnect()
    root.quit()

def xscrollSet(lo, hi):
    if float(lo) <= 0.0 and float(hi) >= 1.0:
        # grid_remove is currently missing from Tkinter!
        xscrollbar.tk.call("grid", "remove", xscrollbar)
        xscrollOn = False
    else:
        xscrollbar.grid()
        xscrollOn = True
    xscrollbar.set(lo, hi)        
    
def yscrollSet(lo, hi):
    if float(lo) <= 0.0 and float(hi) >= 1.0:
        # grid_remove is currently missing from Tkinter!
        yscrollbar.tk.call("grid", "remove", yscrollbar)
        yscrollOn = False
    else:
        yscrollbar.grid()
        yscrollOn = True
    yscrollbar.set(lo, hi)        

def updateCanvas(event):        
    canvas.configure(scrollregion=canvas.bbox("all"))
    
def donothing():
    return
#     filewin = Toplevel(root)
#     button = Button(filewin, text="Do nothing button")
#     button.pack()
                
simplot = SimPlot()
root = simplot.root

handler = Handler(root)    

# MenuFrame      32  32
# BaconFrame    184 216 184
# ToastFrame    284 500 468
# AdcFrame       64 564

WIDTH  = 2560
HEIGHT =  1600          # height of the whole app
MAIN   =  488          # width of the Connect panel

 
root.geometry(str(WIDTH) + "x" + str(HEIGHT))
root.title("Labeler")
root.bind_class("Entry","<Control-a>", selectall)
root.bind("<Alt-F4>", quit)
root.bind('<Control-c>', quit)
root.protocol("WM_DELETE_WINDOW", quit)

#global menu
menu = Menu(root)
menuBar = MenuBar(menu, handler)
root.config(menu=menu)

#
# scroll bars
#
xscrollOn = False
yscrollOn = False

xscrollbar = Scrollbar(root, orient=HORIZONTAL)
xscrollbar.grid(column=0, row=1, sticky=E+W)
yscrollbar = Scrollbar(root)
yscrollbar.grid(column=1, row=0, sticky=N+S)

canvas = Canvas(root, yscrollcommand=yscrollSet, xscrollcommand=xscrollSet)
canvas.grid(row=0, column=0, sticky=N+S+E+W)

yscrollbar.config(command=canvas.yview)
xscrollbar.config(command=canvas.xview)
#
# make the canvas expandable
#
root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

rootFrame = Frame(canvas)
rootFrame.rowconfigure(1, weight=1)
rootFrame.columnconfigure(1, weight=1)
canvas.create_window(0, 0, anchor=NW, window=rootFrame)

rootFrame.bind("<Configure>", updateCanvas)

#
# Frames on top of canvas
#
# menuFrame = MenuFrame(rootFrame, handler, width=WIDTH-4, height=32, bd=1, relief=SUNKEN)
# menuFrame.grid_propagate(False)
# menuFrame.grid(column=1, row=1, columnspan=2)
# handler.addMenuFrame(menuFrame)

handler.addMenuFrame(menuBar)

baconFrame = BaconFrame(rootFrame, handler, width=MAIN, height=284, bd=1, relief=SUNKEN)
baconFrame.grid_propagate(False)
baconFrame.grid(column=1, row=2)
handler.addBaconFrame(baconFrame)

toastFrame = ToastFrame(rootFrame, handler, width=MAIN, height=384, bd=1, relief=SUNKEN)
toastFrame.grid_propagate(False)
toastFrame.grid(column=1, row=3)
handler.addToastFrame(toastFrame)

graphFrame = GraphFrame(rootFrame, handler, simplot, width=WIDTH-MAIN-4, height=568, bd=1, relief=SUNKEN)
graphFrame.grid_propagate(False)
graphFrame.grid(column=2, row=2, rowspan=2)
handler.addGraphFrame(graphFrame)

textFrame = TextFrame(rootFrame, handler, width=MAIN, height=164, bd=1, relief=SUNKEN, bg="#EEEEEE")
textFrame.grid_propagate(False)
textFrame.grid(column=1,row=4)

adcFrame = AdcFrame(rootFrame, handler, width=WIDTH-MAIN-4,  height=80, bd=1, relief=SUNKEN)
adcFrame.grid_propagate(False)
adcFrame.grid(column=2, row=4)
handler.addAdcFrame(adcFrame)



try:
    root.mainloop()
except KeyboardInterrupt:
    pass
