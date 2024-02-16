# Jenkins Update

This section describe what is needed to know for update Jenkins

Can be useful maintain a backup of your data that can be found in the folder **/var/lib/jenkins/** in /tmp/ or other folder. The dimension is 3-5 GB and can require some minutes

In order to update the jenkins version. Can be suggest to copy the configuration file of the service contained in: **/lib/systemd/system/jenkins.service**

The main configuration are information are:
    
    Environment="JENKINS_PORT="-1"
    Environment="JENKINS_HTTPS_LISTEN_ADDRESS=0.0.0.0"
    Environment="JENKINS_HTTPS_PORT=443"
    Environment="JENKINS_HTTPS_KEYSTORE=/var/lib/jenkins/jkeystore.jks"
    Environment="JENKINS_HTTPS_KEYSTORE_PASSWORD=***"
    AmbientCapabilities=CAP_NET_BIND_SERVICE

Remember also to maintain a copy of the **jkeystore.jks** and his password associated 


=== The update step are: ===

**step1**: verify jenkins certifacate in the jenkins file at link [https://www.jenkins.io/doc/book/installing/linux/](https://www.jenkins.io/doc/book/installing/linux/)

**step2**: launch command:

    sudo apt get update

**step 3**: download and install last version

    sudo apt-get --only-upgrade install jenkins


**step 4**: stop running jenkins

    sudo systemctl stop jenkins

**step 5**: set the service configuration following the copied old configuration information

**step 6**: restart jenkins service

    sudo systemctl daemon-reload
    sudo systemctl restart jenkins
