# -*- coding: utf-8 -*-
from blockdiag import parser, builder, drawer
from PyQt5 import QtWidgets, QtSvg, QtGui
from batchlocations.WaferSource import WaferSource
from batchlocations.WaferStacker import WaferStacker
from batchlocations.WaferUnstacker import WaferUnstacker
from batchlocations.WaferBin import WaferBin
from batchlocations.BatchTex import BatchTex
from batchlocations.BatchClean import BatchClean
from batchlocations.TubeFurnace import TubeFurnace
from batchlocations.SingleSideEtch import SingleSideEtch
from batchlocations.TubePECVD import TubePECVD
from batchlocations.PrintLine import PrintLine
from batchlocations.Buffer import Buffer
from batchlocations.IonImplanter import IonImplanter
from batchlocations.SpatialALD import SpatialALD
from batchlocations.InlinePECVD import InlinePECVD
from batchlocations.PlasmaEtcher import PlasmaEtcher
from sys import platform as _platform

from blockdiag.imagedraw import svg # needed for pyinstaller
from blockdiag.noderenderer import roundedbox # needed for pyinstaller

class dummy_env(object):
    
    def process(dummy0=None,dummy1=None):
        pass

    def now(self):
        pass
    
    def event(dummy0=None):
        pass

class BatchlocationSettingsDialog(QtWidgets.QDialog):
    def __init__(self, _parent):
        super(QtWidgets.QDialog, self).__init__(_parent)
        # create dialog screen for each parameter in curr_params
        
        self.parent = _parent
        self.batchlocations = self.parent.tools_widget.batchlocations
        self.locationgroups = self.parent.tools_widget.locationgroups        
        self.load_definition = self.parent.tools_widget.load_definition
        self.view = self.parent.batchlocations_view           
        self.model = self.parent.batchlocations_model
        self.statusbar = self.parent.statusBar()        

        svg.setup(svg) # needed for pyinstaller
        roundedbox.setup(roundedbox) # needed for pyinstaller

        # find out which batchlocation was selected
        self.row = self.view.selectedIndexes()[0].parent().row()
        self.index = self.view.selectedIndexes()[0].row()
        self.modified_batchlocation_number = self.locationgroups[self.row][self.index]       
        batchlocation = self.batchlocations[self.modified_batchlocation_number]

        env = dummy_env()
        curr_params = {}
        curr_diagram = None        
        # load default settings list
        if (batchlocation[0] == "WaferSource"):
            curr_params = WaferSource(env).params
            curr_diagram  = WaferSource(env).diagram
        elif (batchlocation[0] == "WaferStacker"):
            curr_params = WaferStacker(env).params
            curr_diagram  = WaferStacker(env).diagram             
        elif (batchlocation[0] == "WaferUnstacker"):
            curr_params = WaferUnstacker(env).params
            curr_diagram  = WaferUnstacker(env).diagram            
        elif (batchlocation[0] == "BatchTex"):
            curr_params = BatchTex(env).params
            curr_diagram  = BatchTex(env).diagram            
        elif (batchlocation[0] == "BatchClean"):
            curr_params = BatchClean(env).params            
            curr_diagram  = BatchClean(env).diagram            
        elif (batchlocation[0] == "TubeFurnace"):
            curr_params = TubeFurnace(env).params
            curr_diagram  = TubeFurnace(env).diagram            
        elif (batchlocation[0] == "SingleSideEtch"):
            curr_params = SingleSideEtch(env).params
            curr_diagram  = SingleSideEtch(env).diagram            
        elif (batchlocation[0] == "TubePECVD"):
            curr_params = TubePECVD(env).params
            curr_diagram  = TubePECVD(env).diagram            
        elif (batchlocation[0] == "PrintLine"):
            curr_params = PrintLine(env).params            
            curr_diagram  = PrintLine(env).diagram            
        elif (batchlocation[0] == "WaferBin"):
            curr_params = WaferBin(env).params
            curr_diagram  = WaferBin(env).diagram            
        elif (batchlocation[0] == "Buffer"):
            curr_params = Buffer(env).params            
            curr_diagram  = Buffer(env).diagram            
        elif (batchlocation[0] == "IonImplanter"):
            curr_params = IonImplanter(env).params
            curr_diagram  = IonImplanter(env).diagram            
        elif (batchlocation[0] == "SpatialALD"):
            curr_params = SpatialALD(env).params            
            curr_diagram  = SpatialALD(env).diagram            
        elif (batchlocation[0] == "InlinePECVD"):
            curr_params = InlinePECVD(env).params 
            curr_diagram  = InlinePECVD(env).diagram            
        elif (batchlocation[0] == "PlasmaEtcher"):
            curr_params = PlasmaEtcher(env).params 
            curr_diagram  = PlasmaEtcher(env).diagram
        else:
            return                            

        # update default settings list with currently stored settings
        curr_params.update(batchlocation[1])
        
        self.setWindowTitle(self.tr("Tool settings"))

        tabwidget = QtWidgets.QTabWidget()
        
        self.strings = []
        self.integers = []
        self.doubles = []
        self.booleans = []
        
        setting_types = ["configuration","process","automation","downtime"]
        setting_type_tabs = {"configuration" : "Configuration",
                               "process" : "Process",
                               "automation" : "Automation",
                               "downtime" : "Downtime"}        
        setting_type_titles = {"configuration" : "<b>Tool configuration</b>",
                               "process" : "<b>Process settings</b>",
                               "automation" : "<b>Automation settings</b>",
                               "downtime" : "<b>Downtime settings</b>"}
        for j in setting_types:
            if not (j in list(curr_params.values())):
                continue
            
            vbox = QtWidgets.QVBoxLayout()
            vbox.addWidget(QtWidgets.QLabel(setting_type_titles[j]))

            if (j == "configuration"):
                # Make QLineEdit for name in configuration tab
                hbox = QtWidgets.QHBoxLayout()
                self.strings.append(QtWidgets.QLineEdit(curr_params['name']))
                self.strings[-1].setObjectName('name')
                self.strings[-1].setMaxLength(5)
                description = QtWidgets.QLabel('Name of the individual tool')
                self.strings[-1].setToolTip('Name of the individual tool')
                hbox.addWidget(self.strings[-1])
                hbox.addWidget(description)
                hbox.addStretch(1)
                vbox.addLayout(hbox)
            
            for i in sorted(curr_params.keys()):
            # Make QSpinBox or QDoubleSpinbox for integers and doubles
                if isinstance(curr_params[i], int) and (curr_params[i + "_type"] == j):
                    hbox = QtWidgets.QHBoxLayout()
                    description = QtWidgets.QLabel(curr_params[i + "_desc"])              
                    self.integers.append(QtWidgets.QSpinBox())
                    self.integers[-1].setAccelerated(True)
                    self.integers[-1].setMaximum(999999999)
                    self.integers[-1].setValue(curr_params[i])
                    self.integers[-1].setObjectName(i)
                    if (curr_params[i] >= 100):
                        self.integers[-1].setSingleStep(100)
                    elif (curr_params[i] >= 10):
                        self.integers[-1].setSingleStep(10)      
                    if i + "_desc" in curr_params:
                        self.integers[-1].setToolTip(curr_params[i + "_desc"])
                    hbox.addWidget(self.integers[-1])
                    hbox.addWidget(description)
                    hbox.addStretch(1)
                    vbox.addLayout(hbox)
                elif isinstance(curr_params[i], float) and (curr_params[i + "_type"] == j):
                    hbox = QtWidgets.QHBoxLayout()
                    description = QtWidgets.QLabel(curr_params[i + "_desc"])
                    self.doubles.append(QtWidgets.QDoubleSpinBox())
                    self.doubles[-1].setAccelerated(True)
                    self.doubles[-1].setMaximum(999999999)
                    self.doubles[-1].setValue(curr_params[i])
                    self.doubles[-1].setSingleStep(0.1)
                    self.doubles[-1].setObjectName(i)
                    if i + "_desc" in curr_params:
                        self.doubles[-1].setToolTip(curr_params[i + "_desc"])             
                    hbox.addWidget(self.doubles[-1]) 
                    hbox.addWidget(description)
                    hbox.addStretch(1)                
                    vbox.addLayout(hbox)

            vbox.addStretch(1)
            generic_widget = QtWidgets.QWidget()
            generic_widget.setLayout(vbox)
            tabwidget.addTab(generic_widget, setting_type_tabs[j])

        ### Description tab ###
        vbox_description = QtWidgets.QVBoxLayout() # vbox for description elements

        # Diagram
        tree = parser.parse_string(curr_diagram)
        diagram = builder.ScreenNodeBuilder.build(tree)
        draw = drawer.DiagramDraw('SVG', diagram, filename="")
        draw.draw()
        svg_string = draw.save()

        svg_widget = QtSvg.QSvgWidget()
        svg_widget.load(str(svg_string).encode('latin-1'))
        
        hbox = QtWidgets.QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(svg_widget)
        hbox.addStretch(1)
        vbox_description.addLayout(hbox)

        # Text
        hbox = QtWidgets.QHBoxLayout()           
        browser = QtWidgets.QTextBrowser()
        browser.insertHtml(curr_params['specification'])
        browser.moveCursor(QtGui.QTextCursor.Start)        
        hbox.addWidget(browser)
        vbox_description.addLayout(hbox)
        
        generic_widget_description = QtWidgets.QWidget()
        generic_widget_description.setLayout(vbox_description)
        tabwidget.addTab(generic_widget_description, "Description")
        
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(tabwidget)        

        ### Avoid shrinking all the diagrams ###
        #svg_widget.setMinimumHeight(svg_widget.height()) 

        ### Buttonbox for ok or cancel ###
        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonbox.accepted.connect(self.read)
        buttonbox.rejected.connect(self.reject)
        if _platform == "linux" or _platform == "linux2":
            buttonbox.layout().setDirection(QtWidgets.QBoxLayout.RightToLeft)

        layout.addWidget(buttonbox)
        self.setMinimumWidth(800)

    def read(self):
        load_definition_operators = self.parent.operators_widget.load_definition
        load_definition_technicians = self.parent.technicians_widget.load_definition

        # read contents of each widget
        # update settings in self.batchlocations[self.modified_batchlocation_number] of parent
        new_params = {}
        for i in self.strings:
            new_params[str(i.objectName())] = str(i.text())

        for i in self.integers:
            new_params[str(i.objectName())] = int(i.text())

        for i in self.doubles:
            new_params[str(i.objectName())] = float(i.text())
        
        self.batchlocations[self.modified_batchlocation_number][1].update(new_params)
        self.load_definition(False)

        # update other widgets in case name was changed
        load_definition_operators(False)
        load_definition_technicians(False)

        if self.row:
            parent = self.model.index(self.row, 0)
            self.view.setExpanded(parent, True) # expand locationgroup again
            index = self.model.index(self.index, 0, parent)            
            self.view.setCurrentIndex(index) # select tool again            
        
        self.statusbar.showMessage(self.tr("Tool settings updated"),3000)
        self.accept()