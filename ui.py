import tkMessageBox
import Tkinter

from tkFileDialog import askopenfile,asksaveasfilename


class App(Tkinter.Frame):
    def __init__(self, master=None):
        Tkinter.Frame.__init__(self, master)
        
        #Lets set the window size and name
        self.master.title("Warcraft III to Dota 2 conversion toolkit.")
        self.master.maxsize(800,600)
        self.configure(height=600,width=800)
        
        self.pack()

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
        fileHandle = askopenfile(mode="r",**options)
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
        fileHandle = askopenfile(mode="r",**options)
        

# create the application
myapp = App()
myapp.menuCreation()

# start the program
myapp.mainloop()