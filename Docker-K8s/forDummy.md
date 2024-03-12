# Starting using K8s

some useful tool that you need are kubectl and helm. The installation of these tool can be done exploiting the below script:



```bash
#!/bin/bash

# k8s version 1.27
KUBEV="v1.27"
HELMV="3.5.4"
proxy="http://163.162.8.137:9112"

sudo apt-get update
# apt-transport-https may be a dummy package; if so, you can skip that package
sudo apt-get install -y apt-transport-https ca-certificates curl

# If the folder `/etc/apt/keyrings` does not exist, it should be created before the curl command, read the note below.
# sudo mkdir -p -m 755 /etc/apt/keyrings
dirname='/etc/apt/keyrings'

if [ -d "$dirname" ]; then
    echo "$dirname exists and is a directory."
else
    echo "$dirname does not exist, it will be create now"
    sudo mkdir -p -m 755 $dirname
fi

#echo -e "download the keyring.gpg on /etc/apt/keyrings\n"
curl --proxy ${proxy} -fsSL  https://pkgs.k8s.io/core:/stable:/${KUBEV}/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

# This overwrites any existing configuration in /etc/apt/sources.list.d/kubernetes.list
#echo -e "existing configuration in /etc/apt/sources.list.d/kubernetes.list will be overwritten\n"
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/${KUBEV}/deb/ /"| sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl


## BELOW DOESN'T WORK
#curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
#sudo apt-get install apt-transport-https --yes
#echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
#sudo apt-get update
#sudo apt-get install helm

export https_proxy=${proxy}
if [ ! -e helm-v${HELMV}-linux-amd64.tar.gz ]; then
   wget https://get.helm.sh/helm-v${HELMV}-linux-amd64.tar.gz
fi

dirname='/user/local/bin/helm'

if [ -d "$dirname" ]; then
    echo "$dirname exists and is a directory."
else
    echo "$dirname does not exist, it will be create now"
    sudo mkdir -p -m 755 $dirname
fi

tar -xvf helm-v${HELMV}-linux-amd64.tar.gz
sudo mv linux-amd64/helm /usr/local/bin/helm


while ! helm version; do
  echo "Waiting for Helm to be ready"
  sleep 5
done
```

then is needed copy the kubeconfig.yaml configuration file in the folder ./kube as file config, this is possible using the following commands:

    mkdir .kube
    mv kubeconfig.yaml ./kube/config
    sudo chown $(id -u):$(id -g) $HOME/.kube/config
    
Now to set autocmpete use:

    kubectl completion bash | sudo tee /etc/bash_completion.d/kubectl > /dev/null
    
After that you need to restart the bash shell

Now to check that everything works run the command

    kubectl get nodes