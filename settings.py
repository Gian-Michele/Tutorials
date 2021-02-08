from threading import Lock
import xapp_configuration
import redis
import json
import logging
from datetime import datetime


class Settings:
    def __init__(self):
        self.lock = Lock()
        self.configuration = xapp_configuration.configuration

        # Logging file configuration
        logging.basicConfig(format='[%(levelname)s] %(asctime)s (%(threadName)s) %(message)s',
                            level=self.configuration['config']['LOG_LEVEL'])

        # If config exists in redis, take it and use it
        try:
            r = redis.Redis(host=self.configuration['config']['REDIS_URL'], port=self.configuration['config']['REDIS_PORT'], db=0, decode_responses=True)
            r_keys = r.keys()
            if 'config' in r_keys:
                logging.info('Found configuration in Redis, loading it!')
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

                self.configuration = data

            else:
                logging.info('No configuration found in Redis. Saving deployment configuration...')
                r.set('config', json.dumps(self.configuration["config"]))
                r.set('metadata', json.dumps(self.configuration["metadata"]))
                r.set('jsonSchemaOptions', json.dumps(self.configuration["jsonSchemaOptions"]))
                r.set('uiSchemaOptions', json.dumps(self.configuration["uiSchemaOptions"]))
                r.set('description', str(self.configuration["description"]))
                r.set('last_modified', datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

            logging.info('Configuration: {config}'.format(config=self.configuration))

            # Set the ready state to true
            r.set('ready', 'True')

        except:
            logging.error('Settings Failed to connect to Redis!')

        # else, use the one from the configuration file, already done

    def set_settings(self, key, value):
        try:
            r = redis.Redis(host=self.configuration['config']['REDIS_URL'],
                            port=self.configuration['config']['REDIS_PORT'],
                            db=0, decode_responses=True)
            r.set(key, value)
        except:
            logging.error('Failed to write settings to Redis!')