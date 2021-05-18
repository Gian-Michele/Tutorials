# https://stackoverflow.com/questions/33816761/google-protocol-buffers-protobuf-in-python3-trouble-with-parsefromstring-en

import oranCommand_pb2
from xapp_configuration import configuration
from pynats import NATSClient


def stop_cell_command_message(target_cell):
    peer_msg = oranCommand_pb2.OpenRAN_commandMessage()
    peer_msg.messageType = 3
    peer_msg.originator = 'xAPP'

    cell = oranCommand_pb2.OpenRAN_StopCellRequest()
    cell.cellId = target_cell

    peer_msg.stopcellrequest.CopyFrom(cell)

    return peer_msg


def create_handover_command_message(ue_idx, target_cell, source_cell):
    peer_msg = oranCommand_pb2.OpenRAN_commandMessage()
    peer_msg.messageType = 1
    peer_msg.originator = 'HandoverManager'

    handover = oranCommand_pb2.OpenRan_UeHandoverCommand()
    handover.ueRicId = ue_idx
    handover.targetCell = target_cell
    handover.sourceCell = source_cell

    peer_msg.handover.CopyFrom(handover)

    return peer_msg


if __name__ == '__main__':
    action = 1
    ue = '1'
    targetCell = '153'  # target cell used also to force switch off
    sourceCell = '3'

    # to encode the protobuf message
    result_msg_step1 = create_handover_command_message(ue, targetCell, sourceCell)
    stop_msg_step1 = stop_cell_command_message(targetCell)
    serialized_msg = result_msg_step1.SerializeToString()
    serialized_stop_msg = stop_msg_step1.SerializeToString()
    print('---------------------')
    print('proto: \n{}'.format(result_msg_step1))
    print('proto serialized to string: {}'.format(serialized_msg))
    print('proto serialized to bytes: {}'.format(serialized_msg.hex()))
    print('---------------------')
    print('proto: \n{}'.format(stop_msg_step1))
    print('proto serialized to string: {}'.format(serialized_stop_msg))
    print('proto serialized to bytes: {}'.format(serialized_stop_msg.hex()))
    print('---------------------')

    # to decode the protobuf message
    msg = oranCommand_pb2.OpenRAN_commandMessage()
    msg2 = oranCommand_pb2.OpenRAN_commandMessage()
    msg_size = msg.ParseFromString(serialized_msg)
    msg2_size = msg2.ParseFromString(serialized_stop_msg)

    print('proto again from pkt of {} bytes: \n{}'.format(msg_size, msg))
    print('proto again from pkt of {} bytes: \n{}'.format(msg2_size, msg2))

    url = configuration['config']['NATS_URL']
    topic = configuration['config']['DRAX_COMMAND_TOPIC']
    print('NATS url {}\n TOPIC {}'.format(url, topic))

    if action == 1:
        msg_to_send = serialized_stop_msg
    else:
        msg_to_send = serialized_msg
    with NATSClient(url) as client:
        client.publish(topic, payload=msg_to_send)



