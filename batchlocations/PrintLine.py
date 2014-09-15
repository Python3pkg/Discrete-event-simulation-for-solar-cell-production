# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:59:54 2014

@author: rnaber

TODO
Add IV measurement automation

"""

from __future__ import division
from PyQt4 import QtCore
from batchlocations.BatchContainer import BatchContainer
#import simpyx as simpy
import simpy
import numpy as np

class PrintLine(QtCore.QObject):
        
    def __init__(self, _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output
        
        self.params = {}
        self.params['specification'] = self.tr("PrintLine consists of:\n")
        self.params['specification'] += self.tr("- Input container\n")
        self.params['specification'] += self.tr("- A number of print and dry stations\n")
        self.params['specification'] += self.tr("- A firing furnace\n")
        self.params['specification'] += self.tr("- Output container\n")
        self.params['specification'] += "\n"
        self.params['specification'] += self.tr("The machine accepts cassettes which are unloaded one unit at a time. ")
        self.params['specification'] += self.tr("Each wafer then travels to a number of printers and dryers, ")
        self.params['specification'] += self.tr("before entering a firing furnace. ")
        self.params['specification'] += self.tr("Units are finally placed in an infinitely sized container.")
        self.params['name'] = ""
        self.params['name_desc'] = self.tr("Name of the individual batch location")
        self.params['cassette_size'] = 100
        self.params['cassette_size_desc'] = self.tr("Number of units in a single cassette")
        self.params['max_cassette_no'] = 4
        self.params['max_cassette_no_desc'] = self.tr("Number of cassette positions at input")
        self.params['units_on_belt_input'] = 8
        self.params['units_on_belt_input_desc'] = self.tr("Number of units that fit on the belt between wafer source and printer")
        self.params['time_step'] = 1
        self.params['time_step_desc'] = self.tr("Time for one unit to progress one position (seconds)")
        self.params['time_cassette_to_belt'] = 1
        self.params['time_cassette_to_belt_desc'] = self.tr("Time for placing one unit onto the first belt (seconds)")
        self.params['time_print'] = 2
        self.params['time_print_desc'] = self.tr("Time to print one wafer (seconds)")
        self.params['time_dry'] = 90
        self.params['time_dry_desc'] = self.tr("Time  for one wafer to go from printer to dryer and ")
        self.params['time_dry_desc'] += self.tr("to next input (printing or firing) (seconds)")
        self.params['no_print_steps'] = 3
        self.params['no_print_steps_desc'] = self.tr("Number of print and dry stations")
        self.params['firing_tool_length'] = 7.0
        self.params['firing_tool_length_desc'] = self.tr("Distance between firing furnace input and output (meters)")
        self.params['firing_belt_speed'] = 5.0 # 5 is roughly 200 ipm
        self.params['firing_belt_speed_desc'] = self.tr("Speed at which all units travel (meters per minute)")
        self.params['firing_unit_distance'] = 0.2
        self.params['firing_unit_distance_desc'] = self.tr("Minimal distance between wafers (meters)")
        self.params['verbose'] = False
        self.params['verbose_desc'] = self.tr("Enable to get updates on various functions within the tool")
        self.params.update(_params)
        
        if (self.params['verbose']):               
            string = str(self.env.now) + " - [PrintLine][" + self.params['name'] + "] Added a print line"
            self.output_text.sig.emit(string)

        self.input = BatchContainer(self.env,"input",self.params['cassette_size'],self.params['max_cassette_no'])
        self.output = InfiniteContainer(self.env,"output")

        self.start_time = self.env.now
        self.idle_times = {}
        for i in np.arange(self.params['no_print_steps']+1): # plus one for the firing furnace
            self.idle_times[i] = 0

        self.next_step = {} # trigger events
        self.belts = {} # belts preceeding printers
        self.inputs = {} # cassette-like input before belts

        for i in np.arange(self.params['no_print_steps']):
            self.next_step[i] = self.env.event()
            self.belts[i] = BatchContainer(self.env,"belt_input",self.params['units_on_belt_input'],1)
            self.inputs[i] = BatchContainer(self.env,"input",self.params['cassette_size'],1) # buffer inside printer line            
            self.env.process(self.run_belt(i))
            self.env.process(self.run_printer(i))

        self.firing_input = BatchContainer(self.env,"firing_input",1,1)
        self.env.process(self.run_firing_furnace())

    def report(self):
        string = "[PrintLine][" + self.params['name'] + "] Units processed: " + str(self.output.container.level)
        self.output_text.sig.emit(string)
        
        if (self.params['verbose']):
            for i in self.idle_times:
                idle_time = 100*self.idle_times[i]/(self.env.now-self.start_time)
                string = "[PrintLine][" + self.params['name'] + "][part" + str(i) + "] Idle time: " + str(np.round(idle_time,1)) + " %"
                self.output_text.sig.emit(string)

    def run_belt(self, num):        
        while True:
            yield self.next_step[num]
                        
            if (num):
                yield self.inputs[num].container.get(1)
            else:                
                yield self.input.container.get(1)
                
            yield self.env.timeout(self.params['time_cassette_to_belt']) 
            yield self.belts[num].container.put(1)
            
            if (self.params['verbose']):
                string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Put wafer on printer belt " + str(num)
                self.output_text.sig.emit(string)
            
    def run_printer(self, num):        
        while True:
            if (not num):
                input_check = (self.input.container.level > 0)
            else:
                input_check = (self.inputs[num].container.level > 0)
            
            if (self.belts[num].space_available(1)) & (input_check):
                yield self.next_step[num].succeed()
                self.next_step[num] = self.env.event() # make new event

            if (not self.belts[num].space_available(1)) | ((not input_check) & (self.belts[num].container.level > 0)):
                # if belt is fully loaded print one
                # else if input is empty but still wafers present on belt, continue printing until empty
                yield self.belts[num].container.get(1)
                yield self.env.timeout(self.params['time_print'])
                
                if (self.params['verbose']):
                    string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Printed a wafer on printer " + str(num)
                    self.output_text.sig.emit(string)
                self.env.process(self.run_wafer_instance_drying(num))
            else:
                # if not printing, delay for time needed to load one wafer
                yield self.env.timeout(self.params['time_step'])
                self.idle_times[num] += self.params['time_step']

    def run_wafer_instance_drying(self, num):        
        yield self.env.timeout(self.params['time_dry'])
        
        if (self.params['verbose']):
            string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Dried a wafer on dryer " + str(num)
            self.output_text.sig.emit(string)
        
        if (num+1 < self.params['no_print_steps']):
            # go to next printer
            yield self.inputs[num+1].container.put(1)
        else:
            # go to firing furnace
            yield self.firing_input.container.put(1)            

    def run_firing_furnace(self):
        while True:        
            if (self.firing_input.container.level):
                yield self.firing_input.container.get(1)
                self.env.process(self.run_wafer_instance_firing())
                yield self.env.timeout(60*self.params['firing_unit_distance']/self.params['firing_belt_speed']) # same lane cannot accept new unit until after x seconds
            else:
                yield self.env.timeout(1) # check every second for new wafers
                self.idle_times[len(self.idle_times)-1] += 1
            
    def run_wafer_instance_firing(self):
        yield self.env.timeout(60*self.params['firing_tool_length']/self.params['firing_belt_speed'])        
        yield self.output.container.put(1)
        
        if (self.params['verbose']):
            string = str(self.env.now) + " [PrintLine][" + self.params['name'] + "] Fired a wafer"
            self.output_text.sig.emit(string)

class InfiniteContainer(object):
    
    def __init__(self, env, name=""):        
        self.env = env
        self.name = name
        self.container = simpy.Container(self.env,init=0)