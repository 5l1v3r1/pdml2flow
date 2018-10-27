#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
import xml.sax
import imp
import inspect

from os import path
from pkg_resources import iter_entry_points, resource_filename
from shutil import copytree
from shlex import split
from base64 import b32encode, b32decode

from argparse import ArgumentParser

from .logging import *
from .conf import Conf
from .plugin import *
from .pdmlhandler import PdmlHandler

def pdml2flow():

    # initialize argument parsing
    parser = ArgumentParser(
        description='Aggregates wireshark pdml to flows',
        prefix_chars='-+'
    )

    # set up plugin argument parser
    plugin_parser = parser.add_argument_group('Plugins')

    # load plugins
    plugins = {}
    plugin_parsers = []
    for entry_point in iter_entry_points(group=Conf.PLUGIN_GROUP):
        name = str(entry_point).split(' =',1)[0]
        plugin = entry_point.load()
        if inspect.isclass(plugin) \
            and not plugin in Conf.SUPPORTED_PLUGIN_INTERFACES \
            and any([
                issubclass(plugin, supported_plugin_interface)
                for supported_plugin_interface in Conf.SUPPORTED_PLUGIN_INTERFACES
            ]):

            plugin.arguments(plugin_parser)
            plugin_parser.add_argument(
                '+{}'.format(name),
                dest='PLUGIN_{}'.format(name),
                type=str,
                nargs='?',
                metavar='args'.format(name),
                help=plugin.help()
            )

            # register plugin
            plugins[name] = plugin
        else:
            warning('Plugin not supported: {}'.format(name))

    parser.add_argument(
        '-f',
        dest='FLOW_DEF_STR',
        action='append',
        help='Fields which define the flow, nesting with: \'{}\' [default: {}]'.format(
            Conf.FLOW_DEF_NESTCHAR, Conf.FLOW_DEF_STR
        )
    )
    parser.add_argument(
        '-t',
        type=int,
        dest='FLOW_BUFFER_TIME',
        help='Lenght (in seconds) to buffer a flow before writing the packets [default: {}]'.format(
            Conf.FLOW_BUFFER_TIME
        )
    )
    parser.add_argument(
        '-l',
        type=int,
        dest='DATA_MAXLEN',
        help='Maximum lenght of data in tshark pdml-field [default: {}]'.format(
            Conf.DATA_MAXLEN
        )
    )
    parser.add_argument(
        '-s',
        dest='EXTRACT_SHOW',
        action='store_true',
        help='Extract show names, every data leaf will now look like {{ raw : [] , show: [] }} [default: {}]'.format(
            Conf.EXTRACT_SHOW
        )
    )
    parser.add_argument(
        '-x',
        dest='XML_OUTPUT',
        action='store_true',
        help='Switch to xml output [default: {}]'.format(
            Conf.XML_OUTPUT
        )
    )
    parser.add_argument(
        '-c',
        dest='COMPRESS_DATA',
        action='store_true',
        help='Removes duplicate data when merging objects, will not preserve order of leaves [default: {}]'.format(
            Conf.COMPRESS_DATA
        )
    )
    parser.add_argument(
        '-a',
        dest='FRAMES_ARRAY',
        action='store_true',
        help='Instead of merging the frames will append them to an array [default: {}]'.format(
            Conf.FRAMES_ARRAY
        )
    )
    parser.add_argument(
        '-m',
        dest='METADATA',
        action='store_true',
        help='Appends flow metadata [default: {}]'.format(
            Conf.METADATA
        )
    )
    parser.add_argument(
        '-d',
        dest='DEBUG',
        action='store_true',
        help='Debug mode [default: {}]'.format(
            Conf.DEBUG
        )
    )
    parser.add_argument(
        '-0',
        dest='PRINT_0',
        action='store_true',
        help='Terminates lines with null character [default: {}]'.format(
            Conf.PRINT_0
        )
    )

    # Encode the next argument after +plugin
    # to ensure that it does not start with a
    # prefix_char
    conf = vars(
        parser.parse_args([
            v if i == 0 or v[0] == '+' or Conf.ARGS[i-1][0] != '+'
            else b32encode(v.encode()).decode()
            for i, v in enumerate(Conf.ARGS)
        ])
    )

    # split each flowdef to a path
    if conf['FLOW_DEF_STR'] is not None:
        conf['FLOW_DEF'] = Conf.get_real_paths(
            conf['FLOW_DEF_STR'],
            Conf.FLOW_DEF_NESTCHAR
        )

    # load plugins
    conf['PLUGINS'] = []
    for conf_name, args in conf.items():
        if conf_name.startswith('PLUGIN_'):
            plugin_name = conf_name[7:]
            conf['PLUGINS'].append(
                # instantiate plugin
                plugins[plugin_name](
                    *split(
                        b32decode(args.encode()).decode() if args is not None else ''
                    )
                )
            )

    # start parsing
    start_parser(conf)

def pdml2xml():
    Conf.XML_OUTPUT = True
    pdml2frame('xml')

def pdml2json():
    pdml2frame('json')

def pdml2frame(output_type):
    parser = ArgumentParser(
        description='Converts wireshark pdml to {}'.format(
            output_type
        )
    )
    Conf.DATA_MAXLEN = sys.maxsize
    Conf.FLOW_BUFFER_TIME = 0
    Conf.FLOW_DEF_STR = [ 'frame.number' ]
    Conf.FLOW_DEF = Conf.get_real_paths(
        Conf.FLOW_DEF_STR,
        Conf.FLOW_DEF_NESTCHAR
    )
    parser.add_argument(
        '-s',
        dest='EXTRACT_SHOW',
        action='store_true',
        help='Extract show names, every data leaf will now look like {{ raw : [] , show: [] }} [default: {}]'.format(
            Conf.EXTRACT_SHOW
        )
    )
    parser.add_argument(
        '-d',
        dest='DEBUG',
        action='store_true',
        help='Debug mode [default: {}]'.format(
            Conf.DEBUG
        )
    )
    conf = vars(
        parser.parse_args(Conf.ARGS)
    )
    start_parser(conf)

def start_parser(conf = {}):
    # apply configuration
    Conf.set(conf)
    # print config
    for name, value in Conf.get().items():
        debug('{} : {}'.format(name, value))
    try:
        xml.sax.parse(Conf.IN, PdmlHandler())
    except xml.sax._exceptions.SAXParseException as e:
        # this might happen when a pdml file is malformed
        warning('Parser returned exception: {}'.format(e))
        handler.endDocument()

def pdml2flow_new_plugin():
    parser = ArgumentParser(
        description='Initializes a new plugin'
    )
    parser.add_argument(
        'dst',
        type=str,
        nargs='+',
        help='Where to initialize the plugin, basename will become the plugin name'
    )
    conf = vars(parser.parse_args(Conf.ARGS))
    for dst in conf['dst']:
        plugin_name = path.basename(dst)
        copytree(
            resource_filename(__name__, '/plugin-skeleton'),
            dst
        )
