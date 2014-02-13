import tkMessageBox
import Tkinter
import ttk
from tkFileDialog import askopenfilename, asksaveasfilename

import simplejson
import traceback

import lib.uiHelperFunctions as UIUtils
from read_w3e import ReadW3E
from read_object import ObjectReader, TranslationHandle

from pprint import pprint as pprint

try:
    from PIL import Image, ImageTk
    #print("yes PIL, maybe topdown")
    from topdownViewer import TopDownViewer
    useTopDown = True
    #print("yes PIL, yes topdown")
except:
    useTopDown = False
    print("no PIL, no topdown")
    print(traceback.format_exc())

class TerrainTab(Tkinter.Frame):
    def    __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.settingFrame = Tkinter.Frame(self)
        self.openButton = Tkinter.Button(self.settingFrame, text="Open!", command=self.openFile).pack(side=Tkinter.LEFT)
        
        self.filenameText = Tkinter.StringVar()
        self.filename = Tkinter.Label(self.settingFrame, textvariable=self.filenameText).pack(side=Tkinter.LEFT)
        self.settingFrame.pack()
        #settings
        tmp="disabled"
        if useTopDown:
            tmp = "normal"
        self.topDownOption = Tkinter.IntVar()
        self.topDown = Tkinter.Checkbutton(self, text="Generate TopDown (beta)", anchor="w", variable=self.topDownOption,state=tmp, command=self.onTopDown).pack()
        #end settings
        #start tabs
        self.tabHandle = ttk.Notebook(self)
        
        self.topDownTab = self.TopDownTab()
        self.headerTab = self.HeaderInfoTab()
        
        self.tabHandle.add(self.headerTab, text="HeaderInfo")
        self.tabHandle.add(self.topDownTab, text="TopDownViewer", state=tmp)
        
        self.tabHandle.pack(fill=Tkinter.BOTH, expand=1)
        #end tabs
        self.pack(fill=Tkinter.BOTH, expand=1)
        
    def onTopDown(self):
        pass
    
    def openFile(self):
        
        options = {
            "initialdir" : "input/",
            "initialfile" : "war3map.w3e",
            "defaultextension" : ".w3e",
            "filetypes"    : [("Warcraft III Terrain", ".w3e")],
            "title" : "This is a title"
        }
        filename = askopenfilename(**options)
        self.filenameText.set(filename)
        if filename:
            mapInfo = ReadW3E(filename)
            
            if self.topDownOption.get() == 1:
                print("Time to generate a topdown")
                #time to run TopDownViewer
                topdownInstance = TopDownViewer(mapInfo)
                print("Generated.")
                self.topDownTab.setImage(topdownInstance.img)
                
            tmpInfo = mapInfo.mapInfo
            del tmpInfo["info"]
            self.headerTab.setText(simplejson.dumps(tmpInfo, sort_keys=True, indent=4 * ' '))
        else:
            self.headerInfoText.set("")
            
    class TopDownTab(Tkinter.Frame):        
        def __init__(self, master=None):
            Tkinter.Frame.__init__(self, master)
            self.img = Tkinter.PhotoImage(data="R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7") 
            
            self.grid_rowconfigure(0,weight=1)
            self.grid_columnconfigure(0,weight=1)
            
            
            self.xscrollbar = Tkinter.Scrollbar(self, orient=Tkinter.HORIZONTAL)
            self.xscrollbar.grid(row=1, sticky=Tkinter.E+Tkinter.W)
            
            self.yscrollbar = Tkinter.Scrollbar(self)
            self.yscrollbar.grid(row=0,column=1, sticky=Tkinter.N+Tkinter.S)
            
            self.canvas = Tkinter.Canvas(self, bd=0, xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
            
            self.xscrollbar.config(command=self.canvas.xview)
            self.yscrollbar.config(command=self.canvas.yview)
            
            self.canvas.grid(row=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
            
            self.id = self.canvas.create_image(0,0,image=self.img, anchor=Tkinter.NW)
            
            self.pack(fill=Tkinter.BOTH, expand=1)
            
        def setImage(self, img):
            self.img = ImageTk.PhotoImage(img)
            self.canvas.config(scrollregion=(0,0,img.size[0], img.size[1]))
            self.canvas.itemconfig(self.id, image=self.img)
            
    class HeaderInfoTab(Tkinter.Frame):
        def __init__(self, master=None):
            Tkinter.Frame.__init__(self, master)
            
            self.mainText = Tkinter.StringVar()
            self.mainLabel = Tkinter.Label(self, textvariable=self.mainText, anchor=Tkinter.W, justify=Tkinter.LEFT).grid(row=0)
            self.pack()
            
        def setText(self, text):
            self.mainText.set(text)
    
class DataTab(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        #Row 0
        self.settingFrame = Tkinter.Frame(self)
        self.openButton = Tkinter.Button(self.settingFrame, text="Open!", command=self.openFile).pack(side=Tkinter.LEFT)
        
        self.filenameText = Tkinter.StringVar()
        self.filename = Tkinter.Label(self.settingFrame, textvariable=self.filenameText).pack(side=Tkinter.LEFT)
        self.settingFrame.pack()
        #Row 1        
        self.translateVar =  Tkinter.IntVar()
        self.translate = Tkinter.Checkbutton(self, text="Translation", anchor="w", variable=self.translateVar,state="disabled").pack()
        #Row 2
        self.tabHandle = ttk.Notebook(self)
        
        self.originalTab = UIUtils.GenericTreeTab(self.tabHandle)
        self.customTab = UIUtils.GenericTreeTab(self.tabHandle)
        self.transTab = UIUtils.GenericTreeTab(self.tabHandle)
        
        self.tabHandle.add(self.originalTab, text="OriginalInfo")
        self.tabHandle.add(self.customTab, text="CustomInfo")
        self.tabHandle.add(self.transTab, text="Translation")
        self.tabHandle.pack(fill=Tkinter.BOTH, expand=1)
        
        self.pack(fill=Tkinter.BOTH, expand=1)
        
    def openFile(self):
        options = {
            "initialdir" : "input/",
            "defaultextension" : ".w3t",
            "filetypes" : [
                ("Warcraft III Items",          ".w3t"),
                ("Warcraft III Units",          ".w3u"),           
                ("Warcraft III Destructables",  ".w3b"),
                ("Warcraft III Doodats",        ".w3d"),
                ("Warcraft III Abilities",      ".w3a"),
                ("Warcraft III Buffs",          ".w3h"),
                ("Warcraft III Upgrades",       ".w3q")
            ],
            "title" : "This is also a title!"
        }
        filename = askopenfilename(**options)
        self.filenameText.set(filename)
        if filename:
            #this is where we do stuff
            fileInfo = ObjectReader(filename)
            self.originalTab.setInfo(fileInfo.originalInfo)
            self.customTab.setInfo(fileInfo.customInfo)
            translated = TranslationHandle(fileInfo)
            self.transTab.setInfo(translated.info)
class InfoTab(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.infoLabel = Tkinter.Label(self, text="WC3-to-VMF is a toolkit made by SinZ and Yoshi2 \r\nThis project is available on Github: http://github.com/SinZ163/w3x-to-vmf/").pack()
        self.pack(fill=Tkinter.BOTH, expand=1)
        
root = Tkinter.Tk()

root.title("Warcraft III to Dota 2 conversion toolkit.")
tabHandle = ttk.Notebook(root)

terrainTab = TerrainTab(tabHandle)
dataTab = DataTab(tabHandle)
infoTab = InfoTab(tabHandle)

tabHandle.add(terrainTab, text="Terrain")
tabHandle.add(dataTab, text="Data")
tabHandle.add(infoTab, text="Info")
tabHandle.pack(fill=Tkinter.BOTH, expand=1)
root.mainloop()