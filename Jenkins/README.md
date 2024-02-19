# Starting with Jenkins
Jenkins is a framework for CI/CD where is possible define pipelines for test build/deploy/run of a software

The Jenkins Architecture is Master-Slave, the master is a controller node that can launch workload on a slave node using as agent to run command in the slave nodes. Typically Slave node could support different configuration to test the software with different O.S. or different CPUs etc ..

![jenkins-architecture.png](images/jenkins-architecture.png "Jenkins Architecture")

A Jenkins instance is running on host VM or Container configured as controller node, additional nodes  can be added as agent node.
The best way to work is to run test on the Agent Node while the control node is used to overview the system

![./images/jenkins-is-the-way.png](images/jenkins-is-the-way.png)

now we can see how install Jenkins: [How install Jenkins](Jenkins_Installation.md)