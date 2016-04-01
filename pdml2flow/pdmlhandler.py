#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import xml.sax
import functools

from .autovivification import AutoVivification
from .utils import autoconvert
from .conf import Conf
from .flow import Flow
from .logging import *

class PdmlHandler(xml.sax.ContentHandler):
    def __init__(self):
        self.__frame = {}
        self.__flows = {}

    # Call when an element starts
    def startElement(self, tag, attributes):
        if tag == 'packet':
            self.__frame = AutoVivification()
        else:
            if 'name' in  attributes:
                name = attributes.getValue('name')
                if len(name) > 0:
                    # Build object tree
                    name_access = functools.reduce(
                        lambda x,y: x[y], [self.__frame] + name.split(Conf.PDML_NESTCHAR)
                    )
                    new = {
                        'raw': [],
                        'show': [],
                    }
                    # Extract raw data
                    if 'show' in attributes:
                        show = attributes.getValue('show')
                        if len(show) > Conf.DATA_MAXLEN:
                            show = Conf.DATA_TOO_LONG
                        new['raw'] += [autoconvert(show)]
                    # Extract showname
                    if 'showname' in attributes:
                        showname = attributes.getValue('showname')
                        if len(showname) > Conf.DATA_MAXLEN:
                            showname = Conf.DATA_TOO_LONG
                        new['show'] += [showname]
                    if not Conf.EXTRACT_SHOW:
                        del new['show']
                    name_access.merge(new, compress_data=Conf.COMPRESS_DATA)

    # Call when an elements ends
    def endElement(self, tag):
        if tag == 'packet':
            # advance time
            Flow.newest_overall_frame_time = max(Flow.newest_overall_frame_time, self.__frame['frame']['time_epoch']['raw'][0])
            # write out expired flows
            new_flows = {}
            for (flowid, flow) in self.__flows.items():
                if flow.not_expired():
                    new_flows[flowid] = flow
                else:
                    print(flow)
            self.__flows = new_flows
            # the flow definition
            flowid = Flow.get_flow_id(self.__frame)
            # ignore frames without a flowid
            if flowid:
                try: 
                    flow = self.__flows[flowid]
                    self.__flows[flowid].add_frame(self.__frame)
                    debug('oldflow: {}'.format(flowid))
                except KeyError:
                    # flow unknown add new flow
                    self.__flows[flowid] = Flow(self.__frame)
                    debug('newflow: {}'.format(flowid))

    def endDocument(self):
        # print all flows @ end
        for (flowid, flow) in self.__flows.items():
            # before printing clean all empty laves
            print(flow)