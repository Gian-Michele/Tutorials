# Useful Linux Command

This tutorial contains a list of useful command using linux (ubuntu)

### sctp

To verify a bind port in a system (include sctp port) the command to use is:

    sudo netstat --sctp -tulpn

### Disc memory

To verify the memory on the disc use the command:

    df -h

To verify the dimension of a folder

    du -hs <folder name>

### networking

In order to configure the interface in a ubuntu machine you have to setup the file **/etc/network/interfaces**. The two option are:

- dhcp based interface configuration:

        auto eth0
        iface eth0 inet dhcp

- static configuration:

        auto eth0
        iface eth0 inet static
        address 192.168.3.202
        netmask 255.255.248.0
        gateway 192.168.3.1
        dns-nameservers 192.168.3.3 192.168.3.4


 to update the configuration can be used the command:

    sudo ifdown eth0 && sudo ifup eth0

 or

    sudo systemctl restart networking


### ping command

the most generic ping command in ubuntu is:

		ping -c <numero ping> -i <secondi di attesa> -s <numero byte ping> <indirizzo ip>

where **-s** is the size of ping in byte with additional 8 byte of the header

### routing command

To add static route to a not visible machine the command to use is:

	sudo route add -net x.y.z.0 netmask 255.255.255.0 gw x1.y1.z1.k1

where -net the destination subnetwork  and **gw** is the IP address  *x1.y1.z1.k1* that allow mi to arrive at the destination subnetwork

**route del -net** command can be used to remove a static route

The GW x1.y1.z1.k1 has to be configured to pass the data through the interfaces using the script below that allow to pass the packet to the WANIF an LANIF interfaces:

```bash
#! /bin/bash

IPTABLES=/sbin/iptables

WANIF='ens160'
LANIF='ens192'

# enable ip forwarding in the kernel
echo 'Enabling Kernel IP forwarding...'
/bin/echo 1 > /proc/sys/net/ipv4/ip_forward

# flush rules and delete chains
echo 'Flushing rules and deleting existing chains...'
$IPTABLES -F
$IPTABLES -X

# enable masquerading to allow LAN internet access
echo 'Enabling IP Masquerading and other rules...'
$IPTABLES -t nat -A POSTROUTING -o $LANIF -j MASQUERADE
$IPTABLES -A FORWARD -i $LANIF -o $WANIF -m state --state RELATED,ESTABLISHED -j ACCEPT
$IPTABLES -A FORWARD -i $WANIF -o $LANIF -j ACCEPT

$IPTABLES -t nat -A POSTROUTING -o $WANIF -j MASQUERADE
$IPTABLES -A FORWARD -i $WANIF -o $LANIF -m state --state RELATED,ESTABLISHED -j ACCEPT
$IPTABLES -A FORWARD -i $LANIF -o $WANIF -j ACCEPT

echo 'Done.'
```

In order to allow to know the IP of the device that contact me the masquerading has to be removed deleting the rows with MASQUERADING

Alternative mode to allow packet forwording is using the command below:

    sudo sysctl net.ipv4.conf.all.forwarding=1
    sudo iptables -P FORWARD ACCEPT
