configuration = {
    "metadata": {
        "name": "xApp Name",
        "configName": "",
        "namespace": "default"
    },
    "description": "xApp Description...",
    "last_modified": "06/07/2020 23:32:00",
    'config': {
        'REDIS_URL': '',
        'REDIS_PORT': 0,
        'LOG_LEVEL': 20,  # CRITICAL=50, ERROR=40, WARNING=30, INFO=20, DEBUG=10, NOTSET=0
        'KAFKA_URL': 'localhost',   # '10.20.20.20',
        'KAFKA_PORT': '9092',   # '31090',
        'kafka_producer_topic': 'node-info',    # 'xapp_specific_topic',
        'KAFKA_LISTEN_TOPIC': 'test2',
        'periodic_publish': True,
        'publish_interval': 1  # in seconds
    },
    "jsonSchemaOptions": {},
    "uiSchemaOptions": {}
}
