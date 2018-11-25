#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
import xml.sax
import imp

from os import path
from shutil import copytree, ignore_patterns
from pkg_resources import resource_filename
from configparser import ConfigParser

from .logging import *
from .conf import Conf
from .plugin import *
from .pdmlhandler import PdmlHandler

def _add_common_arguments(argparser):
    argparser.add_argument(
        '-s',
        dest='EXTRACT_SHOW',
        action='store_true',
        help='Extract show names, every data leaf will now look like {{ raw : [] , show: [] }} [default: {}]'.format(
            Conf.EXTRACT_SHOW
        )
    )
    argparser.add_argument(
        '-d',
        dest='DEBUG',
        action='store_true',
        help='Debug mode [default: {}]'.format(
            Conf.DEBUG
        )
    )

def pdml2flow():

    def add_arguments_cb(argparser):
        argparser.add_argument(
            '-f',
            dest='FLOW_DEF_STR',
            action='append',
            help='Fields which define the flow, nesting with: \'{}\' [default: {}]'.format(
                Conf.FLOW_DEF_NESTCHAR, Conf.FLOW_DEF_STR
            )
        )
        argparser.add_argument(
            '-t',
            type=int,
            dest='FLOW_BUFFER_TIME',
            help='Lenght (in seconds) to buffer a flow before writing the packets [default: {}]'.format(
                Conf.FLOW_BUFFER_TIME
            )
        )
        argparser.add_argument(
            '-l',
            type=int,
            dest='DATA_MAXLEN',
            help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(
                Conf.DATA_MAXLEN
            )
        )
        argparser.add_argument(
            '-c',
            dest='COMPRESS_DATA',
            action='store_true',
            help='Removes duplicate data when merging objects, will not preserve order of leaves [default: {}]'.format(
                Conf.COMPRESS_DATA
            )
        )
        argparser.add_argument(
            '-a',
            dest='FRAMES_ARRAY',
            action='store_true',
            help='Instead of merging the frames will append them to an array [default: {}]'.format(
                Conf.FRAMES_ARRAY
            )
        )
        _add_common_arguments(argparser)

    def postprocess_conf_cb(conf):
        """Split each flowdef to a path."""
        if conf['FLOW_DEF_STR'] is not None:
            conf['FLOW_DEF'] = Conf.get_real_paths(
                conf['FLOW_DEF_STR'],
                Conf.FLOW_DEF_NESTCHAR
        )

    Conf.load(
        'Aggregates wireshark pdml to flows',
        add_arguments_cb,
        postprocess_conf_cb
    )

    start_parser()

def pdml2frame():

    def add_arguments_cb(argparser):
        _add_common_arguments(argparser)

    def postprocess_conf_cb(conf):
        conf['DATA_MAXLEN'] = sys.maxsize
        conf['FLOW_BUFFER_TIME'] = 0
        conf['FLOW_DEF_STR'] = [ 'frame.number' ]
        conf['FLOW_DEF'] = Conf.get_real_paths(
            conf['FLOW_DEF_STR'],
            Conf.FLOW_DEF_NESTCHAR
        )

    Conf.load(
        'Converts wireshark pdml to frames',
        add_arguments_cb,
        postprocess_conf_cb
    )

    start_parser()

def start_parser():

    # print config
    for name, value in Conf.get().items():
        debug('{} : {}'.format(name, value))

    handler = PdmlHandler()
    try:
        xml.sax.parse(
            Conf.IN,
            handler
        )
    except xml.sax._exceptions.SAXParseException as e:
        # this might happen when a pdml file is malformed
        warning('Parser returned exception: {}'.format(e))
        handler.endDocument()

def pdml2flow_new_plugin():

    def add_arguments_cb(argparser):
        argparser.add_argument(
            'DST',
            type=str,
            nargs='+',
            help='Where to initialize the plugin, basename will become the plugin name'
        )

    Conf.load(
        'Initializes a new plugin',
        add_arguments_cb
    )

    for dst in Conf.DST:
        plugin_name = path.basename(dst)
        plugin_conf = ConfigParser({
            'plugin_name': plugin_name
        })
        copytree(
            resource_filename(__name__, '/plugin-skeleton'),
            dst,
            ignore=ignore_patterns('__pycache__')
        )
        with open(path.join(dst, Conf.PLUGIN_CONF_NAME), mode='w') as fd:
            plugin_conf.write(fd)
