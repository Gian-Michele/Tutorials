#!/usr/bin/env python3
# -*- coding: utf-8 -*-
########################################################################
# date:         08/02/2021
# author:       Gian Michele Dell'Aera
########################################################################

import json
import requests
import argparse


# to reboot the cell
def get_reboot(cell):
    url = 'http://192.168.2.10:31315/api/cellconfiguration/reboot/Cell' + str(cell)
    resp = requests.get(url)
    if resp.status_code != 200:
        # This means something went wrong.
        print("Error code {}".format(resp.status_code))
        return None
    else:
        info = resp.content
        print("Reboot Success")
        return True


# get all the cell info
def get_cell_info(cell):
    url = 'http://192.168.2.10:31315/api/cellconfiguration/summary/Cell' + str(cell)
    resp = requests.get(url)
    if resp.status_code != 200:
        # This means something went wrong.
        print("Error code {}".format(resp.status_code))
        return None
    else:
        return resp.json()


# get all the cell  fool info
def cell_switch(cell):
    default_info = {
    "downlinkEARCN": "3100",
    "bandwidth": "100",
    "refSigPow": "-10",
    "prachIndex": "0",
    "pci": "8",
    "freqBandInd": "band-7",
    "cellID": "256",
    "plmnID": "00101",
    "tac": "12345",
    "enbID": "256",
    "mmeIPAddress": "192.168.10.14",
    "mmePort": "36412",
    "previousCellId": "1024",
    "mocnList": [
        {
        "plmnId": "00101",
        "defMmeSet": "DEFAULT_MME_SET",
        "defMmeSetIndex": 1,
        "mmeSets": [
            {
            "id": 1,
            "mmeSetId": "DEFAULT_MME_SET",
            "mmeSetIP": "10.20.20.30",
            "mmeSetPort": "36412"
            }
            ],
            "index": 0
        },
        {
        "plmnId": "00202",
        "defMmeSet": "MME_SET_2",
        "defMmeSetIndex": 1,
        "mmeSets": [
            {
            " id": 1,
            "mmeSetId": "MME_SET_2",
            "mmeSetIP": "10.11.11.10",
            "mmeSetPort": "8080"
            }
            ],
        "index": 1
        }
        ],
    "defaultPLMN": 1,
    "configureMocn": "true"
    }
    print("Function Not ready")
    return None


# get only cell status the cell info
def get_cell_status(cell):
    url = 'http://192.168.2.10:31315/api/cellconfiguration/summary/Cell' + str(cell)
    resp = requests.get(url)
    if resp.status_code != 200:
        # This means something went wrong.
        print("Error code {}".format(resp.status_code))
        return None
    else:
        info = resp.json()
        # tmp = info['cell']['oam_state_management']['rf_tx_status']
        if info['cell']['oam_state_management']['rf_tx_status'] == 'on-air':
            return True
        else:
            return False


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--ID', action="store", dest="id", required=True, help='cell_id')
    parser.add_argument('-r', '--REBOOT', action="store", dest="reboot", required=False, help='reboot ON/OFF')
    # parser.add_argument('-f', '--Fool', action="store", dest="foolInfo", required=False, help='full cell information'
    #                                                                                          ' ON/OFF')
    args = parser.parse_args()

    cell_id = args.id
    reboot = 'OFF'
    fool_info = False
    if args.reboot is not None:
        if args.reboot == 'ON':
            reboot = 'ON'

    # if args.foolInfo is not None:
    #    if args.foolInfo == 'ON':
    #        fool_info = True

    # if fool_info:
    #    cell_info = get_cell_full_info(cell_id)
    #    print(cell_info)
    # else:
    cell_info = get_cell_info(cell_id)
    print("Received:\n{}".format(json.dumps(cell_info, indent=2)))

    if cell_info is not None:

        if get_cell_status(cell_id) is True:
            print('-------------')
            print('Cell {} is ON-AIR'.format(cell_id))
            print('-------------')
        else:
            print('-------------')
            print('Cell {} is NOT ON-AIR'.format(cell_id))
            print('-------------')

    if reboot == 'ON':
         get_reboot(cell_id)

