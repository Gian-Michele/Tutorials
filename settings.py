from threading import Lock
import xapp_configuration
import redis
import json
import logging
from datetime import datetime


class Settings:
    def __init__(self):
        self.pci_152 = 0    # default value
        self.pci_153 = 1    # default value
        self.pci_152_status = 'OFF'    # ON/OFF default value OFF
        self.pci_153_status = 'OFF'    # ON/OFF default value OFF
        date = str(datetime.now())
        date_tmp = date.split(':')
        date_tmp2 = date_tmp[0] + '-' + date_tmp[1] + '-' + date_tmp[2]
        date_time = date_tmp2.split(' ')
        log_file_name = date_time[0] + '-' + date_time[1] + '-xapp.log'

        self.lock = Lock()
        self.configuration = xapp_configuration.configuration
        # add by TIM to update NATS Information

        self.nats_url = self.configuration['config']['NATS_URL']
        self.nats_topic = self.configuration['config']['DRAX_COMMAND_TOPIC']

        # Logging file configuration
        self.log_obj = logging.getLogger('xapp-log')
        formatter = logging.Formatter('[%(levelname)s] %(asctime)s (%(threadName)s) %(message)s')
        self.file_handler = logging.FileHandler(log_file_name)
        self.file_handler.setFormatter(formatter)
        self.log_level = self.configuration['config']['LOG_LEVEL']
        if self.log_level == 20:
            self.log_obj.setLevel(level=logging.INFO)
        self.log_obj.addHandler(self.file_handler)

        # information on the log level
        # logging.basicConfig(format='[%(levelname)s] %(asctime)s (%(threadName)s) %(message)s',
        #                    level=self.configuration['config']['LOG_LEVEL'])

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

    # set the pci value of the cells
    def set_pci(self, pci_152, pci_153):
        self.pci_152 = pci_152
        self.pci_153 = pci_153

    # return the information on the pci involved
    def get_pci(self):
        return self.pci_152, self.pci_153

    def print_log(self, msg, type_log):
        if type_log == 'INFO':
            self.log_obj.info(msg)
        if type_log == 'DEBUG':
            self.log_obj.debug(msg)
        if type_log == 'WARNING':
            self.log_obj.warning(msg)
        if type_log == 'ERROR':
            self.log_obj.error(msg)
