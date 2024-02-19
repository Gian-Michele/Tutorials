# DOCKER COMMANDS 
General Docker documentation can be found in: [https://docs.docker.com/](https://docs.docker.com/)],  more detail for ubuntu host installation on in [https://docs.docker.com/engine/install/ubuntu/](https://docs.docker.com/engine/install/ubuntu/)

Additional information below:

**Installazione di Doker**

Start updating existing packege:

    sudo apt-get update

Needed library

    sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common    

Adding GPG di Docker (GPG is an open-source data encryption system (documents or messages) based on a public / private key pair, which makes use of complex non-reversible algorithms)

    curl -fsSL https://download.docker.com/linux/ubuntu/gpg --proxy http:~/~/<proxy> | sudo apt-key add -


Now is connected to the Docker repository using the following command for x86_64 e amd64 with Ubuntu OS
    
    sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"


Now the last packet to install

    sudo apt-get install docker-ce docker-ce-cli containerd.io


can set up the command docker to be run without sudo in front using the following command:

    sudo usermod -aG docker labuser


**Container Images**

The list of images can be obtained with:

    docker images

or

    docker image ls


In order to build a new image use the following command:

    docker build . -t <name of the images>:<TAG> -f <dockerfiles>  --no-cache 


**es**: *docker build . -t lte_image:123 -f dockerfiles_lte.dockerfile --no-cache*

Can be used -t or --tag to give a name to the images

To remove the image can be used the following command

    docker rmi <image name>:<TAG>


**es**: docker rmi lte_image:latest

In order to save an image in a file to easy transport the image 

    docker save -o <file name>.tar <image name-tag>

**es**: *docker save -o lte.saved_image.tar lte_image:123*

In order to load an image from a .tar file 

    docker load -i <nome file>.tar


**Container Volume**

It is possible create some volume that can can be attached to a container in order to be read when someone docker crash for debug


    docker volume create <volume-name>

To read the volume information use the following command:

    docker volume inspect <volume-name>


**es**: //docker volume inspect lte_volume// allow to shows:

{{{"CreatedAt": "2019-09-24T17:11:28+02:00",
"Driver": "local",
"Labels": null,
"Mountpoint": "/var/lib/docker/volumes/lte_volume/_data",
"Name": "phluido.lte",
"Options": null,
"Scope": "local"
}}}

**Mountpoint **is the directory location of the information


To read information in the volumes could be usefol change some permission

    sudo chown -R ubuntu /var/lib/docker/volumes

Also per for group:

    sudo chgrp -R ubuntu /var/lib/docker/volumes   

Example of command to copy file in the volume:

    cp <nome file>.cfg /var/lib/docker/volumes/lte_volume/_data


To list the information in the volume:

    sudo ls  var/lib/docker/volumes/lte_volume/_data


To remove the volume:

    docker volume rm <volume-name> 

To observe the memory allocated to a volume use:

    docker system df -v

**Docker Run**

An example of docker run with a volume attached to the image~:

    docker run -ti --rm --privileged --shm-size=256M --network="host" --ipc="host" --mount source=lte_volume, target=/volume lte_images confing_file.cfg


the parameter

**--rm**: at the end of the command also the container is closed'

**--network="host"**: allows to expose the same network of the host

**--mount source=lte_volume,target=/volume** this is the commando to mounr the volume with name lte_volume to the target directory defined in the container

In order to run in background can be used the command:


    /dev/null 2>&1 &

**-d**: can be used to be detacched by the container after the run


    sudo docker run --name nss2 -p 831:830 -d netconf/network-slice-subnet:1.0


**-p** is used to expose externally a different port respect the internal one. In the example above 830 is exposed to port 831

**--name** give a name to the container

The list of running and stopped container can be showed using:

    docker ps -a



To restart the container:


    docker restart <Container Name>


To stop the container:

    docker stop <Container Name>


To enter using a terminal inside the container the command to use:

    sudo docker exec -it <container name> bash


To remove a container :
    
    docker rm <Container name>

It is possible copy a fine inside a container using the comand:

    sudo docker cp <nome file>  <container id>:/<container directory destination>


### DOCKER behind a PROXY

To handle the proxy in docker the following commands are obtained by the link: [https://www.serverlab.ca/tutorials/containers/docker/how-to-set-the-proxy-for-docker-on-ubuntu/](https://www.serverlab.ca/tutorials/containers/docker/how-to-set-the-proxy-for-docker-on-ubuntu/)

Step1) It is needed to create the folder docker.service.d 

    sudo mkdir /etc/systemd/system/docker.service.d


Step2)  create the file **/etc/systemd/system/docker.service.d/http-proxy.conf** where proxy configuration will be inserted as below

    Environment="HTTP_PROXY=http://proxy.example.com:80/" 
    Environment="HTTPS_PROXY=http://proxy.example.com:80/"


Step3) launch load new configuration using command below

    sudo systemctl daemon-reload


Verify that the configuration has been loaded using the command:

    sudo systemctl show ~-~-property Environment docker

Restart Docker:

    sudo systemctl restart docker

### DOCKER free memory

The fast way to free memory in Docker is use the command below:

    docker system prune

This will remove all the stopped container and unused volumes

In order to remove all a more strong command using -a or --all:

    docker system prune -a 
    
    