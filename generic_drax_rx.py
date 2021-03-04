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

from controller.nats_interface_drax import ReceivingInterface
import json
import time
import oranCommand_pb2
import argparse

if __name__ == '__main__':

    all_topic = list()
    all_topic.append('Topic_OPENRAN_COMMANDS.OranController')
    wait_t = 0.2            # sleeping time in seconds

    rx_info = ReceivingInterface(all_topic)
    last_t = -1
    packet_counter = 0
    while True:
        pkt = rx_info.get_instance().get_recv_pack()
        t = rx_info.get_instance().get_recv_pack_timing()
        if len(pkt) > 0:
            if last_t < t:
                packet_counter = packet_counter + 1

                print("\n##########################################")
                print("receive the packet number {} ".format(packet_counter))

                # to decode the protobuf message
                msg = oranCommand_pb2.OpenRAN_commandMessage()
                msg_size = msg.ParseFromString(pkt)

                print('proto again from pkt of {} bytes: \n{}'.format(msg_size, msg))
                # print("{}".format(pkt))
                last_t = t
        time.sleep(wait_t)

