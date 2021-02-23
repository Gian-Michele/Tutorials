from kafka import KafkaProducer
import json
import time
kafka_producer = KafkaProducer(bootstrap_servers='192.168.2.10:31090',
                               value_serializer=lambda v: json.dumps(v).encode('utf-8'))
if kafka_producer.bootstrap_connected():
    print('Connected to Kafka')
    message = {
        'info1': 1,
        'info2': 2
    }
    message_to_tx = json.dumps(message, indent=2, sort_keys=True)

    # kafka_producer.send('node-info', value=message_to_tx.encode())
    kafka_producer.send(topic='node-info', partition=0, value=message)
    # need to wait some second before close the program
    time.sleep(2)
