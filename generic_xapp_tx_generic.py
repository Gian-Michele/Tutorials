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

from controller.nats_interface import InstructiveInterface, ReceivingInterface
import argparse
import json
import time

if __name__ == '__main__':

    topic = 'ric_2_acceleran'

    tx_info = InstructiveInterface(topic)

    msg = {
        'type': 'get_info',
        'pci': 2
    }

    tx_info.get_instance().tx_from_external_platform(msg)
    topic_list = list()
    topic_list.append('acceleran_2_ric')
    rx_info = ReceivingInterface(topic_list)
    last_t = -1
    packet_counter = 0
    find = False
    while find is not True:
        pkt = rx_info.get_instance().get_recv_pack()
        t = rx_info.get_instance().get_recv_pack_timing()
        if len(pkt) > 0:
            if last_t < t:
                packet_counter = packet_counter + 1
                pkt = json.dumps(pkt, indent=2)
                print("\n##########################################")
                print("receive the packet number {} a time: {}".format(packet_counter, t))
                print("{}".format(pkt))
                last_t = t
                find = True
                rx_info.get_instance().stop_recv()
        time.sleep(1)




