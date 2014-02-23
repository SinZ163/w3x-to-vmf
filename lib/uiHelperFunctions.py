import Tkinter
import ttk
class GenericTreeTab(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        
        self.grid_rowconfigure(0,weight=1)
        self.grid_columnconfigure(0,weight=1)
            
        self.xscrollbar = AutoScrollbar(self,orient=Tkinter.HORIZONTAL)
        self.xscrollbar.grid(row=1,column=0, sticky=Tkinter.E+Tkinter.W)
        
        self.yscrollbar = AutoScrollbar(self)
        self.yscrollbar.grid(row=0,column=1, sticky=Tkinter.N+Tkinter.S)
       
        self.tree = ttk.Treeview(self, columns=('Values'),xscrollcommand=self.xscrollbar.set,yscrollcommand=self.yscrollbar.set)
        self.tree.column('Values', width=100, anchor=Tkinter.W)
        self.tree.heading('Values', text='Values')
        
        self.tree.grid(row=0,column=0, sticky=Tkinter.N+Tkinter.S+Tkinter.E+Tkinter.W)
        
        self.xscrollbar.config(command=self.tree.xview)
        self.yscrollbar.config(command=self.tree.yview)
        
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
    def setInfo(self, info):
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