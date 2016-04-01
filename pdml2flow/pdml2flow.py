#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import time 
import sys
import json
import dict2xml
import argparse
import xml.sax
import functools
from .autovivification import AutoVivification
from .utils import autoconvert
from .conf import Conf

def debug(*objs):
    if Conf.DEBUG:
        print("[Debug: {}] ".format(Flow.newest_overall_frame_time), *objs, file=sys.stderr)

def warning(*objs):
    print("[Warning: {}] ".format(Flow.newest_overall_frame_time), *objs, file=sys.stderr)

class Flow():

    """ The overall packet time """
    newest_overall_frame_time = 0

    def __init__(self, first_frame):
        first_frame_time = first_frame['frame']['time_epoch']['raw'][0]
        self.__newest_frame_time = self.__first_frame_time = first_frame_time
        self.__id = self.get_flow_id(first_frame)
        if Conf.FRAMES_ARRAY:
            self.__frames = []
        else:
            self.__frames = AutoVivification()
        self.__framecount = 0
        self.add_frame(first_frame)

    def __repr__(self):
        # clean the frame data
        self.__frames = self.__frames.clean_empty()
        if Conf.XML_OUTPUT:
            return dict2xml.dict2xml(self.__dict__, wrap='flow')
        else:
            return json.dumps(self.__dict__)

    def __str__(self):
        return '{}'.format(self.__repr__())

    @staticmethod
    def get_flow_id(frame):
        flowid = [frame[d] for d in Conf.FLOW_DEF]
        valid = any([type(i) is not AutoVivification for i in flowid])
        # check if flowid is empty
        if not valid:
            return None
        return str(flowid)

    def add_frame(self, frame):
        # check if packet expands flow length
        frame_time = frame['frame']['time_epoch']['raw'][0]
        self.__first_frame_time = min(self.__first_frame_time, frame_time) 
        self.__newest_frame_time = max(self.__newest_frame_time, frame_time)
        self.__framecount += 1
        # Extract data
        if Conf.FRAMES_ARRAY:
            self.__frames.append(frame)
        else:
            self.__frames.merge(frame, compress_data=Conf.COMPRESS_DATA)
        # Print flow duration
        debug('flow duration: {}'.format(self.__newest_frame_time - self.__first_frame_time))

    def not_expired(self):
        return self.__newest_frame_time > (Flow.newest_overall_frame_time - Conf.FLOW_BUFFER_TIME)

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

def main():
    parser = argparse.ArgumentParser(description='Aggregates wireshark pdml to flows')
    parser.add_argument('-f',
                        default=Conf.FLOW_DEF_STR,
                        dest='FLOW_DEF_STR',
                        action='append',
                        help='Fields which define the flow, nesting with: \'{}\' [default: {}]'.format(Conf.FLOW_DEF_NESTCHAR, Conf.FLOW_DEF_STR)
                        )
    parser.add_argument('-t',
                        default=Conf.FLOW_BUFFER_TIME,
                        type=int,
                        dest='FLOW_BUFFER_TIME',
                        help='Lenght (in seconds) to buffer a flow before writing the packets [default: {}]'.format(Conf.FLOW_BUFFER_TIME)
                        )
    parser.add_argument('-l',
                        default=Conf.DATA_MAXLEN,
                        type=int,
                        dest='DATA_MAXLEN',
                        help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(Conf.DATA_MAXLEN)
                        )
    parser.add_argument('-s',
                        default=Conf.EXTRACT_SHOW,
                        dest='EXTRACT_SHOW',
                        action='store_true',
                        help='Extract show names, every data leave will now look like {{ raw : [] , show: [] }} [default: {}]'.format(Conf.EXTRACT_SHOW)
                        )
    parser.add_argument('-x',
                        default=Conf.XML_OUTPUT,
                        dest='XML_OUTPUT',
                        action='store_true',
                        help='Switch to xml output [default: {}]'.format(Conf.XML_OUTPUT)
                        )
    parser.add_argument('-c',
                        default=Conf.COMPRESS_DATA,
                        dest='COMPRESS_DATA',
                        action='store_true',
                        help='Removes duplicate data when merging objects, will not preserve order of leaves [default: {}]'.format(Conf.COMPRESS_DATA)
                        )
    parser.add_argument('-a',
                        default=Conf.FRAMES_ARRAY,
                        dest='FRAMES_ARRAY',
                        action='store_true',
                        help='Instaead of merging the frames will append them to an array [default: {}]'.format(Conf.FRAMES_ARRAY)
                        )
    parser.add_argument('-d',
                        default=Conf.DEBUG,
                        dest='DEBUG',
                        action='store_true',
                        help='Debug mode [default: {}]'.format(Conf.DEBUG)
                        )
    conf = vars(parser.parse_args())
    # split each flowdef to a path
    try:
        if(conf.FLOW_DEF_STR):
            conf.FLOW_DEF = Conf.get_real_paths(conf.FLOW_DEF_STR, Conf.FLOW_DEF_NESTCHAR)
    except AttributeError:
        pass
    # apply configuration
    Conf.set(conf)
    # create an XMLReader
    parser = xml.sax.make_parser()
    # turn off namepsaces
    parser.setFeature(xml.sax.handler.feature_namespaces, 0)
    # override the default ContextHandler
    handler = PdmlHandler()
    parser.setContentHandler(handler)
    try:
        parser.parse(sys.stdin)
    except xml.sax._exceptions.SAXParseException as e:
        # this might happen when a pdml file is malformed
        warning('Parser returned exception: {}'.format(e))
        handler.endDocument()

if ( __name__ == '__main__'):
    main()
