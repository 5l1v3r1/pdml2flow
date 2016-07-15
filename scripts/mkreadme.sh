#!/bin/bash
TOPLEVEL=$(git rev-parse --show-toplevel)

# install pdml2flow
sudo pip install -e "${TOPLEVEL}"

cat <<EOF > "${TOPLEVEL}/README.md"
# pdml2flow [![PyPI version](https://badge.fury.io/py/pdml2flow.svg)](https://badge.fury.io/py/pdml2flow) 
_Aggregates wireshark pdml to flows_

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
$(pdml2flow -h)
\`\`\`

## Example
Sniff from interface:
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow
\`\`\`

Write xml output
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow -x
\`\`\`

Read a .pcap file
\`\`\`shell
$ tshark -r pcap_file -Tpdml | pdml2flow
\`\`\`

Aggregate based on ethernet source and ethernet destination address
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow -f eth.src -f eth.dst
\`\`\`

Pretty print flows using [jq]
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow | jq
\`\`\`

Post-process flows using [FluentFlow]
\`\`\`shell
$ tshark -i interface -Tpdml | pdml2flow | fluentflow rules.js
\`\`\`

## Utils

The following utils are part of this project

### pdml2json
_Converts pdml to json_

### Usage
\`\`\`shell
$ pdml2json -h
$(pdml2json -h)
\`\`\`

### pdml2xml
_Converts pdml to xml_

### Usage
\`\`\`shell
$ pdml2xml -h
$(pdml2xml -h)
\`\`\`

[python]: https://www.python.org/
[wireshark]: https://www.wireshark.org/
[dict2xml]: https://github.com/delfick/python-dict2xml
[jq]: https://stedolan.github.io/jq/
[FluentFlow]: https://github.com/t-moe/FluentFlow

[Build Status master]: https://travis-ci.org/Enteee/pdml2flow.svg?branch=master
[Coverage Status master]: https://coveralls.io/repos/github/Enteee/pdml2flow/badge.svg?branch=master
[Build Status develop]: https://travis-ci.org/Enteee/pdml2flow.svg?branch=develop
[Coverage Status develop]: https://coveralls.io/repos/github/Enteee/pdml2flow/badge.svg?branch=develop
EOF
