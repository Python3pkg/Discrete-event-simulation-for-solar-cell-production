# -*- coding: utf-8 -*-
from PyQt5 import QtCore, QtWidgets, QtGui
from .dialogs.CassetteLoopSettingsDialog import CassetteLoopSettingsDialog

class CassetteloopsWidget(QtCore.QObject):
    def __init__(self, parent=None):
        super(CassetteloopsWidget, self).__init__(parent)
        
        self.parent = parent
        self.cassette_loops = []
        self.view = self.parent.cassetteloops_view        
        self.model = self.parent.cassetteloops_model
        self.group_names = self.parent.tools_widget.group_names
        self.statusbar = self.parent.statusBar()

        # 1 = stack buffer; 2 = single cassette buffer; 3 = dual cassette buffer
        self.input_types = {}
        self.input_types['WaferSource'] = []
        self.input_types['WaferStacker'] = [3]
        self.input_types['WaferUnstacker'] = [1]
        self.input_types['BatchTex'] = [2]
        self.input_types['BatchClean'] = [2]
        self.input_types['TubeFurnace'] = [3] 
        self.input_types['SingleSideEtch'] = [3]
        self.input_types['TubePECVD'] = [3]
        self.input_types['PrintLine'] = [3]
        self.input_types['WaferBin'] = [3]
        self.input_types['Buffer'] = [2]
        self.input_types['IonImplanter'] = [2]
        self.input_types['SpatialALD'] = [3]
        self.input_types['InlinePECVD'] = [2,3]
        self.input_types['PlasmaEtcher'] = [1]

        self.output_types = {}
        self.output_types['WaferSource'] = [1]
        self.output_types['WaferStacker'] = [1]
        self.output_types['WaferUnstacker'] = [3]
        self.output_types['BatchTex'] = [2]
        self.output_types['BatchClean'] = [2]
        self.output_types['TubeFurnace'] = [3]
        self.output_types['SingleSideEtch'] = [3]
        self.output_types['TubePECVD'] = [3]
        self.output_types['PrintLine'] = []
        self.output_types['WaferBin'] = []
        self.output_types['Buffer'] = [2]
        self.output_types['IonImplanter'] = [2]
        self.output_types['SpatialALD'] = [3]
        self.output_types['InlinePECVD'] = [2,3]
        self.output_types['PlasmaEtcher'] = [1]

    def generate_cassetteloops(self):
        # generate a default cassette loop list from locationgroups       

        self.cassette_loops = []
        unavailable_groups = []
        found_loops = []
        batchlocations = self.parent.tools_widget.batchlocations
        locationgroups = self.parent.tools_widget.locationgroups

        # find possible loops using every possible start position
        for search_start_position in range(len(locationgroups)-1):           
            
            if search_start_position in unavailable_groups:
                continue

            begin = end = -1 
            
            # find first locationgroup where all tools have a dual cassette output buffer
            for i in range(search_start_position,len(locationgroups)-1):
                suitable = True
                for j in range(len(locationgroups[i])):
                    name = batchlocations[locationgroups[i][j]][0]
                    
                    if not 3 in self.output_types[name]:
                        suitable = False
                    
                if suitable:
                    begin = i
                    break
            
            # quit if no suitable locationgroup was found
            if begin == -1:
                continue

            # find last locationgroup where all tools have a dual cassette output buffer
            for i in range(begin+1,len(locationgroups)):

                suitable = True # suitable as a cassette loop ending or not
                stop_search = False
                
                for j in range(len(locationgroups[i])):
                    name = batchlocations[locationgroups[i][j]][0]
                
                    if not 3 in self.input_types[name]:
                        suitable = False
                        
                    if not 2 in self.input_types[name] or 1 in self.input_types[name]:
                        stop_search = True
                    
                if suitable:
                    end = i

                if stop_search:
                    break

            # quit if no suitable locationgroup was found
            if end == -1:
                continue
            
            if not begin == -1 and not end == -1:
                found_loops.append([begin,end])
                
                for i in range(0,end):
                    unavailable_groups.append(i)

        transport_time = 60 # default duration for cassette return to source
        time_per_unit = 10 # default additional duration for each cassette
        min_units = 1 # default minimum number of cassettes for return transport
        max_units = 99 # default maximum number of cassettes for return transport

        for i in range(len(found_loops)):
            begin = found_loops[i][0]
            end = found_loops[i][1]
            
            if begin == -1 or end == -1:
                continue
        
            if not begin >= end:
                self.cassette_loops.append([begin,end,50,100,transport_time,time_per_unit,min_units,max_units])

    def print_cassetteloop(self, num):
        
        batchlocations = self.parent.tools_widget.batchlocations
        locationgroups = self.parent.tools_widget.locationgroups
        
        if (num >= len(locationgroups)):
            return "Error"
        
        tool = locationgroups[num][0]
        return self.group_names[batchlocations[tool][0]]

    def load_definition(self, default=True):

        if (default):
            self.generate_cassetteloops()

        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Cassette loops'])                       

        for i, value in enumerate(self.cassette_loops):
            parent = QtGui.QStandardItem('Loop ' + str(i))

            if (not len(self.cassette_loops[i])):
                continue

            if not (self.cassette_loops[i][0] == -1):
                for j in range(self.cassette_loops[i][0],self.cassette_loops[i][1]+1):
                    child = QtGui.QStandardItem(self.print_cassetteloop(j))
                    child.setEnabled(False)
                    parent.appendRow(child)

            self.model.appendRow(parent)
            index = self.model.index(i, 0)
            self.view.setExpanded(index, False)

    def import_locationgroups(self):
        self.load_definition() # generate default loops and load it into interface
        self.statusbar.showMessage(self.tr("Cassette loops generated"),3000)
    
    def add_cassetteloop_view(self):
        cassetteloops_dialog = CassetteLoopSettingsDialog(self.parent)
        cassetteloops_dialog.setModal(True)
        cassetteloops_dialog.show()       
    
    def del_cassetteloop_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select a cassette loop"),3000)
            return
                
        row = self.view.selectedIndexes()[0].row()
        del self.cassette_loops[row]

        self.load_definition(False)

        self.statusbar.showMessage(self.tr("Cassette loop removed"),3000)

    def reset_cassetteloops(self, tool_number):
        # empty cassette loops that are affected by a tool list change
    
        locationgroups = self.parent.tools_widget.locationgroups

        if (len(self.cassette_loops) == 0):
            return

        # find first locationgroup that refers to changed tool
        changed_group = -1
        for i in range(len(locationgroups)):
            
            if tool_number in locationgroups[i]:
                changed_group = i
                break

        if changed_group == -1:
            return

        # empty loops where the tools were changed
        for i in range(len(self.cassette_loops)):           
            for j in range(self.cassette_loops[i][0],self.cassette_loops[i][1]+1):
                if j >= changed_group:
                    self.cassette_loops[i][0] = -1
                    self.cassette_loops[i][1] = -1
            
        self.load_definition(False)
    
    def edit_cassetteloop_view(self):
        if (not len(self.view.selectedIndexes())):
            # if nothing selected
            self.statusbar.showMessage(self.tr("Please select a cassette loop"),3000)
            return
        
        cassetteloops_dialog = CassetteLoopSettingsDialog(self.parent)
        cassetteloops_dialog.setModal(True)
        cassetteloops_dialog.show()   
    
    def trash_cassetteloops_view(self):

        if not len(self.cassette_loops):
            return           
        
        msgBox = QtWidgets.QMessageBox(self.parent)
        msgBox.setWindowTitle(self.tr("Warning"))
        msgBox.setIcon(QtWidgets.QMessageBox.Warning)
        msgBox.setText(self.tr("This will remove all cassette loops. Continue?"))
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        msgBox.setDefaultButton(QtWidgets.QMessageBox.Ok)
        ret = msgBox.exec_()
        
        if (ret == QtWidgets.QMessageBox.Ok):
            self.trash_cassetteloops()
            
    def trash_cassetteloops(self):            
        self.cassette_loops = []
        self.model.clear()
        self.model.setHorizontalHeaderLabels(['Cassette loops']) 
        self.statusbar.showMessage(self.tr("All cassette loops were removed"),3000)