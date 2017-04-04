# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from dialogs.AddBatchlocationDialog import AddBatchlocationDialog

class AddBatchlocationView(QtCore.QObject):
    def __init__(self, _parent):
        super(QtCore.QObject, self).__init__(_parent)
        
        self.parent = _parent

        # start dialog to enable user to add batch location
        add_batchlocation_dialog = AddBatchlocationDialog(self.parent)
        add_batchlocation_dialog.setModal(True)
        add_batchlocation_dialog.show()