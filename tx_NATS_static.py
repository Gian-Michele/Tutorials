
import json
import time
import asyncio
import configparser
import ssl
from nats.aio.client import Client as NATSClient


def tx_to_external_platform(message_to_tx, topic, num_message):

    # read information for transmission
    config = configparser.ConfigParser()
    fp_config = open('nats_config.ini')
    config.read_file(fp_config)
    fp_config.close()

    nc_tx = NATSClient()  # nc client to receive message from subscription
    nats_server_ip = config.get('NATS_SERVER', 'ip_address', fallback="163.162.89.28")
    nats_server_port = config.getint('NATS_SERVER', 'port', fallback=4222)
    nats_use_tls = config.get('NATS_SERVER', 'use_tls')
    nats_user = config.get('NATS_SERVER', 'user')
    nats_pass = config.get('NATS_SERVER', 'password')
    nats_cert_file = config.get('NATS_SERVER', 'cert_file')
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(send_to_nats_static(nc_tx, loop, message_to_tx, num_message, nats_server_ip,
                                                nats_server_port, topic, nats_use_tls, nats_user, nats_pass,
                                                nats_cert_file))


async def send_to_nats_static(nc_tx, loop: asyncio.AbstractEventLoop, message, counter, nats_server_ip,
                              nats_server_port, topic, nats_use_tls, nats_user, nats_pass, nats_cert_file):
    nats_topic = topic

    msg_to_tx = {'NUM': counter, 'msg': message}
    tx = json.dumps(msg_to_tx).encode()

    if nats_use_tls:
        ssl_ctx = ssl.create_default_context(purpose=ssl.Purpose.SERVER_AUTH, cafile=nats_cert_file)
        await nc_tx.connect(
            servers="tls://{}:{}".format(nats_server_ip, nats_server_port),
            loop=loop,
            user=nats_user,
            password=nats_pass,
            tls=ssl_ctx)
    else:
        await nc_tx.connect("{}:{}".format(nats_server_ip, nats_server_port), loop=loop)

    await nc_tx.publish(nats_topic, tx)
    print('Sent Json {} bytes to NATS server at {}:{}'.format(len(message), nats_server_ip, nats_server_port))
    # Terminate connection to NATS.
    await nc_tx.close()

