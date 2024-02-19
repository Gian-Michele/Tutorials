import iperf3
import json

# ---------------------
ip = '163.162.89.53'
port = 5201
protocol = 'udp'
duration = 10
direction = 'DL'
pkt_size = 1360
rate = 50   # Mbps
# --------------------

client_iperf = iperf3.Client()
if direction == 'DL':
    print('DL Direction')
    client_iperf.reverse = True
else:
    print('UL Direction')
    client_iperf.reverse = True
client_iperf.blksize = pkt_size
client_iperf.duration = duration
client_iperf.protocol = protocol
client_iperf.server_hostname = ip
client_iperf.port = port
bit_rate = int(rate) * 1000000
client_iperf.bandwidth = bit_rate
results = client_iperf.run()
# for debug
# print("result:\n{}".format(json.dumps(results.json, indent=2)))

if "end" in results.json:
    if client_iperf.protocol == 'udp':
        received_bit_per_second = results.json['end']['sum']['bits_per_second'] / 1000000
        num_packets = results.json['end']['sum']['packets']
        jitter_ms = results.json['end']['sum']['jitter_ms']
        lost_pertcent = results.json['end']['sum']['lost_percent']

        result_step = {
            'direction': direction,
            'packet_size': pkt_size,
            'tx_packet': bit_rate/1000000,
            'rx_packet': received_bit_per_second,
            'num_packets': num_packets,
            'lost_percent': lost_pertcent,
            'jitter_ms': jitter_ms
        }
    else:
        received_bit_per_second = results.json['end']['sum']['bits_per_second'] / 1000000
        num_packets = results.json['end']['sum']['packets']
        jitter_ms = results.json['end']['sum']['jitter_ms']
        lost_pertcent = results.json['end']['sum']['lost_percent']
        result_step = {
            'direction': direction,
            'packet_size': pkt_size,
            'tx_packet': bit_rate/1000000,
            'rx_packet': received_bit_per_second,
            'num_packets': num_packets,
            'lost_percent': lost_pertcent,
            'jitter_ms': jitter_ms
        }

    print ( 'result:\n{}'.format(json.dumps(result_step, indent=2)))