# -*- coding: utf-8 -*-
"""
Created on Sun Aug 17 14:56:30 2014

@author: rnaber
"""

from __future__ import division
from batchlocations.BatchProcess import BatchProcess
from batchlocations.BatchContainer import BatchContainer

class BatchTransport(object):
    # For simple one-way transports

    def __init__(self, env, batchconnections, name="", batch_size=1, verbose=False):
        self.env = env
        self.batch_size = batch_size
        self.batchconnections = batchconnections
        self.name = name
        self.verbose = verbose
        self.transport_counter = 0
        self.wait_time = 60 # simulation runs much faster with higher values!!!
        
        if (self.verbose):
            print str(self.env.now) + " - [BatchTransport]" + self.name + " Added simple transporter"
            
        self.env.process(self.run())
    
    def run(self):
        while True:
            for i in self.batchconnections:
                if isinstance(self.batchconnections[i][0],BatchContainer):
                    # load-in from BatchContainer to BatchProcess
                    if (self.batchconnections[i][0].container.level >= self.batch_size) & \
                            self.batchconnections[i][1].space_available(self.batch_size):
                                                  
                        with self.batchconnections[i][1].resource.request() as request_output:
                            yield request_output
                        
                            yield self.batchconnections[i][0].container.get(self.batch_size)
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += self.batch_size
                            yield self.batchconnections[i][1].container.put(self.batch_size)
                            self.batchconnections[i][1].start_process()
                            
                            if (self.verbose):
                                print str(self.env.now) + " [BatchTransport]" + self.name + " Transport from " + \
                                    self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended"                            

                elif isinstance(self.batchconnections[i][1],BatchContainer):
                    # load-out into BatchContainer to BatchProcess
                    if (self.batchconnections[i][0].container.level >= self.batch_size) & \
                            self.batchconnections[i][1].space_available(self.batch_size) & \
                            self.batchconnections[i][0].process_finished:

                        with self.batchconnections[i][0].resource.request() as request_input:
                            yield request_input
                        
                            yield self.batchconnections[i][0].container.get(self.batch_size)
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += self.batch_size
                            yield self.batchconnections[i][1].container.put(self.batch_size)
                            self.batchconnections[i][0].process_finished = 0
                            
                            if (self.verbose):
                                print str(self.env.now) + " [BatchTransport]" + self.name + " Transport from " + \
                                    self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended"                            
                                
                elif (isinstance(self.batchconnections[i][0],BatchProcess)) & \
                        (isinstance(self.batchconnections[i][1],BatchProcess)):
                    # transport from BatchProcess to BatchProcess
                    # only call if you're sure in- and output are BatchProcess
                    if (self.batchconnections[i][0].container.level >= self.batch_size) & \
                            self.batchconnections[i][1].space_available(self.batch_size) & \
                            self.batchconnections[i][0].process_finished:                           
                        #parentheses are crucial
                    
                        with self.batchconnections[i][0].resource.request() as request_input, \
                            self.batchconnections[i][1].resource.request() as request_output:
                            yield request_input                                    
                            yield request_output
                            
                            yield self.batchconnections[i][0].container.get(self.batch_size)
                            yield self.env.timeout(self.batchconnections[i][2])
                            self.transport_counter += self.batch_size                            
                            yield self.batchconnections[i][1].container.put(self.batch_size)                        

                            self.batchconnections[i][0].process_finished = 0                    
                            self.batchconnections[i][1].start_process()
                            
                            if (self.verbose):
                                print str(self.env.now) + " [BatchTransport]" + self.name + " Transport from " + \
                                    self.batchconnections[i][0].name + " to " + self.batchconnections[i][1].name + " ended"
                    
            yield self.env.timeout(self.wait_time)
            
            