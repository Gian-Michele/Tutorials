########################################################################
# date:         08/07/2020
# author:       Gian Michele Dell'Aera
#
#       This script report 2 class object to hanlde NATS bup/sub BUS
#       
########################################################################

# from useful.functions_lib import UsefulLibrary
import threading
import json
import time
import asyncio
import configparser
import ssl
from nats.aio.client import Client as NATSClient


# Class for recover information from NATS
class ReceivingInterface:
    def __init__(self, topic_subcription):
        """
        Init parameter require only topic for subscription
        """
        self.pars_config = configparser.ConfigParser()
        fp_config = open('nats_config.ini')
        self.pars_config.read_file(fp_config)
        fp_config.close()

        self.loop = None
        self.nc = NATSClient()      # nc client to receive message from subscription
        self.nats_counter = 0
        self.nats_server_ip = self.pars_config.get('NATS_SERVER', 'ip_address', fallback="163.162.89.28")
        self.nats_server_port = self.pars_config.getint('NATS_SERVER', 'port', fallback=4222)
        self.nats_use_tls = self.pars_config.get('NATS_SERVER', 'use_tls')
        self.nats_user = self.pars_config.get('NATS_SERVER', 'user')
        self.nats_pass = self.pars_config.get('NATS_SERVER', 'password')
        self.nats_cert_file = self.pars_config.get('NATS_SERVER', 'cert_file')

        ReceivingInterface.__instance = self
        self.__lock = threading.Lock()

        # information provided to external xAPP
        self.last_received_pkt = dict()
        self.last_time_packet = time.time()

        self.main_thread = threading.Thread(target=self.__listen_from_oai_thread_nats,
                                            args=(self.nats_server_ip, self.nats_server_port, topic_subcription),
                                            daemon=True)
        self.main_thread.start()

    @staticmethod
    def get_instance():
        """ retrieve the singleton instance of Controller class """
        return ReceivingInterface.__instance

    # simple function to receive information from the NATS BUS
    def get_recv_pack(self):
        self.__lock.acquire()
        val = self.last_received_pkt
        self.__lock.release()
        return val

    def stop_recv(self):
        self.loop.stop()
        print("Stop Reception")

    # simple function to receive information from the last received packet in NATS BUS
    def get_recv_pack_timing(self):
        self.__lock.acquire()
        val = self.last_time_packet
        self.__lock.release()
        return val

    def get_recv_pack_with_time(self):
        self.__lock.acquire()
        val = self.last_received_pkt
        timing = self.last_time_packet
        self.__lock.release()
        return val, timing

    # main thread that receive packet from the controller_interface block (subscribing at nats)
    def __listen_from_oai_thread_nats(self, nats_ip, nats_port, topic):
        """ Function executed from separated thread: listening continuously
        (until self.t2_event event is set) for incoming packets (from 'nats controller_interface').
        These packets are processed in order to known the "talking" nodes (source IP),
        so it can keep up to date the several data structure.
        To do this, in detail, is used a occurrences' collection.
        """

        # Using the secondary thread loop to receive packets from controller_interface through NATS
        # Creating a loop for the current thread and setting to be used for asyncio
        loop = asyncio.new_event_loop()
        self.loop = loop
        asyncio.set_event_loop(loop)

        # Used to share data between coroutines about last packet arrival time
        self.last_time_packet = time.time()

        # Creating two tasks: one to receive packets with NATS, the other to monitor every 30s
        # if not receiving data anymore from nodes (this is a timeout). Both procedures are run
        # concurrently but on the same thread
        if len(topic) == 2:
            print("topic 1: {}, topic 2: {}".format(topic[0], topic[1]))

        loop.create_task(self.__receive_from_nats(loop, nats_ip, nats_port, topic))

        try:
            loop.run_forever()
        except KeyboardInterrupt:
            print("Exception due to Keyboard interrupt")

    async def __receive_from_nats(self, loop, ip, port, topic):
        # Topic to subscribe to, for receiving data, below an example of topic
        string_name = topic[0]
        if len(topic) == 2:
            string_name = topic[0] + ' ' + topic[1]

        print('Try Connection to NATS server at {}:{} for "{}" topic'.format(ip, port, string_name))

        if self.nats_use_tls:
            ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=self.nats_cert_file)
            await self.nc.connect(
                servers="tls://{}:{}".format(ip, port),
                name="Buffer Connection - Controller:{}".format(string_name),
                loop=loop,
                user=self.nats_user,
                password=self.nats_pass,
                connect_timeout=20,
                tls=ssl_ctx)
        else:
            await self.nc.connect(
                servers="{}:{}".format(ip, port),
                name="Buffer Connection - Controller:{}".format(string_name),
                loop=loop)

        print('Buffer Connection active Correctly')
        counter = 0

        # Callback called when a packet is receive through NATS
        async def message_handler(msg):
            # To print the packet counter
            nonlocal counter
            counter += 1
            # print("Received packet number {}".format(counter))

            # Updating the time of the last received packet
            self.__lock.acquire()
            self.last_time_packet = time.time()
            self.__lock.release()

            # Taking the data from NATS packet
            data = msg.data.decode()
            json_data = json.loads(data)
            recv_val = json_data['msg']

            try:
                # recover dictionary information (similar to socket thread)
                if isinstance(recv_val, str):
                    dict_data = json.loads(recv_val)  # convert in type dictionary
                else:
                    dict_data = recv_val
                self.__lock.acquire()
                self.last_received_pkt = dict_data
                self.__lock.release()

            except Exception as ex:
                print("An error occurred: {}".format(ex))

        # At this point the execution blocks until some data is received (and the callback is called)
        self.sid_subscription = await self.nc.subscribe(topic[0], cb=message_handler)
        if len(topic) > 1:
            self.sid_subscription_x = await self.nc.subscribe(topic[1], cb=message_handler)


