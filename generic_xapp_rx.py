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

from controller.nats_interface import ReceivingInterface
import json
import time
import argparse

if __name__ == '__main__':

    parser = argparse.ArgumentParser()    
    parser.add_argument('-t', '--topic', action="store", dest="topic", required=True, help='topic for pub-sub service')
    parser.add_argument('-x', '--xapp_topic', action="store", dest="x_topic", required=False,
                        help='topic for pub-sub xAPP')
    args = parser.parse_args()

    all_topic = list()
    topic = args.topic      # selected topic
    all_topic.append(topic)
    wait_t = 0.2            # sleeping time in seconds

    if args.x_topic is None:
        print("xAPP monitoring not activated")
    else:
        x_topic = args.x_topic
        all_topic.append(x_topic)

    rx_info = ReceivingInterface(all_topic)
    last_t = -1
    packet_counter = 0
    while True:
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
        time.sleep(wait_t)

