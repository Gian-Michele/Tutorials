# Capture packets in Kubernetes

## ksniff
To capture in K8s a possible tool is [ksniff](https://github.com/eldadru/ksniff#installation).
To install it you need [krew](https://krew.sigs.k8s.io/docs/user-guide/quickstart/) installed in you system.

One you have all setup you can run something like this:

    kubectl sniff -n <namespace> <pod-name> [-c <container>] -o <outputfile.pcap>
