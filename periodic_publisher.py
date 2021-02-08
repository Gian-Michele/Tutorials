import time
import logging

def run(settings, out_queue, data_store):
    logging.info('Starting periodic publisher thread...')
    while True:
        # Lock settings and get the settings
        with settings.lock:
            periodic_publish = settings.configuration['config']['periodic_publish']
            kafka_producer_topic = settings.configuration['config']['kafka_producer_topic']
            publish_interval = settings.configuration['config']['publish_interval']

        # If periodic publish is enabled, publish on kafka
        if periodic_publish:
            data = {'topic': kafka_producer_topic, 'data': data_store}
            out_queue.put(data)

            time.sleep(publish_interval)
