# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from sys import platform as _platform

class AddOperatorConnectionDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super(QtWidgets.QDialog, self).__init__(parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = parent

        # find out which connection was selected
        self.row = self.parent.operators_view.selectedIndexes()[0].parent().row()
        self.index = self.parent.operators_view.selectedIndexes()[0].row()        
        
        self.setWindowTitle(self.tr("Add operator connection"))
        vbox = QtWidgets.QVBoxLayout()

        title_label = QtWidgets.QLabel(self.tr("Available connections:"))
        vbox.addWidget(title_label)

        self.dataset_cb = []
        for i, value in enumerate(self.parent.batchconnections):
            self.dataset_cb.append(QtWidgets.QCheckBox(self.parent.print_batchconnection(i)))
            if i in self.parent.operators[self.row][0]:
                self.dataset_cb[i].setChecked(True)

        scroll_area = QtWidgets.QScrollArea()
        checkbox_widget = QtWidgets.QWidget()
        checkbox_vbox = QtWidgets.QVBoxLayout()

        for i in range(len(self.dataset_cb)):
            self.dataset_cb[i].setMinimumWidth(400) # prevent obscured text
            checkbox_vbox.addWidget(self.dataset_cb[i])

        checkbox_widget.setLayout(checkbox_vbox)
        scroll_area.setWidget(checkbox_widget)
        vbox.addWidget(scroll_area)

        ### Buttonbox for ok or cancel ###
        hbox = QtWidgets.QHBoxLayout()
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft)
        hbox.addStretch(1) 
        hbox.addWidget(buttonbox)
        hbox.addStretch(1)
        hbox.setContentsMargins(0,0,0,4)                
        vbox.addLayout(hbox)

        self.setLayout(vbox)
        self.setMinimumWidth(800)

    def read(self):
        # Add connections to operator
        self.parent.operators[self.row][0] = []
        for i in range(len(self.dataset_cb)):
            if self.dataset_cb[i].isChecked():
                self.parent.operators[self.row][0].append(i)
        
        self.parent.operators[self.row][0].sort()
        
        self.parent.load_definition_operators(False)
        
        # re-expand the operator parent item
        index = self.parent.operators_model.index(self.row, 0)
        self.parent.operators_view.setExpanded(index, True)              
            
        self.parent.statusBar().showMessage("Operator connections updated") 
        
        self.accept()