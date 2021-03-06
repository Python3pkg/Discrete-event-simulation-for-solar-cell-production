# -*- coding: utf-8 -*-
from PyQt5 import QtCore
import simpy
         
class BatchProcess(QtCore.QObject):
    
    def __init__(self,  _env, _output=None, _params = {}):
        QtCore.QObject.__init__(self)
        self.env = _env
        self.output_text = _output       

        self.params = {}
        self.params['name'] = ""
        self.params['type'] = "BatchProcess"        
        self.params['batch_size'] = 1
        self.params['process_time'] = 1
        self.params['downtime_runs'] = 0
        self.params['downtime_time'] = 0
        self.params['downtime_duration'] = 0
        self.params.update(_params)        
        
        self.name = self.params['name']
        self.resource = simpy.Resource(self.env, 1)
        self.process_finished = 0
        self.start_time = self.env.now
        self.process_time_counter = 0
        self.start = self.env.event()
        self.first_run = True
        self.process_counter = 0
        self.last_downtime = 0
        self.status = 1 # up or down
#        self.container = simpy.Container(self.env,capacity=self.params['batch_size'],init=0)
        self.store = simpy.Store(self.env,self.params['batch_size'])
            
        self.env.process(self.run())
        
        if self.params['downtime_time']: 
            self.env.process(self.uptime_counter())

    def run(self):
        batch_size = self.params['batch_size']
        process_time = self.params['process_time']
        
        while True:
            yield self.start
            
            if self.first_run:
                self.start_time = self.env.now
                self.first_run = False
                
#            if (self.container.level >= batch_size) & (not self.process_finished):
            if (len(self.store.items) == batch_size) & (not self.process_finished):
                with self.resource.request() as request:
                    yield request
                    yield self.env.timeout(process_time) 
                    self.process_finished = 1
                    self.process_counter += 1
                    self.process_time_counter += process_time
                    
#                    string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] End process " #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG
            
    def space_available(self,_batch_size):
        # see if space is available for the specified _batch_size
#        if ((self.container.level+_batch_size) <= self.params['batch_size']):
        if ((len(self.store.items)+_batch_size) <= self.params['batch_size']):            
            return True
        else:
            return False

    def start_process(self):
        self.start.succeed()
        self.start = self.env.event() # make new event

    def check_downtime(self): # will be called by BatchTransport
        if self.params['downtime_runs']:
            # see if downtime period is needed 
            if (self.process_counter >= self.params['downtime_runs']):
                self.env.process(self.downtime_cycle())

    def uptime_counter(self):
        # check repeatedly whether time limit has been reached
        downtime_time = self.params['downtime_time']
        downtime_duration = self.params['downtime_duration']
    
        while True:
            yield self.env.timeout(1)
            
#            if ((self.env.now - self.last_downtime) >= downtime_time) & (not self.container.level):
            if ((self.env.now - self.last_downtime) >= downtime_time) & (not len(self.store.items)):                
                # perform a downtime cycle at time limit and when empty
                    
                with self.resource.request() as request:
                    yield request
                    self.status = 0                   
                    yield self.env.timeout(downtime_duration)
                    self.status = 1
                    self.process_counter = 0
                    self.last_downtime = self.env.now

#                    string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] End downtime " #DEBUG
#                    self.output_text.sig.emit(string) #DEBUG

    def downtime_cycle(self):
        # perform downtime cycle
        with self.resource.request() as request:
            yield request
            self.status = 0                   
            yield self.env.timeout(self.params['downtime_duration'])
            self.status = 1
            self.process_counter = 0
            self.last_downtime = self.env.now

#            string = str(self.env.now) + " [" + self.params['type'] + "][" + self.params['name'] + "] End downtime " #DEBUG
#            self.output_text.sig.emit(string) #DEBUG
        
    def idle_time(self):
        if (self.env.now-self.start_time):
            return 100-(100*self.process_time_counter/(self.env.now-self.start_time))
        else:
            return 0