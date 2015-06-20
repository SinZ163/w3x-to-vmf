import simplejson
import Tkinter
import ttk
from tkFileDialog import askopenfilename, asksaveasfilename, askopenfile
class GenericTreeTab(Tkinter.Frame):
    def __init__(self, master=None):
        self.name = "GenericTreeTab"
        
        self.info = None
        Tkinter.Frame.__init__(self, master)
        
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
            
        self.xscrollbar = AutoScrollbar(self,orient=Tkinter.HORIZONTAL)
        self.xscrollbar.grid(row=2,column=0, sticky=Tkinter.E+Tkinter.W)
        
        self.yscrollbar = AutoScrollbar(self)
        self.yscrollbar.grid(row=0,column=1, sticky=Tkinter.N+Tkinter.S)
       
        self.tree = ttk.Treeview(self, columns=('Values'),xscrollcommand=self.xscrollbar.set,yscrollcommand=self.yscrollbar.set)
        self.tree.column('Values', width=100, anchor=Tkinter.W)
        self.tree.heading('Values', text='Values')
        
        self.tree.grid(row=0,column=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
        
        self.xscrollbar.config(command=self.tree.xview)
        self.yscrollbar.config(command=self.tree.yview)
        
        self.jsonOutputButton = Tkinter.Button(self, text="Save as JSON", command=self.save).grid(row=1,column=0, sticky=Tkinter.S+Tkinter.W)
        
        self.pack(fill=Tkinter.BOTH, expand=1)
        
    def serializeInfo(self, info, parent=""):
        if type(info) is dict:
            for key in sorted(info.iterkeys()):
                if type(info[key]) is dict or type(info[key]) is list:
                    newParent = self.tree.insert(parent,"end", text=key, open=True)
                    self.serializeInfo(info[key], newParent)
                else:
                    self.tree.insert(parent,"end", text=key, values=[unicode(str(info[key]), "utf-8")])
        elif type(info) is list:
            i = 0
            for value in info:
                if type(value) is dict or type(value) is list:
                    newParent = self.tree.insert(parent,"end", text=i, open=True)
                    self.serializeInfo(value, newParent)
                else:
                    self.tree.insert(parent,"end", text=i, values=[unicode(str(value), "utf-8")])
                i = i + 1
            #do list stuff here
        else:
            self.tree.insert(parent, "end", text=info)
            #do normal stuff here
    def save(self):
        jsonOutput(self)
    def setInfo(self, info, file_extention, filename):
        print("HI")
        self.info = info
        self.file_extention = file_extention
        self.filename = filename
        #print(info)
        x = self.tree.get_children()
        for item in x:
            self.tree.delete(item)
        self.serializeInfo(info)
#copied from http://effbot.org/zone/tkinter-autoscrollbar.htm
class AutoScrollbar(Tkinter.Scrollbar):
    # a scrollbar that hides itself if it's not needed.  only
    # works if you use the grid geometry manager.
    def set(self, lo, hi):
        if float(lo) <= 0.0 and float(hi) >= 1.0:
            # grid_remove is currently missing from Tkinter!
            self.tk.call("grid", "remove", self)
        else:
            self.grid()
        Tkinter.Scrollbar.set(self, lo, hi)
    def pack(self, **kw):
        raise Tkinter.TclError, "cannot use pack with this widget"
    def place(self, **kw):
        raise Tkinter.TclError, "cannot use place with this widget"

#Not actually in a class
def jsonOutput(self):
        #file is loaded?
        if self.name == "DataTab":
            if len(self.filenameText.get()) > 0:
                currentTab = self.tabHandle.index(self.tabHandle.select())
                if currentTab == 0:
                    #OriginalInfo
                    filename = self.filenameText.get().rpartition("/")[2]+"-original.json"
                    info = self.fileInfo["originalInfo"]
                elif currentTab == 1:
                    #CustomInfo
                    filename = self.filenameText.get().rpartition("/")[2]+"-custom.json"
                    info = self.fileInfo["customInfo"]
                elif currentTab == 2:
                    #Translation
                    filename = self.filenameText.get().rpartition("/")[2]+".json"
                    info = translate_info(self.fileInfo["customInfo"], self.filenameText.get().rpartition(".")[2])
                else:
                    print("unknown tab")
                    return
        else:
            info = self.info
            filename = self.filename.rpartition("/")[2]+"-"+self.file_extention+".json"
        options = {
            "initialdir" : "output/",
            "defaultextension" : ".json",
            "filetypes" : [("JSON", ".json")],
            "initialfile" : filename
        }
        newFilename = asksaveasfilename(**options)
        with open(newFilename,"w") as f:
            f.write(simplejson.dumps(info, sort_keys=True, indent=4 * ' '))