#!/usr/bin/env python3
# vim: set fenc=utf8 ts=4 sw=4 et :
import sys
from os import path
from shlex import split
from base64 import b32encode, b32decode
from pkg_resources import require, DistributionNotFound
from argparse import ArgumentParser
from pkg_resources import iter_entry_points, resource_filename
from inspect import isclass

from .plugin import Plugin2

DEFAULT = object()

class Conf():
    """The global configuration class"""

    @staticmethod
    def get_real_paths(paths, nestchar):
        return [ path.split(nestchar) + ['raw'] for path in paths ]

    @staticmethod
    def get_version():
        try:
            return require('pdml2flow')[0].version
        except DistributionNotFound:
            return 'development'

    VERSION = get_version.__func__()

    ARGS = sys.argv[1:]
    IN = sys.stdin
    OUT = sys.stdout
    OUT_DEBUG = sys.stderr
    OUT_WARNING = sys.stderr
    OUT_ERROR = sys.stderr

    FLOW_DEF_NESTCHAR = '.'
    FLOW_DEF_STR = [
                'vlan{}id'.format(FLOW_DEF_NESTCHAR),
                'ip{}src'.format(FLOW_DEF_NESTCHAR),
                'ip{}dst'.format(FLOW_DEF_NESTCHAR),
                'ipv6{}src'.format(FLOW_DEF_NESTCHAR),
                'ipv6{}dst'.format(FLOW_DEF_NESTCHAR),
                'udp{}stream'.format(FLOW_DEF_NESTCHAR),
                'tcp{}stream'.format(FLOW_DEF_NESTCHAR),
    ]
    FLOW_DEF = get_real_paths.__func__(FLOW_DEF_STR, FLOW_DEF_NESTCHAR)
    DATA_MAXLEN = 200
    DATA_TOO_LONG = 'Data too long'
    PDML_NESTCHAR = '.'
    FLOW_BUFFER_TIME = 180
    EXTRACT_SHOW = False
    STANDALONE = False
    COMPRESS_DATA = False
    FRAMES_ARRAY = False
    FRAME_TIME = ['frame', 'time_epoch', 'raw', 0]
    DEBUG = False
    METADATA = False
    PARSE_SOURCE = sys.stdin
    SUPPORTED_PLUGIN_INTERFACES = [Plugin2]
    PLUGINS = []
    PLUGIN_GROUP = 'pdml2flow.plugins'
    PLUGIN_CONF_NAME = 'conf.ini'

    @staticmethod
    def set(conf):
        """Applies a configuration to the global config object"""
        for name, value in conf.items():
            if value is not None:
                setattr(Conf, name.upper(), value)

    @staticmethod
    def get():
        """Gets the configuration as a dict"""
        return {
            attr: getattr(Conf, attr)
            for attr in dir(Conf()) if not callable(getattr(Conf, attr)) and not attr.startswith("__")
        }

    @staticmethod
    def load(description, add_arguments_cb=lambda x: None, postprocess_conf_cb=lambda x: None):
        """Loads the global Conf object from command line arguments.

        Encode the next argument after +plugin to ensure that
        it does not start with a prefix_char
        """

        argparser = ArgumentParser(
            description=description,
            prefix_chars='-+'
        )

        argparser.add_argument(
            '--version',
            dest='PRINT_VERSION',
            action='store_true',
            help='Print version and exit'
        )

        # set up plugin argument argparser
        plugin_argparser = argparser.add_argument_group('Plugins')

        plugins = {}
        for entry_point in iter_entry_points(group=Conf.PLUGIN_GROUP):
            name = str(entry_point).split(' =',1)[0]
            plugin = entry_point.load()
            if isclass(plugin) \
                and not plugin in Conf.SUPPORTED_PLUGIN_INTERFACES \
                and any([
                    issubclass(plugin, supported_plugin_interface)
                    for supported_plugin_interface in Conf.SUPPORTED_PLUGIN_INTERFACES
                ]):

                plugin_argparser.add_argument(
                    '+{}'.format(name),
                    dest='PLUGIN_{}'.format(name),
                    type=str,
                    nargs='?',
                    default = DEFAULT,
                    metavar='args'.format(name),
                    help=plugin.help()
                )

                # register plugin
                plugins[name] = plugin
            else:
                warning('Plugin not supported: {}'.format(name))

        add_arguments_cb(argparser)

        conf = vars(
            argparser.parse_args([
                v if i == 0 or v[0] == '+' or Conf.ARGS[i-1][0] != '+'
                else b32encode(v.encode()).decode()
                for i, v in enumerate(Conf.ARGS)
            ])
        )

        postprocess_conf_cb(conf)

        # apply configuration
        Conf.set(conf)

        if Conf.PRINT_VERSION:
            print(
                'pdml2flow version {}'.format(
                    Conf.VERSION
                ),
                file=Conf.OUT
            )
            sys.exit(0)

        # initialize plugins
        Conf.PLUGINS = []
        for conf_name, args in conf.items():
            if conf_name.startswith('PLUGIN_') and args != DEFAULT:
                plugin_name = conf_name[7:]
                Conf.PLUGINS.append(
                    # instantiate plugin
                    plugins[plugin_name](
                        *split(
                            b32decode(args.encode()).decode() if args is not None else ''
                        )
                    )
                )

