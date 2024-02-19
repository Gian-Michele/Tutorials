#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# date:         22/01/2021
# author:       Gian Michele Dell'Aera
#
#       This script is used to automatize the test procedure based on IPERF
#       Information contained in config.in are used to describe the test procedure
#
########################################################################

import os
import time
import socket
import threading
import configparser
import subprocess
import argparse
import json
import csv
from testtools import *
from collections import ChainMap


# save the results of the tests in a csv file
class CSVWriter:
    def __init__(self, file_name):
        self.iteration = 0
        self.csv_file = file_name
        # the following fields are populated at the first call of save()
        self.fields = None
        self.writer = None

    def save(self, results_set):
        # add the header to the CSV file only once
        if self.iteration == 0:
            self.fields = [field for res in results_set for field in list(res.keys())]
            self.writer = csv.DictWriter(self.csv_file, fieldnames=self.fields)
            self.writer.writeheader()
        self.writer.writerow(dict(ChainMap(*results_set)))
        self.iteration = self.iteration + 1


def check_connection_and_latency(ip_val):
    ping_response = subprocess.Popen(["/bin/ping", "-c10", "-w10", ip_val], stdout=subprocess.PIPE).stdout.read()
    ping_response = str(ping_response).split('received,')[1]
    info = ping_response.split('%')
    packet_loss = float(info[0])
    connection = False
    if packet_loss < 10:
        connection = True
        tmp = info[1].split('=')[1]
        e2e_latency = float(tmp.split('/')[1])
        print("E2E average latency {}".format(e2e_latency))

    return connection


# Function to check the connection toward an ip
def check_connection(ip_val):
    respond = os.system('ping -w 2 ' + ip_val + ' > /dev/null 2>&1')
    if respond == 0:
        return True
    else:
        return False


# Waiting for Messages from test Attenuator System
def incoming(session):
    buffer = ''
    while True:
        try:
            chunk = session.recv(256)
            if chunk:
                buffer += ''.join(map(chr, chunk))
                last = 0
                process = ''
                for i in range(0, len(buffer)):
                    if buffer[i] == '\n' or buffer[i] == '\r':
                        if len(process):
                            # process the response
                            # we just print to console as an example
                            print(process)
                            process = ''
                        last = i
                    else:
                        process += buffer[i]
                buffer = buffer[last +1:len(buffer)]
        except BlockingIOError:
            pass
        except ConnectionResetError:
            break


# Function to set a new value of attenuation
def set_new_attenuation(session, attenuation_val, attenuation_port='A'):
    script_list = list()
    command = 'SA' + str(attenuation_port) + ' ' + str(attenuation_val)
    script_list.append(command)
    script_list.append('RAA')

    for cmd_val in script_list:
        session.send((cmd_val + '\n').encode())

    # waiting check on Attenuator Thread
    time.sleep(3)
    print('New Attenuator Script Applied')


