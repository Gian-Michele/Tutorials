from kafka import KafkaConsumer
import json
import logging


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

    # {'timestamp': 1590609372749960768, 'type': 'UE_MEASUREMENT', 'ueMeasurement': {'cellId': 'Dageraadplaats', 'rsrp': 94, 'rsrq': 27, 'ueCellId': 'Dageraadplaats', 'ueRicId': 'UE_22520'}}

    while True:
        with settings.lock:
            tmp_kafka_topics = settings.configuration['config']['KAFKA_LISTEN_TOPICS']

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
                # if 'type' in payload:
                #     if payload['type'] == 'UE_MEASUREMENT':
                #         logging.debug("Received on KAFKA:\n{msg}".format(msg=payload))
                #         nats_queue.put(payload)
                        # print("At [{time}] on topic [{topic}] received msg type [{type}] that ue [{ue}] sees serving cell [{s_cell}] and neighbour cell [{n_cell}]".format(
                        #     time=datetime.fromtimestamp(payload['timestamp'] // 1000000000),
                        #     topic=msg.topic,
                        #     type=payload['type'],
                        #     n_cell=payload['ueMeasurement']['cellId'],
                        #     ue=payload['ueMeasurement']['ueRicId'],
                        #     s_cell=payload['ueMeasurement']['ueCellId']
                        #     )
                        # )
