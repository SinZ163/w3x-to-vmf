import tkMessageBox
import Tkinter
import ttk
import tkSimpleDialog
from tkFileDialog import askopenfilename, asksaveasfilename, askopenfile

import copy
import io
import simplejson
import traceback

from WC3MapObject import WC3Map

import lib.uiHelperFunctions as UIUtils
from lib.ReadFiletype.read_w3e import read_W3E
from lib.ReadFiletype.read_wts import read_WTS
from lib.ReadFiletype.read_object import read_object, translate_info

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

class MainTab(Tkinter.Frame):
    def __init__(self, master=None):
        self.name = "MainTab"
    
        Tkinter.Frame.__init__(self, master)
        self.tabHandle = ttk.Notebook(self)
                
        self.openFrame = Tkinter.Frame(self)
        
        self.openButton = Tkinter.Button(self.openFrame, text="Open Warcraft III map", command=self.openFile)
        self.openButton.pack(side=Tkinter.LEFT)
        
        self.filenameText = Tkinter.StringVar()
        self.filename = Tkinter.Label(self.openFrame, textvariable=self.filenameText)
        self.filename.pack(side=Tkinter.LEFT)
        
        self.openFrame.pack(side=Tkinter.TOP, anchor="n")
        
        self.filelist = Tkinter.Listbox(self.tabHandle, selectmode=Tkinter.SINGLE)
        self.filelist.bind("<Double-Button-1>", self.onSelect)
        self.filelist.pack(fill=Tkinter.BOTH, expand=1)

        self.terrainTab = TerrainTab(self.tabHandle, w3x=True)
        
        self.unitTab = UIUtils.GenericTreeTab(self.tabHandle)
        self.itemTab = UIUtils.GenericTreeTab(self.tabHandle)
        self.abilTab = UIUtils.GenericTreeTab(self.tabHandle)
        
        self.tabHandle.add(self.filelist, text="W3X Files")
        self.tabHandle.add(self.terrainTab, text="Terrain", state="disabled")
        self.tabHandle.add(self.unitTab, text="Units", state="disabled")
        self.tabHandle.add(self.itemTab, text="Items", state="disabled")
        self.tabHandle.add(self.abilTab, text="Abilities", state="disabled")
        self.tabHandle.pack(fill=Tkinter.BOTH, expand=1)
                
        self.pack(fill=Tkinter.BOTH, expand=1)
        
    def openFile(self):
        self.filelist.delete(0, Tkinter.END)
        options = {
            "initialdir" : "input/",
            "initialfile" : "",
            "defaultextension" : ".w3x",
            "filetypes"    : [("Warcraft III Frozen Throne map", ".w3x")],
            "title" : "Open a Frozen Throne map"
        }
        file = askopenfile(mode="rb", **options)
        self.filenameText.set(file.name)
        
        self.map = WC3Map(file, forceV1=True)
        with open("lib/wc3Files_compact.txt", "r") as f:
            self.map.createListfile(template=f)
        
        triggers = None
        try:
            triggers = read_WTS(io.BytesIO(self.map.mpq.read_file("war3map.wts")))
        except:
            triggers = None
        for file in self.map.listfile:
            file_extention = file.rpartition(".")[2]
            try:
                if file == "war3map.w3e":
                    #We have terrain
                    self.tabHandle.tab(1, state="normal")
                    self.terrainTab.openFile(io.BytesIO(self.map.mpq.read_file("war3map.w3e")))
                if file_extention in ("w3t", "w3u", "w3a"):
                    #We have items, units or abilities
                    fileInfo = read_object(io.BytesIO(self.map.mpq.read_file(file)), file_extention, triggerDB=triggers)#ObjectReader(filename)
                    if file_extention == "w3u":
                        self.tabHandle.tab(2, state="normal")
                        print("SETTING INFO")
                        self.unitTab.setInfo(translate_info(fileInfo["customInfo"], file_extention), file_extention, self.filenameText.get())
                    if file_extention == "w3t":
                        self.tabHandle.tab(3, state="normal")
                        self.itemTab.setInfo(translate_info(fileInfo["customInfo"], file_extention), file_extention, self.filenameText.get())
                    if file_extention == "w3a":
                        self.tabHandle.tab(4, state="normal")
                        self.abilTab.setInfo(translate_info(fileInfo["customInfo"], file_extention), file_extention, self.filenameText.get())
            except:
                print(traceback.format_exc())
            self.filelist.insert(Tkinter.END, file)
        
    def onSelect(self, event):
        index = int(self.filelist.curselection()[0])
        value = self.filelist.get(index)
        print 'You selected item %d: "%s"' % (index, value)
        
