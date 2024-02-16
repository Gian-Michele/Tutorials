from kafka import KafkaProducer
from json import dumps
import jsonpickle


def run(settings, kafka_outgoing_queue):
    '''

    :param settings:
    :param kafka_outgoing_queue:
    :return:

    The kafka_outgoing_queue should receive data in the format:
    {
        'topic': 'Kafka_Topic',
        'data': {}
    }
    '''

    ### Kafka producer
    with settings.lock:
        kafka_producer = KafkaProducer(bootstrap_servers=[settings.configuration['config']['KAFKA_URL'] + ':' + settings.configuration['config']['KAFKA_PORT']],
                                       value_serializer=lambda x:
                                       dumps(jsonpickle.encode(x)).encode('utf-8')
                                       )

    while True:
        outgoing_data = kafka_outgoing_queue.get()
        kafka_producer.send(outgoing_data['topic'], outgoing_data['data'])
