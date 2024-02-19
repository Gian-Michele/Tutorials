from kafka import KafkaConsumer
import json
import logging
import datetime
import time
from controller.nats_interface import InstructiveInterface
from jsonschema import validate, SchemaError


def run(settings, in_queue):

    fp_schema = open('schema.json', 'r')
    json_schema = json.load(fp_schema)
    # TODO create multi kafka topic support, use threads as listeners

    with settings.lock:
        kafka_url = settings.configuration['config']['KAFKA_URL']
        kafka_port = settings.configuration['config']['KAFKA_PORT']
        pci_152 = settings.pci_152
        pci_153 = settings.pci_153
        if settings.log_level >= 10:
            settings.print_log('Kafka Listener Started', 'INFO')
    try:
        consumer = KafkaConsumer(
            bootstrap_servers=[kafka_url + ':' + kafka_port]
        )
        logging.info("Successfully connected to Kafka server [{url}:{port}]".format(
            url=kafka_url,
            port=kafka_port
        ))
    except:
        with settings.lock:
            settings.print_log("Failed to connect to Kafka Topic!", 'ERROR')
        return

    tx_info = InstructiveInterface('node-info')
    # {
    # 'timestamp': 1590609372749960768, 'type': 'UE_MEASUREMENT',
    # 'ueMeasurement': {
    # 'cellId': 'Dageraadplaats', 'rsrp': 94, 'rsrq': 27, 'ueCellId': 'Dageraadplaats', 'ueRicId': 'UE_22520'
    # }
    # }

    default_json_152 = {
        "cpuLoad": 1.0,
        "eTime": 1963800,
        "numRruDescriptors": 1,
        "numUeDescriptors": 0,
        "sTime": 1963500,
        "rru": [
            {
                "dsThroughput": 1111,
                "ipAddress_p1": "x.y.z.k",
                "pci": pci_152,
                "rtt_latency": 1111,
                "usThroughput": 1111
            }
        ],
        "ues": []

    }
    default_json_153 = {
        "cpuLoad": 1.0,
        "eTime": 1963800,
        "numRruDescriptors": 1,
        "numUeDescriptors": 0,
        "sTime": 1963500,
        "rru": [
            {
                "dsThroughput": 1111,
                "ipAddress_p1": "x.y.z.k",
                "pci": pci_153,
                "rtt_latency": 1111,
                "usThroughput": 1111
            }
        ],
        "ues": []
    }

    neighbour_cells_152 = None
    neighbor_cells_153 = None

    ue_id_serv152 = list()
    ue_id_serv153 = list()
    other152_ues = list()
    other153_ues = list()
    ue_dl_thr = list()
    ue_ul_thr = list()

    accum_counter = 15

    counter = 0
    while True:
        with settings.lock:
            tmp_kafka_topics = settings.configuration['config']['KAFKA_LISTEN_TOPIC']

        kafka_topics = parse_kafka_topics_from_settings(tmp_kafka_topics)

        if consumer.subscription():
            if not kafka_topics.issubset(consumer.subscription()):
                consumer.subscribe(kafka_topics)
                logging.info('Subscribed to new topics: [{topics}]'.format(topics=kafka_topics))
        else:
            consumer.subscribe(kafka_topics)
            logging.info('Initial subscribe to topics: [{topics}]'.format(topics=kafka_topics))

        raw_msgs = consumer.poll(timeout_ms=1000)

        for tp, msgs in raw_msgs.items():

            for msg in msgs:
                payload = json.loads(msg.value)
                in_queue.put(payload)
                if 'type' in payload:
                    # logging.debug("Received on KAFKA:\n{msg}".format(msg=payload))
                    if payload['type'] == 'UE_MEASUREMENT':
                        # nats_queue.put(payload)
                        print("At [{}] received msg type [{}] that ue [{}] - dRaxId [{}] sees cell [{}] and Serving "
                              "cell [{}]".format(datetime.datetime.fromtimestamp(payload['timestamp'] // 1000000000),
                                                 payload['type'],
                                                 payload['ueMeasurement']['ueRicId'],
                                                 payload['ueMeasurement']['ueDraxId'],
                                                 payload['ueMeasurement']['cellId'],
                                                 payload['ueMeasurement']['ueCellId'])
                              )

                        # update user_list
                        key = str(payload['ueMeasurement']['ueRicId'])
                        user_dict[key] = payload['ueMeasurement']['ueDraxId']
                        # ------------------------------------------------------------------------
                        # create json to TX for Cell 152
                        if payload['ueMeasurement']['cellId'] == 'Cell152':
                            default_json_152['sTime'] = payload['timestamp'] // 1000000000
                            default_json_152, neighbour_cells_152, ue_id_serv152, other152_ues = \
                                add_measurement_to_json(default_json_152, payload, ue_id_serv152, other152_ues,
                                                        pci_152, pci_153)

                        if payload['ueMeasurement']['cellId'] == 'Cell153':
                            default_json_153['sTime'] = payload['timestamp'] // 1000000000
                            default_json_153, neighbor_cells_153, ue_id_serv153, other153_ues = \
                                add_measurement_to_json(default_json_153, payload, ue_id_serv153, other153_ues,
                                                        pci_152, pci_153)

                        if neighbour_cells_152 is not None:
                            if len(neighbour_cells_152) > 0:        # todo: could be  done better
                                if len(ue_id_serv153) > 0:
                                    ue_id = ue_id_serv153[0]        # todo: probably a for over the UEs

                                    found = False
                                    for i in range(0, len(default_json_153['ues'])):

                                        if default_json_153['ues'][i]['rnti'] == ue_id:
                                            # in information on neighbor is not present needs to be add
                                            if len(default_json_153['ues'][i]['neighborCells']) == 0:
                                                default_json_153['ues'][i]['numNeighborDescriptors'] = 1
                                                default_json_153['ues'][i]['neighborCells'] = neighbour_cells_152
                                            found = True

                                    if found is False:
                                        with settings.lock:
                                            settings.print_log('UE {} not found in Cell153'.format(ue_id),
                                                               'ERROR')

                        if neighbor_cells_153 is not None:
                            if len(neighbor_cells_153) > 0:        # todo: could be  done better
                                if len(ue_id_serv152) > 0:
                                    ue_id = ue_id_serv152[0]        # todo: probably a for over the UEs

                                    found = False
                                    for i in range(0, len(default_json_152['ues'])):
                                        if default_json_152['ues'][i]['rnti'] == ue_id:
                                            if len(default_json_152['ues'][i]['neighborCells']) == 0:
                                                default_json_152['ues'][i]['neighborCells'] = neighbor_cells_153
                                                default_json_152['ues'][i]['numNeighborDescriptors'] = 1
                                            found = True

                                    if found is False:
                                        with settings.lock:
                                            settings.print_log('UE {} not found in Cell153'.format(ue_id),
                                                               'ERROR')

                    if payload['type'] == 'THROUGHPUT_REPORT':
                        print("At [{}] received msg type [{}] that ue [{}] sees serving cell [{}] DL THR [{}], "
                              "UL THR [{}]".format(datetime.datetime.fromtimestamp(payload['timestamp'] // 1000000000),
                                                   payload['type'],
                                                   payload['throughputReport']['cellId'],
                                                   payload['throughputReport']['ueRicId'],
                                                   payload['throughputReport']['dlThroughput'],
                                                   payload['throughputReport']['ulThroughput'])
                              )
                        ue_id = int(payload['throughputReport']['ueRicId'].split('_')[1])
                        dl = float(payload['throughputReport']['dlThroughput'])
                        ul = float(payload['throughputReport']['ulThroughput'])
                        ue_dl_thr, ue_ul_thr = update_thr(ue_dl_thr, ue_ul_thr, ue_id, dl, ul)

                    if payload['type'] == 'BLER_REPORT':
                        print("At [{time}] received msg type [{type}] that ue [{ue}] sees serving cell [{cell}] "
                              "DL BLER [{dlBler}], UL BLER [{ulBler}]".format(
                              time=datetime.datetime.fromtimestamp(payload['timestamp'] // 1000000000),
                              type=payload['type'],
                              cell=payload['blerReport']['cellId'],
                              ue=payload['blerReport']['ueRicId'],
                              dlBler=payload['blerReport']['dlBler'],
                              ulBler=payload['blerReport']['ulBler'])
                              )
                    if payload['type'] == 'CQI_REPORT':
                        print("-----------------")
                        print("Received CQI info")
                        print("-----------------")
                if 'beaconInfo' in payload:
                    print("Received Beacon {}".format(payload['beaconInfo']['componentId']))
                    # if payload['beaconInfo']['componentId'] == "Cell152":
                    #    cell_152_on = True
                    # if payload['beaconInfo']['componentId'] == "Cell153":
                    #    cell_153_on = True
        counter = counter + 1
        if counter == accum_counter:
            print('-----------------------------------')
            print('-----------------------------------')
            print('--    TX DATA TO Near RT RIC     --')
            print('-----------------------------------')
            print('-----------------------------------')
            print('List 152: served {}, not served {}'.format(ue_id_serv152, other152_ues))
            # ---------
            # update DL THR
            for ue1 in ue_id_serv152:
                for ue2 in ue_dl_thr:
                    if ue2['id'] == ue1:
                        found = False
                        for idx in range(0, len(default_json_152['ues'])):
                            if default_json_152['ues'][idx]['rnti'] == ue1:
                                found = True
                                default_json_152['ues'][idx]['dlThroughput'] = ue2['thr']/ue2['count']
                        if found is False:
                            print('UE {} not found in Cell152 during dl thr update'.format(ue1))
                            with settings.lock:
                                if settings.log_level >= 10:
                                    settings.print_log('UE {} not found in Cell152 during dl thr update'.format(ue1),
                                                       'ERROR')
                #
                # Update UL THR
                for ue2 in ue_ul_thr:
                    if ue2['id'] == ue1:
                        found = False
                        for idx in range(0, len(default_json_152['ues'])):
                            if default_json_152['ues'][idx]['rnti'] == ue1:
                                found = True
                                default_json_152['ues'][idx]['ulThroughput'] = ue2['thr'] / ue2['count']
                        if found is False:
                            print('UE {} not found in Cell152 during ul thr update'.format(ue1))
                            with settings.lock:
                                if settings.log_level >= 10:
                                    settings.print_log('UE {} not found in Cell152 during ul thr update'.format(ue1),
                                                       'ERROR')

            print('List 153: served {}, not served {}'.format(ue_id_serv153, other153_ues))
            for ue1 in ue_id_serv153:
                # ---------------------
                # Update DL THR
                for ue2 in ue_dl_thr:
                    if ue2['id'] == ue1:
                        found = False
                        for idx in range(0, len(default_json_153['ues'])):
                            if default_json_153['ues'][idx]['rnti'] == ue1:
                                found = True
                                default_json_153['ues'][idx]['dlThroughput'] = ue2['thr']/ue2['count']
                        if found is False:
                            print('UE {} not found in Cell152 during dl thr update'.format(ue1))
                            with settings.lock:
                                if settings.log_level >= 10:
                                    settings.print_log('UE {} not found in Cell152 during dl thr update'.format(ue1),
                                                       'ERROR')
                # -------------
                # Update UL THR
                for ue2 in ue_ul_thr:
                    if ue2['id'] == ue1:
                        found = False
                        for idx in range(0, len(default_json_153['ues'])):
                            if default_json_153['ues'][idx]['rnti'] == ue1:
                                found = True
                                default_json_153['ues'][idx]['ulThroughput'] = ue2['thr'] / ue2['count']
                        if found is False:
                            print('UE {} not found in Cell152 during ul thr update'.format(ue1))
                            with settings.lock:
                                if settings.log_level >= 10:
                                    settings.print_log('UE {} not found in Cell152 during ul thr update'.format(ue1),
                                                       'ERROR')

            # Check - status of nodes before transmit information
            with settings.lock:
                if settings.pci_152_status == 'ON':
                    cell_152_on = True
                else:
                    cell_152_on = False
                if settings.pci_153_status == 'ON':
                    cell_153_on = True
                else:
                    cell_153_on = False

            if cell_152_on is True:
                try:
                    time_now = time.time()
                    default_json_152['eTime'] = int(time_now)
                    validate(default_json_152, json_schema)
                    tx_info.get_instance().tx_to_external_platform(default_json_152)
                except SchemaError as ex:
                    print("Schema for cell 152 is Not valid:\n{}".format(ex))
            if cell_153_on is True:
                try:
                    time_now = time.time()
                    default_json_153['eTime'] = int(time_now)
                    validate(default_json_153, json_schema)
                    tx_info.get_instance().tx_to_external_platform(default_json_153)
                except SchemaError as ex:
                    print("Schema for cell 153 is Not valid:\n{}".format(ex))

            # reset all variable
            counter = 0
            default_json_152 = {
                "cpuLoad": 1.0,
                "eTime": 1963800,
                "numRruDescriptors": 1,
                "numUeDescriptors": 0,
                "sTime": 1963500,
                "rru": [
                    {
                        "dsThroughput": 1111,
                        "ipAddress_p1": "x.y.z.k",
                        "pci": pci_152,
                        "rtt_latency": 1111,
                        "usThroughput": 1111
                    }
                ],
                "ues": []
            }
            default_json_153 = {
                "cpuLoad": 1.0,
                "eTime": 1963800,
                "numRruDescriptors": 1,
                "numUeDescriptors": 0,
                "sTime": 1963500,
                "rru": [
                    {
                        "dsThroughput": 1111,
                        "ipAddress_p1": "x.y.z.k",
                        "pci": pci_153,
                        "rtt_latency": 1111,
                        "usThroughput": 1111
                    }
                ],
                "ues": []
            }

            msg_start_152 = False
            msg_start_153 = False
            neighbour_cells_152 = None
            neighbor_cells_153 = None

            ue_id_serv152 = list()
            ue_id_serv153 = list()
            other152_ues = list()
            other153_ues = list()

            ue_dl_thr = list()
            ue_ul_thr = list()

