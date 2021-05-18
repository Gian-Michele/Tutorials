#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# date:         08/07/2020
# author:       Gian Michele Dell'Aera
#
#       This script is an example of xapp for receiving nodes log 
#       information.
#       topic: 'node-info' is the topic subscribed to receive node log
#       wait_t: is the sleeping time at each while iteration
#       
########################################################################

from controller import nats_interface_static
from controller.nats_interface import ReceivingInterface
import argparse
import json
import time

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ID', action="store", dest="id", required=True, help='cell_id')
    #                                                                                          ' ON/OFF')
    args = parser.parse_args()

    cell_id = args.id
    MAX_TIME = 20   # Max Number of cycle

    topic = 'ric_2_accelleran'
    # selection of the PCI
    if int(cell_id) == 152:
        msg = {
            'type': 'get_info',
            'pci': 2
        }
    else:
        msg = {
            'type': 'get_info',
            'pci': 1
        }

    nats_interface_static.tx_to_external_platform(msg, topic, 1)
    topic_list = list()
    topic_list.append('accelleran_2_ric')
    rx_info = ReceivingInterface(topic_list)
    # topic = 'accelleran_2_ric'
    last_t = -1
    packet_counter = 0
    waiting_time = 0
    find = False
    while find is not True:
        pkt = rx_info.get_instance().get_recv_pack()
        t = rx_info.get_instance().get_recv_pack_timing()
        if len(pkt) > 0:
            if last_t < t:
                # pkt = None
                # pkt = nats_interface_static.rx_from_external_platform(topic)
                # if pkt is not None:
                pkt = json.dumps(pkt, indent=2)
                print("\n##########################################")
                print("receive the packet number {} a time: {}".format(packet_counter, time.time()))
                print("{}".format(pkt))
                find = True
                rx_info.get_instance().stop_recv()
        if waiting_time < MAX_TIME:
            waiting_time = waiting_time + 1
        else:
            break
        time.sleep(1)

    if find is False:
        rx_info.get_instance().stop_recv()
        print('Time expired - No messages arrived')

    msg_1 = {
        'type': 'ho_command',
        'ueID': 708,
        'source_cell': 152,
        'destination_cell': 153
    }

    nats_interface_static.tx_to_external_platform(msg_1, topic, 1)


