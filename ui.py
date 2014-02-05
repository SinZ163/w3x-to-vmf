import tkMessageBox
import Tkinter
import ttk

from tkFileDialog import askopenfilename,asksaveasfilename

from read_w3e import ReadW3E

class App(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        
        #Lets set the window size and name
        self.master.title("Warcraft III to Dota 2 conversion toolkit.")
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)
        
        self.master.maxsize(800,600)
        self.configure(height=600,width=800)
        
        self.pack()
        
        self.tree = ttk.Treeview(self)
        self.tree.heading('#0', text="Path", anchor="w")
        self.tree.insert("", 0, text="hai", open=True)

    def about(self):
        tkMessageBox.showinfo("About", """
        WC3-to-VMF is a toolkit made by SinZ and Yoshi2
        """)
    def menuCreation(self):
        #create the menu bar itself
        menubar = Tkinter.Menu(self.master)
        #add stuff to it
        
        #terrain drop-down
        terrainMenu = Tkinter.Menu(menubar, tearoff=0)
        terrainMenu.add_command(label="Open WC3 Terrain file", command=self.openTerrainFile)
        terrainMenu.add_command(label="Open WC3 Data file", command=self.openObjectFile)
        menubar.add_cascade(label="Manual", menu=terrainMenu)
        #help drop-down
        helpMenu = Tkinter.Menu(menubar, tearoff=0)
        helpMenu.add_command(label="About WC3-to-VMF", command=self.about)
        menubar.add_cascade(label="Help", menu=helpMenu)
        #exit button
        menubar.add_command(label="Exit", command=self.master.quit)
        
        #add it to the window
        self.master.config(menu=menubar)
        
    def openTerrainFile(self):
        options = {
            "defaultextension" : ".w3e",
            "filetypes" : [("Warcraft III Terrain", ".w3e")],
            "title" : "This is a title"
        }
        filename = askopenfilename(**options)
        mapInfo = ReadW3E(filename)
        #print(mapInfo.mapInfo)
        #I actually have no idea what I am doing here
        TreeFrame = ttk.Frame(self, padding = "3")
        tree = ttk.Treeview(TreeFrame, columns = ('Values'))
        tree.column('Values', width = 100, anchor = "center")
        tree.heading('Values', text='Values')
        self.JSONTree(tree, '', mapInfo.mapInfo)
        tree.pack(side="bottom")
    def openObjectFile(self):
        options = {
            "defaultextension" : ".w3t",
            "filetypes" : [
                ("Warcraft III Units",          ".w3u"),
                ("Warcraft III Items",          ".w3t"),
                ("Warcraft III Destructables",  ".w3b"),
                ("Warcraft III Doodats",        ".w3d"),
                ("Warcraft III Abilities",      ".w3a"),
                ("Warcraft III Buffs",          ".w3h"),
                ("Warcraft III Upgrades",       ".w3q")
            ],
            "title" : "This is also a title!"
        }
        fileHandle = askopenfilename(**options)
    #voodoo magic is fun?
    def JSONTree(self, Tree, Parent, Dictionery, TagList = []):
         for key in Dictionery : 
          if isinstance(Dictionery[key],dict): 
           Tree.insert(Parent, 'end', key, text = key)
           TagList.append(key)
           JSONTree(Tree, key, Dictionery[key], TagList)
           pprint(TagList)
          elif isinstance(Dictionery[key],list): 
           Tree.insert(Parent, 'end', key, text = key) # Still working on this
          else : 
           Tree.insert(Parent, 'end', key, text = key, value = Dictionery[key])

# create the application
myapp = App()
myapp.menuCreation()

# start the program
myapp.mainloop()