from threading import Thread
import iperf3


class TestTool:
    def __init__(self, config):
        # Import Test Information
        self.thr = Thread(target=self._do_work, args=(config,))
        self.results = None

    def start_test(self):
        self.thr.start()
        return self

    def get_results(self):
        self.thr.join()
        return self.results

    def start_data_collection(self):
        self.start_test()

    def get_collected_data(self):
        return self.get_results()


class Iperf(TestTool):
    def _do_work(self, config):
        client = iperf3.Client()
        client.duration = config['duration']
        client.server_hostname = config['ip']
        client.port = config['port']
        if "protocol" in config:
            client.protocol = config['protocol']
        if "pkt_size" in config:
            client.blksize = config['pkt_size']
        if "direction" in config:
            if config['direction'].upper() == 'DL':
                client.reverse = False
            elif config['direction'].upper() == 'UL':
                client.reverse = True
        # In case UDP protocol is used, apply the target throughput
        # iperf also accepts a target bandwidth for TCP protocol, but that is not used here
        # if client.protocol == "udp" and "throughput" in self.test_params:
        if "thr_max" in config:
            client.bandwidth = config['thr_max']

        results = client.run()
        if "end" in results.json:
            if client.protocol == "udp":
                self.results = results.json["end"]["sum"]
            elif client.protocol == "tcp":
                self.results = results.json["end"]["sum_received"]

                # add keys to have tcp results similar to udp ones
                self.results['jitter_ms'] = float("nan")
                self.results['lost_packets'] = float("nan")
                self.results['packets'] = float("nan")
                self.results['lost_percent'] = float("nan")
            # remove useless keys
            del self.results['start']
            del self.results['end']
            del self.results['seconds']
            del self.results['bytes']
