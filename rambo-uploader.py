#!/usr/bin/python
import shlex
import subprocess
import os
import sys
import wx, wx.html
import ConfigParser

#
# About Dialog
#
version = "0.1-Dev"

class HtmlWindow(wx.html.HtmlWindow):
	def __init__(self, parent, id, size=(600,400)):
		wx.html.HtmlWindow.__init__(self,parent, id, size=size)
	def OnLinkClicked(self, link):
		wx.LaunchDefaultBrowser(link.GetHref())

class AboutBox(wx.Dialog):
	def __init__(self):
		aboutText = """<p>RAMBo Uploader and Tester version %(version)s. Developed by <a href="http://ultimachine.com">UltiMachine</a>. 
		<br /> <br />
		<b>Version Info</b>
		<br />Python : %(python)s
		<br />wxPython : %(wxpy)s 
		<br /> <br />
		<b>License Info</b><br />
		This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version. <br />
		This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details. <br />
		You should have received a copy of the GNU General Public License along with this program.  If not, see <a href="http://www.gnu.org/licenses/">http://www.gnu.org/licenses/</a>.</p>"""
		wx.Dialog.__init__(self, None, -1, "About",style=wx.DEFAULT_DIALOG_STYLE|wx.THICK_FRAME|wx.RESIZE_BORDER|wx.TAB_TRAVERSAL)
		hwin = HtmlWindow(self, -1, size=(400,200))
		vers = {}
		vers["python"] = sys.version.split()[0]
		vers["wxpy"] = wx.VERSION_STRING
		vers["version"] = version
		hwin.SetPage(aboutText % vers)
		btn = hwin.FindWindowById(wx.ID_OK)
		irep = hwin.GetInternalRepresentation()
		hwin.SetSize((irep.GetWidth()+25, irep.GetHeight()+10))
		self.SetClientSize(hwin.GetSize())
		self.CentreOnParent(wx.BOTH)
		self.SetFocus()

#
# ATmega 
#
class atmega():
	"atmega properties to pass to avrdude"
	def __init__(self):
		self.name = "m2560"
		self.lockBits = "0x0F"
		self.extFuse = "0xFD"
		self.highFuse = "0xD0"
		self.lowFuse = "0xFF"
		self.bootloader = "./stk500boot_v2_mega2560.hex"

#
# AVRDUDE, dude
#
class avrdude():
	"avrdude properties"
	def __init__(self):
		self.path = "avrdude"
		self.programmer = "avrispmkII"
		self.programmerSN = "000200149639"
		self.port = "usb"
	def upload(self, target):
		#call avrdude as a subprocess
		cmd = self.path + " -c " + self.programmer + " -P " + self.port + ":" +self.programmerSN
		if target.name:
			cmd += " -p " + target.name
		if target.bootloader:
			cmd += " -U " + target.bootloader
		if target.extFuse:
			cmd += " -Uefuse:w:" + target.extFuse + ":m"
		if target.highFuse:
			cmd += " -Uhfuse:w:" + target.highFuse + ":m"
		if target.lowFuse:
			cmd += " -Ulfuse:w:" + target.lowFuse + ":m"
		if target.lockBits:
			cmd += " -Ulock:w:" +target.lockBits + ":m"
		print(cmd)
		args = shlex.split(cmd)
		p = subprocess.Popen(args)

