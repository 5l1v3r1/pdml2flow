#!/bin/bash
TOPLEVEL=$(git rev-parse --show-toplevel)

cat <<EOF > "${TOPLEVEL}/README.md"
# pdml2flow
_Aggregates wireshark pdml to flows_

## Prerequisites
* [python] version 3

## Installation
    $ sudo python setup.py install

## Usage
\`\`\`shell
$ pdml2flow -h
$(${TOPLEVEL}/pdml2flow.py -h)
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
$(${TOPLEVEL}/pdml2json.py -h)
\`\`\`

### pdml2xml
_Converts pdml to xml_

### Usage
\`\`\`shell
$ pdml2xml -h
$(${TOPLEVEL}/pdml2xml.py -h)
\`\`\`

[python]: https://www.python.org/
[wireshark]: https://www.wireshark.org/
[dict2xml]: https://github.com/delfick/python-dict2xml
[jq]: https://stedolan.github.io/jq/
[FluentFlow]: https://github.com/t-moe/FluentFlow
EOF
