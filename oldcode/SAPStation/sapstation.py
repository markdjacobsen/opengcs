__author__ = 'markjacobsen'
import wx
import wx.aui

from Reference.apmtools import *
from strings import sapstring
from sap_panel_navigator import *
import config
import flightplan
from sap_panel_swarm import *
from sap_panel_flight import *
from sap_panel_schedule import *
from sap_panel_map import *
import aircraft

class SAPStation(wx.Frame):

    def __init__(self, parent, id=-1, title=sapstring("str_title"),
                 pos=wx.DefaultPosition, size=(config.app_width, config.app_height),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)

        self._mgr = wx.aui.AuiManager(self)
        #self._routelist = []

        # This is the master data object, containing information on swarms and flights
        self.roster = flightplan.Roster()

        # create main panes

        self.tree1 = SAPPanelNavigator(self)
        self.tree1.on_selection_observers.append(self.tree_selection_changed)

        self.text2 = wx.TextCtrl(self, -1, sapstring("str_frame_flightplan"),
                            wx.DefaultPosition, wx.Size(200,150),
                            wx.NO_BORDER | wx.TE_MULTILINE)

        #self.text3 = wx.TextCtrl(self, -1, sapstring("str_frame_map"),
        #                    wx.DefaultPosition, wx.Size(200,150),
        #                    wx.NO_BORDER | wx.TE_MULTILINE)


        self.center_panel = SAPPanelSchedule(self)

        # create toolbar
        tb1 = wx.ToolBar(self, -1, wx.DefaultPosition, wx.DefaultSize,
                         wx.TB_FLAT | wx.TB_NODIVIDER)
        tb1.SetToolBitmapSize(wx.Size(48,48))
        tbOpenButton = tb1.AddLabelTool(101, sapstring("str_tb_open"), wx.ArtProvider_GetBitmap(wx.ART_ERROR))
        tbSwarmButton = tb1.AddLabelTool(102, sapstring("str_tb_swarm"), wx.ArtProvider_GetBitmap(wx.ART_ERROR))
        tb1.Realize()

        # create toolbar bindings
        self.Bind(wx.EVT_TOOL, self.on_click_tb1, tbOpenButton)
        self.Bind(wx.EVT_TOOL, self.on_click_tb2, tbSwarmButton)

        # add the panes to the manager
        self._mgr.AddPane(self.tree1, wx.LEFT, sapstring("str_frame_tree"))
        self._mgr.AddPane(self.text2, wx.BOTTOM, sapstring("str_frame_flightplan"))
        #self._mgr.AddPane(self.text3, wx.CENTER)
        self._mgr.AddPane(self.center_panel, wx.CENTER)

        # add the toolbar to the manager
        self._mgr.AddPane(tb1, wx.aui.AuiPaneInfo().
                          Name("tb1").Caption("Big Toolbar").
                          ToolbarPane().Top().
                          LeftDockable(False).RightDockable(False))

        # tell the manager to 'commit' all the changes just made
        self._mgr.Update()

        self.Bind(wx.EVT_CLOSE, self.OnClose)


    def OnClose(self, event):
        # TODO this causes a bug
        # wx._core.PyAssertionError: C++ assertion "Assert failure" failed at
        # /BUILD/wxPython-src-3.0.0.0/src/common/wincmn.cpp(1517) in RemoveEventHandler():
        # where has the event handler gone?
        # deinitialize the frame manager
        self._mgr.UnInit()
        # delete the frame
        self.Destroy()

    def on_click_tb1(self,event):
        # Old code for opening file... kept for reference
        # print("open button clicked")
        # openFileDialog = wx.FileDialog(self, sapstring("str_openfiledialog"), "", "",
        #                                "All Files (*.*)|*.*", wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        # if openFileDialog.ShowModal() == wx.ID_CANCEL:
        #     return
        #
        # self._routelist = []
        # newroute = route()
        # newroute.loadFromFile(openFileDialog.GetPath())
        # self.text2.SetValue(newroute.getFlightPlanText())
        # self._routelist.append(newroute)
        #
        # # test calculating headings between waypoints
        # s = ""
        # tools = navtools()
        # for x in range(0,len(newroute.waypoints)-1):
        #     s += repr(tools.getHeadingToWaypoint(newroute.waypoints[x], newroute.waypoints[x+1])) + ', '
        # print s
        return

    def on_click_tb2(self,event):
        return

    def tree_selection_changed(self,selection):
        """
        Subscribes to notifications from the SAPPanelNavigator control. Whenever the user
        selects a different object in the tree, this function gets called. Its main
        purpose is to update the center pane with the right type of panel for the
        selected item.
        :param selection: The data object attached to the selected tree item
        :return:
        """
        print(selection)
        self._mgr.DetachPane(self.center_panel)
        self.center_panel.Destroy()

        if isinstance(selection, flightplan.Swarm):
            print("Select swarm")
            self.center_panel = SAPPanelSwarm(self,selection)
        elif isinstance(selection, flightplan.Flight):
            print("Select flight")
            self.center_panel = SAPPanelFlight(self)
        else:
            if selection == "MAP":
                self.center_panel = SAPPanelMap(self)
            if selection == "SCHEDULE":
                self.center_panel = SAPPanelSchedule(self)

        self._mgr.AddPane(self.center_panel, wx.CENTER)
        self._mgr.Update()

app = wx.App()
frame = SAPStation(None)
frame.Show()
app.MainLoop()