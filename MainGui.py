# -*- coding: utf-8 -*-
"""
Created on Wed Sep 10 15:19:49 2014

@author: rnaber
"""

from __future__ import division
import numpy as np
from PyQt4 import QtCore, QtGui
icon_name = ":Logo_Tempress.ico"
from RunSimulationThread import RunSimulationThread
from copy import deepcopy

class MainGui(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MainGui, self).__init__(parent)
        self.setWindowTitle(self.tr("Solar cell manufacturing simulation"))
        self.setWindowIcon(QtGui.QIcon(icon_name))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint) # DISABLE BEFORE RELEASE

        self.simulation_thread = RunSimulationThread()
        self.simulation_thread.signal.sig.connect(self.simulation_end_signal)

        self.clip = QtGui.QApplication.clipboard()
        self.batchlocations_model = QtGui.QStandardItemModel()
        self.batchlocations_view = QtGui.QTreeView()
        self.locationgroups_model = QtGui.QStandardItemModel()
        self.batchconnections_model = QtGui.QStandardItemModel()
        self.operators_model = QtGui.QStandardItemModel()
        self.operators_view = QtGui.QTreeView()

        self.batchlocations = {} #tool class name, no of tools, dict with settings
        self.batchlocations[0] = ["WaferSource", {'name' : '0'}]
        self.batchlocations[1] = ["WaferUnstacker", {'name' : '0'}]
        self.batchlocations[2] = ["WaferUnstacker",{'name' : '1'}]
        self.batchlocations[3] = ["BatchTex", {'name' : '0'}]
        self.batchlocations[4] = ["TubeFurnace", {'name' : '0'}]
        self.batchlocations[5] = ["TubeFurnace", {'name' : '1'}]
        self.batchlocations[6] = ["SingleSideEtch", {'name' : '0'}]
        self.batchlocations[7] = ["TubePECVD", {'name' : '0'}]
        self.batchlocations[8] = ["TubePECVD", {'name' : '1'}]
        self.batchlocations[9] = ["PrintLine", {'name' : '0'}]
        self.batchlocations[10] = ["PrintLine", {'name' : '1'}]

        self.locationgroups = {}
        self.batchconnections = {}

        self.operators = {}
        self.operators[0] = [[0,1],{'name' : '0'}]
        self.operators[1] = [[2,3],{'name' : '1'}]    
        self.operators[2] = [[4,5],{'name' : '2'}]
        self.operators[3] = [[6,7],{'name' : '3'}]
        self.operators[4] = [[8,9],{'name' : '4'}]
        self.operators[5] = [[10,11,12,13],{'name' : '5'}]

        self.params = {}
        self.params['time_limit'] = 1000
        
        self.create_menu()
        self.create_main_frame()
        self.load_default_line()

    def open_file(self):
        pass

    def save_to_file(self):
        pass

    def save_to_file_as(self):
        pass

    def load_default_line(self):        
        self.exec_batchlocations()
        self.exec_locationgroups()
        self.exec_batchconnections()

        for i in self.locationgroups:
            parent = QtGui.QStandardItem(self.batchlocations[self.locationgroups[i][0]][0])

            for j in self.locationgroups[i]:
                child = QtGui.QStandardItem(self.batchlocations[j][1]['name'])
                parent.appendRow(child)
            self.batchlocations_model.appendRow(parent)
            self.batchlocations_view.setFirstColumnSpanned(i, self.batchlocations_view.rootIndex(), True)            

        for i in self.operators:
            parent = QtGui.QStandardItem('Operator ' + self.operators[i][1]['name'])

            for j, value in enumerate(self.operators[i][0]):               
                child = QtGui.QStandardItem(self.print_batchconnection(self.operators[i][0][j]))
                parent.appendRow(child)
            self.operators_model.appendRow(parent)
            self.operators_view.setFirstColumnSpanned(i, self.batchlocations_view.rootIndex(), True) 

    def add_batchlocation(self):
        pass

    def del_batchlocation(self):
        pass
    
    def edit_batchlocation(self):
        pass    

    def up_batchlocation(self):
        pass

    def down_batchlocation(self):
        pass

    def print_batchlocation(self, num):
        return self.batchlocations[num][0] + " " + self.batchlocations[num][1]['name']

    def exec_batchlocations(self):
        # generate a default locationgroups list from batchlocations

        self.locationgroups = {}
        num = 0
        for i in self.batchlocations:
            # generate new locationgroups
            
            if (i == 0):
                self.locationgroups[num] = [0]
                num += 1
            elif (self.batchlocations[i][0] == self.batchlocations[i-1][0]):
                self.locationgroups[num-1].append(i)
            else:
                self.locationgroups[num] = [i]
                num += 1   

    def exec_locationgroups(self):
        # generate a default batchconnections list from locationgroups        
        self.batchconnections = {}

        transport_time = 90
        time_per_unit = 20
                           
        num = 0
        for i in np.arange(len(self.locationgroups)-1):
            for j, value in enumerate(self.locationgroups[i]):
                for k, value in enumerate(self.locationgroups[i+1]):
                    self.batchconnections[num] = [[i,j],[i+1,k],transport_time, time_per_unit]
                    num  += 1                            

    def print_batchconnection(self, num):
        value1 = self.locationgroups[self.batchconnections[num][0][0]][self.batchconnections[num][0][1]]
        value2 = self.locationgroups[self.batchconnections[num][1][0]][self.batchconnections[num][1][1]]
        self.print_batchlocation
        return self.print_batchlocation(value1) + " -> " + self.print_batchlocation(value2)           

    def edit_batchconnection(self):
        pass

    def exec_batchconnections(self):
        # generate a default operators list from batchconnections list
    
        for i in self.operators:
            # erase existing batchconnections in the operators list
            self.operators[i][0] = []
            
        num = 0
        curr_locationgroup = 0
        for i in self.batchconnections:
            if (self.batchconnections[i][0][0] == curr_locationgroup):
                self.operators[num][0].append(i)
            else:
                curr_locationgroup = self.batchconnections[i][0][0]
                num += 1
                self.operators[num][0].append(i)                           

    def add_operator(self):
        pass

    def del_operator(self):
        pass

    def edit_operator(self):
        pass    

    def run_simulation(self):
        if not self.simulation_thread.isRunning():
            self.simulation_thread.batchlocations = deepcopy(self.batchlocations)
            self.simulation_thread.locationgroups = deepcopy(self.locationgroups)
            self.simulation_thread.batchconnections = deepcopy(self.batchconnections)
            self.simulation_thread.operators = deepcopy(self.operators)

            self.simulation_thread.params = {}
            self.simulation_thread.params['time_limit'] = 1000
            self.simulation_thread.params.update(self.params)
            
            self.simulation_thread.stop_simulation = False
            self.simulation_thread.start()
            self.run_sim_button.setEnabled(False)
            self.stop_sim_button.setEnabled(True)

    def stop_simulation(self):
        self.simulation_thread.stop_simulation = True

    def simulation_end_signal(self):
        self.run_sim_button.setEnabled(True)
        self.stop_sim_button.setEnabled(False)

    def on_about(self):
        msg = self.tr("Solar cell manufacturing simulation\n\n- Author: Ronald Naber (rnaber@tempress.nl)\n- License: Public domain")
        QtGui.QMessageBox.about(self, self.tr("About the application"), msg)
    
    def create_main_frame(self):
        self.main_frame = QtGui.QWidget()        

        ##### Batch locations #####        
        self.batchlocations_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.batchlocations_model.setHorizontalHeaderLabels(['Batch locations'])
        self.batchlocations_view.setModel(self.batchlocations_model)
        self.batchlocations_view.setUniformRowHeights(True)
        self.batchlocations_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.batchlocations_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)          
        
        add_batchlocation_button = QtGui.QPushButton()
        self.connect(add_batchlocation_button, QtCore.SIGNAL('clicked()'), self.add_batchlocation)
        add_batchlocation_button.setIcon(add_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        add_batchlocation_button.setToolTip(self.tr("Add batchlocation"))
        add_batchlocation_button.setStatusTip(self.tr("Add batchlocation"))
        
        del_batchlocation_button = QtGui.QPushButton()
        self.connect(del_batchlocation_button, QtCore.SIGNAL('clicked()'), self.del_batchlocation)
        del_batchlocation_button.setIcon(del_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        del_batchlocation_button.setToolTip(self.tr("Remove batchlocation"))
        del_batchlocation_button.setStatusTip(self.tr("Remove batchlocation"))

        edit_batchlocation_button = QtGui.QPushButton()
        self.connect(edit_batchlocation_button, QtCore.SIGNAL('clicked()'), self.edit_batchlocation)
        edit_batchlocation_button.setIcon(edit_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        edit_batchlocation_button.setToolTip(self.tr("Edit settings"))
        edit_batchlocation_button.setStatusTip(self.tr("Edit settings"))

        up_batchlocation_button = QtGui.QPushButton()
        self.connect(up_batchlocation_button, QtCore.SIGNAL('clicked()'), self.up_batchlocation)
        up_batchlocation_button.setIcon(up_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_ArrowUp))
        up_batchlocation_button.setToolTip(self.tr("Move up in list"))
        up_batchlocation_button.setStatusTip(self.tr("Move up in list"))
        
        down_batchlocation_button = QtGui.QPushButton()
        self.connect(down_batchlocation_button, QtCore.SIGNAL('clicked()'), self.down_batchlocation)
        down_batchlocation_button.setIcon(down_batchlocation_button.style().standardIcon(QtGui.QStyle.SP_ArrowDown))
        down_batchlocation_button.setToolTip(self.tr("Move down in list"))
        down_batchlocation_button.setStatusTip(self.tr("Move down in list"))

        exec_batchlocations_button = QtGui.QPushButton()
        self.connect(exec_batchlocations_button, QtCore.SIGNAL('clicked()'), self.exec_batchlocations)
        exec_batchlocations_button.setIcon(exec_batchlocations_button.style().standardIcon(QtGui.QStyle.SP_DialogApplyButton))
        exec_batchlocations_button.setToolTip(self.tr("Apply changes"))
        exec_batchlocations_button.setStatusTip(self.tr("Apply changes"))

        buttonbox0 = QtGui.QDialogButtonBox()
        buttonbox0.addButton(add_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(del_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(edit_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(up_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(down_batchlocation_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox0.addButton(exec_batchlocations_button, QtGui.QDialogButtonBox.ActionRole)

        vbox0 = QtGui.QVBoxLayout()
        vbox0.addWidget(self.batchlocations_view)
        vbox0.addWidget(buttonbox0)

        ##### Operators #####
        self.operators_view.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.operators_model.setHorizontalHeaderLabels(['Operators'])
        self.operators_view.setModel(self.operators_model)
        self.operators_view.setUniformRowHeights(True)
        self.operators_view.setDragDropMode(QtGui.QAbstractItemView.NoDragDrop)
        self.operators_view.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)

        add_operator_button = QtGui.QPushButton()
        self.connect(add_operator_button, QtCore.SIGNAL('clicked()'), self.add_operator)
        add_operator_button.setIcon(add_operator_button.style().standardIcon(QtGui.QStyle.SP_DialogOkButton)) 
        add_operator_button.setToolTip(self.tr("Add operator"))
        add_operator_button.setStatusTip(self.tr("Add operator"))
        
        del_operator_button = QtGui.QPushButton()
        self.connect(del_operator_button, QtCore.SIGNAL('clicked()'), self.del_operator)
        del_operator_button.setIcon(del_operator_button.style().standardIcon(QtGui.QStyle.SP_DialogCancelButton))
        del_operator_button.setToolTip(self.tr("Remove operator"))
        del_operator_button.setStatusTip(self.tr("Remove operator"))

        edit_operator_button = QtGui.QPushButton()
        self.connect(edit_operator_button, QtCore.SIGNAL('clicked()'), self.edit_operator)
        edit_operator_button.setIcon(edit_operator_button.style().standardIcon(QtGui.QStyle.SP_FileDialogDetailedView))
        edit_operator_button.setToolTip(self.tr("Edit settings"))
        edit_operator_button.setStatusTip(self.tr("Edit settings"))

        buttonbox1 = QtGui.QDialogButtonBox()
        buttonbox1.addButton(add_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(del_operator_button, QtGui.QDialogButtonBox.ActionRole)
        buttonbox1.addButton(edit_operator_button, QtGui.QDialogButtonBox.ActionRole)

        vbox1 = QtGui.QVBoxLayout()
        vbox1.addWidget(self.operators_view)
        vbox1.addWidget(buttonbox1)

        ##### Top buttonbox #####

        open_file_button = QtGui.QPushButton()
        tip = self.tr("Open file")
        self.connect(add_operator_button, QtCore.SIGNAL('clicked()'), self.open_file)
        open_file_button.setIcon(open_file_button.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton)) 
        open_file_button.setToolTip(tip)
        open_file_button.setStatusTip(tip)

        save_file_button = QtGui.QPushButton()
        tip = self.tr("Save to file")
        self.connect(save_file_button, QtCore.SIGNAL('clicked()'), self.save_to_file)
        save_file_button.setIcon(save_file_button.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton)) 
        save_file_button.setToolTip(tip)
        save_file_button.setStatusTip(tip)

        self.run_sim_button = QtGui.QPushButton()
        tip = self.tr("Run simulation")
        self.connect(self.run_sim_button, QtCore.SIGNAL('clicked()'), self.run_simulation)
        self.run_sim_button.setIcon(self.run_sim_button.style().standardIcon(QtGui.QStyle.SP_MediaPlay)) 
        self.run_sim_button.setToolTip(tip)
        self.run_sim_button.setStatusTip(tip)
        
        self.stop_sim_button = QtGui.QPushButton()
        tip = self.tr("Stop simulation")
        self.connect(self.stop_sim_button, QtCore.SIGNAL('clicked()'), self.stop_simulation)
        self.stop_sim_button.setIcon(self.stop_sim_button.style().standardIcon(QtGui.QStyle.SP_MediaStop)) 
        self.stop_sim_button.setToolTip(tip)
        self.stop_sim_button.setStatusTip(tip)
        self.stop_sim_button.setEnabled(False)        

        top_buttonbox = QtGui.QDialogButtonBox()
        top_buttonbox.addButton(open_file_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(save_file_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.run_sim_button, QtGui.QDialogButtonBox.ActionRole)
        top_buttonbox.addButton(self.stop_sim_button, QtGui.QDialogButtonBox.ActionRole)
        
        toolbar_hbox = QtGui.QHBoxLayout()                
        toolbar_hbox.addWidget(top_buttonbox)
        
        ##### Main layout #####
        top_hbox = QtGui.QHBoxLayout()
        top_hbox.setDirection(QtGui.QBoxLayout.LeftToRight)
        top_hbox.addLayout(vbox0)
        top_hbox.addLayout(vbox1)

  
        vbox = QtGui.QVBoxLayout()       
        vbox.addLayout(toolbar_hbox)
        vbox.addLayout(top_hbox) 
                                                         
        self.main_frame.setLayout(vbox)

        self.setCentralWidget(self.main_frame)

        self.status_text = QtGui.QLabel("")     
        self.statusBar().addWidget(self.status_text,1)
        self.statusBar().showMessage(self.tr("Ready"))

    def create_menu(self):        
        self.file_menu = self.menuBar().addMenu(self.tr("File"))

        tip = self.tr("Open file")        
        load_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_DialogOpenButton),self.tr("&Open..."), self)
        self.connect(load_action, QtCore.SIGNAL("triggered()"), self.open_file)
        load_action.setToolTip(tip)
        load_action.setStatusTip(tip)
        load_action.setShortcut('Ctrl+O')

        tip = self.tr("Save to file")        
        save_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_DialogSaveButton),self.tr("&Save"), self)
        self.connect(save_action, QtCore.SIGNAL("triggered()"), self.save_to_file)
        save_action.setToolTip(tip)
        save_action.setStatusTip(tip)
        save_action.setShortcut('Ctrl+S')

        tip = self.tr("Save to file as...")        
        saveas_action = QtGui.QAction(self.tr("Save as..."), self)
        self.connect(save_action, QtCore.SIGNAL("triggered()"), self.save_to_file_as)
        saveas_action.setToolTip(tip)
        saveas_action.setStatusTip(tip)        

        tip = self.tr("Quit")        
        quit_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_ArrowBack),self.tr("&Quit"), self)
        self.connect(quit_action, QtCore.SIGNAL("triggered()"), self.close)
        quit_action.setToolTip(tip)
        quit_action.setStatusTip(tip)
        quit_action.setShortcut('Ctrl+Q')

        self.file_menu.addAction(load_action)
        self.file_menu.addAction(save_action)
        self.file_menu.addAction(saveas_action)        
        self.file_menu.addAction(quit_action)
           
        self.help_menu = self.menuBar().addMenu(self.tr("Help"))

        tip = self.tr("About the application")        
        about_action = QtGui.QAction(self.style().standardIcon(QtGui.QStyle.SP_FileDialogInfoView),self.tr("About..."), self)
        self.connect(about_action, QtCore.SIGNAL("triggered()"), self.on_about)
        about_action.setToolTip(tip)
        about_action.setStatusTip(tip)
        about_action.setShortcut('F1')

        self.help_menu.addAction(about_action)