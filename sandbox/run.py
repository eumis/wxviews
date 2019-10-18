from pyviews.core import InheritedDict
from wxviews.app import register_dependencies, launch
from sandbox.viewmodel import SandboxViews
from wxviews.core import WxRenderingContext


def run_sandbox():
    register_dependencies()
    node_globals = InheritedDict({'views': SandboxViews(['events', 'sizers', 'binding'])})
    launch(WxRenderingContext({'node_globals': node_globals}), 'app')


if __name__ == '__main__':
    run_sandbox()

# import wx

# class MainWindow(wx.Frame):
#     def __init__(self, parent, title):
#         wx.Frame.__init__(self, parent, title=title, size=(200,100))
#         self.control = wx.TextCtrl(self, style=wx.TE_MULTILINE)
#         self.CreateStatusBar() # A Statusbar in the bottom of the window

#         # Setting up the menu.
#         filemenu= wx.Menu()

#         # wx.ID_ABOUT and wx.ID_EXIT are standard IDs provided by wxWidgets.
#         filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
#         filemenu.AppendSeparator()
#         filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

#         # Creating the menubar.
#         menuBar = wx.MenuBar()
#         menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
#         self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
#         self.Show(True)

# app = wx.App(False)
# frame = MainWindow(None, "Sample editor")
# app.MainLoop()
