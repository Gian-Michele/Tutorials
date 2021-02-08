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


def goodbye(settings):
    settings.set_settings('ready', 'False')


if __name__ == '__main__':
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
    while True:
        time.sleep(1)
