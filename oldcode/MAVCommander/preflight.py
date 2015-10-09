import wx
from forms.checklists import ChecklistPanel
from forms.checklists import ChecklistItemPanel
from checklist_items import *

class PreflightFrame(wx.Frame):
    def __init__(self, parent, master, system_id, id=-1, title='MAV Preflight',
                 pos=wx.DefaultPosition, size=(1000, 500),
                 style=wx.DEFAULT_FRAME_STYLE):
        wx.Frame.__init__(self, parent, id, title, pos, size, style)


        self.sizer = wx.BoxSizer(wx.VERTICAL)
        # *** TEST CODE TO DISPLAY CHECKLISTITEMPANELS
        #for i in range(0,5):
        #    self.sizer.Add(ChecklistItemPanel(self))

        # *** TEST CODE TO DISPLAY CHECKLISTPANEL
        checklist_panel = ChecklistPanel(self, master, system_id)
        self.sizer.Add(checklist_panel)

        checklist_panel.sizerMiddle.Add(ChecklistItem_ZeroizeAirspeed(checklist_panel), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_Voltage(checklist_panel,(12.0,11.0)), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_Arm(checklist_panel), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_PositiveAirspeed(checklist_panel), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_GPSHealth(checklist_panel), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_TrimCentered(checklist_panel,(5.0,5.0,5.0)), wx.EXPAND)
        # TODO I had to add a second, unnecessary arg to the next line to make it work
        checklist_panel.sizerMiddle.Add(ChecklistItem_ThrottleDown(checklist_panel,(0.0,0.0)), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_DemoServos(checklist_panel,((1,1000),(1,2000),(2,1000),(2,2000),(4,1000),(4,2000))), wx.EXPAND)
        checklist_panel.sizerMiddle.Add(ChecklistItem_ParameterDiff(checklist_panel), wx.EXPAND)
        #for i in range(0,7):
        #    checklist_panel.sizerMiddle.Add(ChecklistItemPanel(checklist_panel), wx.EXPAND)

        self.SetSizer(self.sizer)
        self.Fit()



# Create our wxPython application and show our frame
if __name__=="main":
    app = wx.App()
    frame = PreflightFrame(None)
    frame.Show()
    app.MainLoop()