#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import time 
import sys
import json
import dict2xml
import argparse
import xml.sax
import functools

FLOW_DEF_NESTCHAR = '.'
FLOW_DEF=[
            'vlan{}id'.format(FLOW_DEF_NESTCHAR),
            'ip{}src'.format(FLOW_DEF_NESTCHAR),
            'ip{}dst'.format(FLOW_DEF_NESTCHAR),
            'ipv6{}src'.format(FLOW_DEF_NESTCHAR),
            'ipv6{}dst'.format(FLOW_DEF_NESTCHAR),
            'udp{}stream'.format(FLOW_DEF_NESTCHAR),
            'tcp{}stream'.format(FLOW_DEF_NESTCHAR),
]
DATA_MAXLEN = 200
DATA_TOO_LONG = 'Data too long'
PDML_NESTCHAR = '.'
FLOW_BUFFER_TIME = 180
EXTRACT_SHOW = False
STANDALONE = False
XML_OUTPUT = False
COMPRESS_DATA = False
FRAMES_ARRAY = False
DEBUG = False

parser = argparse.ArgumentParser(description='Aggregates wireshark pdml to flows')
parser.add_argument('-f',
                    default=FLOW_DEF,
                    dest='flowdef',
                    action='append',
                    help='Fields which define the flow, nesting with: {} [default: {}]'.format(FLOW_DEF_NESTCHAR, FLOW_DEF)
                    )
parser.add_argument('-t',
                    default=FLOW_BUFFER_TIME,
                    type=int,
                    dest='flow_buffer_time',
                    help='Lenght (in seconds) to buffer a flow before writing the packets [default: {}]'.format(FLOW_BUFFER_TIME)
                    )
parser.add_argument('-l',
                    default=DATA_MAXLEN,
                    type=int,
                    dest='data_maxlen',
                    help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(DATA_MAXLEN)
                    )
parser.add_argument('-s',
                    default=EXTRACT_SHOW,
                    dest='extract_show',
                    action='store_true',
                    help='Extract show names, every data leave will now look like {{ raw : [] , show: [] }} [default: {}]'.format(EXTRACT_SHOW)
                    )
parser.add_argument('-x',
                    default=XML_OUTPUT,
                    dest='xml',
                    action='store_true',
                    help='Switch to xml output [default: {}]'.format(XML_OUTPUT)
                    )
parser.add_argument('-c',
                    default=COMPRESS_DATA,
                    dest='compress_data',
                    action='store_true',
                    help='Removes duplicate data when merging objects, will not preserve order of leaves [default: {}]'.format(COMPRESS_DATA)
                    )
parser.add_argument('-a',
                    default=FRAMES_ARRAY,
                    dest='frames_array',
                    action='store_true',
                    help='Instaead of merging the frames will append them to an array [default: {}]'.format(FRAMES_ARRAY)
                    )
parser.add_argument('-d',
                    default=DEBUG,
                    dest='debug',
                    action='store_true',
                    help='Debug mode [default: {}]'.format(DEBUG)
                    )

class AutoVivification(dict):
    """
    Implementation of perl's autovivification feature.
    see: https://stackoverflow.com/questions/635483/what-is-the-best-way-to-implement-nested-dictionaries-in-python
    """
    def __getitem__(self, item):
        try:
            return dict.__getitem__(self, item)
        except KeyError:
            value = self[item] = type(self)()
            return value

# merges b into a recursively
# also merges lists and :
# * merge({a:a},{a:b}) = {a:[a,b]}
# * merge({a:[a]},{a:b}) = {a:[a,b]}
# * merge({a:a},{a:[b]}) = {a:[a,b]}
# * merge({a:[a]},{a:[b]}) = {a:[a,b]}
def merge(a, b, path=None):
    if path is None: path = []
    for key in b:
        if key in a:
            if isinstance(a[key], dict) and isinstance(b[key], dict):
                merge(a[key], b[key], path + [str(key)])
            else:
                if type(a[key]) is list and type(b[key]) is list:
                    a[key] += b[key]
                elif type(a[key]) is list and type(b[key]) is not list:
                    a[key] += [b[key]]
                elif type(a[key]) is not list and type(b[key]) is list:
                    a[key] = [a[key]] + b[key]
                elif type(a[key]) is not list and type(b[key]) is not list:
                    a[key] = [a[key]] + [b[key]]
                if args.compress_data:
                    # remove duplicates
                    a[key] = list(set(a[key]))
        else:
            a[key] = b[key]
    return a

def get_from_dict(dataDict, mapList):
    return functools.reduce(lambda d, k: d[k], mapList, dataDict)

def boolify(string):
    if string == 'True':
        return True
    if string == 'False':
        return False
    raise ValueError('Not a bool')

# Try to convert variables into datatypes
def autoconvert(string):
    for fn in (boolify, int, float):
        try:
            return fn(string)
        except ValueError:
            pass
    return string

def debug(*objs):
    if args.debug:
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
        if args.frames_array:
            self.__frames = []
        else:
            self.__frames = AutoVivification()
        self.__framecount = 0
        self.add_frame(first_frame)

    def __repr__(self):
        if args.xml:
            return dict2xml.dict2xml(self.__dict__, wrap='flow')
        else:
            return json.dumps(self.__dict__)

    def __str__(self):
        return '{}'.format(self.__repr__())

    @staticmethod
    def get_flow_id(frame):
        flowid = [get_from_dict(frame, d)['raw'] for d in args.flowdef]
        valid = any([ type(i) is not AutoVivification for i in flowid])
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
        if args.frames_array:
            self.__frames.append(frame)
        else:
            self.__frames = merge(self.__frames, frame)
        # Print flow duration
        debug('flow duration: {}'.format(self.__newest_frame_time - self.__first_frame_time))

    def not_expired(self):
        return self.__newest_frame_time > (Flow.newest_overall_frame_time - args.flow_buffer_time)

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
                        lambda x,y: x[y], [self.__frame] + name.split(PDML_NESTCHAR)
                    )
                    new = {
                        'raw': [],
                        'show': [],
                    }
                    # Extract raw data
                    if 'show' in attributes:
                        show = attributes.getValue('show')
                        if len(show) > args.data_maxlen:
                            show = DATA_TOO_LONG
                        new['raw'] += [autoconvert(show)]
                    # Extract showname
                    if 'showname' in attributes:
                        showname = attributes.getValue('showname')
                        if len(showname) > args.data_maxlen:
                            showname = DATA_TOO_LONG
                        new['show'] += [showname]
                    if not args.extract_show:
                        del new['show']
                    merge(name_access, new)

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
            print(flow)

def main():
    global args, parser
    args = parser.parse_args()
    # remove default flowdef if other flowdef was given
    if(len(FLOW_DEF) < len(args.flowdef)):
        args.flowdef = args.flowdef[len(FLOW_DEF):]
    # split each flowdef to a path
    args.flowdef = [ path.split(FLOW_DEF_NESTCHAR) for path in args.flowdef ]
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
