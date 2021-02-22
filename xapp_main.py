import logging
import threading
from settings import Settings
import redis_listener
import time
import kafka_producer
import queue
import processor
import kafka_listener
import periodic_publisher
import atexit

# add by Gian Michele
import configparser
import rest_api_interface
import json
import time
from controller.nats_interface import ReceivingInterface
import tx_NATS_static

def goodbye(settings):
    settings.set_settings('ready', 'False')


if __name__ == '__main__':

    # read information for transmission
    config = configparser.ConfigParser()
    fp_config = open('nats_config.ini')
    config.read_file(fp_config)
    fp_config.close()

    nats_server_ip = config.get('NATS_SERVER', 'ip_address', fallback="163.162.89.28")
    nats_server_port = config.getint('NATS_SERVER', 'port', fallback=4222)
    nats_use_tls = config.get('NATS_SERVER', 'use_tls')
    nats_user = config.get('NATS_SERVER', 'user')
    nats_pass = config.get('NATS_SERVER', 'password')
    nats_cert_file = config.get('NATS_SERVER', 'cert_file')


    ### Settings
    settings = Settings()

    ### Define at exit function cleanup
    atexit.register(goodbye, settings)

    logging.info('xApp starting...')

    ### Data store
    data_store = {}

    ### Queues
    # Kafka In-Queue
    in_queue = queue.Queue()

    # Kafka Out-Queue
    out_queue = queue.Queue()

    # Kafka Periodic Out-Queue
    periodic_out_queue = queue.Queue()

    ### Threads
    # Redis listener
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

    ### xApp loop
    #while True:
    #    time.sleep(1)
    topic_list = list()
    topic_list.append('ric_2_acceleran')
    last_t = -1
    packet_counter = 0
    rx_info = ReceivingInterface(topic_list)
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
                last_t = t
                if 'type' in pkt:

                    if pkt['type'] == 'get_info':
                        if pkt['pci'] == 1:
                            id = 152
                        if pkt['pci'] == 2:
                            id = 153
                        result = rest_api_interface.get_cell_status(id)
                        topic_list_2_ric = list()
                        topic_list_2_ric.append('acceleran_2_ric')
                        if result is True:
                            print('-------------')
                            print('Cell {} is ON-AIR'.format(id))
                            print('-------------')
                            val = 'ON'
                        else:
                            print('-------------')
                            print('Cell {} is NOT ON-AIR'.format(id))
                            print('-------------')
                            val = 'OFF'

                        msg_new = {
                            'type': 'info',
                            'pci': pkt['pci'],
                            'status': val
                        }
                        tx_NATS_static.tx_to_external_platform(msg_new, 'acceleran_2_ric', 1)
                        # tx.tx_from_external_platform(msg_new)
                else:
                    print('unknown message')
        time.sleep(2)
        print('next')



