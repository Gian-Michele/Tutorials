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

from controller.nats_interface import InstructiveInterface
import argparse
import json
import time

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--pci', action="store", dest="pci", required=True, help='pci value selected')
    parser.add_argument('-r', '--rnti', action="store", dest="rnti", required=True, help='user rnti')
    parser.add_argument('-t','--topic', action="store", dest="topic", required=True, help='topic for pub-sub service')

    parser.add_argument('-dl', '--max_dl', action="store", dest="max_prb", required=False,
                        help='user max number of DL prb')
    parser.add_argument('-ul', '--max_ul', action="store", dest="max_prb_ul", required=False,
                        help='user max number of UL prb when -dl is 0')

    parser.add_argument('-um', '--max_ul_mcs', action="store", dest="max_mcs_ul", required=False,
                        help='user max mcs usable in UL from 4 to 23')

    parser.add_argument('-dm', '--max_dl_mcs', action="store", dest="max_mcs_dl", required=False,
                        help='user max mcs usable in DL from 4 to 28')

    parser.add_argument('-rk', '--max_rank', action="store", dest="max_rank_dl", required=False,
                        help='user max rank usable in dl the value can be 1 or 2')
  

    args = parser.parse_args()
    pci = int(args.pci)
    rnti = int(args.rnti)
    if args.max_prb is not None:
        max_prb_dl = int(args.max_prb)
    else:
        max_prb_dl = -1
    if args.max_prb_ul is not None:
        max_prb_ul = int(args.max_prb_ul)
    else:
         max_prb_ul = -1
    if args.max_mcs_dl is not None:
        max_mcs_dl = int(args.max_mcs_dl)
    else:
        max_mcs_dl = -1
    if args.max_mcs_ul is not None:
        max_mcs_ul = int(args.max_mcs_ul)
    else:
        max_mcs_ul = -1
    if args.max_rank_dl is not None:
        max_rank_dl = int(args.max_rank_dl)
    else:
        max_rank_dl = -1


    topic = args.topic

    tx_info = InstructiveInterface(topic)
    splinter_id = 100
    
    # DL info:
    if(max_prb_dl + max_rank_dl + max_mcs_dl) > -3:
        num_resource = max_prb_dl
        direction = 'DL'
        tx_info.get_instance().vran_instructive_message_generation(splinter_id, rnti, pci, num_resource, direction, max_mcs_dl, max_rank_dl)

    time.sleep(2)

    # UL info
    if(max_prb_ul + max_mcs_ul) > -2:
        num_resource = max_prb_ul
        direction = 'UL'
        tx_info.get_instance().vran_instructive_message_generation(splinter_id, rnti, pci, num_resource, direction, max_mcs_ul,-1)




