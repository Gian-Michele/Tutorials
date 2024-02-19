import os
import time
import socket
import threading
import configparser
import argparse
from Automated_Test_Script import incoming, read_attenuation, set_new_attenuation

parser = argparse.ArgumentParser()
parser.add_argument('-i', help="Index (starting from 1) of the attenuator on the base of the config.ini file",
                    dest="idx")
parser.add_argument('-a', help="attenuation value", dest="att", required=False)
args = parser.parse_args()
idx = int(args.idx)
if args.att is not None:
    set_new_value = True
    attenuation_val = int(args.att)
else:
    set_new_value = False

# Import Test Information
config = configparser.ConfigParser()
fp_config = open('config.ini')
config.read_file(fp_config)
fp_config.close()

attenuator_ip_list = config.get('ATTENUATOR', 'ip_address').replace(" ", "").split(',')

attenuator_number = idx   # supported value is 1 or 2

# connect to 1st Attenuator System
att_session = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
att_session.connect((attenuator_ip_list[attenuator_number-1], 3001))
att_session.setblocking(False)

# receive responses and process
t1 = threading.Thread(target=incoming, args=(att_session,), daemon=True)
t1.start()

# read attenuation
read_attenuation(att_session)
if set_new_value:
    set_new_attenuation(att_session, attenuation_val)