import tkMessageBox
import Tkinter
import ttk
import tkSimpleDialog
from tkFileDialog import askopenfilename, asksaveasfilename

import simplejson
import traceback

import lib.uiHelperFunctions as UIUtils
from lib.ReadFiletype_Scripts.read_w3e import ReadW3E
from lib.ReadFiletype_Scripts.read_object import ObjectReader, TranslationHandle

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
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.openFrame = Tkinter.Frame(self)
        self.openButton = Tkinter.Button(self.openFrame, text="Open!", command=self.openFile).pack(side=Tkinter.LEFT)
        
        self.filenameText = Tkinter.StringVar()
        self.filename = Tkinter.Label(self.openFrame, textvariable=self.filenameText).pack(side=Tkinter.LEFT)
        self.openFrame.pack()
        #settings
        self.settingsFrame = Tkinter.Frame(self)
        tmp="disabled"
        if useTopDown:
            tmp = "normal"
        
        self.debugInfo = Tkinter.Button(self.settingsFrame, text="TopDown Settings",command=self.newDebugInfo, state = tmp).pack(side=Tkinter.LEFT)
        
        self.topDownOption = Tkinter.IntVar()
        self.topDown = Tkinter.Checkbutton(self.settingsFrame, text="Generate TopDown (beta)", anchor="w", variable=self.topDownOption,state=tmp).pack(side=Tkinter.LEFT)
        self.rawOption = Tkinter.IntVar()
        self.rawButton = Tkinter.Checkbutton(self.settingsFrame,text="Visualise raw info (slow)", anchor="w", variable=self.rawOption).pack(side=Tkinter.LEFT)
        
        
        
        self.settingsFrame.pack()
        #end settings
        #start tabs
        self.tabHandle = ttk.Notebook(self)
        
        self.topDownTab = self.TopDownTab(self)
        self.headerTab = self.HeaderInfoTab()
        self.rawTab = UIUtils.GenericTreeTab()
        
        self.tabHandle.add(self.headerTab, text="HeaderInfo")
        self.tabHandle.add(self.topDownTab, text="TopDownViewer", state=tmp)
        self.tabHandle.add(self.rawTab, text="Raw Info")
        
        self.tabHandle.pack(fill=Tkinter.BOTH, expand=1)
        #end tabs
        self.pack(fill=Tkinter.BOTH, expand=1)
        
        self.WC3_Topdown_ImageGen = TopDownViewer()
        
        self.debugSettings = {"validTile" : False, "invalidTile" : False, "height" : False,
                              "ramp" : False, "water" : False, "blight" : False}
    
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
            
            if self.rawOption.get() == 1:
                self.rawTab.setInfo(mapInfo.mapInfo)
                
            if self.topDownOption.get() == 1:
                print("Time to generate a topdown")
                #time to run TopDownViewer
                topdownImage = self.WC3_Topdown_ImageGen.createImage(mapInfo, self.debugSettings)
                print("Generated.")
                self.topDownTab.setImage(topdownImage)
                
            tmpInfo = mapInfo.mapInfo
            del tmpInfo["info"]
            self.headerTab.setText(simplejson.dumps(tmpInfo, sort_keys=True, indent=4 * ' '))
        else:
            self.headerInfoText.set("")
            
    class TopDownTab(Tkinter.Frame):        
        def __init__(self, master=None):
            Tkinter.Frame.__init__(self, master)
            self.img = Tkinter.PhotoImage(data="R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7") 
            
            self.master = master
            
            self.grid_rowconfigure(0,weight=1)
            self.grid_columnconfigure(0,weight=1)
            
            
            self.xscrollbar = UIUtils.AutoScrollbar(self, orient=Tkinter.HORIZONTAL)
            self.xscrollbar.grid(row=1, sticky=Tkinter.E+Tkinter.W)
            
            self.yscrollbar = UIUtils.AutoScrollbar(self)
            self.yscrollbar.grid(row=0,column=1, sticky=Tkinter.N+Tkinter.S)
            
            self.canvas = Tkinter.Canvas(self, bd=0, xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
            
            self.xscrollbar.config(command=self.canvas.xview)
            self.yscrollbar.config(command=self.canvas.yview)
            
            self.canvas.grid(row=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
            
            self.id = self.canvas.create_image(0,0,image=self.img, anchor=Tkinter.NW)
            
            self.saveButton = Tkinter.Button(self, text="Save!", command=self.save)
            self.saveButton.grid(row=2,column=0)
            
            self.zoomFrame = Tkinter.Frame(self)
            self.zoomIn = Tkinter.Button(self.zoomFrame, text="Zoom In!",command=self.zoomIn).pack(side=Tkinter.LEFT)
            self.zoomOut = Tkinter.Button(self.zoomFrame, text="Zoom Out!",command=self.zoomOut).pack(side=Tkinter.LEFT)
            self.zoomWarning = Tkinter.Label(self.zoomFrame, text="Warning, spamming the zoom buttons will eat your RAM alive and may crash!").pack(side=Tkinter.LEFT)
            
            self.zoomFactor = Tkinter.Label(self.zoomFrame, text="Current zoom factor: 1.0x")
            self.zoomFactor.pack(side=Tkinter.LEFT)
            
            self.zoomFrame.grid(row=3,column=0,columnspan=1, sticky=Tkinter.E+Tkinter.W)
            self.pack(fill=Tkinter.BOTH, expand=1)
            
            self.debugInfoOpen = False
            self.debugWindow = None
            
            
            
        def setImage(self, img):
            self.originalImg = img
            self.ratio = 1
            self.img = ImageTk.PhotoImage(img)
            self.canvas.config(scrollregion=(0,0,img.size[0], img.size[1]))
            self.canvas.itemconfig(self.id, image=self.img)
            
        def zoomIn(self):
            if self.ratio + 0.1 < 1.6: # maximum zoom limit: 1.5x
                if self.id: self.canvas.delete(self.id)
                
                self.ratio = self.ratio + 0.1
                self.zoomFactor.config(text = "Current zoom factor: {0}x".format(float(self.ratio)))
                
                img = self.originalImg.resize((int(self.originalImg.size[0]*self.ratio), int(self.originalImg.size[1]*self.ratio)))
                self.img = ImageTk.PhotoImage(img)
                
                self.canvas.create_image(0, 0, image=self.img, anchor=Tkinter.NW)
                
                self.canvas.config(scrollregion=(0,0,img.size[0], img.size[1]))
                #self.canvas.itemconfig(self.id, image=self.img)
            
        def zoomOut(self):
            if self.ratio-0.1 > 0.1: # minimum zoom limit: 0.1x
                if self.id: self.canvas.delete(self.id)
                
                self.ratio = self.ratio - 0.1
                self.zoomFactor.config(text = "Current zoom factor: {0}x".format(float(self.ratio)))
                
                img = self.originalImg.resize((int(self.originalImg.size[0]*self.ratio), int(self.originalImg.size[1]*self.ratio)))
                self.img = ImageTk.PhotoImage(img)
                
                self.canvas.create_image(0, 0, image=self.img, anchor=Tkinter.NW)
                
                self.canvas.config(scrollregion=(0,0,img.size[0], img.size[1]))
                #self.canvas.itemconfig(self.id, image=self.img)
        def save(self):
            saveDialog = self.SaveDialog(self)
            if saveDialog.result:
                options = {
                    "initialdir" : "output/",
                    "initialfile" : "topdown.png",
                    "defaultextension" : ".png",
                    "filetypes"    : [("PNG", ".png"),("JPEG", ".jpg")],
                    "title" : "This is a title"
                }
                location = asksaveasfilename(**options)
                if location:
                    extention = location.split(".")
                    extention = extention[len(extention)-1]
                    if saveDialog.result == 1:
                        self.originalImg.save(location, extention.upper())
        class SaveDialog(tkSimpleDialog.Dialog):
            def __init__(self, master=None):
                self.master = master
                self.option = Tkinter.IntVar()
                
                tkSimpleDialog.Dialog.__init__(self, master, "Save Options")
            def body(self, master):
                
                self.origRadio = Tkinter.Radiobutton(master, text="Original Size:", variable=self.option, value=1)
                self.origRadio.grid(row=0)
                
                self.zoomRadio = Tkinter.Radiobutton(master, text="Zoomed Size:", variable=self.option, value=2, state="disabled")
                self.zoomRadio.grid(row=1)
                
                return self.origRadio
            def apply(self):
                self.result = self.option.get()
    def newDebugInfo(self):
        self.debugWindow = self.DApplication(self)
    
    class DApplication(tkSimpleDialog.Dialog):
        def __init__(self, master=None):
            self.debugSettings = dict(master.debugSettings)
            
            self.water = Tkinter.BooleanVar()
            self.blight = Tkinter.BooleanVar()
            self.validTile = Tkinter.BooleanVar()
            self.invalidTile = Tkinter.BooleanVar()
            self.ramp = Tkinter.BooleanVar()
            self.height = Tkinter.BooleanVar()
            
            self.master = master
            
            tkSimpleDialog.Dialog.__init__(self, master, "Debug Settings")
            
        def body(self, master):
            self.waterCheck = Tkinter.Checkbutton(self, text="Highlight Water (Blue)", anchor="w",
                                                  variable=self.water, onvalue = True, offvalue = False)
            self.blightCheck = Tkinter.Checkbutton(self, text="Highlight Undead Ground (Violet)", anchor="w", 
                                                   variable=self.blight, onvalue = True, offvalue = False)
            self.rampCheck = Tkinter.Checkbutton(self, text="Highlight Ramp Tiles (Red)", anchor="w", 
                                                 variable=self.ramp, onvalue = True, offvalue = False)
            self.heightCheck = Tkinter.Checkbutton(self, text="Show Tile Height (Not added yet)", anchor="w",
                                                   variable=self.height, onvalue = True, offvalue = False, state = "disabled")
            self.validTileCheck = Tkinter.Checkbutton(self, text="Show Tileinfo for known tiles", anchor="w", 
                                                      variable=self.validTile, onvalue = True, offvalue = False)
            self.invalidTileCheck = Tkinter.Checkbutton(self, text="Show Tileinfo for unknown tiles", anchor="w", 
                                                        variable=self.invalidTile, onvalue = True, offvalue = False)
            
            
            
            if self.debugSettings["water"] == True: self.waterCheck.select()
            if self.debugSettings["blight"] == True: self.blightCheck.select()
            if self.debugSettings["ramp"] == True: self.rampCheck.select()
            if self.debugSettings["height"] == True: self.heightCheck.select()
            if self.debugSettings["validTile"] == True: self.validTileCheck.select()
            if self.debugSettings["invalidTile"] == True: self.invalidTileCheck.select()
            
            
            self.waterCheck.pack(fill = "both")
            self.blightCheck.pack(fill = "both")
            self.rampCheck.pack(fill = "both")
            self.heightCheck.pack(fill = "both")
            self.validTileCheck.pack(fill = "both")
            self.invalidTileCheck.pack(fill = "both")
            
            
        def apply(self):
            self.master.debugSettings["water"] = self.water.get()
            self.master.debugSettings["blight"] = self.blight.get()
            self.master.debugSettings["validTile"] = self.validTile.get()
            self.master.debugSettings["invalidTile"] = self.invalidTile.get()
            self.master.debugSettings["ramp"] = self.ramp.get()
            self.master.debugSettings["height"] = self.height.get()
            
            
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