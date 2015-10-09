"""
This is the tree control that appears on the left edge of SAPStation. It is derived from wx.TreeCtrl.
"""

__author__ = 'markjacobsen'

import wx
from strings import *
import flightplan
import os
from sap_frame_preflight import *


class SAPPanelNavigator(wx.Panel):
    def __init__(self,parent):
        wx.Panel.__init__(self, parent = parent,size=(200,300))

        self.roster = parent.roster
        self.parent = parent
        self.on_selection_observers = []

        self.tree = wx.TreeCtrl(self,-1,wx.DefaultPosition,(200,200),
                                wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT|wx.TR_EDIT_LABELS)
        self.root = self.tree.AddRoot("Navigator")

        # Create an image list for the tree
        isz = (16,16)
        il = wx.ImageList(isz[0], isz[1])
        self.img_swarm     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER,      wx.ART_OTHER, isz))
        self.img_flight     = il.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, isz))
        #self.tree.SetImageList(il)

        # These are hard-coded options on the navigator, identified by strings in the data field
        self.item_map = self.tree.AppendItem(self.root,sapstring("str_map"))
        self.item_roster = self.tree.AppendItem(self.root,sapstring("str_schedule"))

        self.tree.SetItemPyData(self.item_map,"MAP")
        self.tree.SetItemPyData(self.item_roster,"SCHEDULE")


        btn_add_swarm = wx.Button(self, 10, sapstring("str_add_swarm"), (20, 20))
        btn_delete_swarm = wx.Button(self, 20, sapstring("str_delete_swarm"), (20, 20))

        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.tree,1,wx.EXPAND)
        vbox.Add(btn_add_swarm,0,wx.EXPAND)
        vbox.Add(btn_delete_swarm,0,wx.EXPAND)
        self.SetSizer(vbox)

        # Bindings
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selection_changed, self.tree)
        self.Bind(wx.EVT_TREE_ITEM_MENU, self.on_context_menu, self.tree)
        self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.on_begin_label_edit, self.tree)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.on_end_label_edit, self.tree)

        self.Bind(wx.EVT_BUTTON, self.on_add_swarm, btn_add_swarm)
        self.Bind(wx.EVT_BUTTON, self.on_delete_swarm, btn_delete_swarm)



    def on_selection_changed(self, event):
        item = self.tree.GetSelection()
        data = self.tree.GetItemPyData(item)

        for observer in self.on_selection_observers:
            observer(data)

    def on_begin_label_edit(self,event):
        # Only edit labels for Swarms and Flights
        # If there is no data attached, it should be immutable
        item = self.tree.GetSelection()
        if self.tree.GetItemPyData(item) is None:
            event.Veto()

    def on_end_label_edit(self,event):
        # TODO update object names with new name
        return

    def on_add_swarm(self,event):
        # Create a new swarm object and add it to the Roster

        new_swarm = flightplan.Swarm()

        # TODO: remove these hard-coded flight plans
        new_swarm.takeoff_plan = ""
        new_swarm.enroute_plan = ""
        new_swarm.land_plan = ""

        new_swarm.name = sapstring("str_new_swarm")
        self.roster.add_swarm(new_swarm)

        # Add the new swarm to th etree
        new_swarm_treeitem = self.tree.AppendItem(self.root,sapstring("str_new_swarm"),self.img_swarm)
        self.tree.SetPyData(new_swarm_treeitem, new_swarm)

        print(self.tree.GetCount())

    def on_delete_swarm(self,event):
        # TODO rewrite to use get_selected_swarm()
        item = self.tree.GetSelection()

        # If the user has right-clicked a swarm, get the swarm
        # If the user has right-clicked af light, get the owning swarm
        # If the user has right-clicked something else, we have an error and need to escape
        print(self.tree.GetItemPyData(item))
        if isinstance(self.tree.GetItemPyData(item), flightplan.Swarm):

            swarm = self.tree.GetItemPyData(item)
            swarm_item = item
        elif isinstance(self.tree.GetItemPyData(item), flightplan.Flight):
            swarm_item = self.tree.GetItemParent(item)
            swarm = self.tree.GetItemPyData(swarm_item)
        else:
            return

        # TODO confirm

        # Remove the object
        self.roster.remove_swarm(swarm)

        # Remove from the tree
        self.tree.Delete(item)


    def on_context_menu(self,event):
        menu = wx.Menu()
        popupID_Generate = wx.NewId()
        popupID_DeleteSwarm = wx.NewId()
        popupID_DeleteFlight = wx.NewId()
        popupID_LaunchFlight = wx.NewId()
        popupID_AddSwarm = wx.NewId()
        popupID_AddFlight = wx.NewId()

        #item = wx.MenuItem(menu, popupID_Generate,sapstring("str_generate_flights"))
        #menu.AppendItem(item)

        menu.Append(popupID_Generate,sapstring("str_generate_flights"))
        menu.Append(popupID_DeleteSwarm,sapstring("str_delete_swarm"))
        menu.Append(popupID_DeleteFlight,sapstring("str_delete_flight"))
        menu.Append(popupID_LaunchFlight,sapstring("str_launch_flight"))
        menu.Append(popupID_AddSwarm,sapstring("str_add_swarm"))
        menu.Append(popupID_AddFlight,sapstring("str_add_flight"))


        self.Bind(wx.EVT_MENU, self.on_generate, id=popupID_Generate)
        self.Bind(wx.EVT_MENU, self.on_delete_swarm, id=popupID_DeleteSwarm)
        self.Bind(wx.EVT_MENU, self.on_delete_flight, id=popupID_DeleteFlight)
        self.Bind(wx.EVT_MENU, self.on_launch_flight, id=popupID_LaunchFlight)
        self.Bind(wx.EVT_MENU, self.on_add_swarm, id=popupID_AddSwarm)
        self.Bind(wx.EVT_MENU, self.on_add_flight, id=popupID_AddFlight)

        self.PopupMenu(menu)
        menu.Destroy()



    def on_generate(self,event):
        # TODO error checking before wiping old data
        # TODO rewrite to use get_selected_swarm()
        item = self.tree.GetSelection()

        # If the user has right-clicked a swarm, get the swarm
        # If the user has right-clicked af light, get the owning swarm
        # If the user has right-clicked something else, we have an error and need to escape
        print(self.tree.GetItemPyData(item))
        if isinstance(self.tree.GetItemPyData(item), flightplan.Swarm):

            swarm = self.tree.GetItemPyData(item)
            swarm_item = item
        elif isinstance(self.tree.GetItemPyData(item), flightplan.Flight):
            swarm_item = self.tree.GetItemParent(item)
            swarm = self.tree.GetItemPyData(swarm_item)
        else:
            return

        print(os.getcwd())
        swarm.generate_flight_plans()
        swarm.save_flight_plans()

        # Add the flights to the tree
        self.tree.DeleteChildren(swarm_item)

        for flight in swarm.flights:
            new_flight_treeitem = self.tree.AppendItem(swarm_item,flight.name,self.img_flight)
            self.tree.SetPyData(new_flight_treeitem, flight)


    def on_add_flight(self,event):
        print("TODO: on_add_flight()")

    def on_delete_flight(self,event):
        print("TODO: on_delete_flight()")

    def on_launch_flight(self,event):
        item = self.tree.GetSelection()
        if isinstance(self.tree.GetItemPyData(item), flightplan.Flight):
            flight = self.tree.GetItemPyData(item)
            launcher = SAPFramePreflight(self.parent,flight)
            launcher.Show()
        print("TODO: on_launch_flight()")

    def get_selected_swarm(self,event):
        item = self.tree.GetSelection()
        if isinstance(self.tree.GetItemPyData(item), flightplan.Swarm):
            swarm = self.tree.GetItemPyData(item)
            swarm_item = item
        elif isinstance(self.tree.GetItemPyData(item), flightplan.Flight):
            swarm_item = self.tree.GetItemParent(item)
            swarm = self.tree.GetItemPyData(swarm_item)
        else:
            swarm = None

        return swarm