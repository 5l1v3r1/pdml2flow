# pdml2flow [![PyPI version](https://badge.fury.io/py/pdml2flow.svg)](https://badge.fury.io/py/pdml2flow) 

When analyzing network traffic, we can either inspect each frame individually
or analyze groups of captured frames. Such groups of frames are called flows.
For example, grouping by port numbers gives us network flows. Network flows
are helpful if we want to analyze communication behavior between applications.
On the other hand if we group by MAC addresses, we obtain hardware flows. Those
are interesting for debugging switching and trunking.

Doing this in Wireshark or tshark is difficult. `pdml2flow` was designed to
solve this use case. `pdml2flow` reads `tshark` output using the Packet
Description Markup Language and writes flows either in JSON or XML. Using the
[`-f` option](https://github.com/Enteee/pdml2flow#usage), one can simply change
the flow definition. Furthermore, [plugins written in python](https://github.com/Enteee/pdml2flow#plugins)
do have access to the frames and flows and implement custom flow processing logic.
With [`pdml2flow-new-plugin`](https://github.com/Enteee/pdml2flow#create-a-new-plugin)
bootstrapping a new plugin is only a matter of seconds. If flow aggregation is
not needed, [`pdml2frame`](https://github.com/Enteee/pdml2flow#pdml2frame)
enables python powered frame processing.

| Branch  | Build  | Coverage |
| ------- | ------ | -------- |
| master  | [![Build Status master]](https://travis-ci.org/Enteee/pdml2flow) | [![Coverage Status master]](https://coveralls.io/github/Enteee/pdml2flow?branch=master) |
| develop  | [![Build Status develop]](https://travis-ci.org/Enteee/pdml2flow) | [![Coverage Status develop]](https://coveralls.io/github/Enteee/pdml2flow?branch=develop) |

## Prerequisites

* [python]:
  - 3.4
  - 3.5
  - 3.5-dev
  - 3.6
  - 3.6-dev
  - 3.7-dev
  - nightly
* [pip](https://pypi.python.org/pypi/pip)

## Installation

```shell
$ sudo pip install pdml2flow
```

## Usage

```shell
$ pdml2flow -h
usage: pdml2flow [-h] [--version] [-f FLOW_DEF_STR] [-t FLOW_BUFFER_TIME]
                 [-l DATA_MAXLEN] [-c] [-a] [-s] [-d] [+json [args]]
                 [+xml [args]]

Aggregates wireshark pdml to flows

optional arguments:
  -h, --help           show this help message and exit
  --version            Print version and exit
  -f FLOW_DEF_STR      Fields which define the flow, nesting with: '.'
                       [default: ['vlan.id', 'ip.src', 'ip.dst', 'ipv6.src',
                       'ipv6.dst', 'udp.stream', 'tcp.stream']]
  -t FLOW_BUFFER_TIME  Lenght (in seconds) to buffer a flow before writing the
                       packets [default: 180]
  -l DATA_MAXLEN       Maximum lenght of data in tshark pdml-field [default:
                       200]
  -c                   Removes duplicate data when merging objects, will not
                       preserve order of leaves [default: False]
  -a                   Instead of merging the frames will append them to an
                       array [default: False]
  -s                   Extract show names, every data leaf will now look like
                       { raw : [] , show: [] } [default: False]
  -d                   Debug mode [default: False]

Plugins:
  +json [args]         usage: JSON output [-h] [-0] optional arguments: -h,
                       --help show this help message and exit -0 Terminates
                       lines with null character
  +xml [args]          usage: XML output [-h] [-0] optional arguments: -h,
                       --help show this help message and exit -0 Terminates
                       lines with null character
```

### Environment Variables

| Name | Descripton |
| ---- | ---------- |
| LOAD_PLUGINS | If set to `False`, skips loading of all plugins |

## Examples

Sniff from interface and write json:
```shell
$ tshark -i interface -Tpdml | pdml2flow +json
```

Read a .pcap file
```shell
$ tshark -r pcap_file -Tpdml | pdml2flow +json
```

Aggregate based on ethernet source and ethernet destination address
```shell
$ tshark -i interface -Tpdml | pdml2flow -f eth.src -f eth.dst +json
```

Pretty print flows using [jq]
```shell
$ tshark -i interface -Tpdml | pdml2flow +json | jq
```

Post-process flows using [FluentFlow]
```shell
$ tshark -i interface -Tpdml | pdml2flow +json | fluentflow rules.js
```

## Plugins

* [elasticsearch](https://github.com/Enteee/pdml2flow-elasticsearch#readme): Saves pdml2flow output in Elasticsearch
* [base64-strings](https://github.com/Enteee/pdml2flow-base64strings#readme): Extract strings encoded in base64
* [frame-inter-arrival-time](https://github.com/Enteee/pdml2flow-frame-inter-arrival-time): Calculate frame inter arrival times
* [pdml2flow/plugins/](pdml2flow/plugins/): Plugins shipped by default

### Interface

```python
# vim: set fenc=utf8 ts=4 sw=4 et :

class Plugin2(object): # pragma: no cover
    """Version 2 plugin interface."""

    @staticmethod
    def help():
        """Return a help string."""
        pass

    def __init__(self, *args):
        """Called once during startup."""
        pass

    def __deinit__(self):
        """Called once during shutdown."""
        pass

    def flow_new(self, flow, frame):
        """Called every time a new flow is opened."""
        pass

    def flow_expired(self, flow):
        """Called every time a flow expired, before printing the flow."""
        pass

    def flow_end(self, flow):
        """Called every time a flow ends, before printing the flow."""
        pass

    def frame_new(self, frame, flow):
        """Called for every new frame."""
        pass
```

### Create a New Plugin

[![asciicast](https://asciinema.org/a/208963.png)](https://asciinema.org/a/208963)

## Utils

The following utils are part of this project

### pdml2frame
_Wireshark pdml to frames, with plugins_

```shell
$ pdml2frame -h
usage: pdml2frame [-h] [--version] [-s] [-d] [+json [args]] [+xml [args]]

Converts wireshark pdml to frames

optional arguments:
  -h, --help    show this help message and exit
  --version     Print version and exit
  -s            Extract show names, every data leaf will now look like { raw :
                [] , show: [] } [default: False]
  -d            Debug mode [default: False]

Plugins:
  +json [args]  usage: JSON output [-h] [-0] optional arguments: -h, --help
                show this help message and exit -0 Terminates lines with null
                character
  +xml [args]   usage: XML output [-h] [-0] optional arguments: -h, --help
                show this help message and exit -0 Terminates lines with null
                character
```

## Testing

* [Test documentation](test/README.md)

running the tests:

```shell
$ python setup.py test
```

## Similar Software

* `tshark -T json`: Out of the box frame as JSON output. Use this in conjunction
with a JSON stream parser to replicate the functionality of `pdml2frame`.
* [PyShark](https://kiminewt.github.io/pyshark/): Python wrapper for tshark, allowing
python packet parsing using wireshark dissectors. An excellent tool for packet
processing in python. Does not support flow aggregation out of the box.
* [dpkt](https://dpkt.readthedocs.io/en/latest/): A python module for fast, simple
packet creation and parsing, with definitions for the basic TCP/IP protocols. Does
not support all protocols implemented in wireshark.
* [Scapy](https://scapy.net/): Packet crafting/parsing in python. Focuses on packet
crafting.

[python]: https://www.python.org/
[wireshark]: https://www.wireshark.org/
[tshark]: https://www.wireshark.org/docs/man-pages/tshark.html
[dict2xml]: https://github.com/delfick/python-dict2xml
[jq]: https://stedolan.github.io/jq/
[FluentFlow]: https://github.com/t-moe/FluentFlow
[pdml]: https://wiki.wireshark.org/PDML

[Build Status master]: https://travis-ci.org/Enteee/pdml2flow.svg?branch=master
[Coverage Status master]: https://coveralls.io/repos/github/Enteee/pdml2flow/badge.svg?branch=master
[Build Status develop]: https://travis-ci.org/Enteee/pdml2flow.svg?branch=develop
[Coverage Status develop]: https://coveralls.io/repos/github/Enteee/pdml2flow/badge.svg?branch=develop
