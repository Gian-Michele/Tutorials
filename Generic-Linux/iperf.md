## IPERF	

Example of usage of iperf:

	iperf -c <ip_address> -u -b 40M -i 1 -l 1360 -t 100 -p 12345

**-c** the iperf is configured as client and needs to be followed by the ip of the server

**-u** transport protocol selected is UDP (default TCP)

**-b** Tha transmission bandwidth is set(in this case 40M bit)

**-i** indication if the check period (in this case every second report on the transmission is show on the terminal)

**-l** trasport block dimension at UDP level. 1360 is a good dimension 

**-w** for TCP protocol can be set the window dimension for congestion control

**-t** is the time of duration of the test in second (100 s in thi case)

**-p** the port of the server where data has to be transmitted 

Below the command for configure an iperf server at port 12345

	iperf -s -i 1 -p 12345 -u