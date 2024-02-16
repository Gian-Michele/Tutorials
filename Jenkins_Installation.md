# Jenkins Installation

The installation of Jenkins could be performed using a container (installation 1) or as a daemon service (installation 2). **Option 2** is more easy to handle for the control node that can exploit the network configuration of the host node

## Installation 1 - installing jenkins using Docker 

First step pull the container from Docker HUB

    docker pull jenkins/jenkins:2.366.3-jdk11

The second step consist on: RUN the Container using docker run containing also the **--env** to handle proxy. The option **--env** could be removed because at the first access the proxy configuration is asked to the user.


    docker run --name jenkins-container -v jenkins_home:/var/jenkins_home -p 8080:8080 -p 50000:50000 --restart=on-failure --env JAVA_TOOL_OPTIONS="-Dhttps.proxyHost=123.123.123.123 -Dhttps.proxyPort=9112 -Dhttp.proxyHost=123.123.123.123 -Dhttp.proxyPort=9112" -d jenkins/jenkins:2.366.3-jdk11
    

Now open a browser on [http://localhost.8080](http://localhost.8080)

The admin user password can be obtained using following command:

    docker exec -it jenckins-container cat /var/jenkins_home/secrets/initialAdminPassword/


Follow the procedure to install the suggested plugins (use retry if at the first attempt some plugin installation fails)

If system seems freezed you can Stop and Start the container because often after the installation of the plugins you need to relaunch the container

## Installation 2 - installing jenksin on an Ubuntu VM 

This is the one is used for the tutorial

First step: check java version using command **java --version**, the version needs to be  openjdk version "11.0.12" 2021-07-20 or higher

Then run the following commands in the same order:

    curl  --proxy http://x.y.z.v:1111 -fsSL https://pkg.jenkins.io/debian-stable/jenkins.io-2023.key | sudo tee  /usr/share/keyrings/jenkins-keyring.asc > /dev/null

then: 

    echo deb [signed-by=/usr/share/keyrings/jenkins-keyring.asc] https:~/~/pkg.jenkins.io/debian-stable binary/ | sudo tee /etc/apt/sources.list.d/jenkins.list > /dev/nul


update the package:

    sudo apt-get update

now install jenkins:

    sudo apt-get install jenkins
Now to modify jenkins configuration you need to change the configuration file (for example could be modified the port where the service is exposed). The command to use is:

    sudo vi /lib/systemd/system/jenkins.service

Once the configuration file is modified the jenkins service needs to be relaunched using following commands

reload the systemctl deamon is needed to update the system

    sudo systemctl daemon-reload

and then restart jenkins

    sudo systemctl restart jenkins

Continuing in the tutorial more explanation on the configuration element will be provided

now the next section will explain how [add a node](Add_a_Node.md)