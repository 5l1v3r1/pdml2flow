#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
import argparse
import xml.sax

from .conf import Conf
from .pdmlhandler import PdmlHandler

def pdml2flow():
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
    parser.add_argument('-m',
                        default=Conf.METADATA,
                        dest='METADATA',
                        action='store_true',
                        help='Appends flow metadata [default: {}]'.format(Conf.METADATA)
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
    start_parser(conf)

def pdml2xml():
    Conf.XML_OUTPUT = True
    pdml2frame()

def pdml2json():
    pdml2frame()

def pdml2frame():
    parser = argparse.ArgumentParser(description='Converts wireshark pdml to json')
    Conf.DATA_MAXLEN = sys.maxsize
    Conf.FLOW_BUFFER_TIME = 0
    Conf.FLOW_DEF_STR = [ 'frame.number' ]
    Conf.FLOW_DEF = Conf.get_real_paths(Conf.FLOW_DEF_STR, Conf.FLOW_DEF_NESTCHAR)
    parser.add_argument('-s',
                        default=Conf.EXTRACT_SHOW,
                        dest='EXTRACT_SHOW',
                        action='store_true',
                        help='Extract show names, every data leave will now look like {{ raw : [] , show: [] }} [default: {}]'.format(Conf.EXTRACT_SHOW)
                        )
    parser.add_argument('-c',
                        default=Conf.COMPRESS_DATA,
                        dest='COMPRESS_DATA',
                        action='store_true',
                        help='Removes duplicate data when merging objects, will not preserve order of leaves [default: {}]'.format(Conf.COMPRESS_DATA)
                        )
    parser.add_argument('-d',
                        default=Conf.DEBUG,
                        dest='DEBUG',
                        action='store_true',
                        help='Debug mode [default: {}]'.format(Conf.DEBUG)
                        )
    conf = vars(parser.parse_args())
    start_parser(conf)

def start_parser(conf):
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