class window(wx.Frame):
	def __init__(self):
		"""Constructor"""
		wx.Frame.__init__(self, None, wx.ID_ANY,
			"RAMBo Uploader and Tester",
			size=(600,400)
			)
		#Load Config
		self.config = ConfigParser.RawConfigParser()
		
		#Setup Menus
		menuBar = wx.MenuBar()
		menu = wx.Menu()
		m_saveConfig = menu.Append(wx.ID_SAVE, "&Save Config", "Save Configuration.")
		self.Bind(wx.EVT_MENU, self.OnSave, m_saveConfig)
		m_loadConfig = menu.Append(wx.ID_OPEN, "&Load Config", "Load Configuration.")
		self.Bind(wx.EVT_MENU, self.OnLoad, m_loadConfig)
		menuBar.Append(menu, "&File")
		menu = wx.Menu()
		m_about = menu.Append(wx.ID_ABOUT, "&About", "Information about this program")
		self.Bind(wx.EVT_MENU, self.OnAbout, m_about)
		menuBar.Append(menu, "&Help")
		self.SetMenuBar(menuBar)

		#Setup Tabs
		p = wx.Panel(self)
		nb = wx.Notebook(p)
		nb.AddPage(uploadTab(nb,self), "Upload/Test")
		self.isp1set = ispSettingsTab(nb)
		self.isp2set = ispSettingsTab(nb)
		nb.AddPage(self.isp1set, "ISP1 Settings")
		nb.AddPage(self.isp2set, "ISP2 Settings")
		nb.AddPage(ispSettingsTab(nb), "Target Settings")
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(nb, 1, wx.ALL|wx.EXPAND, 5)
		p.SetSizer(sizer)
		self.Layout()
		self.Show()
		
		#init settings
		self.isp1 = avrdude()
		self.isp2 = avrdude()
		self.avr1 = atmega()
		self.avr2 = atmega()

	def OnSave(self,event):
		self.dirname = ''
		dlg = wx.FileDialog(self, "Save Configuration", "", "",
                                   "*.conf", wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)
		if dlg.ShowModal() == wx.ID_OK:
			cfgfile = open(dlg.GetPath(),'w')
			if(not self.config.has_section('isp1')): self.config.add_section('isp1')
			if(not self.config.has_section('isp2')): self.config.add_section('isp2')
			if(not self.config.has_section('avr1')): self.config.add_section('avr1')
			if(not self.config.has_section('avr2')): self.config.add_section('avr2')
			self.isp1set.getConfig(self.isp1,self.avr1)
			self.isp2set.getConfig(self.isp2,self.avr2)
			self.config.set('isp1','isp1',self.isp1.__dict__)
			self.config.set('isp2','isp2',self.isp2.__dict__)
			self.config.set('avr1','avr1',self.avr1.__dict__)
			self.config.set('avr2','avr2',self.avr2.__dict__)
			self.config.write(cfgfile)
			cfgfile.close()
		dlg.Destroy()

	def OnLoad(self,event):
		self.dirname = ''
		dlg = wx.FileDialog(self, "Load Configuration", self.dirname, "", "*.conf", wx.FD_OPEN)
		if dlg.ShowModal() == wx.ID_OK:
			self.config.read(dlg.GetPath())
			self.isp1.__dict__ = eval(self.config.get('isp1', 'isp1'))
			self.isp2.__dict__ = eval(self.config.get('isp2', 'isp2'))
			self.avr1.__dict__ = eval(self.config.get('avr1', 'avr1'))
			self.avr2.__dict__ = eval(self.config.get('avr2', 'avr2'))
			self.isp1set.loadConfig(self.isp1,self.avr1)
			self.isp2set.loadConfig(self.isp2,self.avr2)
		dlg.Destroy()

	def OnAbout(self, event):
		dlg = AboutBox()
		dlg.ShowModal()
		dlg.Destroy()
	
	def uploadISP1(self, event):
		self.isp1.upload(self.avr1)
	def uploadISP2(self, event):
		self.isp2.upload(self.avr2)
	def uploadISPAll(self, event):
		self.isp1.upload(self.avr1)
		self.isp2.upload(self.avr2)
#
# Notebook Tabs
#
class uploadTab(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self,parent,window):
		""""""
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		gs = wx.FlexGridSizer(5,2,5,5)
		
		#buttons
		self.uploadISP1 = wx.Button(self,label='Upload ISP1')
		self.uploadISP1.Bind(wx.EVT_BUTTON, window.uploadISP1)
		self.uploadISP2 = wx.Button(self,label='Upload ISP2')
		self.uploadISP2.Bind(wx.EVT_BUTTON, window.uploadISP2)
		self.uploadAll = wx.Button(self,label='Upload All')
		self.uploadAll.Bind(wx.EVT_BUTTON, window.uploadISPAll)

		self.runTest= wx.Button(self,label='Run Test')
		self.serialNumber = wx.TextCtrl(self)
		gs.AddMany([(self.uploadISP1), (self.uploadISP2), (self.uploadAll),           (wx.StaticText(self), wx.EXPAND),(wx.StaticText(self, label="Serial Number"), wx.EXPAND), (self.serialNumber, 1, ), (self.runTest)])
		self.SetSizer(gs)