class TerrainTab(Tkinter.Frame):
    def __init__(self, master=None, w3x=False):
        self.w3x = w3x
    
        Tkinter.Frame.__init__(self, master)
        self.settingsFrame = Tkinter.Frame(self)
        tmp="disabled"
        if useTopDown:
            tmp = "normal"
            
        if w3x == False:
            self.openFrame = Tkinter.Frame(self)
            self.openButton = Tkinter.Button(self.openFrame, text="Open!", command=self.openFile).pack(side=Tkinter.LEFT)
            
            self.filenameText = Tkinter.StringVar()
            self.filename = Tkinter.Label(self.openFrame, textvariable=self.filenameText).pack(side=Tkinter.LEFT)
            self.openFrame.pack()
            
            self.topDownOption = Tkinter.IntVar()
            self.topDown = Tkinter.Checkbutton(self.settingsFrame, text="Generate TopDown (beta)", anchor="w", variable=self.topDownOption,state=tmp).pack(side=Tkinter.LEFT)
            self.rawOption = Tkinter.IntVar()
            self.rawButton = Tkinter.Checkbutton(self.settingsFrame,text="Visualise raw info (slow)", anchor="w", variable=self.rawOption).pack(side=Tkinter.LEFT)
        
        self.debugInfo = Tkinter.Button(self.settingsFrame, text="TopDown Settings",command=self.newDebugInfo, state = tmp).pack(side=Tkinter.LEFT)
        
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
    
    def openFile(self, w3xInfo = None):
        if self.w3x:
            mapInfo = read_W3E(w3xInfo)
            self.mapInfo = mapInfo
            
            print("Time to generate a topdown")
            #time to run TopDownViewer
            topdownImage = self.WC3_Topdown_ImageGen.createImage(mapInfo, self.debugSettings)
            print("Generated.")
            self.topDownTab.setImage(topdownImage)
                
            tmpInfo = copy.copy(mapInfo)
            del tmpInfo["info"]
            self.headerTab.setText(simplejson.dumps(tmpInfo, sort_keys=True, indent=4 * ' '))
        else:
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
                with open(filename, "rb") as mapfile:
                    mapInfo = read_W3E(mapfile)
                    self.mapInfo = mapInfo
                
                if self.rawOption.get() == 1:
                    self.rawTab.setInfo(mapInfo)
                    
                if self.topDownOption.get() == 1:
                    print("Time to generate a topdown")
                    #time to run TopDownViewer
                    topdownImage = self.WC3_Topdown_ImageGen.createImage(mapInfo, self.debugSettings)
                    print("Generated.")
                    self.topDownTab.setImage(topdownImage)
                    
                tmpInfo = mapInfo
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
        self.debugWindow = self.DApplication(self, self.mapInfo)
    
    class DApplication(tkSimpleDialog.Dialog):
        def __init__(self, master=None, mapInfo=False):
            self.mapInfo = mapInfo
            
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
            
            if self.mapInfo:
                topdownImage = self.master.WC3_Topdown_ImageGen.createImage(self.mapInfo, self.master.debugSettings)
                self.master.topDownTab.setImage(topdownImage)
            
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
        self.name = "DataTab"
    
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
        
        #self.jsonOutput = Tkinter.Button(self, text="Save as JSON", command=UIUtils.jsonOutput).pack(side=Tkinter.LEFT)
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
            file_extension = filename.rpartition(".")[2]
            
            #this is where we do stuff
            with open(filename, "rb") as f:
                fileInfo = read_object(f, file_extension)#ObjectReader(filename)
                
            self.fileInfo = fileInfo #for json output
            
            self.originalTab.setInfo(fileInfo["originalInfo"], "original", filename)
            self.customTab.setInfo(fileInfo["customInfo"], "custom", filename)
            
            translated = translate_info(fileInfo["customInfo"], file_extension)
            self.transTab.setInfo(translated, "translated", filename)
class InfoTab(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        self.infoLabel = Tkinter.Label(self, text="WC3-to-VMF is a toolkit made by SinZ and Yoshi2 \r\nThis project is available on Github: http://github.com/SinZ163/w3x-to-vmf/").pack()
        self.pack(fill=Tkinter.BOTH, expand=1)
        
root = Tkinter.Tk()

root.title("Warcraft III to Dota 2 conversion toolkit.")
tabHandle = ttk.Notebook(root)

mainTab = MainTab(tabHandle)
terrainTab = TerrainTab(tabHandle)
dataTab = DataTab(tabHandle)
infoTab = InfoTab(tabHandle)

tabHandle.add(mainTab, text="WC3 Map")
tabHandle.add(terrainTab, text="Terrain")
tabHandle.add(dataTab, text="Data")
tabHandle.add(infoTab, text="Info")
tabHandle.pack(fill=Tkinter.BOTH, expand=1)
root.mainloop()