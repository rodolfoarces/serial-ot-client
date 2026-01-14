#!/usr/bin/env python3
"""
Pymodbus serial client Example.
Based on https://minimalmodbus.readthedocs.io/en/stable/usage.html
"""

import logging
import sys
import argparse
import logging
import minimalmodbus
import configparser
import requests
import json
import time
from datetime import datetime


requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

logger = logging.getLogger("serial-client-ot")

token = None

def setup_instrument(args):
    """Setup the minimalmodbus instrument."""
    global instrument
    logger
    try:
        logger.debug("Setting up instrument with provided parameters.")
        instrument = minimalmodbus.Instrument(args.port, args.id)  # port name, slave address (in decimal)
    except Exception as ex:
        logger.debug(f"Error during instrument setup: {ex}")
        print_error (0, "Setup", "Error during instrument setup", args)
        sys.exit(1)
    except SerialException as serial_ex:
        print_error (0, "Setup", "Error during instrument setup", args)
        sys.exit(1)

    
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

def validate_config(args, config):
    """Validate the configuration parameters."""
    # Serial connection settings
    if config.has_section('connection'):
        logger.debug("'connection' section found.")
        if args.port is None:
            logger.debug("Serial port provided in command line, skipping config file setting.")
            if config.has_option('connection', 'port'):
                args.port = config.get('connection', 'port')
                logger.debug(f"Port set to {args.port} from config file.")
            else:
                logger.debug("No port setting found in config file.")
                args.port = '/dev/ttyS0'
        if args.baudrate is None:
            logger.debug("Baudrate provided in command line, skipping config file setting.")
            if config.has_option('connection', 'baudrate'):
                args.baudrate = config.getint('connection', 'baudrate')
                logger.debug(f"Baudrate set to {args.baudrate} from config file.")
            else:
                logger.debug("No baudrate setting found in config file.")
                args.baudrate = 9600
        if args.id is None:
            logger.debug("Device ID provided in command line, skipping config file setting.")        
            if config.has_option('connection', 'id'):
                args.id = config.getint('connection', 'id')
                logger.debug(f"Device ID set to {args.id} from config file.")
            else:
                logger.debug("No device ID setting found in config file.")
                args.id = 0
        if args.parity is None:
            logger.debug("Parity provided in command line, skipping config file setting.")
            if config.has_option('connection', 'parity'):
                args.parity = config.get('connection', 'parity').upper()
                logger.debug(f"Parity set to {args.parity} from config file.")
            else:
                logger.debug("No parity setting found in config file.")
                args.parity = 'N'
        if args.stop_bits is None:
            logger.debug("Stop bits provided in command line, skipping config file setting.")
            if config.has_option('connection', 'stop_bits'):
                args.stop_bits = config.getint('connection', 'stop_bits')
                logger.debug(f"Stop bits set to {args.stop_bits} from config file.")
            else:
                logger.debug("No stop bits setting found in config file.")
                args.stop_bits = 1
        if args.byte_size is None:
            logger.debug("Byte size provided in command line, skipping config file setting.")
            if config.has_option('connection', 'byte_size'):
                args.byte_size = config.getint('connection', 'byte_size')
                logger.debug(f"Byte size set to {args.byte_size} from config file.")
            else:
                logger.debug("No byte size setting found in config file.")
                args.byte_size = 8
        if args.framer is None:
            logger.debug("Framer provided in command line, skipping config file setting.")
            if config.has_option('connection', 'framer'):
                args.framer = config.get('connection', 'framer').lower()
                logger.debug(f"Framer set to {args.framer} from config file.")
            else:
                logger.debug("No framer setting found in config file.")
                args.framer = 'rtu'
    else:
        logger.debug("'connection' section not found.")
    # Remote forwarding settings
    if args.remote is not None:
        if config.has_section('remote'):
            logger.debug("'remote' section found.")
            if args.manager is None:
                logger.debug("Manager URL provided in command line, skipping config file setting.")
                if config.has_option('remote', 'manager'):
                    args.manager = config.get('remote', 'manager')
                    logger.debug(f"Manager set to {args.manager} from config file.")
                else:
                    logger.debug("No manager setting found in config file.")
                    args.manager = "http://localhost:55000"
            if args.username is None:
                logger.debug("Username provided in command line, skipping config file setting.")
                if config.has_option('remote', 'username'):
                    args.username = config.get('remote', 'username')
                    logger.debug(f"Username set to {args.username} from config file.")
                else:
                    logger.debug("No username setting found in config file.")
                    args.username = "wazuh"
            if args.password is None:
                logger.debug("Password provided in command line, skipping config file setting.")
                if config.has_option('remote', 'password'):
                    args.password = config.get('remote', 'password')
                    logger.debug(f"Password set to *** from config file.")
                else:
                    logger.debug("No password setting found in config file.")
                    args.password = "wazuh"
    else:
        logger.debug("'remote' section not found.")