class ispSettingsTab(wx.Panel):
	"""
	This will be the first notebook tab
	"""
	#----------------------------------------------------------------------
	def __init__(self,parent):
		""""""
		wx.Panel.__init__(self, parent=parent, id=wx.ID_ANY)
		sizer = wx.BoxSizer(wx.HORIZONTAL)
		fgs = wx.FlexGridSizer(6, 2, 9, 25)
		programmerTxt = wx.StaticText(self, label="Programmer : ")
		programmerSNTxt = wx.StaticText(self, label="Serial Number : ")
		portTxt = wx.StaticText(self, label="Port : ")
		nameTxt = wx.StaticText(self, label="AVR Target : ")
		lockBitsTxt = wx.StaticText(self, label="Lock Bits : ")
		extFuseTxt = wx.StaticText(self, label="Ext Fuse : ")
		highFuseTxt = wx.StaticText(self, label="High Fuse : ")
		lowFuseTxt = wx.StaticText(self, label="Low Fuse : ")
		bootloaderTxt = wx.StaticText(self, label="Flash : ")
		self.name = wx.TextCtrl(self)
		self.lockBits = wx.TextCtrl(self)
		self.extFuse = wx.TextCtrl(self)
		self.highFuse = wx.TextCtrl(self)
		self.lowFuse = wx.TextCtrl(self)
		self.bootloader = wx.TextCtrl(self)
		self.programmer = wx.TextCtrl(self)
		self.programmerSN = wx.TextCtrl(self)
		self.port = wx.TextCtrl(self)
		fgs.AddMany([(programmerTxt), (self.programmer, 1, wx.EXPAND), (programmerSNTxt), (self.programmerSN, 1, wx.EXPAND), (portTxt), (self.port, 1, wx.EXPAND), (nameTxt), (self.name, 1, wx.EXPAND), (lockBitsTxt),
                (self.lockBits, 1, wx.EXPAND), (extFuseTxt), (self.extFuse, 1, wx.EXPAND), (highFuseTxt),(self.highFuse, 1, wx.EXPAND), (lowFuseTxt),(self.lowFuse, 1, wx.EXPAND), (bootloaderTxt),(self.bootloader, 1, wx.EXPAND)])
		fgs.AddGrowableCol(1, 1)
		sizer.Add(fgs, proportion=1, flag=wx.ALL|wx.EXPAND, border=15)
		self.SetSizer(sizer)
	def getConfig(self,avrdude,atmega):
		atmega.name = self.name.GetValue()
		atmega.lockBits = self.lockBits.GetValue()
		atmega.extFuse = self.extFuse.GetValue()
		atmega.highFuse = self.highFuse.GetValue()
		atmega.lowFuse = self.lowFuse.GetValue()
		atmega.bootloader = self.bootloader.GetValue()
		avrdude.programmer = self.programmer.GetValue()
		avrdude.programmerSN = self.programmerSN.GetValue()
		avrdude.port = self.port.GetValue()
	def loadConfig(self,avrdude,atmega):
		self.name.SetValue(atmega.name)
		self.lockBits.SetValue(atmega.lockBits)
		self.extFuse.SetValue(atmega.extFuse)
		self.highFuse.SetValue(atmega.highFuse)
		self.lowFuse.SetValue(atmega.lowFuse)
		self.bootloader.SetValue(atmega.bootloader)
		self.programmer.SetValue(avrdude.programmer)
		self.programmerSN.SetValue(avrdude.programmerSN)
		self.port.SetValue(avrdude.port)

#
# main, meng
#
def main():
	ex = wx.App()
	frame = window()
	ex.MainLoop()

if __name__ == "__main__":
	main()

