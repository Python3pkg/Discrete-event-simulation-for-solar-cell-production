# -*- coding: utf-8 -*-
"""
Created on Mon Aug 18 13:55:53 2014

@author: rnaber

TODO
Output put action should yield to two things: put and timer
If time_limit is reached because there is no output space available, destroy wafer?

"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
import numpy as np

class SingleSideEtch(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        
        self.params = {}
        self.params['specification'] = self.tr("SingleSideEtch consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- A number of process lanes\n")
        self.params['specification'] += self.tr("- Output container\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("Each lane runs independently and continuously, ")
        self.params['specification'] += self.tr("but can only accept a new unit after a certain time interval. ")
        self.params['specification'] += self.tr("Because it runs continuously ")
        self.params['specification'] += self.tr("(independent of whether there is an output position available or not) ")
        self.params['specification'] += self.tr("the output automation cannot function as a master of the input.\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("There are several of types of automation. ")
        self.params['specification'] += self.tr("Assumed now is that each lane is fed separately with new wafers, ")
        self.params['specification'] += self.tr("with no interruption between cassettes (i.e. cassettes stacked on top of each other).\n")

        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['no_of_lanes'] = 5
        self.params['no_of_lanes_desc'] = self.tr("Number of process lanes")
        self.params['tool_length'] = 10
        self.params['tool_length_desc'] = self.tr("Distance between input and output (meters)")
        self.params['belt_speed'] = 1.8
        self.params['belt_speed_desc'] = self.tr("Speed at which all units travel (meters per minute)")
        self.params['unit_distance'] = 0.2
        self.params['unit_distance_desc'] = self.tr("Minimal distance between wafers (meters)")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 8
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input and the same number at output")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)         
        
        self.transport_counter = 0
        self.start_time = self.env.now
        
        if (self.params['verbose']):
            string = str(self.env.now) + " - [SingleSideEtch][" + self.params['name'] + "] Added a single side etch"
            self.output_text.sig.emit(string)
        
        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])                  
        self.output = BatchContainer(self.env,"output",self.params['cassette_size'],self.params['max_cassette_no'])
        
        self.idle_times = {}
        for i in np.arange(self.params['no_of_lanes']):
            self.env.process(self.run_one_lane(i))
            self.idle_times[i] = 0

    def report(self):
        string = "[SingleSideEtch][" + self.params['name'] + "] Units processed: " + str(self.transport_counter - self.output.container.level)
        self.output_text.sig.emit(string)
        
        if (self.params['verbose']):
            for i in self.idle_times:
                idle_time = 100*self.idle_times[i]/(self.env.now-self.start_time)
                string = "[SingleSideEtch][" + self.params['name'] + "][lane" + str(i) + "] Idle time: " + str(np.round(idle_time,1)) + " %"
                self.output_text.sig.emit(string)

    def run_one_lane(self, lane_number):       
        while True:
            if (self.input.container.level > 0):
                yield self.input.container.get(1)
                self.env.process(self.run_wafer_instance(lane_number))
                yield self.env.timeout(60*self.params['unit_distance']/self.params['belt_speed']) # same lane cannot accept new unit until after x seconds
            else:                
                yield self.env.timeout(1)
                self.idle_times[lane_number] += 1
                
    def run_wafer_instance(self, lane_number):
        yield self.env.timeout(60*self.params['tool_length']/self.params['belt_speed'])
        yield self.output.container.put(1) 
        self.transport_counter += 1
        
        if (self.params['verbose']) & ((self.transport_counter % self.params['cassette_size']) == 0):            
            string = str(np.around(self.env.now)) + " [SingleSideEtch][" + self.params['name'] + "] Processed " + str(self.params['cassette_size']) + " units"
            self.output_text.sig.emit(string)