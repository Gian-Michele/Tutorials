from kafka import KafkaConsumer
import logging
import json
print("Kafka Consumer:")
try:
    consumer = KafkaConsumer(
        bootstrap_servers='localhost:9092',
        value_deserializer=lambda m: json.loads(m.decode('utf-8'))
    )
    logging.info("Succesfully connected to Kafka server [{url}:{port}]".format(
        url='localhost',
        port='9092'
    ))
    val_sub = consumer.subscription()
    print('Subscription: {}'.format(val_sub))

    kafka_topics = 'node-info'
    logging.info('Subscribed to new topics: [{topics}]'.format(topics=kafka_topics))

except:
    logging.error("Failed to connect to Kafka Topic!")

while True:
    if val_sub is None:
        consumer.subscribe(kafka_topics)
        val_sub = consumer.subscription()
        print('Subscribed to {}'.format(val_sub))

    raw_msgs = consumer.poll(timeout_ms=1000)
    for tp, msgs in raw_msgs.items():
        for msg in msgs:
            json_data = json.dumps(msg.value, indent=2, sort_keys=True)
            top = msg.topic
            print("topic {} and topic in msg {}\n msg {}".format(tp[0], top, json_data))

