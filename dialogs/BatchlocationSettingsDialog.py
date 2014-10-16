# -*- coding: utf-8 -*-
"""
Created on Fri Sep 12 18:00:48 2014

@author: rnaber
"""

from __future__ import division
from PyQt4 import QtGui
from batchlocations.WaferSource import WaferSource
from batchlocations.WaferUnstacker import WaferUnstacker
from batchlocations.WaferBin import WaferBin
from batchlocations.BatchTex import BatchTex
from batchlocations.BatchClean import BatchClean
from batchlocations.TubeFurnace import TubeFurnace
from batchlocations.SingleSideEtch import SingleSideEtch
from batchlocations.TubePECVD import TubePECVD
from batchlocations.PrintLine import PrintLine
from batchlocations.Buffer import Buffer

class dummy_env(object):
    
    def process(dummy0=None,dummy1=None):
        pass

    def now(self):
        pass
    
    def event(dummy0=None):
        pass

class BatchlocationSettingsDialog(QtGui.QDialog):
    def __init__(self, _parent):
        super(QtGui.QDialog, self).__init__(_parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = _parent

        # find out which batchlocation was selected
        self.row = self.parent.batchlocations_view.selectedIndexes()[0].parent().row()
        index = self.parent.batchlocations_view.selectedIndexes()[0].row()
        self.modified_batchlocation_number = self.parent.locationgroups[self.row][index]       
        batchlocation = self.parent.batchlocations[self.modified_batchlocation_number]

        env = dummy_env()
        curr_params = {}
        # load default settings list
        if (batchlocation[0] == "WaferSource"):
            curr_params = WaferSource(env).params
        elif (batchlocation[0] == "WaferUnstacker"):
            curr_params = WaferUnstacker(env).params
        elif (batchlocation[0] == "BatchTex"):
            curr_params = BatchTex(env).params
        elif (batchlocation[0] == "BatchClean"):
            curr_params = BatchClean(env).params            
        elif (batchlocation[0] == "TubeFurnace"):
            curr_params = TubeFurnace(env).params
        elif (batchlocation[0] == "SingleSideEtch"):
            curr_params = SingleSideEtch(env).params
        elif (batchlocation[0] == "TubePECVD"):
            curr_params = TubePECVD(env).params
        elif (batchlocation[0] == "PrintLine"):
            curr_params = PrintLine(env).params            
        elif (batchlocation[0] == "WaferBin"):
            curr_params = WaferBin(env).params
        elif (batchlocation[0] == "Buffer"):
            curr_params = Buffer(env).params            
        else:
            return                         
        
        # update default settings list with currently stored settings
        curr_params.update(batchlocation[1])
        
        self.setWindowTitle(self.tr("Available settings"))
        vbox = QtGui.QVBoxLayout()

        if 'specification' in curr_params:
            spec = QtGui.QPlainTextEdit(curr_params['specification'])
            spec.setReadOnly(True)
            vbox.addWidget(spec)
        else:
            title_label = QtGui.QLabel(self.tr("Edit settings:"))
            vbox.addWidget(title_label)             
        
        self.strings = []
        for i in sorted(curr_params.keys()):
            if ("_desc" in i) | ('specification' in i):
                continue
            elif isinstance(curr_params[i], str):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.strings.append(QtGui.QLineEdit(curr_params[i]))
                self.strings[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.strings[-1].setToolTip(curr_params[i + "_desc"])
                hbox.addWidget(label)
                hbox.addWidget(self.strings[-1]) 
                vbox.addLayout(hbox)
        
        self.integers = []
        for i in sorted(curr_params.keys()):
            if isinstance(curr_params[i], int) & (not i == 'verbose'):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.integers.append(QtGui.QSpinBox())
                self.integers[-1].setAccelerated(True)
                self.integers[-1].setMaximum(999999999)
                self.integers[-1].setValue(curr_params[i])
                self.integers[-1].setObjectName(i)
                if (curr_params[i] >= 100):
                    self.integers[-1].setSingleStep(100)
                elif (curr_params[i] >= 10):
                    self.integers[-1].setSingleStep(10)                     
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.integers[-1].setToolTip(curr_params[i + "_desc"])                  
                hbox.addWidget(label)
                hbox.addWidget(self.integers[-1])  
                vbox.addLayout(hbox)

        self.doubles = []
        for i in sorted(curr_params.keys()):
            if isinstance(curr_params[i], float):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.doubles.append(QtGui.QDoubleSpinBox())
                self.doubles[-1].setAccelerated(True)
                self.doubles[-1].setMaximum(999999999)
                self.doubles[-1].setValue(curr_params[i])
                self.doubles[-1].setSingleStep(0.1)
                self.doubles[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.doubles[-1].setToolTip(curr_params[i + "_desc"])             
                hbox.addWidget(label)
                hbox.addWidget(self.doubles[-1]) 
                vbox.addLayout(hbox)
        
        self.booleans = []
        for i in sorted(curr_params.keys()):
            if isinstance(curr_params[i], bool):
                hbox = QtGui.QHBoxLayout()
                label = QtGui.QLabel(i)
                self.booleans.append(QtGui.QCheckBox())                
                self.booleans[-1].setChecked(curr_params[i])
                self.booleans[-1].setObjectName(i)
                if i + "_desc" in curr_params:
                    label.setToolTip(curr_params[i + "_desc"])
                    self.booleans[-1].setToolTip(curr_params[i + "_desc"])               
                hbox.addWidget(label)
                hbox.addWidget(self.booleans[-1]) 
                vbox.addLayout(hbox)

        buttonbox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        vbox.addWidget(buttonbox)

        self.setLayout(vbox)

    def read(self):
        # read contents of each widget
        # update settings in self.batchlocations[self.modified_batchlocation_number] of parent
        new_params = {}
        for i in self.strings:
            new_params[str(i.objectName())] = str(i.text())

        for i in self.integers:
            new_params[str(i.objectName())] = int(i.text())

        for i in self.doubles:
            new_params[str(i.objectName())] = float(i.text())

        for i in self.booleans:
            new_params[str(i.objectName())] = i.isChecked()
        
        self.parent.batchlocations[self.modified_batchlocation_number][1].update(new_params)
        self.parent.load_definition_batchlocations(False)

        if self.row: # expand row again after reloading definitions
            index = self.parent.batchlocations_model.index(self.row, 0)
            self.parent.batchlocations_view.setExpanded(index, True)
        
        self.parent.statusBar().showMessage(self.tr("Batch location settings updated"))
        self.accept()