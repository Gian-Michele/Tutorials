SSH Authentication & Remote Switch on/off
=====================================================================

Configurazione SSH
==================

SSH Keys generation on the controller:

	ssh-keygen

This will create inside the user's home a hidden folder named .ssh containing 2 files: id_rsa (the private key) and id_rsa.pub (the public key).

The content of public key (id_rsa.pub) must be pasted into the file */root/.ssh/authorized_keys* in each eNB in order to allow the controller to log in as root inside that machine (to shutdown the machine) without password prompting.

If the file authorized_keys does not exist on the eNB, create it (**as root using command sudo su**) with command:
	
	touch /root/.ssh/authorized_keys
	chmod 600 /root/.ssh/authorized_keys

Then copy the id_rsa.pub file on the remote eNB from the controller and then, on the eNB, put the content of the file in authorized_keys (**as root**):

	cat id_dsa.pub >> /root/.ssh/authorized_keys

SWITCH OFF PC
=========================

The command to use in order to switch off the PC is:

	ssh -i id_rsa root@192.168.x.x shutdown -h now

the command-line can be wrote in a std::string and than sent to the system as:

	system(string.c_string()):


SWITCH ON PC
=========================

The command to use in order to switch on the PC is wakeon lan commad:
	
	wakeonlan MAC_ADDRSS

 