__author__ = 'markjacobsen'

import wx
import config
import flightplan
import aircraft

class SAPPanelSwarm(wx.Panel):
    def __init__(self,parent,swarm):
        wx.Panel.__init__(self, parent = parent)

        self.notebook = wx.Notebook(self)
        self.swarm = swarm

        self.page1 = SAPPanelSwarmPage1(self.notebook,swarm)
        self.page2 = SAPPanelSwarmPage2(self.notebook,swarm)
        self.notebook.AddPage(self.page1,"Swarm Details")
        self.notebook.AddPage(self.page2,"Drop Zone")

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(self.notebook,1,wx.EXPAND)
        self.SetSizer(box)


class SAPPanelSwarmPage1(wx.Panel):
    def __init__(self,parent,swarm):
        wx.Panel.__init__(self, parent = parent)

        self.swarm = swarm

        # Labels
        st_name = wx.StaticText(self, -1, "Swarm Name:")
        st_operator = wx.StaticText(self, -1, "Operator:")
        st_num_acft = wx.StaticText(self, -1, "Num_Acft:")
        st_aircraft = wx.StaticText(self, -1, "Aircraft Type:")
        st_takeoff = wx.StaticText(self,-1, "Takeoff:")
        st_enroute = wx.StaticText(self,-1, "Enroute:")
        st_land = wx.StaticText(self,-1, "Land: ")


        self.ctrl_name = wx.TextCtrl(self, -1, self.swarm.name)
        self.Bind(wx.EVT_TEXT, self.on_name_changed, self.ctrl_name)

        # TODO generate each of these from application data
        operatorList = ["Mark","Jessie","Brandon"]
        aircraftList = aircraft.get_all_aircraft()

        takeoffList = flightplan.get_takeoff_plans()
        enrouteList = flightplan.get_enroute_plans()
        landList = flightplan.get_landing_plans()

        self.ctrl_operator = wx.ComboBox(self, -1, self.swarm.operator, (90, 50), (160, -1), operatorList, wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX, self.on_operator_changed, self.ctrl_operator)

        self.ctrl_num_acft = wx.SpinCtrl(self, -1, "", (30,50))
        self.ctrl_num_acft.SetRange(1,config.swarm_max_size)
        self.ctrl_num_acft.SetValue(self.swarm.num_flights)
        self.Bind(wx.EVT_SPINCTRL, self.on_num_acft, self.ctrl_num_acft)

        self.ctrl_aircraft = wx.ComboBox(self,-1, self.swarm.aircraft, (90,50),(160,-1), aircraftList, wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX,self.on_aircraft_changed,self.ctrl_aircraft)

        self.ctrl_takeoff = wx.ComboBox(self,-1, self.swarm.takeoff_plan, (90,50),(160,-1), takeoffList, wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX,self.on_takeoff_changed,self.ctrl_takeoff)

        self.ctrl_enroute = wx.ComboBox(self,-1, self.swarm.enroute_plan, (90,50),(160,-1), enrouteList, wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX,self.on_enroute_changed,self.ctrl_enroute)

        self.ctrl_land = wx.ComboBox(self,-1, self.swarm.land_plan, (90,50),(160,-1), landList, wx.CB_DROPDOWN)
        self.Bind(wx.EVT_COMBOBOX,self.on_land_changed,self.ctrl_land)

        gbs = self.gbs = wx.GridBagSizer(10,2)
        gbs.Add(st_name, (0, 0))
        gbs.Add(st_operator, (1, 0))
        gbs.Add(st_num_acft, (2, 0))
        gbs.Add(st_aircraft, (3, 0))
        gbs.Add(st_takeoff, (4, 0))
        gbs.Add(st_enroute, (5,0))
        gbs.Add(st_land, (6,0))
        gbs.Add(self.ctrl_name, (0, 1))
        gbs.Add(self.ctrl_operator, (1,1))
        gbs.Add(self.ctrl_num_acft, (2, 1))
        gbs.Add(self.ctrl_aircraft, (3, 1))
        gbs.Add(self.ctrl_takeoff, (4,1))
        gbs.Add(self.ctrl_enroute, (5,1))
        gbs.Add(self.ctrl_land, (6,1))

        self.SetSizer(gbs)

    def on_name_changed(self,event):
        self.swarm.name = self.ctrl_name.GetValue()

    def on_num_acft(self,event):
        self.swarm.num_flights = self.ctrl_num_acft.GetValue()

    def on_aircraft_changed(self,event):
        self.swarm.aircraft = self.ctrl_aircraft.GetValue()

    def on_operator_changed(self,event):
        self.swarm.operator = self.ctrl_operator.GetValue()

    def on_takeoff_changed(self,event):
        self.swarm.takeoff_plan = self.ctrl_takeoff.GetValue()
        print self.swarm.takeoff_plan

    def on_enroute_changed(self,event):
        self.swarm.enroute_plan = self.ctrl_enroute.GetValue()

    def on_land_changed(self,event):
        self.swarm.land_plan = self.ctrl_land.GetValue()

class SAPPanelSwarmPage2(wx.Panel):
    def __init__(self, parent, swarm):
        wx.Panel.__init__(self, parent = parent)
        self.swarm = swarm
        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(wx.StaticText(self, -1, "Page 2"),wx.EXPAND)
        self.SetSizer(box)
