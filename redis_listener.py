from redis import StrictRedis
import logging
import json


def run(settings):
    try:
        address_val = settings.configuration['config']['REDIS_URL']
        port_val = settings.configuration['config']['REDIS_PORT']
        print('address: {}'.format(address_val))
        print('port: {}'.format(port_val))
        r = StrictRedis(host=address_val, port=port_val)

        pubsub = r.pubsub()
        pubsub.psubscribe('__keyspace@0__:*')

        logging.info('Starting Redis Listener...')

        # Blocking
        for item in pubsub.listen():
            logging.info('Detected change in Redis configuration. Updating real time xApp config...')

            data = {}
            temp = r.get('metadata')
            if temp:
                data["metadata"] = json.loads(r.get('metadata'))
            else:
                data["metadata"] = {}

            temp = r.get('config')
            if temp:
                data["config"] = json.loads(r.get('config'))
            else:
                data["config"] = {}

            temp = r.get('jsonSchemaOptions')
            if temp:
                data["jsonSchemaOptions"] = json.loads(r.get('jsonSchemaOptions'))
            else:
                data["jsonSchemaOptions"] = {}

            temp = r.get('uiSchemaOptions')
            if temp:
                data["uiSchemaOptions"] = json.loads(r.get('uiSchemaOptions'))
            else:
                data["uiSchemaOptions"] = {}

            data["description"] = r.get('description')

            data["last_modified"] = r.get('last_modified')

            settings.configuration = data

            logger = logging.getLogger()
            logger.setLevel(settings.configuration['config']['LOG_LEVEL'])

            logging.info('New configuration set!')

            logging.debug('New configuration: {config}'.format(config=settings.configuration))

    except:
        logging.error('Failed to connect to Redis!')
