configuration = {
    "metadata": {
        "name": "xApp Tim",
        "configName": "",
        "namespace": "default"
    },
    "description": "xApp Description...",
    "last_modified": "06/03/2021 23:32:00",
    'config': {
        'NATS_URL': 'nats://192.168.2.10:31000',
        'DRAX_COMMAND_TOPIC': 'Topic_OPENRAN_COMMANDS.OranController',
        'REDIS_URL': '192.168.2.10',
        'REDIS_PORT': 32000,
        'LOG_LEVEL': 40,  # CRITICAL=50, ERROR=40, WARNING=30, INFO=10, DEBUG=20, NOTSET=0
        'KAFKA_URL': '192.168.2.10',   # '10.20.20.20',
        'KAFKA_PORT': '31090',   # '31090',
        'kafka_producer_topic': 'xapp_specific_topic',
        'KAFKA_LISTEN_TOPIC': 'test2',
        'periodic_publish': True,
        'publish_interval': 1  # in seconds
    },
    "jsonSchemaOptions": {},
    "uiSchemaOptions": {}
}
