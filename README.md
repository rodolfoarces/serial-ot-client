# Serial OT client CLI

OT device emulator (client)

## Requirements

Uses the [MinimalModbus](https://minimalmodbus.readthedocs.io/en/stable/) python module, and `requests` for fowarding to API endpoints

`pip install minimalmodbus requests`

## Usage

```
usage: serial-client-ot.py [-h] [-c CONFIG] [-b BAUDRATE] [-i ID] [-j]
                           [-l {critical,error,warning,info,debug}] [-r] [-m MANAGER] [-U USERNAME]
                           [-W PASSWORD] [-o OUTPUT] [-P {N,E,O}] [-S STOP_BITS] [-B BYTE_SIZE] [-p PORT]
                           [-F {rtu,ascii}]

pymodbus synchronous serial server

options:
  -h, --help            show this help message and exit
  -c CONFIG, --config CONFIG
                        set config file name
  -b BAUDRATE, --baudrate BAUDRATE
                        set serial device baud rate
  -i ID, --id ID        set device ID number, default is 0 (any)
  -j, --json            set output in json format
  -l {critical,error,warning,info,debug}, --log-level {critical,error,warning,info,debug}
                        set log level, default is info
  -r, --remote          forward output to remote Wazuh Manager via API
  -m MANAGER, --manager MANAGER
                        Wazuh Manager Url, required for remote API
  -U USERNAME, --username USERNAME
                        Username, required for remote API
  -W PASSWORD, --password PASSWORD
                        Password, required for remote API
  -o OUTPUT, --output OUTPUT
                        set output file name
  -P {N,E,O}, --parity {N,E,O}
                        set parity of serial device, default is N (none)
  -S STOP_BITS, --stop-bits STOP_BITS
                        set number of stop bits for serial device, default is 1
  -B BYTE_SIZE, --byte-size BYTE_SIZE
                        set number of bytesize for serial device, default is 8
  -p PORT, --port PORT  set port or serial device. default is /dev/ttyS0
  -F {rtu,ascii}, --framer {rtu,ascii}
                        set framer type, default is RTU
```

## Example

`python3 serial-client-ot.py -l debug -b 9600 -i 1 -o out.log -P N -S 1 -B 8 -p /dev/ttyS0 -F rtu -r -c ./config.ini -j --manager https://10.1.2.20:55000 --username wazuh --password wazuh`

## Configration file

A configuration file can be used to store values for connection, logging and remote forwarding. The parameters set as command arguments take precedence and will be used instead of parameters on the configuration file. 

Example file [/config.ini](./config.ini).

Example usage: `python3 serial-client-ot.py -c config.ini`