def api_authentication(auth_manager,auth_username, auth_password, args=None):
    """Authenticate to the API and return the token."""
    if auth_manager is None or auth_username is None or auth_password is None or args is None:
        logger.error("Authentication parameters missing")
        print_error(2, "Authentication", "Authentication parameters missing", args)
        sys.exit(5)
        return None
    auth_endpoint = auth_manager + "/security/user/authenticate"
    logger.debug("Starting authentication process")
    # api-endpoint
    try:
        auth_request = requests.get(auth_endpoint, auth=(auth_username, auth_password), verify=False)
    except Exception as ex:
        logger.error(f"Error connecting to authentication endpoint: {ex}")
        print_error(3, "Connection", "Could not connect to authentication endpoint", args)
        sys.exit(3)
        return None
    
    r = auth_request.content.decode("utf-8")
    auth_response = json.loads(r)
    try:
        return auth_response["data"]["token"]
    except KeyError:
        # "title": "Unauthorized", "detail": "Invalid credentials"
        if auth_response["title"] == "Unauthorized":
            logger.error("Authentication error")
            print_error(4, "Authentication", "Authentication error", args)
            sys.exit(4)
            return None
    except Exception as ex:
        logger.error(f"Unknown error during authentication: {ex}")
        print_error (5, "Unknown", "Unknow error during authentication", args)
        return None
    
def print_message(device_id, address, value, value_type, args=None, format_json=False, remote=False):
    """Print the message in the desired format or forward to remote host."""
    current_iso_time = datetime.now().isoformat()
    if format_json or args.json:
        message = json.dumps({ "datetime": current_iso_time, "device_id": device_id, "status": "Success", "address": address, "value": value})
    else:
        message = f"{current_iso_time} - serial-client-ot - id: {device_id} status: success address: {address} value: {value_type(value)}"

    if remote or args.remote is not None:
        logger.debug(f"Forwarding message to remote host: {message}")
        # API authentication
        # Set token
        token = api_authentication(args.manager, args.username, args.password, args)
        if token is None:
            logger.error("Authentication failed, cannot forward logs")
            logger.debug("Exiting program")
            sys.exit(2)
        # API processing
        msg_headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + token}
        msg_data = { "events": [ message ]}
        logger.debug(json.dumps(msg_data))
        msg_url = f"{args.manager}/events?wait_for_complete=true"
        try:
            forward_request = requests.post(msg_url, json=msg_data, headers=msg_headers, verify=False)
            r = json.loads(forward_request.content.decode('utf-8'))
            # Check 
            if forward_request.status_code != 200:
                    logger.error("There were errors sending the logs")
                    print_error(6, "Connection", "Errors sending logs to endpoint", args)
                    logger.debug(json.dumps(r))
            else:
                logger.debug(json.dumps(r))
        except Exception as ex:
            logger.error(f"Error connecting to authentication endpoint: {ex}")
            print_error(7, "Connection", "Could not connect to event endpoint", args)
            sys.exit(3)
        time.sleep(2)
    else:
        print(message)

def print_error(error_code=int(0),status="Error",message="Unknown error", args=None):
    current_iso_time = datetime.now().isoformat()
    if args is not None:
        if args.json is not None:
            error_message = { "datetime": current_iso_time, "error_code": error_code, "error_status": status, "error_message": message}
        else:
            error_message = f"{current_iso_time} - serial-client-ot - error_code: {error_code} error_status: {status} error_message: {message}"
    else:
        error_message = f"{current_iso_time} - serial-client-ot - error_code: {error_code} error_status: {status} error_message: {message}"
    
    if args.remote is not None:
        logger.debug(f"Forwarding message to remote host: {error_message}")
        # API authentication
        # Set token
        token = api_authentication(args.manager, args.username, args.password, args)
        if token is None:
            logger.error("Authentication failed, cannot forward logs")
            logger.debug("Exiting program")
            sys.exit(2)
        # API processing
        msg_headers = {"Content-Type": "application/json; charset=utf-8", "Authorization": "Bearer " + token}
        msg_data = { "events": [ error_message ]}
        logger.debug(json.dumps(msg_data))
        msg_url = f"{args.manager}/events?wait_for_complete=true"
        try:
            forward_request = requests.post(msg_url, json=msg_data, headers=msg_headers, verify=False)
            r = json.loads(forward_request.content.decode('utf-8'))
            # Check 
            if forward_request.status_code != 200:
                    logger.error("There were errors sending the logs")
                    print(6, "Connection", "Errors sending logs to endpoint", args)
                    logger.debug(json.dumps(r))
            else:
                logger.debug(json.dumps(r))
        except Exception as ex:
            logger.error(f"Error connecting to authentication endpoint: {ex}")
            print(7, "Connection", "Could not connect to event endpoint", args)
            sys.exit(3)
        time.sleep(2)
    else:
        print(error_message)        

