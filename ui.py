import tkMessageBox
import Tkinter
import ttk

import traceback

from tkFileDialog import askopenfilename,asksaveasfilename

from read_w3e import ReadW3E

try:
	from PIL import Image, ImageTk
	print("yes PIL, maybe topdown")
	from topdownViewer import TopDownViewer
	useTopDown = True
	print("yes PIL, yes topdown")
except:
	useTopDown = False
	print("no PIL, no topdown")
	print(traceback.format_exc())
	
class TerrainTab(Tkinter.Frame):
	def	__init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.configure(height=600,width=800)
		self.openButton = Tkinter.Button(self, text="Open!", command=self.openFile).grid(row=0,column=0)
		
		self.filenameText = Tkinter.StringVar()
		self.filename = Tkinter.Label(self, textvariable=self.filenameText).grid(row=0,column=1)
		
		tmp="disabled"
		if useTopDown:
			tmp = "normal"
		self.topDownOption = Tkinter.IntVar()
		self.topDown = Tkinter.Checkbutton(self, text="Show TopDown (beta)", anchor="w", variable=self.topDownOption,state=tmp).grid(row=1)
		
		self.headerInfoText = Tkinter.StringVar()
		self.headerInfo = Tkinter.Label(self, textvariable=self.headerInfoText).grid(row=2)
		
		if useTopDown:
			global topdown
			topdown = Tkinter.PhotoImage(data="R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7")
			self.topDown = Tkinter.Label(self, image=topdown)
			self.topDown.image = topdown
			self.topDown.grid(row=3)
		self.pack()
	def	openFile(self):
		options = {
			"defaultextension" : ".w3e",
			"filetypes"	: [("Warcraft III Terrain", ".w3e")],
			"title" : "This is a title"
		}
		filename = askopenfilename(**options)
		self.filenameText.set(filename)
		if filename:
			mapInfo = ReadW3E(filename)
			self.headerInfoText.set("offsetX: {offsetX}\r\noffsetY: {offsetY}\r\nwidth: {width}\r\nheight: {height}\r\n".format(**mapInfo.mapInfo))
			if self.topDownOption:
				print("Time to generate a topdown")
				#time to run TopDownViewer
				topdownInstance = TopDownViewer(mapInfo)
				global topdown
				topdown = topdownInstance.img
				self.topDown.configure(image=topdown)
				self.topDown.image = topdown
		else:
			self.headerInfoText.set("")
class DataTab(Tkinter.Frame):
	def	__init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.configure(height=600,width=800)
class InfoTab(Tkinter.Frame):
	def	__init__(self, master=None):
		Tkinter.Frame.__init__(self, master)
		self.configure(height=600,width=800)
		self.infoLabel = Tkinter.Label(self, text="WC3-to-VMF is a toolkit made by SinZ and Yoshi2 \r\nThis project is available on Github: http://github.com/SinZ163/w3x-to-vmf/").pack()
root = Tkinter.Tk()
root.title("Warcraft III to Dota 2 conversion toolkit.")
tabHandle = ttk.Notebook(root)

terrainTab = TerrainTab(tabHandle)
dataTab = DataTab(tabHandle)
infoTab = InfoTab(tabHandle)

tabHandle.add(terrainTab, text="Terrain")
tabHandle.add(dataTab, text="Data")
tabHandle.add(infoTab, text="Info")
tabHandle.pack()
root.mainloop()