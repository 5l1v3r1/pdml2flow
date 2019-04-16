#!/usr/bin/env bash
set -exuo pipefail

TOPLEVEL="$( cd "$(dirname "$0")" ; pwd -P )/../"

# install pdml2flow
pip install --upgrade -e "${TOPLEVEL}"

cat <<EOF > "${TOPLEVEL}/README.md"
# pdml2flow [![PyPI version](https://badge.fury.io/py/pdml2flow.svg)](https://badge.fury.io/py/pdml2flow) 
_Aggregates wireshark pdml to flows, with plugins_

When analyzing network traffic, it is sometimes helpful to group captured frames. For example by port numbers to obtain network flows or using MAC addresses for hardware flows. Doing this in [Wireshark][wireshark] or [tshark] is difficult. \`pdml2flow\` was designed to solve this use case. \`pdml2flow\` reads [tshark] output using the [Packet Description Markup Language][pdml] and writes flows either in JSON or XML. These flows are also accessible from a python plugin interface. If flow aggregation is not needed, \`pdml2frame\` can be be used to process [pdml] with plugins.

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

* [Elasticsearch](https://github.com/Enteee/pdml2flow-elasticsearch#readme)
* [base64-strings](https://github.com/Enteee/pdml2flow-base64strings#readme)
* see [pdml2flow/plugins/](pdml2flow/plugins/) for a full list of supported plugins

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