def main():
    parser = argparse.ArgumentParser(description="pymodbus synchronous serial server")
    parser.add_argument( "-c", "--config", help="set config file name", default=None, type=str)
    parser.add_argument( "-b", "--baudrate", help="set serial device baud rate", type=int )
    parser.add_argument( "-i", "--id", help="set device ID number, default is 0 (any)", type=int)
    parser.add_argument( "-j", "--json", help="set output in json format", default=None, action="store_true")
    parser.add_argument( "-l", "--log-level", choices=["critical", "error", "warning", "info", "debug"], help="set log level, default is info", type=str)
    parser.add_argument( "-r", "--remote", help="forward output to remote Wazuh Manager via API", action="store_true", default=None)
    parser.add_argument( "-m", "--manager", help = "Wazuh Manager Url, required for remote API", action="store", type=str )
    parser.add_argument( "-U", "--username", help = "Username, required for remote API", action="store", type=str )
    parser.add_argument( "-W", "--password", help = "Password, required for remote API", action="store", type=str )
    parser.add_argument( "-o", "--output", help="set output file name", default=None, type=str)
    parser.add_argument( "-P", "--parity", help="set parity of serial device, default is N (none)", choices=["N", "E", "O"], type=str)
    parser.add_argument( "-S", "--stop-bits", help="set number of stop bits for serial device, default is 1", type=int)
    parser.add_argument( "-B", "--byte-size", help="set number of bytesize for serial device, default is 8", type=int)
    parser.add_argument( "-p", "--port", help="set port or serial device. default is /dev/ttyS0", type=str)
    parser.add_argument( "-F", "--framer", choices=["rtu", "ascii"], help="set framer type, default is RTU", type=str )
    args = parser.parse_args()

    # Logging command parameters override config file settings
    logger.debug("Final command line arguments after processing config file and overrides: %s", args)

    # Setup logging to file or console
    if args.output is not None:
        # create console handler with a higher log level
        fh = logging.FileHandler(args.output, mode='a', encoding='utf-8')
    else:
        # create console handler with a higher log level
        fh = logging.StreamHandler()
    
    # create formatter and set it for the handler depending on log level
    if args.log_level is not None:
        if args.log_level.upper() == "INFO":
            fh_formatter = logging.Formatter('%(message)s')
        else:
            fh_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    else:
        fh_formatter = logging.Formatter('%(message)s')
    # Add the formatter to fh
    fh.setFormatter(fh_formatter)
    if args.log_level is not None:
        fh.setLevel(args.log_level.upper())
    else:
        fh.setLevel("INFO")
    
    logger.addHandler(fh)
    #pymodbus_apply_logging_config(args.log.upper())
    logger.setLevel(fh.level)

    # Log the final arguments
    logger.debug("Command line arguments: %s", args)

    if args.config is not None:

        logger.debug(f"Reading configuration file {args.config}")
        config = configparser.ConfigParser()
        config.read(args.config)
        
        if args.output is not None:
            logger.debug("Log output provided in command line, skipping config file setting.")  
        # Logging settings
        if config.has_section('logging'):
            logger.debug("'logging' section found.")
            if args.log_level is not None:
                logger.debug("Log level provided in command line, skipping config file setting.")
            else:
                if config.has_option('logging', 'level'):
                    args.log_level = config.get('logging', 'level').upper()
                    logger.debug(f"Log level set to {args.log_level} from config file.")
            if config.has_option('logging', 'output'):
                args.output = config.get('logging', 'file')
                logger.debug(f"Log output set to {args.output} from config file.")
        else:
            logger.debug("'logging' section not found.")

    try:
        if args.help is not None:
            parser.print_help()
            sys.exit(0)
    except AttributeError as ex:
        pass

    validate_config(args, config)

    # Setup the instrument connection
    setup_instrument(args)
    
    
    #########################################
    ## Example: Read temperature from register 3
    #########################################
    ## Read information from the instrument
    try:
        logger.debug("Reading temperature from register 3")
        temperature = instrument.read_register(3, 0)  # Register number, number of decimals
        ## Print the result
        print_message(device_id=args.id, address=3, value=temperature, value_type=int, format_json=args.json, args=args)
    except Exception as ex:
        logger.debug(f"Error reading from instrument: {ex}")
        print_error(1, "Connection", "Could not read values from instrument", args)
        sys.exit(1)
    
    

if __name__ == "__main__":
    main()