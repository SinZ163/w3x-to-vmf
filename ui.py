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
        menubar.add_cascade(label="Terrain", menu=terrainMenu)
        #help drop-down
        helpMenu = Tkinter.Menu(menubar, tearoff=0)
        helpMenu.add_command(label="About WC3-to-VMF", command=self.about)
        menubar.add_cascade(label="Help", menu=helpMenu)
        #exit button
        menubar.add_command(label="Exit", command=self.master.quit)
        
        #add it to the window
        self.master.config(menu=menubar)
        
    def openTerrainFile(self):
        options = {}
        options["defaultextension"] = ".w3e"
        options["filetypes"] = [("Warcraft III Terrain", ".w3e")]
        options["title"] = "This is a title"
        fileHandle = askopenfile(mode="r",**options)
        

# create the application
myapp = App()
myapp.menuCreation()

# start the program
myapp.mainloop()