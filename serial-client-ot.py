#!/usr/bin/env python3
import sys
import argparse
import logging
import minimalmodbus

logger = logging.getLogger("serial-client-ot")

def setup_instrument(args):
    """Setup the minimalmodbus instrument."""
    global instrument
    logger
    instrument = minimalmodbus.Instrument(args.port, args.id)  # port name, slave address (in decimal)
    logger.debug(f"Instrument created on port {args.port} with id {args.id}")
    instrument.serial.baudrate = args.baudrate   # Baudrate
    logger.debug(f"Set baudrate to {args.baudrate}")
    instrument.serial.bytesize = args.byte_size     # Number of data bits
    logger.debug(f"Set byte size to {args.byte_size}")
    # Parity
    if args.parity == "N":
        instrument.serial.parity   = minimalmodbus.serial.PARITY_NONE
        logger.debug("Set parity to NONE")
    elif args.parity == "E":
        instrument.serial.parity   = minimalmodbus.serial.PARITY_EVEN
        logger.debug("Set parity to EVEN")
    elif args.parity == "O":
        instrument.serial.parity   = minimalmodbus.serial.PARITY_ODD
        logger.debug("Set parity to ODD")
    # Framer mode
    if args.framer == "rtu":
        instrument.mode = minimalmodbus.MODE_RTU
        logger.debug("Set framer mode to RTU")
    elif args.framer == "ascii":
        instrument.mode = minimalmodbus.MODE_ASCII
        logger.debug("Set framer mode to ASCII")

    instrument.serial.stopbits = args.stop_bits # Number of stop bits
    logger.debug(f"Set stop bits to {args.stop_bits}")


def main():
    parser = argparse.ArgumentParser(description="pymodbus synchronous serial server")
    parser.add_argument( "-l",  "--log-level", choices=["critical", "error", "warning", "info", "debug"], help="set log level, default is info", dest="log", default="info", type=str)
    parser.add_argument( "-b", "--baudrate", help="set serial device baud rate", default=9600, type=int )
    parser.add_argument( "-i", "--id", help="set number of device_id, default is 0 (any)", default=0, type=int)
    parser.add_argument( "-o", "--output", help="set output file name", default=None, type=str)
    parser.add_argument( "-P", "--parity", help="set parity of serial device, default is N (none)", choices=["N", "E", "O"], default="N", type=str)
    parser.add_argument( "-S", "--stop-bits", help="set number of stop bits for serial device, default is 1", default=1, type=int)
    parser.add_argument( "-B", "--byte-size", help="set number of bytesize for serial device, default is 8", default=8, type=int)
    parser.add_argument( "-p", "--port", help="set port or serial device. default is /dev/ttyS0",default="/dev/ttyS0", type=str, required=True)
    parser.add_argument( "-F", "--framer", choices=["rtu", "ascii"], help="set framer type, default is RTU", default="rtu", type=str )
    args = parser.parse_args()

    try:
        if args.help is not None:
            parser.print_help()
            sys.exit(0)
    except AttributeError as ex:
        pass

    # Setup logging to file or console
    if args.output is not None:
        # create console handler with a higher log level
        fh = logging.FileHandler(args.output, mode='a', encoding='utf-8')
    else:
        # create console handler with a higher log level
        fh = logging.StreamHandler()
    
    # create formatter and set it for the handler depending on log level
    if args.log.upper() == "INFO":
        fh_formatter = logging.Formatter('%(message)s')
    else:
        fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add the formatter to fh
    fh.setFormatter(fh_formatter)
    fh.setLevel(args.log.upper())

    logger.addHandler(fh)
    #pymodbus_apply_logging_config(args.log.upper())
    logger.setLevel(args.log.upper())
    logger.debug("Command line arguments: %s", args)    
    setup_instrument(args)
    temperature = instrument.read_register(3, 0)  # Registernumber, number of decimals
    print(temperature)



if __name__ == "__main__":
    main()