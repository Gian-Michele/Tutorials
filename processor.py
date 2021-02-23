import logging
import threading
import requests
import action_taker


def send_handover_command(handover_list, handover_nats_topic):

    action_taker.trigger_handover(handover_list, handover_nats_topic)


def send_subband_masking_command():
    pass


def publish_on_kafka(out_queue, topic, data):
    '''
     topic: Kafka topic where to publish the data
     data: Data to send on the Kafka databus. This should be JSON
    '''
    out_queue.put(
        {
            'topic': topic,
            'data': data
        }
    )


def create_api_url(settings, endpoint):
    with settings.lock:
        drax_ric_api_gateway_url = settings.configuration['config']['API_GATEWAY_URL']
        drax_ric_api_gateway_port = settings.configuration['config']['API_GATEWAY_PORT']

    api_url = 'http://{drax_ric_api_gateway_url}:{drax_ric_api_gateway_port}/api{endpoint}'.format(
        drax_ric_api_gateway_url=drax_ric_api_gateway_url,
        drax_ric_api_gateway_port=drax_ric_api_gateway_port,
        endpoint=endpoint
    )

    return api_url


def run(settings, in_queue, out_queue, data_store):

        ### YOUR CODE HERE


        ### Following is a list of examples, uncomment to test them out

        # ### Example 1: Just logging all the messages received from the dRAX Databus
        # logging.info("Received message from dRAX Databus!")
        # logging.debug("dRAX Databus message: {data}".format(data=data))

        # ### Example 2: Publishing one time or event-based data on the dRAX Databus
        # ###            We will publish on topic "my_test_topic", and just republish the "data" data
        # publish_on_kafka(out_queue, "my_test_topic", data)

        # ### Example 3: Periodic publishing of data
        # ###            We will save some data in the data_store and periodically publish that data_store
        # ###            We just save the data in the data_store, and the periodic_publisher thread is periodically publishing the data_store
        # ###            The settings of the periodic publishing is in the xapp_configuration and can be real-time configured
        # data_store = data

        # ### Example 4: Send handover command
        handover_list = [
             {'ueIdx': 'ueRicId_to_handover', 'targetCell': 'Bt1Cell', 'sourceCell': 'Bt2Cell'}
        ]
        # send_handover_command(settings, handover_list)

        ### Example 5: Send subband masking command
        # subband_mask = [
        #     {'cell': 'Cell_1', 'num_of_bands': '13', 'mask': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]},
        #     {'cell': 'Cell_2', 'num_of_bands': '9', 'mask': [1, 1, 1, 1, 1, 1, 1, 1, 1]}
        # ]
        # send_subband_masking_command(settings, subband_mask)

        # ### Example 6: How to use the dRAX RIC API Gateway
        # endpoint = '/xappconfiguration/discover/services/netconf'
        # api_response = requests.get(create_api_url(settings, endpoint))
        #
        # if api_response.status_code == 200:
        #     try:
        #         logging.info(api_response.json())
        #     except:
        #         logging.info('Failed to load JSON, showing raw content of API response:')
        #         logging.info(api_response.text)

        # ### Example 7: Get the ports where the netconf servers of cells are exposed
        # endpoint = '/xappconfiguration/discover/services/netconf'
        # api_response = requests.get(create_api_url(settings, endpoint))
        #
        # for cell, cell_info in api_response.json().items():
        #     for port in cell_info['spec']['ports']:
        #         if port['name'] == 'netconf-port':
        #             logging.info('Cell [{cell}] has NETCONF exposed on port [{port}]'.format(
        #                 cell=cell,
        #                 port=port['node_port']
        #                 )
        #             )