# read the attenuator port
def read_attenuation(session):
    script_list = list()
    script_list.append('RAA')

    for cmd_val in script_list:
        session.send((cmd_val + '\n').encode())

    # waiting check on Attenuator Thread
    time.sleep(3)
    print('New Attenuator Script Applied')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', help="IP address of the UE to be tested", dest="ip")
    parser.add_argument('-p', help="PORT used for IPERF3 service (DEFAULT used 5201)", dest="port", default=5201)
    parser.add_argument('-o', help="Path of the output results file (DEFAULT used test_results.csv)", type=argparse.FileType('w'),
                        default="test_results.csv", dest="results_file")
    args = parser.parse_args()
    user_ip = args.ip
    user_port = int(args.port)
    results_file = args.results_file
    writer = CSVWriter(results_file)

    # Import Test Information
    config = configparser.ConfigParser()
    fp_config = open('config.ini')
    config.read_file(fp_config)
    fp_config.close()

    print("\n-------------------------------")
    print("Check Connection to the user at IP: {} ...".format(user_ip))
    if check_connection_and_latency(user_ip) is True:
        print("     USER REACHABLE")
    else:
        print("     USER NOT REACHABLE")
        print("-------------------------------\n")
        exit(1)
    print("-------------------------------\n")

    # only if attenuator are used for the test
    attenuator_flag = config.get('ATTENUATOR', 'attenuator_support')
    if attenuator_flag.upper() == 'ON':
        # UDP port on the RIC for E2 interface (where send packet)
        attenuator_ip_list = config.get('ATTENUATOR', 'ip_address').replace(" ", "").split(',')

        attenuator_number = 1
        for ip in attenuator_ip_list:
            print("\n-------------------------------")
            print("Check connection to Attenuator Number {} at IP: {}".format(attenuator_number, ip))
            if check_connection(ip) is True:
                print("Attenuator Number {} REACHABLE".format(attenuator_number))
            else:
                print("Attenuator Number {} NOT REACHABLE".format(attenuator_number))
            print("-------------------------------")
            attenuator_number = attenuator_number+1
        print("\n")

        # connect to 1st Attenuator System
        att_session_1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        att_session_1.connect((attenuator_ip_list[0], 3001))
        att_session_1.setblocking(False)

        # receive responses and process
        t1 = threading.Thread(target=incoming, args=(att_session_1,), daemon=True)
        t1.start()
        if len(attenuator_ip_list) == 2:
            att_session_2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            att_session_2.connect((attenuator_ip_list[1], 3001))
            att_session_2.setblocking(False)

            # receive responses and process
            t2 = threading.Thread(target=incoming, args=(att_session_2,), daemon=True)
            t2.start()

        # first set
        # set_new_attenuation(att_session, 95)
        # start of script

    # Test parameter
    print("Reading Test Configuration\n")
    pkt_size = config.get('TEST_LIST', 'pkt_size').replace(" ", "").split(',')
    thr_max = config.get('TEST_LIST', 'thr_max').replace(" ", "").split(',')
    direction = config.get('TEST_LIST', 'direction').replace(" ", "").split(',')

    attenuation = config.get('TEST_LIST', 'attenuation_list_1').replace(" ", "").split(",")
    if len(attenuator_ip_list) == 2:
        attenuation2 = config.get('TEST_LIST', 'attenuation_list_2').replace(" ", "").split(",")
        if len(attenuation) == len(attenuation2):
            print("Input Check Complete")
            test_list = {
                'pkt_size': pkt_size,
                'thr_max': thr_max,
                'direction': direction,
                'attenuation': attenuation,
                'attenuation2': attenuation2
            }
        else:
            print("ERROR: 2 attenuation list need  to have the same length")
            exit(1)
    else:
        print("Input Check Complete")
        test_list = {
            'pkt_size': pkt_size,
            'thr_max': thr_max,
            'direction': direction,
            'attenuation': attenuation,
        }


    #######################
    # iperf configuration
    duration = config.get('IPERF', 'duration')
    protocol = config.get('IPERF', 'protocol')

    print("Starting Test\n")

    for idx1 in test_list['direction']:
        for idx2 in test_list['pkt_size']:
            for idx3 in test_list['thr_max']:

                # iperf configuration
                iperf_config = {
                    'duration': int(duration),
                    'protocol': protocol,
                    'ip': user_ip,
                    'port': user_port,
                    'direction': idx1,
                    'pkt_size': int(idx2),
                    'thr_max': int(idx3) * 1000000
                }

                if attenuator_flag.upper() == 'ON':
                    for idx4 in range(0, len(test_list['attenuation'])):
                        val_attenuation = int(test_list['attenuation'][idx4])
                        ######################
                        # setting attenuator
                        set_new_attenuation(att_session_1, val_attenuation)
                        ######################
                        if len(attenuator_ip_list) == 2:
                            val_attenuation2 = int(test_list['attenuation2'][idx4])
                            ######################
                            # setting attenuator
                            set_new_attenuation(att_session_2, val_attenuation2)
                            ######################
                            # legend of the test
                            test_legend = {
                                'direction': idx1,
                                'pkt_size': int(idx2),
                                'thr_max': int(idx3) * 1000000,
                                'protocol': protocol,
                                'attenuation': val_attenuation,
                                'attenuation2': val_attenuation2
                            }
                            print('----------------')
                            print('Running {} Test: \nPacket Size - {}\nMax Throughput - {} Mbps\nAttenuation 1 - '
                                  '{}\nAttenuation 2 - {}:'.format(idx1, idx2, idx3, val_attenuation,
                                                                   val_attenuation2))
                        else:
                            # legend of the test
                            test_legend = {
                                'direction': idx1,
                                'pkt_size': int(idx2),
                                'thr_max': int(idx3)*1000000,
                                'protocol': protocol,
                                'attenuation': val_attenuation
                            }
                            print('----------------')
                            print('Running {} Test: \nPacket Size - {}\nMax Throughput - {} Mbps\nAttenuation - '
                                  '{}:'.format(idx1, idx2, idx3, val_attenuation))

                        iperf_ue_results = Iperf(iperf_config).start_test().get_results()

                        if iperf_config is not None:
                            print('result:\n{}'.format(json.dumps(iperf_ue_results, indent=2)))
                            # write to file the results preceded by the used combination of parameters
                            res_set = list()
                            res_set.append(test_legend)
                            res_set.append(iperf_ue_results)
                            writer.save(res_set)
                            results_file.flush()

                else:
                    # legend of the test
                    test_legend = {
                        'direction': idx1,
                        'pkt_size': int(idx2),
                        'thr_max': int(idx3)*1000000,
                        'protocol': protocol
                    }
                    print('----------------')
                    print('Running {} Test: \nPacket Size - {}\nMax Throughput - {} Mbps:'.format(idx1, idx2, idx3))

                    iperf_ue_results = Iperf(iperf_config).start_test().get_results()
                    if iperf_config is not None:
                        print('result:\n{}'.format(json.dumps(iperf_ue_results, indent=2)))
                        # write to file the results preceded by the used combination of parameters
                        res_set = list()
                        res_set.append(test_legend)
                        res_set.append(iperf_ue_results)
                        writer.save(res_set)
                        results_file.flush()

                time.sleep(5)

    print('\n-------------------')
    print('End Automated Test')
    print('-------------------')
    results_file.close()