# defined class to send message to the node
class InstructiveInterface:
    def __init__(self, topic_subcription):
        InstructiveInterface.__instance = self
        self.nats_counter_tx = 0
        self.topic = topic_subcription

    @staticmethod
    def get_instance():
        """ retrieve the singleton instance of Controller class """
        return InstructiveInterface.__instance

    # function used to send message from acceleran drax platform
    def tx_to_external_platform(self, message_to_tx):

        # read information for transmission
        config = configparser.ConfigParser()
        fp_config = open('nats_config.ini')
        config.read_file(fp_config)
        fp_config.close()

        nc_tx = NATSClient()  # nc client to receive message from subscription
        nats_server_ip = config.get('NATS_SERVER', 'ip_address', fallback="163.162.89.28")
        nats_server_port = config.getint('NATS_SERVER', 'port', fallback=4222)
        nats_use_tls = config.get('NATS_SERVER', 'use_tls')
        nats_user = config.get('NATS_SERVER', 'user')
        nats_pass = config.get('NATS_SERVER', 'password')
        nats_cert_file = config.get('NATS_SERVER', 'cert_file')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.nats_counter_tx = self.nats_counter_tx + 1
        loop.run_until_complete(self.send_to_nats(nc_tx, loop, message_to_tx, self.nats_counter_tx,
                                                  nats_server_ip, nats_server_port, self.topic, nats_use_tls,
                                                  nats_user, nats_pass, nats_cert_file))

    # function used to and send message to a splinter
    def vran_instructive_message_generation(self, splinter_id, rnti, pci, num_resource=-1, direction='DL',
                                            mcs=-1, rank=-1):

        if direction.upper() == 'DL':
            message = {'direction': direction, 'pci': pci, 'rnti': rnti, 'max_prb_dl': num_resource, 'max_prb_ul': -1,
                       'mcs': mcs, 'rank': rank}
        else:
            message = {'direction': direction, 'pci': pci, 'rnti': rnti, 'max_prb_dl': -1, 'max_prb_ul': num_resource,
                       'mcs': mcs, 'rank': rank}

        message_to_tx = {str(splinter_id): message}

        # read information for transmission
        config = configparser.ConfigParser()
        fp_config = open('nats_config.ini')
        config.read_file(fp_config)
        fp_config.close()

        nc_tx = NATSClient()  # nc client to receive message from subscription
        nats_server_ip = config.get('NATS_SERVER', 'ip_address', fallback="163.162.89.28")
        nats_server_port = config.getint('NATS_SERVER', 'port', fallback=4222)
        nats_use_tls = config.get('NATS_SERVER', 'use_tls')
        nats_user = config.get('NATS_SERVER', 'user')
        nats_pass = config.get('NATS_SERVER', 'password')
        nats_cert_file = config.get('NATS_SERVER', 'cert_file')
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        self.nats_counter_tx = self.nats_counter_tx + 1
        loop.run_until_complete(self.send_to_nats(nc_tx, loop, message_to_tx, self.nats_counter_tx,
                                                  nats_server_ip, nats_server_port, self.topic, nats_use_tls,
                                                  nats_user, nats_pass, nats_cert_file))

    # Function used to send data to NATS server opening and closing a connection
    @staticmethod
    async def send_to_nats(nc_tx, loop: asyncio.AbstractEventLoop, message, counter, nats_server_ip,
                           nats_server_port, topic, nats_use_tls, nats_user, nats_pass, nats_cert_file):
        nats_topic = topic

        msg_to_tx = {'NUM': counter, 'msg': message}
        tx = json.dumps(msg_to_tx).encode()
        
        if nats_use_tls:
            ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=nats_cert_file)
            await nc_tx.connect(
                servers="tls://{}:{}".format(nats_server_ip, nats_server_port),
                loop=loop,
                user=nats_user,
                password=nats_pass,
                tls=ssl_ctx)
        else:
            await nc_tx.connect("{}:{}".format(nats_server_ip, nats_server_port), loop=loop)

        await nc_tx.publish(nats_topic, tx)
        print('Sent Json {} bytes to NATS server at {}:{}'.format(len(message), nats_server_ip, nats_server_port))
        # Terminate connection to NATS.
        await nc_tx.close()


