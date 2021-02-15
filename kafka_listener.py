from kafka import KafkaConsumer
import json
import logging
import datetime
from controller.nats_interface import InstructiveInterface


def parse_kafka_topics_from_settings(tmp_kafka_topics):
    kafka_topics = set()

    # Remove whitespace from string and split by commas
    parsed_kafka_topics = tmp_kafka_topics.replace(" ", "").split(',')

    for topic in parsed_kafka_topics:
        kafka_topics.add(topic)

    return kafka_topics


def run(settings, in_queue):

    logging.info("Starting Kafka listener...")

    # TODO create multi kafka topic support, use threads as listeners

    with settings.lock:
        kafka_url = settings.configuration['config']['KAFKA_URL']
        kafka_port = settings.configuration['config']['KAFKA_PORT']

    try:
        consumer = KafkaConsumer(
            bootstrap_servers=[kafka_url + ':' + kafka_port]
        )
        logging.info("Succesfully connected to Kafka server [{url}:{port}]".format(
            url=kafka_url,
            port=kafka_port
        ))
    except:
        logging.error("Failed to connect to Kafka Topic!")
        return

    tx_info = InstructiveInterface('node-info')
    # {
    # 'timestamp': 1590609372749960768, 'type': 'UE_MEASUREMENT',
    # 'ueMeasurement': {
    # 'cellId': 'Dageraadplaats', 'rsrp': 94, 'rsrq': 27, 'ueCellId': 'Dageraadplaats', 'ueRicId': 'UE_22520'
    # }
    # }

    default_json = {
        "cpuLoad": 1.0,
        "eTime": 1963800,
        "numRruDescriptors": 1,
        "numUeDescriptors": 0,
        "sTime": 1963500,
        "rru": [
            {
                "dsThroughput": 6316,
                "ipAddress_p1": "192.168.10.4",
                "pci": 100,
                "rtt_latency": 694,
                "usThroughput": 936
            }
        ]
        # "ues": [
        #    {
        #        "pci": 10,
        #        "rnti": 10,
        #        "tmsi_flag": 10,
        #        "mmec": 10,
        #        "m-timsi": "timsi",
        #        "dlThroughput": 10,
        #        "ulThroughput": 10,
        #        "rsrp": 10,
        #        "wbCqi": 10,
        #        "wbRi": 10,
        #        "puschSnr": 10,
        #        "pucchSnr": 10,
        #        "dlMcs": 10,
        #        "ulMcs": 10,
        #        "numDlRbs": 10,
        #        "numUlRbs": 10,
        #        "maxDlRank": 2,
        #        "maxDlMcs": 28,
        #        "maxUlMcs": 28,
        #        "maxNumDlRbs": 30,
        #        "maxNumUlRbs": 20,
        #        "rlcBufferDl": 10,
        #        "rlcBufferUl": 10,
        #        "numNeighborDescriptors": 10,
                # "neighborCells": [
                #    {
                #        "pci": 10,
                #        "rsrp": 10,
                #        "rsrq": 10
                #    },
                #    {
                #        "pci": 10,
                #        "rsrp": 10,
                #        "rsrq": 10
                #    },
                #    {
                #        "pci": 10,
                #        "rsrp": 10,
                #        "rsrq": 10
                #    }
                #]
        #    }
        #]
    }

    accum_counter = 10

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
                        print("At [{time}] received msg type [{type}] that ue [{ue}] sees serving "
                              "cell [{s_cell}] and neighbour cell [{n_cell}]".format(time=datetime.datetime.fromtimestamp(payload['timestamp'] // 1000000000),
                              type=payload['type'],
                              n_cell=payload['ueMeasurement']['cellId'],
                              ue=payload['ueMeasurement']['ueRicId'],
                              s_cell=payload['ueMeasurement']['ueCellId'])
                              )
                    if payload['type'] == 'THROUGHPUT_REPORT':
                        print("At [{time}] received msg type [{type}] that ue [{ue}] sees serving cell [{cell}] "
                              "DL THR [{dlThroughput}], UL THR [{ulThroughput}]".format(
                              time=datetime.datetime.fromtimestamp(payload['timestamp'] // 1000000000),
                              type=payload['type'],
                              cell=payload['throughputReport']['cellId'],
                              ue=payload['throughputReport']['ueRicId'],
                              dlThroughput=payload['throughputReport']['dlThroughput'],
                              ulThroughput=payload['throughputReport']['ulThroughput'])
                              )

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

                if 'beaconInfo' in payload:
                    print("Received Beacon {}".format(payload['beaconInfo']['componentId']))
        counter = counter + 1
        if counter == accum_counter:
            print('-----------------------------------')
            print('-----------------------------------')
            print('--    TX DATA TO Near RT RIC     --')
            print('-----------------------------------')
            print('-----------------------------------')
            tx_info.get_instance().tx_from_external_platfom(default_json)
            counter = 0

