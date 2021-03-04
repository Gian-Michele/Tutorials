import logging
import threading
from settings import Settings
import redis_listener
import kafka_producer
import queue
import processor
import kafka_listener
import periodic_publisher
import atexit
import action_taker
# add by Gian Michele
# import configparser
import rest_api_interface
import json
import time
from controller.nats_interface import ReceivingInterface
from controller import nats_interface_static


def goodbye(settings):
    settings.set_settings('ready', 'False')


if __name__ == '__main__':

    # ---------------------------------------------
    # SET THE PCI
    # ---------------------------------------------
    pci_152 = rest_api_interface.get_cell_pci(152)
    if pci_152 is None:
        print('Access to Cell152 Info not allow')
        logging.info('Error in API GET PCI info for Cell153')
        exit(1)

    pci_153 = rest_api_interface.get_cell_pci(153)
    if pci_152 is None:
        print('Access to Cell153 Info not allow')
        logging.info('Error in API GET PCI info for Cell153')
        exit(1)

    # -------------------
    # Settings
    # -------------------
    settings = Settings()
    settings.set_pci(pci_152, pci_153)
    # --------------------------------------------------
    # SET THE STATUS first time
    # --------------------------------------------------
    result_152 = rest_api_interface.get_cell_status(152)
    result_153 = rest_api_interface.get_cell_status(153)
    with settings.lock:
        if result_152 is True:
            settings.pci_152_status = 'ON'
        else:
            settings.pci_152_status = 'OFF'

        if result_153 is True:
            settings.pci_153_status = 'ON'
        else:
            settings.pci_153_status = 'OFF'

    # -------------------------------
    # Define at exit function cleanup
    # -------------------------------
    atexit.register(goodbye, settings)
    settings.print_log('xApp starting...', 'INFO')

    # Data store UNUSED
    data_store = {}

    # ---------------------------
    # Queues UNUSED
    # Kafka In-Queue
    in_queue = queue.Queue()

    # Kafka Out-Queue
    out_queue = queue.Queue()

    # Kafka Periodic Out-Queue
    periodic_out_queue = queue.Queue()
    # --------------------------------

    # --------------------------------
    # Threads
    # Redis listener
    # --------------------------------
    redis_listener_thread = threading.Thread(
        name='REDIS_LISTENER',
        target=redis_listener.run,
        args=(settings,)
    )
    redis_listener_thread.setDaemon(True)
    redis_listener_thread.start()

    # Kafka producer
    kafka_producer_thread = threading.Thread(
        name='KAFKA_PRODUCER',
        target=kafka_producer.run,
        args=(settings, periodic_out_queue, )
    )
    kafka_producer_thread.setDaemon(True)
    kafka_producer_thread.start()

    # Kafka listener
    kafka_listener_thread = threading.Thread(
        name='KAFKA_LISTENER',
        target=kafka_listener.run,
        args=(settings, in_queue,)
    )
    kafka_listener_thread.setDaemon(True)
    kafka_listener_thread.start()

    # Processor
    processor_thread = threading.Thread(
        name='PROCESSOR',
        target=processor.run,
        args=(settings, in_queue, out_queue, data_store)
    )
    processor_thread.setDaemon(True)
    processor_thread.start()

    # Periodic publisher
    periodic_publisher_thread = threading.Thread(
        name='PERIODIC_PUBLISHER',
        target=periodic_publisher.run,
        args=(settings, out_queue, data_store, )
    )
    periodic_publisher_thread.setDaemon(True)
    periodic_publisher_thread.start()

    # ------------------------------------------
    # xApp Main loop
    # while True: waiting for Controller Info
    # ------------------------------------------
    topic_list = list()
    topic_list.append('ric_2_accelleran')
    last_t = -1
    packet_counter = 0
    rx_info = ReceivingInterface(topic_list)
    counter_check = 0
    counter_dimension = 300
    # Loop
    while True:
        # data = in_queue.get()
        pkt = rx_info.get_instance().get_recv_pack()
        t = rx_info.get_instance().get_recv_pack_timing()
        if len(pkt) > 0:
            if last_t < t:
                packet_counter = packet_counter + 1
                pkt_s = json.dumps(pkt, indent=2)
                print("\n##########################################")
                print("receive the packet number {} a time: {}".format(packet_counter, t))
                print("{}".format(pkt_s))
                with settings.lock:
                    if settings.log_level >= 10:
                        settings.print_log('Received Control Message:\n {}'.format(pkt_s), 'INFO')
                last_t = t
                if 'type' in pkt:

                    if pkt['type'] == 'get_info':
                        if pkt['pci'] == pci_152:
                            cell_id = 152
                        if pkt['pci'] == pci_153:
                            cell_id = 153
                        result = rest_api_interface.get_cell_status(cell_id)
                        topic_list_2_ric = list()
                        topic_list_2_ric.append('acceleran_2_ric')
                        if result is True:
                            print('-------------')
                            print('Cell {} is ON-AIR'.format(cell_id))
                            print('-------------')
                            val = 'ON'

                        else:
                            print('-------------')
                            print('Cell {} is NOT ON-AIR'.format(cell_id))
                            print('-------------')
                            val = 'OFF'

                        msg_new = {
                            'type': 'info',
                            'pci': pkt['pci'],
                            'status': val
                        }
                        # update status
                        if cell_id == 152:
                            with settings.lock:
                                settings.pci_152_status = val
                        else:
                            with settings.lock:
                                settings.pci_153_status = val

                        nats_interface_static.tx_to_external_platform(msg_new, 'accelleran_2_ric', 1)

                        with settings.lock:
                            if settings.log_level >= 10:
                                settings.print_log('Response with Info Message:\n'
                                                   '{}'.format(json.dumps(msg_new, indent=2)), 'INFO')

                    elif pkt['type'] == 'ho_command':
                        ue_id = pkt['ueID']
                        source_cell = pkt['source_cell']
                        destination_cell = pkt['destination_cell']
                        print('Received HO Command for UE {}, from Cell {} to Cell {}'.format(ue_id, source_cell,
                                                                                              destination_cell))
                        # todo - Here code for handle Handover
                        handover_list = [
                            {'ueIdx': 'UE_'+str(ue_id), 'targetCell': 'Cell'+str(destination_cell),
                             'sourceCell': 'Cell'+str(source_cell)}
                        ]
                        action_taker.trigger_handover(settings, handover_list)


                else:
                    print('unknown message')
                    logging.info('unknown message arrived at time {}:\n{}'.format(time.ctime(time.time()), pkt_s))
        counter_check = counter_check + 1
        # if the counter achieve the maximum value needs a check that the nodes are already up
        if counter_check == counter_dimension:
            # check Cell152
            result_152 = rest_api_interface.get_cell_status(152)
            result_153 = rest_api_interface.get_cell_status(153)
            with settings.lock:
                if result_152 is True:
                    settings.pci_152_status = 'ON'
                else:
                    settings.pci_152_status = 'OFF'

                if result_153 is True:
                    settings.pci_153_status = 'ON'
                else:
                    settings.pci_153_status = 'OFF'

            counter_check = 0
        time.sleep(1)
        # print('next')



