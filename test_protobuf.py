# https://stackoverflow.com/questions/33816761/google-protocol-buffers-protobuf-in-python3-trouble-with-parsefromstring-en
import oranCommand_pb2


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
    ue = '1'
    cell_1 = '2'
    cell_2 = '3'

    # to encode the protobuf message
    result_msg_step1 = create_handover_command_message(ue, cell_1, cell_2)
    serialized_msg = result_msg_step1.SerializeToString()

    print('proto: \n{}'.format(result_msg_step1))
    print('proto serialized to string: {}'.format(serialized_msg))
    print('proto serialized to bytes: {}'.format(serialized_msg.hex()))

    # to decode the protobuf message
    msg = oranCommand_pb2.OpenRAN_commandMessage()
    msg_size = msg.ParseFromString(serialized_msg)

    print('proto again from pkt of {} bytes: \n{}'.format(msg_size, msg))





