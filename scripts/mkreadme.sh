#!/usr/bin/env bash
set -exuo pipefail

TOPLEVEL="$( cd "$(dirname "$0")" ; pwd -P )/../"

# install pdml2flow
pip install --upgrade -e "${TOPLEVEL}"

cat <<EOF > "${TOPLEVEL}/README.md"
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
_Aggregates wireshark pdml to flows, with plugins_

| Branch  | Build  | Coverage |
| ------- | ------ | -------- |
| master  | [![Build Status master]](https://travis-ci.org/Enteee/pdml2flow) | [![Coverage Status master]](https://coveralls.io/github/Enteee/pdml2flow?branch=master) |
| develop  | [![Build Status develop]](https://travis-ci.org/Enteee/pdml2flow) | [![Coverage Status develop]](https://coveralls.io/github/Enteee/pdml2flow?branch=develop) |

## Prerequisites

$( cat "${TOPLEVEL}/.travis.yml" | 
    sed -n -e '/# VERSION START/,/# VERSION END/ p' |
    sed -e '1d;$d' |
    tr -d \'\"  |
    sed -e 's/\s*-\(.*\)/  -\1/g' |
    sed -e 's/python/\* [python\]/g'
)
* [pip](https://pypi.python.org/pypi/pip)

## Installation

\`\`\`shell
$ sudo pip install pdml2flow
\`\`\`

## Usage

\`\`\`shell
$ pdml2flow -h
$(LOAD_PLUGINS=False pdml2flow -h)
\`\`\`

### Environment Variables

| Name | Descripton |
| ---- | ---------- |
| LOAD_PLUGINS | If set to \`False\`, skips loading of all plugins |

## Examples

Sniff from interface and write json:
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow +json
\`\`\`

Read a .pcap file
\`\`\`shell
$ tshark -r pcap_file -Tpdml | pdml2flow +json
\`\`\`

Aggregate based on ethernet source and ethernet destination address
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow -f eth.src -f eth.dst +json
\`\`\`

Pretty print flows using [jq]
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow +json | jq
\`\`\`

Post-process flows using [FluentFlow]
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow +json | fluentflow rules.js
\`\`\`

## Plugins

* [elasticsearch](https://github.com/Enteee/pdml2flow-elasticsearch#readme): Saves pdml2flow output in Elasticsearch
* [base64-strings](https://github.com/Enteee/pdml2flow-base64strings#readme): Extract strings encoded in base64
* [frame-inter-arrival-time](https://github.com/Enteee/pdml2flow-frame-inter-arrival-time): Calculate frame inter arrival times
* [pdml2flow/plugins/](pdml2flow/plugins/): Plugins shipped by default

### Interface

\`\`\`python
$(cat "${TOPLEVEL}/pdml2flow/plugin.py")
\`\`\`

### Create a New Plugin

[![asciicast](https://asciinema.org/a/208963.png)](https://asciinema.org/a/208963)

## Utils

The following utils are part of this project

### pdml2frame
_Wireshark pdml to frames, with plugins_

\`\`\`shell
$ pdml2frame -h
$(LOAD_PLUGINS=False pdml2frame -h)
\`\`\`

## Testing

* [Test documentation](test/README.md)

running the tests:

\`\`\`shell
$ python setup.py test
\`\`\`

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
EOF
