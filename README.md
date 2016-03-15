# pdml2flow
_Aggregates wireshark pdml to flows_

## Prerequisites
* [python] version 3

## Installation
    sudo python setup.py install

## Usage
    $ pdml2flow.py -h
    usage: pdml2flow.py [-h] [-f FLOWDEF] [-t FLOW_BUFFER_TIME] [-l DATA_MAXLEN]
                    [-s] [-d]
    
    Aggregates wireshark pdml to flows
    
    optional arguments:
      -h, --help           show this help message and exit
      -f FLOWDEF           Fields which define the flow, nesting with: . [default:
                           ['vlan.id', 'ip.src', 'ip.dst', 'ipv6.src', 'ipv6.dst',
                           'udp.stream', 'tcp.stream']]
      -t FLOW_BUFFER_TIME  Lenght (in seconds) to buffer a flow before writing the
                           packets [default: 3]
      -l DATA_MAXLEN       Maximum lenght of data in tshark pdml-field [default:
                           200]
      -s                   Extract show names, every data leave will now look like
                           { raw : [] , show: [] } [default: False]
      -x                   Switch to xml output [default: False]
      -d                   Debug mode [default: False]

## Example
Sniff from interface:

    $ tshark -i interface -Tpdml | pdml2flow.py

Write xml output

    $ tshark -i interface -Tpdml | pdml2flow.py -x

Read a .pcap file

    $ tshark -r pcap_file -Tpdml | pdml2flow.py

Aggregate based on ethernet source and ethernet destination address

    $ tshark -i interface -Tpdml | pdml2flow.py -f eth.src -f eth.dst

Pretty print flows using jq

    $ tshark -i interface -Tpdml | pdml2flow.py | jq

[python]: https://www.python.org/
[wireshark]: https://www.wireshark.org/
[dict2xml]: https://github.com/delfick/python-dict2xml
