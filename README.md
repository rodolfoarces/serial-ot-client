# Serial OT client CLI

OT device emulator (client)

## Requirements

Uses the [MinimalModbus](https://minimalmodbus.readthedocs.io/en/stable/) python module

`pip install minimalmodbus`

## Usage

```
usage: serial-client-ot.py [-h] [-l {critical,error,warning,info,debug}] [-b BAUDRATE] [-i ID] [-o OUTPUT] [-j] [-P {N,E,O}] [-S STOP_BITS] [-B BYTE_SIZE] -p
                           PORT [-F {rtu,ascii}]

pymodbus synchronous serial server

options:
  -h, --help            show this help message and exit
  -l {critical,error,warning,info,debug}, --log-level {critical,error,warning,info,debug}
                        set log level, default is info
  -b BAUDRATE, --baudrate BAUDRATE
                        set serial device baud rate
  -i ID, --id ID        set number of device_id, default is 0 (any)
  -o OUTPUT, --output OUTPUT
                        set output file name
  -j, --json            set output in json format
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

`python3 serial-client-ot.py -l debug -b 9600 -i 1 -o out.log -P N -S 1 -B 8 -p /dev/ttyS1 -F rtu`
