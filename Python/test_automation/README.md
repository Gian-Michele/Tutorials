## Test Automation Script v1.0
This script provides example of how use library on python3.

Installation step are:
1. installare la libreria iperf3 con il comando:

	pip install iperf3

	python3 -m pip install --user  --proxy xxx.yyy.zzz.www:port netconf_client (in caso di presenza di un proxy)


The script can be launched using:

	python3 Automated_Test_Script.py [-i IP] [-p PORT] [-o RESULT_FILE]

Only IP of the tested device is needed

It is ppossible use the script to check the attenuator status

    python3 check_attenuator.py [-i IDX] [-a ATT]

**IDX** is the index of the attenuator in the list contained in the configuration file **conifg.ini**

**ATT** is the value of attenuation to set, without this information the program read the value of attenuation actually set




