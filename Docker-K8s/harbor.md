# Harbor
Harbor is a registy for container images. The https page of Harbor registry can be found in:

https://<harbor_ip_address>/harbor/projects

user: nrtric
password: ******

More detailed documentation ca be found in Harbor [home page](goharbor.io)

In order to upload a new image in the registry the following step are needed:

1) Configure Docker:

configure the http-proxy.conf file in /etc/systemd/system/docker.service.d/ as below (if the file doesnot exist you need to create the folder and the file)

    [Service]
    Environment="HTTP_PROXY=http://localhost:3128"
    Environment="HTTPS_PROXY=http://localhost:3128"
    Environment="NO_PROXY=<harbor ip address>"
    

Create the folder /etc/docker/certs.d/harbor ip address<>/ where it needed to insert the certificate ca.crt

Type the following command to update docker configuration:

    sudo systemctl daemon-reload

    sudo systemctl restart docker

2) Login to the Registry

The command below is used to login to the registry:

    docker login <harbor_ip_address>

user/password are the nrtric/******

3) Tag the images

Use the command below to tag correctly the image:

    docker tag LOCAL_IMAGE_NAME[:LOCAL_TAG] <harbor_ip_address>/nrtric/IMAGE_NAME[:TAG]

where nrtric is the project name

4) Image Push

To push the image use the command below:

    docker push <harbor_ip_address>/nrtric/IMAGE_NAME[:TAG]

5) Image pull

To pull the image use the command below:

    docker pull <harbor_ip_aadress>/nrtric/IMAGE_NAME[:TAG]
