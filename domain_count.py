#!/usr/bin/python
'''
Created on Oct 21, 2016

@author: Rohan Achar
'''

import logging
import logging.handlers
import os
import sys
import argparse
import uuid

sys.path.append(os.path.realpath(os.path.join(os.path.dirname(__file__), "../..")))

from spacetime_local.frame import frame

logger = None
from datamodel.search.datamodel import DomainCount
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Getter

logger = logging.getLogger(__name__)
LOG_HEADER = "[DOMAINCOUNT]"


@Getter(DomainCount)
class DomainCounter(IApplication):

    def __init__(self, frame):
        self.frame = frame
        
    def initialize(self):
        for dc in self.frame.get(DomainCount):
            print dc.__groupby__, dc.link_count
        self.done = True

    def update(self):
        pass
        
    def shutdown(self):
        pass


class Simulation(object):
    '''
    classdocs
    '''
    def __init__(self, address, port):
        '''
        Constructor
        '''
        frame_c = frame(address = "http://" + address + ":" + str(port) + "/", time_step = 1000)
        frame_c.attach_app(DomainCounter(frame_c))

        frame_c.run()


if __name__== "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--address', type=str, help='Address of the distributing server')
    parser.add_argument('-p', '--port', type=int, help='Port used by the distributing server')
    args = parser.parse_args()
    sim = Simulation(args.address, args.port)
